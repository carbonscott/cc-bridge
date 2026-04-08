# Remote Filesystem Access

A `bridge-session` may be running that connects to a remote server. Use the `bridge` CLI to access remote files instead of native tools.

## Setup (run once per session)

```bash
bridge-session start -- ssh sdfiana025 'uv run ~/bridge-server --root-dir /path/to/project'
```

For multiple concurrent sessions, use `--name`:
```bash
bridge-session start --name myproject -- ssh sdfiana025 'uv run ~/bridge-server --root-dir /path/to/project'
```

## Commands

```bash
bridge read <path>              # read a file (with line numbers)
bridge read <path> --limit 50  # read first 50 lines
bridge write <path> --file local.py  # write a file
bridge bash "<command>"         # run a shell command
bridge grep "<pattern>" --glob "*.py"  # search files
bridge glob "**/*.py"           # find files
bridge status                   # check session is alive
bridge edit <path>              # edit a remote file in $EDITOR (auto-syncs on save)
bridge edit <path> --editor nano  # use a specific editor
```

For named sessions, add `--session <name>`:
```bash
bridge --session myproject read <path>
```

## Session Management

```bash
bridge-session list              # list all active sessions
bridge-session status myproject   # check a specific session
bridge-session stop myproject     # stop a specific session
```

## Notes

- All paths are relative to the `--root-dir` passed when starting the session
- `bridge write` reads content from `--file` (local file) or stdin
- Check session is running before starting: `bridge status`
- Without `--name`/`--session`, the default session name is `default`
- Set `BRIDGE_SOCKET` env var to override session name resolution with a direct socket path
