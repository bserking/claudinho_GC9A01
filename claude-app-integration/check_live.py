"""Explicit hardware smoke test: send app events, verify firmware history, clean up."""
import json
from pathlib import Path
import tempfile
import uuid

from device import Device, discover_config
from server import Store


def history_keys(status):
    return {(entry.get("time"), entry.get("uptime"), entry.get("kind"), entry.get("text"))
            for entry in status.get("history", [])}


def main():
    device = Device(discover_config())
    with tempfile.TemporaryDirectory() as directory:
        store = Store(Path(directory) / "test.sqlite3", "integration-test")
        item = store.call("start_status", {"request_id": str(uuid.uuid4()),
                         "title": "Verbindungstest", "surface": "claude_chat"})
        try:
            previous = history_keys(json.loads(device.request("/status.json")))
            for state in ["working", "waiting_for_user", "completed"]:
                item = store.call("report_status", {
                    "session_id": item["session_id"], "event_id": str(uuid.uuid4()),
                    "expected_revision": item["revision"], "state": state, "message": ""})
                delivery = device.deliver(store, item)
                if delivery["state"] != "sent":
                    delivery = device.deliver(store, item)
                    if delivery["state"] != "sent":
                        raise RuntimeError("Display-Meldung nicht bestaetigt")
                status = json.loads(device.request("/status.json"))
                event = Device.payload(item)["tipo"]
                label = {"prompt": "Working", "atencao": "Waiting for you", "parou": "Completed"}[event]
                expected = {event + ": Claude App", label + ": Claude App"}
                current = history_keys(status)
                if not any(entry[-1] in expected for entry in current - previous):
                    raise RuntimeError("Display-Historie bestaetigt das Ereignis nicht")
                previous = current
                print("Bestaetigt:", state)
        finally:
            try:
                device.request("/evento", dict(Device.payload(item), tipo="fim"))
            finally:
                store.db.close()
    print("Live-Test bestanden; Testsitzung entfernt.")


if __name__ == "__main__":
    main()
