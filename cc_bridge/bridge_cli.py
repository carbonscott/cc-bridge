"""cc-bridge CLI: send commands to a running bridge session.

Usage:
    bridge [--session NAME] [--timeout N] [--max-output N] read <path> [--offset N] [--limit N] [--raw]
    bridge [--session NAME] [--timeout N] [--max-output N] write <path> [--file LOCAL_FILE | stdin]
    bridge [--session NAME] [--timeout N] [--max-output N] bash <command>
    bridge [--session NAME] status
"""

import argparse
import json
import os
import socket
import sys
import uuid
from pathlib import Path

DEFAULT_DIR = Path.home() / ".bridge"
DEFAULT_NAME = "default"
DEFAULT_MAX_OUTPUT = 1_000_000


def _resolve_socket(session_name: str) -> Path:
    """Resolve the socket path for a named session."""
    env = os.environ.get("BRIDGE_SOCKET")
    if env:
        return Path(env)
    return DEFAULT_DIR / session_name / "session.sock"


def send_request(request: dict, sock_path: Path) -> dict:
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        sock.connect(str(sock_path))
    except (ConnectionRefusedError, FileNotFoundError):
        print(f"Error: No active bridge session at {sock_path}", file=sys.stderr)
        print("  Start one with: bridge-session start --name <name> -- ssh host 'bridge-server --root-dir /path'", file=sys.stderr)
        sys.exit(2)

    try:
        sock.sendall((json.dumps(request) + "\n").encode())
        sock.shutdown(socket.SHUT_WR)

        data = b""
        while True:
            chunk = sock.recv(65536)
            if not chunk:
                break
            data += chunk
    finally:
        sock.close()

    if not data:
        print("Error: Empty response from session", file=sys.stderr)
        sys.exit(2)

    return json.loads(data.decode())


def make_id() -> str:
    return uuid.uuid4().hex[:8]


def cmd_read(args, sock_path):
    request = {
        "id": make_id(),
        "cmd": "read",
        "args": {"path": args.path},
    }
    if args.offset:
        request["args"]["offset"] = args.offset
    if args.limit:
        request["args"]["limit"] = args.limit
    if args.raw:
        request["args"]["raw"] = True

    resp = send_request(request, sock_path)
    if not resp.get("ok"):
        print(f"Error: {resp.get('error', 'unknown')}", file=sys.stderr)
        sys.exit(1)
    if args.raw:
        sys.stdout.write(resp["data"]["content"])
    else:
        print(resp["data"]["content"])


def cmd_write(args, sock_path):
    if args.file:
        content = Path(args.file).read_text()
    else:
        content = sys.stdin.read()

    request = {
        "id": make_id(),
        "cmd": "write",
        "args": {"path": args.path, "content": content},
    }

    resp = send_request(request, sock_path)
    if not resp.get("ok"):
        print(f"Error: {resp.get('error', 'unknown')}", file=sys.stderr)
        sys.exit(1)
    d = resp["data"]
    print(f"Wrote {d['bytes_written']} bytes to {d['path']}")


def cmd_bash(args, sock_path):
    request = {
        "id": make_id(),
        "cmd": "bash",
        "args": {
            "command": args.command,
            "timeout": args.timeout,
            "max_output": args.max_output,
        },
    }

    resp = send_request(request, sock_path)
    if not resp.get("ok"):
        print(f"Error: {resp.get('error', 'unknown')}", file=sys.stderr)
        sys.exit(1)

    d = resp["data"]
    if d["stdout"]:
        print(d["stdout"], end="")
    if d["stderr"]:
        print(f"[stderr]\n{d['stderr']}", end="", file=sys.stderr)
    if d["exit_code"] != 0:
        print(f"[exit code: {d['exit_code']}]", file=sys.stderr)
        sys.exit(d["exit_code"])


def cmd_status(args, sock_path):
    request = {"id": make_id(), "cmd": "bash", "args": {"command": "echo ok"}}
    resp = send_request(request, sock_path)
    if resp.get("ok"):
        print("Bridge session is active.")
    else:
        print(f"Bridge session error: {resp.get('error', 'unknown')}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="cc-bridge CLI", prog="bridge")
    parser.add_argument("--session", default=DEFAULT_NAME, help="Session name (default: 'default')")
    parser.add_argument("--timeout", type=int, default=120,
                        help="Subprocess timeout in seconds for bash (default: 120)")
    parser.add_argument("--max-output", type=int, default=DEFAULT_MAX_OUTPUT,
                        help="Max output bytes for bash (default: 1000000)")
    sub = parser.add_subparsers(dest="subcmd", required=True)

    # read
    p_read = sub.add_parser("read", help="Read a remote file")
    p_read.add_argument("path", help="File path (relative to root-dir)")
    p_read.add_argument("--offset", type=int, help="Start from line N (0-based)")
    p_read.add_argument("--limit", type=int, help="Max lines to read")
    p_read.add_argument("--raw", action="store_true",
                        help="Return raw content (no line numbers); safe to redirect to a file")

    # write
    p_write = sub.add_parser("write", help="Write a file (reads from stdin or --file)")
    p_write.add_argument("path", help="Remote file path")
    p_write.add_argument("--file", help="Local file to read content from")

    # bash
    p_bash = sub.add_parser("bash", help="Run a shell command")
    p_bash.add_argument("command", help="Command to execute")

    # status
    sub.add_parser("status", help="Check if bridge session is alive")

    args = parser.parse_args()
    sock_path = _resolve_socket(args.session)

    handlers = {
        "read": cmd_read,
        "write": cmd_write,
        "bash": cmd_bash,
        "status": cmd_status,
    }
    handlers[args.subcmd](args, sock_path)


if __name__ == "__main__":
    main()
