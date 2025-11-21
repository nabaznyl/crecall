# Crecall VS Code Extension

## Features

- **Status Bar**: Shows time since last clip
- **Manual Clip Creation**: Command palette → "Crecall: Create Clip"
- **Quick Memory Add**: Command palette → "Crecall: Add Memory"
- **List Clips/Memories**: View clips and memories in output panel
- **Auto-Clip** (optional): Automatic clip creation at configurable intervals

## Commands

- `Crecall: Create Clip` - Create a manual clip with optional note
- `Crecall: Add Memory` - Add a memory to never lose context
- `Crecall: List Clips` - View recent clips
- `Crecall: List Memories` - View all memories
- `Crecall: Show Status` - Show API status and stats

## Configuration

- `crecall.apiUrl`: API server URL (default: http://localhost:8000)
- `crecall.cliPath`: Path to crecall CLI binary (default: crecall)
- `crecall.enableAutoClip`: Enable automatic clip creation (default: false)
- `crecall.autoClipInterval`: Auto-clip interval in milliseconds (default: 300000 = 5 minutes)

## Requirements

- Crecall CLI must be installed and in PATH
- Crecall API server must be running

## Installation

1. Copy this extension to your VS Code extensions folder
2. Reload VS Code
3. Configure settings if needed
4. Start using commands from command palette (Ctrl+Shift+P)

## Usage

### Quick Clip
1. Press `Ctrl+Shift+P`
2. Type "Crecall: Create Clip"
3. Optionally add a note
4. Done! Clip created instantly

### Add Memory
1. Press `Ctrl+Shift+P`
2. Type "Crecall: Add Memory"
3. Enter important note
4. Memory saved forever

### Status Bar
- Click status bar item to see detailed status
- Shows time since last clip
- Warning icon if API is not connected

## Development

```bash
cd vscode-extension
npm install
npm run compile
# Press F5 in VS Code to debug
```

## License

MIT
