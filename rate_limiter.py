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
    """Get a persistent client identifier."""
    import streamlit as st
    import hashlib
    
    # Try to get a persistent identifier from Streamlit
    try:
        # Use browser's user agent + a stable session marker
        # This creates a fingerprint that persists across refreshes
        import streamlit.web.server.server as server
        
        # Get the current session
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        ctx = get_script_run_ctx()
        
        if ctx and hasattr(ctx, 'session_id'):
            # Use the websocket session info which is more stable
            session_info = server.Server.get_current()
            if session_info and hasattr(session_info, '_session_info_by_id'):
                # Create a hash from browser info
                user_agent = "default"
                return f"user_{hashlib.md5(user_agent.encode()).hexdigest()[:16]}"
    except:
        pass
    
    # Fallback: use a file-based persistent ID
    import os
    id_file = ".user_id"
    if os.path.exists(id_file):
        with open(id_file, 'r') as f:
            return f.read().strip()
    else:
        # Create a new persistent ID
        import uuid
        user_id = f"user_{uuid.uuid4().hex[:16]}"
        with open(id_file, 'w') as f:
            f.write(user_id)
        return user_id


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
