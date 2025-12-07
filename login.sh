#!/bin/bash
# AWS SSO Login for any profile
# Usage: login.sh <profile-name>

PROFILE="${1:-prod}"

open -a Terminal && sleep 0.5 && osascript -e "tell application \"Terminal\" to do script \"/opt/homebrew/bin/aws sso login --profile $PROFILE\""
