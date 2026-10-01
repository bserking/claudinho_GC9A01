"""Local stdio MCP status bridge. Python 3.10+, standard library only."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import sys
import time
import uuid
from device import Device, discover_config

PROTOCOL = "2025-06-18"
VERSION = "0.2.2"
STATES = ["working", "waiting_for_user", "completed", "error", "cancelled"]


def schema(properties, required):
    return {"type": "object", "properties": properties, "required": required,
            "additionalProperties": False}


SHORT = {"type": "string", "minLength": 1, "maxLength": 160}
TOOLS = [
    {"name": "start_status", "description": "Start this conversation's working signal. This is NOT the final update: before asking the user a question call report_status waiting_for_user; before a final answer call report_status completed. Reuse request_id only for retries.",
     "inputSchema": schema({"request_id": SHORT, "title": SHORT,
                            "surface": {"type": "string", "enum": ["claude_chat", "claude_cowork"]}},
                           ["request_id", "title", "surface"])},
    {"name": "report_status", "description": "Report an observed task state. Use the latest revision; retry the same event with the same event_id. Does not measure tokens or subscription limits.",
     "inputSchema": schema({"session_id": SHORT, "event_id": SHORT,
                            "expected_revision": {"type": "integer", "minimum": 1},
                            "state": {"type": "string", "enum": STATES},
                            "message": {"type": "string", "maxLength": 240}},
                           ["session_id", "event_id", "expected_revision", "state", "message"])},
    {"name": "list_status", "description": "Read reported statuses for this configured account profile. Old active reports are marked unknown, never completed.",
     "inputSchema": schema({"session_id": SHORT}, [])},
]
for tool in TOOLS:
    tool["annotations"] = {"readOnlyHint": tool["name"] == "list_status",
                           "destructiveHint": False, "openWorldHint": False}


def validate(arguments, spec):
    if not isinstance(arguments, dict):
        raise ValueError("Arguments must be an object")
    if set(arguments) - set(spec["properties"]) or set(spec["required"]) - set(arguments):
        raise ValueError("Missing or unknown argument")
    for key, value in arguments.items():
        rule = spec["properties"][key]
        if rule["type"] == "string":
            if not isinstance(value, str) or not rule.get("minLength", 0) <= len(value) <= rule.get("maxLength", 1000):
                raise ValueError("Invalid string: " + key)
            if rule.get("minLength") and not value.strip():
                raise ValueError("Empty value: " + key)
        elif type(value) is not int or value < rule.get("minimum", 0):
            raise ValueError("Invalid integer: " + key)
        if "enum" in rule and value not in rule["enum"]:
            raise ValueError("Invalid value: " + key)


class Store:
    def __init__(self, path, profile, stale_seconds=900):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, timeout=30)
        self.db.row_factory = sqlite3.Row
        self.profile = profile
        self.stale_seconds = stale_seconds
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY, profile TEXT NOT NULL, request_id TEXT NOT NULL,
                title TEXT NOT NULL, surface TEXT NOT NULL, state TEXT NOT NULL,
                message TEXT NOT NULL, updated_at REAL NOT NULL, revision INTEGER NOT NULL,
                UNIQUE(profile, request_id));
            CREATE TABLE IF NOT EXISTS events (
                profile TEXT NOT NULL, event_id TEXT NOT NULL, fingerprint TEXT NOT NULL,
                result TEXT NOT NULL, PRIMARY KEY(profile, event_id));
            CREATE TABLE IF NOT EXISTS delivery (session_id TEXT PRIMARY KEY, revision INTEGER NOT NULL);
        """)

    def present(self, row):
        item = dict(row)
        item.pop("request_id")
        item["session_id"] = item.pop("id")
        item["source"] = "skill_reported"
        item["provider"] = "claude"
        item["usage"] = {"tokens": None, "limits": None, "availability": "unavailable"}
        active = item["state"] in ("working", "waiting_for_user")
        item["stale_after"] = item["updated_at"] + self.stale_seconds if active else None
        item["stale"] = active and time.time() > item["stale_after"]
        item["reported_state"] = item["state"]
        if item["stale"]:
            item["state"] = "unknown"
        return item

    def get(self, session_id):
        row = self.db.execute("SELECT * FROM sessions WHERE id=? AND profile=?",
                              (session_id, self.profile)).fetchone()
        if row is None:
            raise ValueError("Session not found in this account profile")
        return row

    def call(self, name, args):
        spec = next((t for t in TOOLS if t["name"] == name), None)
        if spec is None:
            raise ValueError("Unknown tool")
        validate(args, spec["inputSchema"])
        with self.db:
            if name == "list_status":
                if "session_id" in args:
                    rows = [self.get(args["session_id"])]
                else:
                    rows = self.db.execute("SELECT * FROM sessions WHERE profile=? ORDER BY updated_at DESC LIMIT 200",
                                           (self.profile,)).fetchall()
                return {"schema_version": 1, "generated_at": time.time(),
                        "sessions": [self.present(row) for row in rows]}
            # Serialize registrations and revisions across desktop processes.
            self.db.execute("BEGIN IMMEDIATE")
            if name == "start_status":
                old = self.db.execute("SELECT * FROM sessions WHERE profile=? AND request_id=?",
                                      (self.profile, args["request_id"])).fetchone()
                if old is not None:
                    if old["title"] != args["title"] or old["surface"] != args["surface"]:
                        raise ValueError("request_id already used for a different registration")
                    return self.present(old)
                session_id = str(uuid.uuid4())
                self.db.execute("INSERT INTO sessions VALUES (?,?,?,?,?,?,?,?,?)",
                                (session_id, self.profile, args["request_id"], args["title"],
                                 args["surface"], "working", "", time.time(), 1))
                return self.present(self.get(session_id))
            fingerprint = hashlib.sha256(json.dumps(args, sort_keys=True).encode()).hexdigest()
            old = self.db.execute("SELECT * FROM events WHERE profile=? AND event_id=?",
                                  (self.profile, args["event_id"])).fetchone()
            if old is not None:
                if old["fingerprint"] != fingerprint:
                    raise ValueError("event_id already used with different arguments")
                return json.loads(old["result"])
            row = self.get(args["session_id"])
            if row["revision"] != args["expected_revision"]:
                raise ValueError("Revision conflict; read list_status before sending a new event")
            self.db.execute("UPDATE sessions SET state=?, message=?, updated_at=?, revision=revision+1 WHERE id=? AND profile=?",
                            (args["state"], args["message"], time.time(), args["session_id"], self.profile))
            result = self.present(self.get(args["session_id"]))
            self.db.execute("INSERT INTO events VALUES (?,?,?,?)",
                            (self.profile, args["event_id"], fingerprint, json.dumps(result)))
            return result


