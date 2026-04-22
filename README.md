# cc-bridge

Minimal bridge for Claude Code remote filesystem access over SSH. Runs a lightweight NDJSON server on a remote host via SSH — no open ports, no daemons.

## Architecture

- **bridge-session** — persistent SSH session daemon; creates a Unix socket locally and pipes requests to the remote server
- **bridge-server** — stateless NDJSON-over-stdio server; runs on the remote host
- **bridge** — CLI client; sends commands to the session socket

## Prerequisites

- Python 3.10+ on both local and remote
- `uv` on local (for install) and remote (for `bridge-server`)
- SSH key-based auth (no password prompts)

## Installation

```bash
git clone https://github.com/carbonscott/cc-bridge.git
cd cc-bridge
uv tool install -e .
```

This makes `bridge` and `bridge-session` available globally. With the editable install (`-e`), source changes take effect immediately.

## Setup

**1. Deploy `bridge-server` to the remote host:**

`bridge-server` is a standalone Python script in the repo root. Copy it to your remote host:

```bash
scp bridge-server YOUR_HOST:~/bridge-server
```

The destination path is your choice — examples below use `~/bridge-server`.

**2. Start a session:**
```bash
bridge-session start -- ssh YOUR_HOST 'uv run ~/bridge-server --root-dir /path/to/project'
```

**3. Verify it's running:**
```bash
bridge status
bridge read some/file.py
```

All paths in bridge commands are relative to `--root-dir`.

## Command Reference

| Command | Purpose |
|---------|---------|
| `bridge read <path>` | Read a remote file (line-numbered; `--raw` for redirectable output) |
| `bridge write <path>` | Upload content to remote (from `--file` or stdin) |
| `bridge bash "<cmd>"` | Run a shell command on remote |
| `bridge status` | Check if session is alive |

### read

```bash
bridge read <path>                          # full file (line-numbered)
bridge read <path> --limit 50               # first 50 lines
bridge read <path> --offset 100             # start from line 100 (0-based)
bridge read <path> --offset 100 --limit 50  # lines 100–149
bridge read <path> --raw > local.py         # raw content, safe to redirect
```

### write

```bash
bridge write <path> --file local.py         # from a local file
echo "content" | bridge write <path>        # from stdin
```

### bash

```bash
bridge bash "pwd"
bridge bash "python3 script.py"
bridge bash "rg 'pattern' . -n"                 # search (prefer rg over grep)
bridge bash "fd -e py"                          # find files (prefer fd over find)
bridge --timeout 600 bash "long_running_cmd"    # custom timeout (default: 120s)
bridge --max-output 5000000 bash "big_cmd"      # raise output cap (default: 1MB)
```

### Global flags

Placed **before** the subcommand. All optional.

| Flag | Default | Applies to | Purpose |
|------|---------|------------|---------|
| `--session <name>` | `default` | all | Target a named session |
| `--timeout <N>` | `120` | `bash` | Subprocess timeout in seconds |
| `--max-output <N>` | `1000000` | `bash` | Max output bytes (truncates beyond) |

On timeout, `bash` returns exit code `-1` with stderr `command timed out after Ns`.

### status

```bash
bridge status
```

Returns "Bridge session is active." or exits with an error.

## Editing Workflow

For non-trivial edits, use a local temp file as a staging area:

1. `bridge read <path> --raw > /tmp/myfile.py` — pull content (raw, no line numbers)
2. Edit locally with your preferred tools
3. `bridge write <path> --file /tmp/myfile.py` — push back

This avoids full-file rewrites and gives you incremental diff editing.

## Named Sessions

Run multiple concurrent sessions by giving each a name:

```bash
# Start named sessions
bridge-session start --name project-a -- ssh YOUR_HOST 'uv run ~/bridge-server --root-dir /path/a'
bridge-session start --name project-b -- ssh YOUR_HOST 'uv run ~/bridge-server --root-dir /path/b'

# Use by name
bridge --session project-a read some/file
bridge --session project-b bash "pwd"

# List all sessions
bridge-session list

# Check a specific session
bridge-session status project-a

# Stop a session
bridge-session stop project-a

# Run in foreground (useful for debugging)
bridge-session start --foreground -- ssh YOUR_HOST 'uv run ~/bridge-server --root-dir /path'
```

Without `--name`, sessions default to `default`. Session files are stored under `~/.bridge/<name>/`.

The `BRIDGE_SOCKET` environment variable overrides session name resolution when set directly to a socket path.

## Gotchas

- `bridge read` output includes line numbers (`     1\tline content`). Use `bridge read <path> --raw` for raw content (safe to redirect).
- **Text files only** — content passes through JSON; binary files will be mangled.
- `bridge bash` output is capped at **1 MB** by default. Scope queries with flags or subdirectory paths to stay under the limit, or raise it with `--max-output`.
- All paths are relative to `--root-dir` set when the session was started.

## Tips

- Add `ControlMaster auto` to your `~/.ssh/config` for this host to speed up reconnects.
- `bash` buffers all output before returning — avoid commands with unbounded output (use `head`, `tail`, etc.).
- Prefer `rg` over `grep` and `fd` over `find` inside `bridge bash` — faster, respect `.gitignore`, smaller output.
