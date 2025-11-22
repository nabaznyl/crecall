# Crecall CLI - Clip & Memory Commands Demo

## Overview
Crecall now supports both **clip** and **memory** management via the CLI with instant recall capabilities (<100ms restore time)!

## Quick Start

### List Clips
\`\`\`bash
# Full command
crecall --clip list

# Short forms
crecall -c list
crecall -c ls

# With limit
crecall -c list 5
\`\`\`

**Output:**
\`\`\`
[crecall] Fetching clips from API...
  ID: clip-20251121-133910-fe7a4a
      DB ID: 10 | Name: Auto
      Created: 2025-11-21 13:39:10

  ID: clip-20251121-133830-b761f9
      DB ID: 9 | Name: Auto
      Created: 2025-11-21 13:38:30
\`\`\`

### Resume from Clip (Instant Recall!)
\`\`\`bash
# Using the clip ID from list
crecall -c resume clip-20251121-133910-fe7a4a

# Aliases work too
crecall -c load clip-20251121-133910-fe7a4a
crecall -c restore clip-20251121-133910-fe7a4a
\`\`\`

**Output:**
\`\`\`
[crecall] Restoring from clip: clip-20251121-133910-fe7a4a
✓ Clip restored in 25ms (instant recall!)
{
    "clip_id": "clip-20251121-133910-fe7a4a",
    "content": { ... },
    "git_branch": "main",
    "working_directory": "/home/user/project"
}
\`\`\`

### Create Manual Clip
\`\`\`bash
crecall -c add "Before refactoring auth module"
\`\`\`

### Clear/Prune Clips
\`\`\`bash
# Keeps last 100 clips
crecall -c clear
crecall -c prune  # alias
\`\`\`

## Memory Commands

### Add Memory
\`\`\`bash
crecall -m add "Important architectural decision: using microservices"
\`\`\`

### List Memories
\`\`\`bash
crecall -m list
crecall -m ls  # short form
\`\`\`

### Resume from Memory
\`\`\`bash
crecall -m resume 5
crecall -m load 5  # alias
\`\`\`

## All Command Forms

| Long Form | Short Form | Aliases |
|-----------|------------|---------|
| \`--clip\` | \`-c\` | |
| \`--memory\` | \`-m\` | \`--mem\` |
| \`clip list\` | \`-c ls\` | \`-c list\` |
| \`clip resume\` | \`-c resume\` | \`-c load\`, \`-c restore\` |
| \`clip add\` | \`-c add\` | |
| \`clip clear\` | \`-c clear\` | \`-c prune\` |
| \`memory list\` | \`-m ls\` | \`-m list\` |
| \`memory resume\` | \`-m resume\` | \`-m load\` |
| \`memory add\` | \`-m add\` | |
| \`memory clear\` | \`-m clear\` | |

## Performance

- **Clip Restore**: <100ms (typically 20-50ms)
- **Memory Load**: <100ms
- **Clip List**: <50ms for 10 items

## Requirements

- API must be running: \`http://localhost:8000\`
- Start API: \`cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000\`

## Tips

1. Use \`crecall -c list\` to see clip IDs, then copy/paste the ID to resume
2. Clips are instant recall - perfect for quick context switches
3. Memories are for long-term important notes
4. Both support selection and execution via CLI

## Next Steps

- [x] CLI commands for clips and memories
- [x] Instant recall (<100ms)
- [x] Updated help text
- [ ] Interactive selection menu (fzf integration)
- [ ] Frontend click-to-load for clips/memories