class MCP:
    def __init__(self, store, device=None):
        self.store = store
        self.device = device
        self.initialized = False

    def handle(self, request):
        if (not isinstance(request, dict) or request.get("jsonrpc") != "2.0"
                or not isinstance(request.get("method"), str)
                or ("id" in request and type(request["id"]) not in (str, int))):
            return {"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "Invalid request"}}
        if "id" not in request:
            return None
        response = {"jsonrpc": "2.0", "id": request["id"]}
        method, params = request["method"], request.get("params", {})
        try:
            if not isinstance(params, dict):
                raise ValueError("params must be an object")
            if method == "initialize":
                self.initialized = True
                result = {"protocolVersion": PROTOCOL, "capabilities": {"tools": {}},
                          "serverInfo": {"name": "claude-info-display", "version": VERSION},
                          "instructions": "The user requested automatic status reporting for the current conversation. Use info-display at each user turn: start_status once, then report_status working on subsequent turns, waiting_for_user before a necessary question, and completed before the final response to the current request. Reuse only this conversation's known session ID. Respect opt-out and host permissions. Use neutral titles and no prompt content. Missing tools or display failures must not block the task. This is model-reported status, not lifecycle monitoring; tokens and limits are unavailable."}
            elif method == "ping":
                result = {}
            elif not self.initialized:
                raise ValueError("Initialize first")
            elif method == "tools/list":
                result = {"tools": TOOLS}
            elif method == "tools/call":
                try:
                    data = self.store.call(params.get("name"), params.get("arguments", {}))
                    if params.get("name") != "list_status":
                        data["display_delivery"] = self.device.deliver(self.store, data) if self.device else {"state": "disabled"}
                        # Keep the required follow-up next to the returned session/revision,
                        # even when the host loaded tools but did not load the whole skill.
                        if data["reported_state"] == "working":
                            data["reporting_hint"] = (
                                "Only the working signal has been recorded. Before your next user-facing "
                                "question, call report_status with state waiting_for_user; before your final "
                                "answer, use completed. Use this session_id and revision as expected_revision "
                                "and a new event_id. Do not ask the user to set the status."
                            )
                    result = {"content": [{"type": "text", "text": json.dumps(data, ensure_ascii=False)}]}
                except (ValueError, sqlite3.Error) as exc:
                    message = str(exc) if isinstance(exc, ValueError) else "Status storage unavailable; retry later"
                    result = {"isError": True, "content": [{"type": "text", "text": message}]}
            else:
                response["error"] = {"code": -32601, "message": "Method not found"}
                return response
            response["result"] = result
        except ValueError as exc:
            response["error"] = {"code": -32602, "message": str(exc)}
        return response


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).resolve().parent / "data")
    parser.add_argument("--profile", default=os.environ.get("CLAUDE_STATUS_PROFILE", "default"))
    parser.add_argument("--stale-seconds", type=int, default=900)
    parser.add_argument("--snapshot", action="store_true", help="Print display JSON and exit")
    parser.add_argument("--output", type=Path, help="With --snapshot, atomically write JSON here")
    parser.add_argument("--device-config", type=Path, help="Existing claudinho.env; otherwise auto-detected")
    parser.add_argument("--no-device", action="store_true", help="Store statuses without contacting hardware")
    parser.add_argument("--check-device", action="store_true", help="Read device information without changing its state")
    args = parser.parse_args()
    if args.stale_seconds < 1 or not args.profile.strip() or (args.output and not args.snapshot):
        parser.error("Use a nonempty profile, positive stale time; --output requires --snapshot")
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdin.reconfigure(encoding="utf-8")
    device = None if args.no_device else Device(args.device_config or discover_config())
    if args.check_device:
        try:
            if not device:
                raise ValueError("Device disabled")
            json.loads(device.request("/mini.json"))
            print("Display erreichbar; Authentifizierung erfolgreich.")
        except (OSError, ValueError) as exc:
            print("Display-Pruefung fehlgeschlagen (Netzwerk oder Konfiguration).", file=sys.stderr)
            raise SystemExit(1) from None
        return
    store = Store(args.data_dir / "status.sqlite3", args.profile, args.stale_seconds)
    try:
        if args.snapshot:
            payload = json.dumps(store.call("list_status", {}), ensure_ascii=False, indent=2)
            if args.output:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                temporary = args.output.with_name(args.output.name + "." + uuid.uuid4().hex + ".tmp")
                try:
                    temporary.write_text(payload, encoding="utf-8")
                    os.replace(temporary, args.output)
                finally:
                    temporary.unlink(missing_ok=True)
            else:
                print(payload)
            return
        mcp = MCP(store, device)
        for line in sys.stdin:
            try:
                request = json.loads(line)
                response = mcp.handle(request)
            except (ValueError, RecursionError):
                response = {"jsonrpc": "2.0", "id": None,
                            "error": {"code": -32700, "message": "Parse error"}}
            if response is not None:
                print(json.dumps(response, ensure_ascii=False), flush=True)
    finally:
        store.db.close()


if __name__ == "__main__":
    main()
