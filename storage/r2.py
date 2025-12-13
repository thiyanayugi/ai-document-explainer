"""
Cloudflare R2 Storage Module

This module provides S3-compatible storage using Cloudflare R2.
R2 is used for optional document storage with encryption at rest.
"""

import os
import uuid
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def is_storage_enabled():
    """Check if object storage is enabled via environment variable."""
    return os.getenv('ENABLE_OBJECT_STORAGE', 'false').lower() == 'true'


def get_r2_client():
    """
    Create and return an S3-compatible client for Cloudflare R2.
    
    Returns:
        boto3.client: Configured S3 client for R2
        
    Raises:
        ValueError: If required environment variables are missing
    """
    account_id = os.getenv('R2_ACCOUNT_ID')
    access_key_id = os.getenv('R2_ACCESS_KEY_ID')
    secret_access_key = os.getenv('R2_SECRET_ACCESS_KEY')
    
    if not all([account_id, access_key_id, secret_access_key]):
        raise ValueError("Missing R2 credentials. Set R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, and R2_SECRET_ACCESS_KEY")
    
    r2_endpoint = f"https://{account_id}.r2.cloudflarestorage.com"
    
    client = boto3.client(
        's3',
        endpoint_url=r2_endpoint,
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        region_name='auto'
    )
    
    return client


def upload_to_r2(file_bytes, filename, content_type='application/octet-stream'):
    """
    Upload a file to Cloudflare R2 with encryption.
    
    Args:
        file_bytes: File content as bytes
        filename: Original filename
        content_type: MIME type of the file
        
    Returns:
        str: Storage key (path) in R2 bucket, or None if upload failed
    """
    if not is_storage_enabled():
        return None
    
    try:
        client = get_r2_client()
        bucket_name = os.getenv('R2_BUCKET_NAME', 'ai-documents')
        
        # Generate unique key with UUID prefix
        file_uuid = str(uuid.uuid4())
        key = f"documents/{file_uuid}-{filename}"
        
        # Upload with server-side encryption
        client.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=file_bytes,
            ContentType=content_type,
            ServerSideEncryption='AES256',
            Metadata={
                'original-filename': filename,
                'upload-timestamp': str(uuid.uuid1().time)
            }
        )
        
        return key
        
    except ClientError as e:
        print(f"Error uploading to R2: {str(e)}")
        return None
    except ValueError as e:
        print(f"R2 configuration error: {str(e)}")
        return None


def download_from_r2(key):
    """
    Download a file from Cloudflare R2.
    
    Args:
        key: Storage key (path) in R2 bucket
        
    Returns:
        bytes: File content, or None if download failed
    """
    if not is_storage_enabled() or not key:
        return None
    
    try:
        client = get_r2_client()
        bucket_name = os.getenv('R2_BUCKET_NAME', 'ai-documents')
        
        response = client.get_object(Bucket=bucket_name, Key=key)
        return response['Body'].read()
        
    except ClientError as e:
        print(f"Error downloading from R2: {str(e)}")
        return None
    except ValueError as e:
        print(f"R2 configuration error: {str(e)}")
        return None


def delete_from_r2(key):
    """
    Delete a file from Cloudflare R2.
    
    Args:
        key: Storage key (path) in R2 bucket
        
    Returns:
        bool: True if deletion successful, False otherwise
    """
    if not is_storage_enabled() or not key:
        return False
    
    try:
        client = get_r2_client()
        bucket_name = os.getenv('R2_BUCKET_NAME', 'ai-documents')
        
        client.delete_object(Bucket=bucket_name, Key=key)
        return True
        
    except ClientError as e:
        print(f"Error deleting from R2: {str(e)}")
        return False
    except ValueError as e:
        print(f"R2 configuration error: {str(e)}")
        return False


def delete_multiple_from_r2(keys):
    """
    Delete multiple files from Cloudflare R2.
    
    Args:
        keys: List of storage keys to delete
        
    Returns:
        int: Number of successfully deleted files
    """
    if not is_storage_enabled() or not keys:
        return 0
    
    deleted_count = 0
    for key in keys:
        if delete_from_r2(key):
            deleted_count += 1
    
    return deleted_count
