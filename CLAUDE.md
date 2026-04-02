# Remote Filesystem Access

A `bridge-session` may be running that connects to a remote server. Use the `bridge` CLI to access remote files instead of native tools.

## Setup (run once per session)

```bash
uv run ~/codes/cc-bridge/bridge-session start -- ssh sdfiana025 'uv run ~/bridge-server --root-dir /path/to/project'
```

## Commands

```bash
uv run ~/codes/cc-bridge/bridge read <path>              # read a file (with line numbers)
uv run ~/codes/cc-bridge/bridge read <path> --limit 50  # read first 50 lines
uv run ~/codes/cc-bridge/bridge write <path> --file local.py  # write a file
uv run ~/codes/cc-bridge/bridge bash "<command>"         # run a shell command
uv run ~/codes/cc-bridge/bridge grep "<pattern>" --glob "*.py"  # search files
uv run ~/codes/cc-bridge/bridge glob "**/*.py"           # find files
uv run ~/codes/cc-bridge/bridge status                   # check session is alive
uv run ~/codes/cc-bridge/bridge edit <path>              # edit a remote file in $EDITOR (auto-syncs on save)
uv run ~/codes/cc-bridge/bridge edit <path> --editor nano  # use a specific editor
```

## Notes

- All paths are relative to the `--root-dir` passed when starting the session
- `bridge write` reads content from `--file` (local file) or stdin
- Check session is running before starting: `uv run ~/codes/cc-bridge/bridge status`
