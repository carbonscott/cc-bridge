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
bridge read <path>                   # read a file (with line numbers)
bridge read <path> --limit 50        # read first 50 lines
bridge read <path> --raw > local.py  # download raw content to a local file
bridge write <path> --file local.py  # upload a local file to remote
bridge bash "<command>"              # run a shell command (use rg/fd for search)
bridge status                        # check session is alive
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
- `bridge read --raw` prints unadorned content — redirect to a file with `>` to download without flooding your context
- For searching/listing remote files, use `bridge bash "rg ..."` or `bridge bash "fd ..."`
- Check session is running before starting: `bridge status`
- Without `--name`/`--session`, the default session name is `default`
- Set `BRIDGE_SOCKET` env var to override session name resolution with a direct socket path
