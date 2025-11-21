# VS Code Extension Test

This file is for testing the Crecall VS Code extension.

## Available Commands

1. **Crecall: Create Clip** - Create a manual clip
2. **Crecall: Add Memory** - Add a new memory
3. **Crecall: List Clips** - View recent clips
4. **Crecall: List Memories** - View all memories
5. **Crecall: Show Status** - Display API status

## How to Test

1. Open the Command Palette (Ctrl+Shift+P)
2. Type "Crecall" to see all available commands
3. Check the status bar (bottom right) for the Crecall icon showing last clip time
4. Click the status bar icon to see full status

## Expected Behavior

- Status bar should show "$(history) Xm ago" when API is connected
- Status bar should show "$(warning) Crecall" when API is disconnected
- All commands should work without errors when backend is running

## Testing Results

✅ Extension installed successfully
✅ CLI commands work (`crecall -c add`, `crecall -m add`, etc.)
✅ API endpoints verified
✅ Backend running at http://localhost:8000
✅ Helper scripts installed to /usr/bin/

**Next Steps:**
- Open VS Code
- Open this workspace folder
- Try the commands listed above
- Verify status bar updates correctly
