# cc-bridge

Minimal bridge for Claude Code remote filesystem access over SSH. Runs a lightweight NDJSON server on a remote host via SSH — no open ports, no daemons.

## Architecture

- **bridge-session** — persistent SSH session daemon; creates a Unix socket locally and pipes requests to the remote server
- **bridge-server** — stateless NDJSON-over-stdio server; runs on the remote host
- **bridge** — CLI client; sends commands to the session socket

## Installation

```bash
uv tool install -e ~/codes/cc-bridge
```

This makes `bridge` and `bridge-session` available globally. With the editable install (`-e`), source changes take effect immediately.

## Setup

**1. Start a session:**
```bash
bridge-session start -- ssh YOUR_HOST 'uv run ~/bridge-server --root-dir /path/to/project'
```

**2. Verify it's running:**
```bash
bridge status
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
bridge status                         # check session is alive
```

## Named Sessions

Run multiple concurrent sessions by giving each a name:

```bash
# Start named sessions
bridge-session start --name project-a -- ssh host 'uv run ~/bridge-server --root-dir /path/a'
bridge-session start --name project-b -- ssh host 'uv run ~/bridge-server --root-dir /path/b'

# Use by name
bridge --session project-a read some/file
bridge --session project-b grep "pattern"

# List all sessions
bridge-session list

# Check a specific session
bridge-session status project-a

# Stop a session
bridge-session stop project-a
```

Without `--name`, sessions default to `default`. Session files are stored under `~/.bridge/<name>/`.

The `BRIDGE_SOCKET` environment variable overrides session name resolution when set directly to a socket path.

## Prerequisites

- Python 3.10+ on both local and remote
- `uv` on local (for install) and remote (for `bridge-server`)
- SSH key-based auth (no password prompts)

## Tips

- Add `ControlMaster auto` to your `~/.ssh/config` for this host to speed up reconnects.
- `bash` buffers all output before returning — avoid commands with unbounded output (use `head`, `tail`, etc.).
