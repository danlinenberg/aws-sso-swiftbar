#!/bin/bash
# AWS SSO Login for any profile (with logout first)
# Usage: login.sh <profile-name>
# This will logout the current SSO session and create a fresh one

PROFILE="${1:-prod}"

# Logout first to clear current session, then login with fresh session
open -a Terminal && sleep 0.5 && osascript -e "tell application \"Terminal\" to do script \"/opt/homebrew/bin/aws sso logout --profile $PROFILE && /opt/homebrew/bin/aws sso login --profile $PROFILE\""
