# Crecall VS Code Extension - Installation Guide

## Method 1: Development Install (Recommended for Testing)

1. **Ensure Prerequisites**
   ```bash
   # Make sure crecall CLI is in PATH
   which crecall
   # Should output: /usr/local/bin/crecall or similar
   
   # If not in PATH, add symlink:
   sudo ln -s /home/anonmaly/crecall/bin/crecall /usr/local/bin/crecall
   ```

2. **Symlink Extension to VS Code**
   ```bash
   # Linux/Mac
   ln -s /home/anonmaly/crecall/vscode-extension ~/.vscode/extensions/crecall-0.1.0
   
   # Or manually copy
   cp -r /home/anonmaly/crecall/vscode-extension ~/.vscode/extensions/crecall-0.1.0
   ```

3. **Reload VS Code**
   - Press `Ctrl+Shift+P`
   - Type "Developer: Reload Window"
   - Extension should now be active!

4. **Verify Installation**
   - Look for "Crecall" in status bar (bottom right)
   - Press `Ctrl+Shift+P` and search for "Crecall"
   - You should see all 5 commands

## Method 2: Package and Install

1. **Install VSCE**
   ```bash
   npm install -g @vscode/vsce
   ```

2. **Package Extension**
   ```bash
   cd /home/anonmaly/crecall/vscode-extension
   vsce package
   # Creates crecall-0.1.0.vsix
   ```

3. **Install VSIX**
   - In VS Code: Extensions view (`Ctrl+Shift+X`)
   - Click "..." menu → "Install from VSIX..."
   - Select `crecall-0.1.0.vsix`

## Configuration

After installation, configure settings in VS Code:

1. Press `Ctrl+,` to open Settings
2. Search for "Crecall"
3. Set:
   - **API URL**: `http://localhost:8000` (default)
   - **CLI Path**: `crecall` (or full path like `/usr/local/bin/crecall`)
   - **Enable Auto-Clip**: `false` (optional, set to true for auto-clips every 5 min)
   - **Auto-Clip Interval**: `300000` (5 minutes in milliseconds)

Or edit settings.json directly:
```json
{
  "crecall.apiUrl": "http://localhost:8000",
  "crecall.cliPath": "crecall",
  "crecall.enableAutoClip": false,
  "crecall.autoClipInterval": 300000
}
```

## Testing

1. **Start Backend API**
   ```bash
   cd /home/anonmaly/crecall/backend
   source ../.venv/bin/activate
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

2. **Test Commands**
   - `Ctrl+Shift+P` → "Crecall: Create Clip"
   - Enter note (optional)
   - Check status bar updates
   
3. **Test Status**
   - Click status bar item
   - Should show API status and clip count

## Troubleshooting

### Extension Not Appearing
- Check VS Code extensions folder: `~/.vscode/extensions/`
- Ensure folder name matches: `crecall-0.1.0`
- Check extension is activated: View → Output → select "Crecall" from dropdown

### CLI Not Found
```bash
# Add to PATH or use full path in settings
"crecall.cliPath": "/home/anonmaly/crecall/bin/crecall"
```

### API Not Connected
- Status bar shows warning icon
- Check backend is running on localhost:8000
- Verify API URL in settings

### Commands Not Working
- Open Developer Tools: Help → Toggle Developer Tools
- Check Console for errors
- Verify crecall CLI works: `crecall --help`

## Development Mode

To develop/debug the extension:

1. Open `vscode-extension` folder in VS Code
2. Press `F5` to launch Extension Development Host
3. New VS Code window opens with extension loaded
4. Make changes, reload window to test

## Next Steps

- Enable auto-clip for automatic context capture
- Try keybindings for quick clip creation
- Integrate with your workflow!
