# AWS SSO Menu Bar Plugin for SwiftBar

A macOS menu bar plugin that shows your AWS SSO session status and provides one-click login when needed.

## Features

- **Real-time session monitoring**: Shows time remaining in menu bar (updates every 10 seconds)
- **Color-coded status**: Green (>2hrs), Yellow (30min-2hrs), Red (<30min/expired)
- **Smart refresh button**: Automatically disabled when session is healthy (>2hrs remaining)
- **Multi-profile support**: Switch between AWS profiles (prod, backend, dev, etc.)
- **One-click login**: Opens Terminal and runs AWS SSO login when clicked
- **Session details**: Shows exact expiration time and status in dropdown

## Screenshots

<img width="271" height="345" alt="image" src="https://github.com/user-attachments/assets/d727f377-7515-479e-a25f-19048d01f258" />

Dropdown menu shows:
- Session status and expiration time
- 🔐 Refresh Session button (greyed out when >2hrs remaining)
- 🌐 Open AWS Console link
- Profile switcher

## Quick Installation

**One-command install:**

```bash
git clone https://github.com/YOUR_USERNAME/aws-sso-swiftbar.git
cd aws-sso-swiftbar
./install.sh
```

The installer will:
- ✅ Check prerequisites (Homebrew, AWS CLI, SwiftBar)
- ✅ Install SwiftBar if needed
- ✅ Set up the plugin directory
- ✅ Configure SwiftBar
- ✅ Test the installation

**After installation:** Click the SwiftBar icon → **Enable All** to activate the plugin.

Then look for the ☁️ icon in your menu bar!

---

## Prerequisites

- macOS
- [Homebrew](https://brew.sh/)
- AWS CLI configured with SSO profiles
- (Optional) [SwiftBar](https://swiftbar.app/) - the installer can install this for you

## Manual Installation

If you prefer to install manually or the automatic installer doesn't work:

### 1. Install SwiftBar

```bash
brew install swiftbar
```

### 2. Clone this repository

```bash
git clone https://github.com/YOUR_USERNAME/aws-sso-swiftbar.git
cd aws-sso-swiftbar
```

### 3. Create SwiftBar plugin directory

```bash
mkdir -p ~/.swiftbar-plugins
```

### 4. Install plugin files

```bash
# Option A: Symlink (changes in repo reflect immediately)
ln -sf "$(pwd)/aws-sso-status.10s.py" ~/.swiftbar-plugins/
ln -sf "$(pwd)/login.sh" ~/.swiftbar-plugins/

# Option B: Copy (standalone installation)
cp aws-sso-status.10s.py login.sh ~/.swiftbar-plugins/
chmod +x ~/.swiftbar-plugins/*.{py,sh}
```

### 5. Configure SwiftBar

1. Open SwiftBar (should be in your Applications folder)
2. Click the SwiftBar icon in your menu bar
3. Select **Preferences** or **Change Plugin Folder**
4. Set plugin folder to: `~/.swiftbar-plugins` (or the full path: `/Users/YOUR_USERNAME/.swiftbar-plugins`)
5. Click **Refresh All**

### 6. Enable the plugin

**Important:** After installing, you must enable the plugin:

1. Click the **SwiftBar icon** in your menu bar
2. Select **Enable All**

This activates the plugin and makes the `☁️` icon appear.

### 7. Verify installation

You should now see a `☁️` icon in your menu bar showing your AWS SSO session time.

## Configuration

### Default Profile

The plugin defaults to the `prod` profile. Your selected profile is saved in `~/.aws/swiftbar-profile`.

### Adding More Profiles

The plugin automatically works with any AWS SSO profile configured in your `~/.aws/config`. Just:
1. Add the profile to your AWS config
2. Switch to it via the "Switch Profile" menu
3. Click "Refresh Session" when needed

No additional configuration required!

### Custom AWS CLI Path

If your AWS CLI is not at `/opt/homebrew/bin/aws`, edit `login.sh` and update the path:

```bash
# Find your AWS CLI path
which aws

# Edit login.sh and update the path
```

The installer does this automatically for you.

## Usage

### View Status

Click the `☁️` icon in your menu bar to see:
- Current profile and session status
- Exact expiration time
- Time remaining

### Refresh Session

Click **🔐 Refresh Session** to:
- Open a Terminal window
- Run `aws sso login` for your current profile
- Authenticate via browser
- Get a new 8-hour session

The button is greyed out when your session has >2 hours remaining.

### Switch Profiles

1. Click the `☁️` icon
2. Navigate to **Switch Profile**
3. Select your desired profile
4. The menu bar updates to show that profile's session status

### Open AWS Console

Click **🌐 Open AWS Console** to open your AWS SSO start URL in your browser.

## Customization

### Update Interval

The plugin refreshes every 10 seconds. To change this, rename the file:

```bash
# For 30-second updates:
mv aws-sso-status.10s.py aws-sso-status.30s.py

# For 5-second updates:
mv aws-sso-status.10s.py aws-sso-status.5s.py
```

### Color Thresholds

Edit `aws-sso-status.10s.py` and modify the `get_color()` function:

```python
def get_color(seconds_remaining):
    if seconds_remaining <= 0:
        return "red"
    elif seconds_remaining < 1800:  # 30 minutes - change this
        return "red"
    elif seconds_remaining < 7200:  # 2 hours - change this
        return "yellow"
    else:
        return "#7ED321"  # Light green - change this hex code
```

### Disable Button Threshold

Edit `aws-sso-status.10s.py` and find the section that disables the button:

```python
else:  # More than 2 hours remaining - change this threshold
    hours_left = int(seconds_remaining // 3600)
    print(f"🔐 Refresh Session | disabled=true tooltip='Session still valid for {hours_left}+ hours. Refresh not needed yet.'")
```

## Troubleshooting

### Menu bar icon not appearing

1. Check SwiftBar is running: `ps aux | grep SwiftBar`
2. Verify plugin folder: SwiftBar → Preferences → Plugin Folder
3. Check file is executable: `ls -la ~/.swiftbar-plugins/aws-sso-status.10s.py`
4. Test plugin directly: `~/.swiftbar-plugins/aws-sso-status.10s.py`

### Refresh button doesn't work

1. Verify AWS CLI path: `which aws`
2. Check login script is executable: `ls -la ~/.swiftbar-plugins/login-*.sh`
3. Test script directly: `~/.swiftbar-plugins/login-prod.sh`
4. Check Terminal has permission to run AppleScript

### Time not updating after login

Wait 10 seconds for the plugin to refresh, or manually refresh SwiftBar.

### Profile switching doesn't work

Check that the `refresh=true` parameter is in the profile buttons. The menu bar should update within 10 seconds of switching profiles.

## File Structure

```
aws-sso-swiftbar/
├── README.md                    # This file
├── install.sh                   # One-command installer
├── aws-sso-status.10s.py        # Main plugin (Python)
└── login.sh                     # Generic login helper for all profiles
```

## How It Works

1. **Token Discovery**: Reads `~/.aws/config` to find SSO profiles and their start URLs
2. **Cache Reading**: Checks `~/.aws/sso/cache/*.json` for cached SSO tokens
3. **Expiration Calculation**: Parses the `expiresAt` field and calculates time remaining
4. **Display**: Formats the output according to SwiftBar's plugin format
5. **Profile Persistence**: Stores selected profile in `~/.aws/swiftbar-profile`

## License

MIT

## Contributing

This is a personal utility. Feel free to fork and customize for your own use.
