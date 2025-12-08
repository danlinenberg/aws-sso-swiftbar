#!/usr/bin/env python3
"""
AWS SSO Session Status for SwiftBar
Monitors AWS SSO session expiration and provides quick login access
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import configparser


PROFILE_PREF_FILE = Path.home() / ".aws" / "swiftbar-profile"


def get_all_sso_profiles():
    """Get all SSO profiles from AWS config"""
    config_path = Path.home() / ".aws" / "config"
    if not config_path.exists():
        return []

    config = configparser.ConfigParser()
    config.read(config_path)

    profiles = []
    for section in config.sections():
        # Check if this profile has SSO configured
        if "sso_start_url" in config[section]:
            # Extract profile name
            if section == "DEFAULT":
                profiles.append("default")
            elif section.startswith("profile "):
                profiles.append(section[8:])  # Remove "profile " prefix

    # Also check DEFAULT section
    if "DEFAULT" in config and "sso_start_url" in config["DEFAULT"]:
        if "default" not in profiles:
            profiles.insert(0, "default")

    return profiles


def get_selected_profile():
    """Get the currently selected profile from preferences"""
    if PROFILE_PREF_FILE.exists():
        try:
            return PROFILE_PREF_FILE.read_text().strip()
        except:
            pass
    return "prod"  # Default


def set_selected_profile(profile_name):
    """Save the selected profile to preferences"""
    PROFILE_PREF_FILE.write_text(profile_name)


def get_sso_start_url(profile_name):
    """Get SSO start URL from AWS config for the specified profile"""
    config_path = Path.home() / ".aws" / "config"
    if not config_path.exists():
        return None

    config = configparser.ConfigParser()
    config.read(config_path)

    section = f"profile {profile_name}" if profile_name != "default" else "DEFAULT"
    if section in config and "sso_start_url" in config[section]:
        return config[section]["sso_start_url"]
    return None


def get_sso_cache_key(sso_start_url):
    """Generate cache key from SSO start URL (SHA1 hash)"""
    return hashlib.sha1(sso_start_url.encode()).hexdigest()


def find_sso_token(profile_name):
    """Find and parse SSO token for the given profile"""
    sso_start_url = get_sso_start_url(profile_name)
    if not sso_start_url:
        return None

    cache_dir = Path.home() / ".aws" / "sso" / "cache"
    if not cache_dir.exists():
        return None

    cache_key = get_sso_cache_key(sso_start_url)
    cache_file = cache_dir / f"{cache_key}.json"

    if cache_file.exists():
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
                return data
        except (json.JSONDecodeError, IOError):
            pass

    # Fallback: search all cache files for matching startUrl
    for cache_file in cache_dir.glob("*.json"):
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
                if data.get("startUrl") == sso_start_url:
                    return data
        except (json.JSONDecodeError, IOError):
            continue

    return None


def format_time_remaining(seconds):
    """Format seconds into human-readable time"""
    if seconds <= 0:
        return "Expired"

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    if hours > 0:
        return f"{hours}h"
    else:
        return f"{minutes}m"


def get_color(seconds_remaining):
    """Get color based on time remaining"""
    if seconds_remaining <= 0:
        return "red"
    elif seconds_remaining < 1800:  # 30 minutes
        return "red"
    elif seconds_remaining < 7200:  # 2 hours
        return "yellow"
    else:
        return "#7ED321"  # Light green


def format_datetime(iso_string):
    """Format ISO datetime string to readable format"""
    try:
        dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        local_dt = dt.astimezone()
        return local_dt.strftime("%b %d, %Y %H:%M")
    except:
        return iso_string


def main():
    # Handle profile selection
    if len(sys.argv) > 1 and sys.argv[1] == "select-profile":
        if len(sys.argv) > 2:
            profile_name = sys.argv[2]
            set_selected_profile(profile_name)
        sys.exit(0)

    profile = get_selected_profile()
    token_data = find_sso_token(profile)

    if not token_data or "expiresAt" not in token_data:
        # No valid session found
        print("☁️ No Session | color=red")
        print("---")
        print(f"No AWS SSO session found for '{profile}'")
        login_script = Path(__file__).parent / "login.sh"
        print(f"🔐 Login to AWS SSO | bash={login_script} param1={profile} terminal=false")
        print("---")

        # Profile selector
        print("Switch Profile")
        all_profiles = get_all_sso_profiles()
        for p in all_profiles:
            script_path = Path(__file__).resolve()
            checkmark = "✓ " if p == profile else ""
            print(f"--{checkmark}{p} | bash={script_path} param1=select-profile param2={p} terminal=false refresh=true")

        return

    # Parse expiration time
    expires_at = token_data["expiresAt"]
    try:
        expiry_dt = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        seconds_remaining = (expiry_dt - now).total_seconds()
    except:
        print("☁️ Error | color=red")
        print("---")
        print("Could not parse expiration time")
        return

    # Format display
    time_str = format_time_remaining(int(seconds_remaining))
    color = get_color(seconds_remaining)

    # Menu bar display
    print(f"☁️ {time_str} | color={color}")
    print("---")

    # Dropdown menu
    print(f"AWS SSO Status ({profile})")
    print(f"Expires: {format_datetime(expires_at)}")
    print(f"Time Remaining: {time_str}")

    if seconds_remaining <= 0:
        print(f"🔴 Session Expired")
    elif seconds_remaining < 1800:
        print(f"🔴 Expiring Soon")
    elif seconds_remaining < 7200:
        print(f"🟡 Expires in < 2 hours")
    else:
        print(f"🟢 Session Active")

    print("---")

    # Action buttons
    login_script = Path(__file__).parent / "login.sh"

    # Always show refresh button (enabled)
    if seconds_remaining <= 0:
        print(f"🔐 Login to AWS SSO | bash={login_script} param1={profile} terminal=false")
    else:
        print(f"🔐 Refresh Session | bash={login_script} param1={profile} terminal=false")

    # AWS Console link
    region = token_data.get("region", "us-east-1")
    start_url = token_data.get("startUrl", "")
    if start_url:
        print(f"🌐 Open AWS Console | href={start_url}")

    print("---")

    # Profile selector
    print("Switch Profile")
    all_profiles = get_all_sso_profiles()
    script_path = Path(__file__).resolve()
    for p in all_profiles:
        checkmark = "✓ " if p == profile else ""
        print(f"--{checkmark}{p} | bash={script_path} param1=select-profile param2={p} terminal=false refresh=true")


if __name__ == "__main__":
    main()
