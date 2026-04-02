# cc-bridge

Minimal bridge for Claude Code remote filesystem access over SSH. Runs a lightweight NDJSON server on a remote host via SSH — no open ports, no daemons.

## Architecture

- **bridge-session** — persistent SSH session daemon; creates a Unix socket locally and pipes requests to the remote server
- **bridge-server** — stateless NDJSON-over-stdio server; runs on the remote host
- **bridge** — CLI client; sends commands to the session socket

## Setup

**1. Start a session:**
```bash
uv run ~/codes/cc-bridge/bridge-session start -- ssh YOUR_HOST 'uv run ~/bridge-server --root-dir /path/to/project'
```

**2. Verify it's running:**
```bash
uv run ~/codes/cc-bridge/bridge status
```

**3. Use the CLI:**
```bash
bridge read <path>                    # read a file (with line numbers)
bridge read <path> --limit 50        # read first 50 lines
bridge write <path> --file local.py  # write a file
bridge bash "<command>"               # run a shell command
bridge grep "<pattern>" --glob "*.py" # search files
bridge glob "**/*.py"                 # find files
bridge edit <path>                    # edit remote file in $EDITOR
```

## Prerequisites

- Python 3.10+ on both local and remote
- `uv` on both local and remote
- SSH key-based auth (no password prompts)

## Tips

- Add `ControlMaster auto` to your `~/.ssh/config` for this host to speed up reconnects.
- `bash` buffers all output before returning — avoid commands with unbounded output (use `head`, `tail`, etc.).
