import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import MagicMock, patch

from device import Device
from server import MCP, Store

ROOT = Path(__file__).resolve().parent


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "status.sqlite3"
        self.store = Store(self.path, "work")

    def tearDown(self):
        self.store.db.close()
        self.temp.cleanup()

    def start(self, request="one"):
        return self.store.call("start_status", {"request_id": request, "title": "Prüfung", "surface": "claude_chat"})

    def update(self, item, state="completed", event="e1"):
        return {"session_id": item["session_id"], "event_id": event,
                "expected_revision": item["revision"], "state": state, "message": "Fertig geprüft"}

    def test_registration_retry_does_not_create_second_session(self):
        first, second = self.start(), self.start()
        self.assertEqual(first["session_id"], second["session_id"])
        self.assertEqual(len(self.store.call("list_status", {})["sessions"]), 1)

    def test_update_retry_and_old_revision(self):
        first = self.start()
        args = self.update(first)
        result = self.store.call("report_status", args)
        self.assertEqual(self.store.call("report_status", args), result)
        args["event_id"] = "late"
        args["state"] = "working"
        with self.assertRaisesRegex(ValueError, "Revision conflict"):
            self.store.call("report_status", args)
        self.assertEqual(self.store.call("list_status", {})["sessions"][0]["state"], "completed")

    def test_account_isolation(self):
        first = self.start()
        other = Store(self.path, "private")
        try:
            self.assertEqual(other.call("list_status", {})["sessions"], [])
            with self.assertRaises(ValueError):
                other.call("report_status", self.update(first))
        finally:
            other.db.close()

    def test_stale_is_unknown_and_usage_unavailable(self):
        first = self.start()
        with self.store.db:
            self.store.db.execute("UPDATE sessions SET updated_at=?", (time.time() - 1000,))
        item = self.store.call("list_status", {})["sessions"][0]
        self.assertEqual(item["state"], "unknown")
        self.assertEqual(item["reported_state"], "working")
        self.assertIsNone(item["usage"]["tokens"])

    def test_payload_uses_firmware_events_without_private_text(self):
        first = self.start()
        self.assertEqual(Device.payload(first)["tipo"], "prompt")
        expected = {"working": "prompt", "waiting_for_user": "atencao", "completed": "parou", "error": "erro", "cancelled": "fim"}
        for state, event in expected.items():
            item = dict(first, reported_state=state, revision=2)
            payload = Device.payload(item)
            self.assertEqual(payload["tipo"], event)
            self.assertLessEqual(len(payload["sessao"]), 11)
            self.assertNotIn("Prüfung", json.dumps(payload, ensure_ascii=False))

    def test_delivery_retry_and_no_obsolete_event(self):
        first = self.start()
        device = Device(None)
        with patch.object(device, "request", return_value="ok") as send:
            self.assertEqual(device.deliver(self.store, first)["state"], "sent")
            self.assertEqual(device.deliver(self.store, first)["state"], "already_sent")
            newer = self.store.call("report_status", self.update(first))
            self.assertEqual(device.deliver(self.store, first)["state"], "skipped")
            self.assertEqual(device.deliver(self.store, newer)["state"], "sent")
            self.assertEqual(send.call_count, 3)
            self.assertEqual(send.call_args_list[-2].args[1]["tipo"], "fim")
            self.assertEqual(send.call_args_list[-1].args[1]["sessao"], "")

    def test_device_failure_keeps_local_status(self):
        device = Device(None)
        mcp = MCP(self.store, device)
        mcp.initialized = True
        with patch.object(device, "request", side_effect=OSError("offline")):
            response = mcp.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {
                "name": "start_status", "arguments": {"request_id": "offline", "title": "Test", "surface": "claude_cowork"}}})
        item = json.loads(response["result"]["content"][0]["text"])
        self.assertEqual(item["display_delivery"]["state"], "failed")
        self.assertEqual(len(self.store.call("list_status", {})["sessions"]), 1)

    def test_invalid_values_are_rejected(self):
        first = self.start()
        args = self.update(first)
        args["expected_revision"] = True
        with self.assertRaises(ValueError):
            self.store.call("report_status", args)
        args["expected_revision"] = 1
        args["state"] = "invented"
        with self.assertRaises(ValueError):
            self.store.call("report_status", args)

    def test_invalid_jsonrpc_ids_are_rejected_without_side_effects(self):
        mcp = MCP(self.store)
        for identity in (True, None, [], {}, 1.5):
            response = mcp.handle({"jsonrpc": "2.0", "id": identity, "method": "initialize"})
            self.assertEqual(response["error"]["code"], -32600)
            self.assertFalse(mcp.initialized)

    def test_http_success_requires_firmware_acknowledgement(self):
        config = Path(self.temp.name) / "device.env"
        config.write_text("CLAUDINHO_IP=192.168.1.83\nCLAUDINHO_TOKEN=" + "x" * 32)
        for body, accepted in ((b"ok\n", True), (b"unexpected page", False)):
            response = MagicMock()
            response.read.return_value = body
            opener = MagicMock()
            opener.open.return_value.__enter__.return_value = response
            with patch("device.urllib.request.build_opener", return_value=opener):
                device = Device(config)
                if accepted:
                    self.assertEqual(device.request("/evento", {}), "ok\n")
                else:
                    with self.assertRaisesRegex(ValueError, "nicht bestaetigt"):
                        device.request("/evento", {})
    def test_stdio_roundtrip_and_restart_snapshot(self):
        messages = [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "test", "version": "1"}}},
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "start_status", "arguments": {"request_id": "stdio", "title": "Grüße", "surface": "claude_cowork"}}},
        ]
        command = [sys.executable, str(ROOT / "server.py"), "--no-device", "--data-dir", self.temp.name, "--profile", "work"]
        process = subprocess.run(command, input="\n".join(json.dumps(m) for m in messages) + "\n", capture_output=True, text=True, encoding="utf-8", timeout=10)
        self.assertEqual(process.returncode, 0, process.stderr)
        responses = [json.loads(line) for line in process.stdout.splitlines()]
        self.assertEqual([r["id"] for r in responses], [1, 2, 3])
        self.assertEqual(len(responses[1]["result"]["tools"]), 3)
        snapshot = subprocess.run(command + ["--snapshot"], capture_output=True, text=True, encoding="utf-8", timeout=10)
        self.assertEqual(json.loads(snapshot.stdout)["sessions"][0]["title"], "Grüße")

    def test_setup_preserves_other_settings_and_is_repeatable(self):
        config = Path(self.temp.name) / "claude.json"
        original = {"preferences": {"example": True}, "mcpServers": {"existing": {"command": "example"}}}
        config.write_text(json.dumps(original))
        # Setup generates files beside itself. Exercise it in an isolated copy,
        # so running the test suite cannot overwrite the installed entry or ZIP.
        setup_root = Path(self.temp.name) / "integration"
        (setup_root / "info-display").mkdir(parents=True)
        shutil.copy2(ROOT / "setup.py", setup_root / "setup.py")
        shutil.copy2(ROOT / "info-display/SKILL.md", setup_root / "info-display/SKILL.md")
        command = [sys.executable, str(setup_root / "setup.py"), "--apply", "--config", str(config)]
        subprocess.run(command, check=True, capture_output=True, timeout=10)
        result = json.loads(config.read_text())
        self.assertEqual(result["preferences"], original["preferences"])
        self.assertEqual(result["mcpServers"]["existing"], original["mcpServers"]["existing"])
        subprocess.run(command, check=True, capture_output=True, timeout=10)
        self.assertEqual(len(list(config.parent.glob("claude.json.before-*"))), 1)


if __name__ == "__main__":
    unittest.main()
