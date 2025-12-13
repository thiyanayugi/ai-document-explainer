"""
Rate limiting module using IP-based tracking with time windows.
Prevents users from bypassing limits by refreshing the browser.
"""

import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

# Rate limit configuration
RATE_LIMIT_FILE = ".rate_limits.json"
ANALYSIS_LIMIT = 10
CHAT_LIMIT = 20
TIME_WINDOW_HOURS = 24  # Reset after 24 hours


def get_rate_limits():
    """Load rate limits from file."""
    if not os.path.exists(RATE_LIMIT_FILE):
        return {}
    
    try:
        with open(RATE_LIMIT_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}


def save_rate_limits(limits):
    """Save rate limits to file."""
    try:
        with open(RATE_LIMIT_FILE, 'w') as f:
            json.dump(limits, f)
    except:
        pass


def clean_old_entries(limits):
    """Remove entries older than TIME_WINDOW_HOURS."""
    cutoff_time = time.time() - (TIME_WINDOW_HOURS * 3600)
    cleaned = {}
    
    for ip, data in limits.items():
        if data.get('last_reset', 0) > cutoff_time:
            cleaned[ip] = data
    
    return cleaned


def get_client_ip():
    """Get client IP address from Streamlit."""
    try:
        import streamlit as st
        # Try to get real IP from headers (works with reverse proxies)
        ctx = st.runtime.scriptrunner.get_script_run_ctx()
        if ctx:
            session_id = ctx.session_id
            # Use session_id as a proxy for IP (more reliable in Streamlit)
            return f"session_{session_id}"
    except:
        pass
    
    # Fallback to a default identifier
    return "default_user"


def check_rate_limit(limit_type='analysis'):
    """
    Check if user has exceeded rate limit.
    
    Args:
        limit_type: 'analysis' or 'chat'
        
    Returns:
        tuple: (can_proceed: bool, remaining: int, error_message: str)
    """
    client_ip = get_client_ip()
    limits = get_rate_limits()
    
    # Clean old entries
    limits = clean_old_entries(limits)
    
    # Get or create user entry
    if client_ip not in limits:
        limits[client_ip] = {
            'analysis_count': 0,
            'chat_count': 0,
            'last_reset': time.time()
        }
    
    user_data = limits[client_ip]
    
    # Check if we need to reset (24 hours passed)
    if time.time() - user_data.get('last_reset', 0) > (TIME_WINDOW_HOURS * 3600):
        user_data = {
            'analysis_count': 0,
            'chat_count': 0,
            'last_reset': time.time()
        }
        limits[client_ip] = user_data
    
    # Check limit based on type
    if limit_type == 'analysis':
        current_count = user_data.get('analysis_count', 0)
        max_limit = ANALYSIS_LIMIT
        remaining = max_limit - current_count
        
        if current_count >= max_limit:
            hours_until_reset = TIME_WINDOW_HOURS - ((time.time() - user_data['last_reset']) / 3600)
            return False, 0, f"Analysis limit reached ({max_limit}/{max_limit}). Resets in {hours_until_reset:.1f} hours."
        
        return True, remaining, ""
    
    elif limit_type == 'chat':
        current_count = user_data.get('chat_count', 0)
        max_limit = CHAT_LIMIT
        remaining = max_limit - current_count
        
        if current_count >= max_limit:
            hours_until_reset = TIME_WINDOW_HOURS - ((time.time() - user_data['last_reset']) / 3600)
            return False, 0, f"Chat limit reached ({max_limit}/{max_limit}). Resets in {hours_until_reset:.1f} hours."
        
        return True, remaining, ""
    
    return True, 0, ""


def increment_rate_limit(limit_type='analysis'):
    """Increment the rate limit counter for the user."""
    client_ip = get_client_ip()
    limits = get_rate_limits()
    
    if client_ip not in limits:
        limits[client_ip] = {
            'analysis_count': 0,
            'chat_count': 0,
            'last_reset': time.time()
        }
    
    if limit_type == 'analysis':
        limits[client_ip]['analysis_count'] = limits[client_ip].get('analysis_count', 0) + 1
    elif limit_type == 'chat':
        limits[client_ip]['chat_count'] = limits[client_ip].get('chat_count', 0) + 1
    
    save_rate_limits(limits)


def get_usage_stats():
    """Get current usage statistics for the user."""
    client_ip = get_client_ip()
    limits = get_rate_limits()
    
    if client_ip not in limits:
        return {
            'analysis_count': 0,
            'chat_count': 0,
            'analysis_remaining': ANALYSIS_LIMIT,
            'chat_remaining': CHAT_LIMIT
        }
    
    user_data = limits[client_ip]
    
    return {
        'analysis_count': user_data.get('analysis_count', 0),
        'chat_count': user_data.get('chat_count', 0),
        'analysis_remaining': ANALYSIS_LIMIT - user_data.get('analysis_count', 0),
        'chat_remaining': CHAT_LIMIT - user_data.get('chat_count', 0)
    }
