"""Adapter for the existing Claudinho /evento firmware API."""
import hashlib
import ipaddress
import json
import time
from pathlib import Path
import urllib.request


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def discover_config():
    for path in [Path.home() / ".claude/plugins/data/claudinho-claudinho/claudinho.env",
                 Path.home() / ".claudinho/claudinho.env"]:
        if path.is_file():
            return path
    return None


class Device:
    def __init__(self, config_path):
        self.config_path = config_path
        self.last_request_finished = 0.0

    def request(self, endpoint, payload=None, *, raw_data=None,
                content_type="application/json", timeout=10):
        if raw_data is not None and (payload is not None or not isinstance(raw_data, bytes)):
            raise ValueError("Raw data must be bytes and cannot be combined with JSON")
        # The synchronous ESP32 web server also renders animations. Avoid bursts
        # (notably the close-session/completed pair) on consecutive connections.
        pause = 1.0 - (time.monotonic() - self.last_request_finished)
        if pause > 0:
            time.sleep(pause)
        config = {}
        if self.config_path is None:
            raise ValueError("Display-Konfiguration fehlt")
        for line in self.config_path.read_text(encoding="utf-8-sig").splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip()
        # The existing setup stores a literal LAN IP, never an arbitrary URL.
        address = ipaddress.ip_address(config.get("CLAUDINHO_IP", ""))
        if not (address.is_private or address.is_loopback):
            raise ValueError("Display muss eine lokale IP-Adresse haben")
        token = config.get("CLAUDINHO_TOKEN", "")
        if len(token) < 16 or "\n" in token or "\r" in token:
            raise ValueError("Display-Schluessel fehlt oder ist ungueltig")
        host = "[" + str(address) + "]" if address.version == 6 else str(address)
        data = raw_data if raw_data is not None else (
            json.dumps(payload).encode("utf-8") if payload is not None else None)
        request = urllib.request.Request("http://" + host + endpoint, data=data,
                                         headers={"Authorization": "Bearer " + token,
                                                  "Content-Type": content_type})
        # Never send LAN authentication through a configured system proxy or redirect.
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
        try:
            with opener.open(request, timeout=timeout) as response:
                body = response.read(65537)
                if len(body) > 65536:
                    raise ValueError("Display-Antwort ist zu gross")
                text = body.decode("utf-8")
                if endpoint == "/evento" and text.strip() != "ok":
                    raise ValueError("Display hat die Meldung nicht bestaetigt")
                return text
        finally:
            self.last_request_finished = time.monotonic()

    @staticmethod
    def payload(item):
        state = item["reported_state"]
        event = {"working": "prompt", "waiting_for_user": "atencao",
                 "completed": "parou", "error": "erro", "cancelled": "fim"}[state]
        identity = item["profile"] + ":" + item["session_id"]
        return {"tipo": event, "sessao": "a" + hashlib.sha256(identity.encode()).hexdigest()[:10],
                "acao": "Cowork" if item["surface"] == "claude_cowork" else "Claude App"}

    def deliver(self, store, item):
        try:
            with store.db:
                store.db.execute("BEGIN IMMEDIATE")
                current = store.present(store.get(item["session_id"]))
                if current["revision"] != item["revision"] or current["stale"]:
                    return {"state": "skipped", "reason": "Neuere oder veraltete Meldung"}
                previous = store.db.execute("SELECT revision FROM delivery WHERE session_id=?",
                                            (item["session_id"],)).fetchone()
                if previous and previous[0] >= item["revision"]:
                    return {"state": "already_sent"}
                payload = self.payload(item)
                if item["reported_state"] == "completed":
                    # Remove the task from the firmware's 30-minute session counter,
                    # then show the completion face without registering it again.
                    self.request("/evento", dict(payload, tipo="fim"))
                    payload["sessao"] = ""
                self.request("/evento", payload)
                store.db.execute("INSERT OR REPLACE INTO delivery VALUES (?,?)",
                                 (item["session_id"], item["revision"]))
            return {"state": "sent"}
        except (OSError, ValueError):
            return {"state": "failed", "reason": "Lokal gespeichert; Display nicht erreichbar oder Konfiguration ungueltig"}
