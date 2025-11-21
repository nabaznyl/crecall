# crecall Installation Guide

## Quick Install (Local Repository)

The `crecall` package is now available via APT from a local repository.

### 1. Repository is Already Configured

The local repository is located at:
```
~/repo/crecall/
```

APT source configured in:
```
/etc/apt/sources.list.d/crecall-local.list
```

### 2. Install Package

```bash
sudo apt update
sudo apt install crecall
```

### 3. Verify Installation

```bash
which crecall           # Should show /usr/bin/crecall
crecall version         # Should show 0.1.0a
crecall help            # Show all commands
```

### 4. First Run

```bash
# Create initial checkpoint
crecall save "Initial checkpoint"

# View summary
crecall summary

# Add memory item
crecall memory add "Installation completed"
```

## Package Details

- **Package**: crecall_0.1.0a-1_all.deb
- **Location**: ~/repo/crecall/crecall_0.1.0a-1_all.deb
- **Data Directory**: ~/.recall_chat (auto-created on first run)
- **Dependencies**: bash, python3, jq, openssl (auto-installed)

## Available Commands

```
save [note]              Save checkpoint
summary|refer            Show summary
total <file>             Plain transcript & pause
total-encrypt <file>     Encrypted transcript & pause
resume --yes             Resume if paused
pause                    Pause session
memory add <text>        Add memory item
memory list [N]          List last N (default 20)
memory clear             Clear memory log
encrypt <file>           Encrypt file
decrypt <file.enc>       Decrypt file
cache prune --keep-last N [--dry-run]
data clear               Wipe log + transcripts
state                    Show state JSON
version                  Show version
help                     Show this help
```

## Migration from Legacy Versions

The package automatically migrates data from:
- `~/.chat_recall/` (original location)
- `~/.crecall/` (previous test location)

Data is migrated to `~/.recall_chat/` on first run.

## Encryption

- Uses AES-256-CBC with PBKDF2
- Auto-generated passphrase: `~/.recall_chat/passphrase`
- Passphrase is created on first encrypted operation
- Keep passphrase file secure (chmod 600)

## Uninstall

```bash
sudo apt remove crecall
```

To remove all data:
```bash
crecall data clear      # Interactive confirmation
# OR manually:
rm -rf ~/.recall_chat
```

## Rebuild Package

If modifications are needed:

```bash
cd ~/crecall
# Edit files in bin/ or debian/
dpkg-buildpackage -us -uc
cp ../crecall_*.deb ~/repo/crecall/
cd ~/repo/crecall
dpkg-scanpackages . /dev/null > Packages
sudo apt update
sudo apt install --reinstall crecall
```

## Testing

Run test suite with preview script:
```bash
crecall-preview
```

## Support

- Homepage: https://example.com/crecall
- Maintainer: Local Maintainer <maintainer@example.com>
- Version: 0.1.0a (preview build)
