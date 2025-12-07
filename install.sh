#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🚀 AWS SSO SwiftBar Plugin Installer"
echo "===================================="
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PLUGIN_DIR="$HOME/.swiftbar-plugins"

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Check prerequisites
echo "Checking prerequisites..."
echo ""

# Check for Homebrew
if ! command -v brew &> /dev/null; then
    print_error "Homebrew is not installed"
    echo "Please install Homebrew first: https://brew.sh"
    exit 1
fi
print_success "Homebrew found"

# Check for AWS CLI
if ! command -v aws &> /dev/null; then
    print_error "AWS CLI is not installed"
    echo "Install it with: brew install awscli"
    exit 1
fi
AWS_CLI_PATH=$(which aws)
print_success "AWS CLI found at: $AWS_CLI_PATH"

# Check for AWS config
if [ ! -f "$HOME/.aws/config" ]; then
    print_error "AWS config not found at ~/.aws/config"
    echo "Please configure AWS SSO first with: aws configure sso"
    exit 1
fi
print_success "AWS config found"

# Check/Install SwiftBar
echo ""
if ! command -v swiftbar &> /dev/null && [ ! -d "/Applications/SwiftBar.app" ]; then
    print_info "SwiftBar not found. Installing..."
    brew install swiftbar
    print_success "SwiftBar installed"
else
    print_success "SwiftBar found"
fi

# Create plugin directory
echo ""
print_info "Setting up plugin directory..."
mkdir -p "$PLUGIN_DIR"
print_success "Plugin directory created: $PLUGIN_DIR"

# Copy or symlink files
echo ""
print_info "Installing plugin files..."

# Ask user if they want to copy or symlink
echo ""
echo "Installation method:"
echo "  1) Symlink (recommended for development - changes in repo reflect immediately)"
echo "  2) Copy (standalone installation)"
read -p "Choose [1/2] (default: 1): " INSTALL_METHOD
INSTALL_METHOD=${INSTALL_METHOD:-1}

# Remove existing files/symlinks first
rm -f "$PLUGIN_DIR/aws-sso-status.10s.py" "$PLUGIN_DIR/login.sh"

if [ "$INSTALL_METHOD" == "1" ]; then
    # Symlink
    ln -sf "$SCRIPT_DIR/aws-sso-status.10s.py" "$PLUGIN_DIR/"
    ln -sf "$SCRIPT_DIR/login.sh" "$PLUGIN_DIR/"
    print_success "Files symlinked to $PLUGIN_DIR"
else
    # Copy
    cp "$SCRIPT_DIR/aws-sso-status.10s.py" "$PLUGIN_DIR/"
    cp "$SCRIPT_DIR/login.sh" "$PLUGIN_DIR/"
    chmod +x "$PLUGIN_DIR/aws-sso-status.10s.py"
    chmod +x "$PLUGIN_DIR/login.sh"
    print_success "Files copied to $PLUGIN_DIR"
fi

# Update AWS CLI path in login.sh if needed
if [ "$AWS_CLI_PATH" != "/opt/homebrew/bin/aws" ]; then
    print_info "Updating AWS CLI path in login.sh..."
    if [ "$INSTALL_METHOD" == "1" ]; then
        # For symlink, we need to update the source file
        sed -i '' "s|/opt/homebrew/bin/aws|$AWS_CLI_PATH|g" "$SCRIPT_DIR/login.sh"
    else
        # For copy, update the copied file
        sed -i '' "s|/opt/homebrew/bin/aws|$AWS_CLI_PATH|g" "$PLUGIN_DIR/login.sh"
    fi
    print_success "AWS CLI path updated to: $AWS_CLI_PATH"
fi

# Configure SwiftBar
echo ""
print_info "Configuring SwiftBar..."

# Check if SwiftBar is running
if pgrep -x "SwiftBar" > /dev/null; then
    print_info "SwiftBar is already running"
else
    print_info "Starting SwiftBar..."
    open -a SwiftBar
    sleep 2
fi

# Set plugin directory
defaults write com.ameba.SwiftBar PluginDirectory "$PLUGIN_DIR"
print_success "Plugin directory configured"

# Refresh SwiftBar
open "swiftbar://refreshallplugins" 2>/dev/null || true
sleep 1

# Test the plugin
echo ""
print_info "Testing plugin..."
if "$PLUGIN_DIR/aws-sso-status.10s.py" > /dev/null 2>&1; then
    print_success "Plugin test successful"
else
    print_error "Plugin test failed"
    echo "You may need to configure AWS SSO first"
fi

# Final instructions
echo ""
echo "===================================="
echo -e "${GREEN}Installation complete!${NC}"
echo "===================================="
echo ""
echo "Next steps:"
echo "  1. Look for the ☁️ icon in your menu bar"
echo "  2. Click it to see your AWS SSO session status"
echo "  3. If you don't see it, open SwiftBar preferences and set:"
echo "     Plugin Folder: $PLUGIN_DIR"
echo "  4. Click 'Refresh All' in SwiftBar menu"
echo ""
echo "Troubleshooting:"
echo "  • If the icon doesn't appear, restart SwiftBar:"
echo "    killall SwiftBar && open -a SwiftBar"
echo ""
echo "  • To test the plugin manually:"
echo "    $PLUGIN_DIR/aws-sso-status.10s.py"
echo ""
echo "Enjoy! 🎉"
