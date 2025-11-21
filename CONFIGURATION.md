# crecall Configuration

Configuration file: `~/.recall_memory/config.json`
Created automatically if missing when running `crecall --settings`.

## Editable Fields (via Settings Menu)
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| auto_save_minutes | integer | 5 | Interval for future auto-save/auto-clip logic (minutes). |
| clip_keep_last | integer | 100 | Retention target for pruning old clips via planned pruning feature. |
| theme | string | "dark" | Preferred UI theme (frontend may adopt later). |
| enable_auto_clip | boolean | false | Placeholder flag to automatically create clips on interval/events. |

## Commands
```bash
# Open interactive menu
crecall --settings
crecall -o
```

## Manual Editing
You may edit `config.json` directly. Fields outside the allowed set may be ignored by future versions.

## Environment Overrides (Planned)
| Variable | Overrides |
|----------|-----------|
| CRECALL_AUTO_SAVE_MINUTES | auto_save_minutes |
| CRECALL_CLIP_KEEP_LAST | clip_keep_last |
| CRECALL_THEME | theme |
| CRECALL_ENABLE_AUTO_CLIP | enable_auto_clip |

If set, environment variables would take precedence during runtime (feature pending implementation).

## Future Additions
- `encryption_mode` (aes-gcm vs aes-cbc)
- `crash_alert` (enable notification on recovery)
- `max_memory_results` (default limit for memory list/search)

## Validation Behavior
- Non-integer numeric fields fallback to default.
- Unsupported theme values fallback to `dark`.
- Boolean parsing accepts: true/false (case-insensitive).

---
This file documents current config scope; extended as features mature.
