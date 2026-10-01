"""Display-Firmware mit vorhandenem Python prüfen oder ausdrücklich per OTA aktualisieren."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import time
import uuid

from device import Device, discover_config

DEFAULT_FIRMWARE = (Path(__file__).resolve().parent.parent / "firmware/bin"
                    / "claudinho-esp32c3-1.8.3-gc9a01.4-ota.bin")
FILENAME = re.compile(r"claudinho-esp32c3-(\d+\.\d+\.\d+-gc9a01\.\d+)-ota\.bin")


class UpdateError(Exception):
    """Eine sichere Meldung ohne Gerätezugangsdaten."""


def firmware_bytes(path):
    match = FILENAME.fullmatch(path.name)
    if match is None:
        raise UpdateError("Nur eine OTA-Datei für ESP32-C3 und GC9A01 ist zulässig; kein Komplettimage.")
    data = path.read_bytes()
    manifest = path.with_name("SHA256SUMS-GC9A01.txt").read_text(encoding="utf-8-sig")
    digests = []
    for line in manifest.splitlines():
        entry = re.fullmatch(r"([0-9a-fA-F]{64})\s+\*?(.+)", line.strip())
        if entry and entry[2] == path.name:
            digests.append(entry[1].lower())
    if not data or len(digests) != 1 or hashlib.sha256(data).hexdigest() != digests[0]:
        raise UpdateError("Die Firmware-Prüfsumme stimmt nicht oder fehlt. Es wurde nichts übertragen.")
    return data, match[1]


def read_status(device, timeout=10):
    status = json.loads(device.request("/mini.json", timeout=timeout))
    if (not isinstance(status, dict) or status.get("placa") != "esp32c3"
            or status.get("display") != "gc9a01-240x240"):
        raise UpdateError("Das Gerät ist kein unterstütztes ESP32-C3-Display mit GC9A01.")
    return status


def update_display(device, firmware, apply=False):
    data, version = firmware_bytes(firmware)
    status = read_status(device)
    print("Firmwaredatei, Prüfsumme und Gerätetyp erfolgreich geprüft.")
    if status.get("versao") == version:
        print("Die Zielversion ist bereits installiert.")
        return
    if not apply:
        print("Es wurde nichts verändert. Zum Aktualisieren denselben Aufruf mit --apply verwenden.")
        return

    boundary = "claudinho-" + uuid.uuid4().hex
    body = (f'--{boundary}\r\nContent-Disposition: form-data; name="f"; '
            f'filename="{firmware.name}"\r\nContent-Type: application/octet-stream\r\n\r\n').encode()
    body += data + f"\r\n--{boundary}--\r\n".encode()
    deadline = time.monotonic() + 60
    if device.request("/cmd", {"manutencao": True}).strip() != "ok":
        raise UpdateError("Die Updatefreigabe wurde nicht angefordert. Es wurde nichts hochgeladen.")
    print("Drücke jetzt BOOT am Display. Die Freigabe wird höchstens 60 Sekunden abgewartet.", flush=True)
    while time.monotonic() < deadline:
        try:
            status = read_status(device, timeout=min(10, max(0.1, deadline - time.monotonic() - 1)))
            if status.get("manut") == "liberada" and time.monotonic() < deadline:
                break
        except (OSError, ValueError):
            pass
        time.sleep(min(2, max(0, deadline - time.monotonic())))
    else:
        raise UpdateError("Keine rechtzeitige BOOT-Freigabe erhalten. Es wurde nichts hochgeladen.")

    print("Firmware wird einmal übertragen. Bitte die Stromversorgung angeschlossen lassen.", flush=True)
    try:
        response = device.request("/ota", raw_data=body,
                                  content_type="multipart/form-data; boundary=" + boundary, timeout=180)
    except (OSError, ValueError):
        raise UpdateError("Keine eindeutige Uploadbestätigung erhalten. Nicht blind wiederholen; zuerst --check ausführen.") from None
    if response.strip() not in ("ok, restarting", "ok, reiniciando"):
        raise UpdateError("Der Upload wurde nicht bestätigt. Nicht blind wiederholen; zuerst --check ausführen.")
    print("Upload bestätigt. Warte auf Neustart und bestätige die neue Version …", flush=True)
    deadline = time.monotonic() + 90
    while time.monotonic() < deadline:
        try:
            status = read_status(device, timeout=min(10, max(0.1, deadline - time.monotonic() - 1)))
            if status.get("versao") == version and time.monotonic() < deadline:
                print("Aktualisierung erfolgreich: Version " + version + " bestätigt.")
                return
        except (OSError, ValueError):
            pass
        time.sleep(min(2, max(0, deadline - time.monotonic())))
    raise UpdateError("Der Upload war bestätigt, die neue Version aber noch nicht nachweisbar. Zuerst --check ausführen.")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="Nur Firmware und Gerät prüfen (Standard)")
    mode.add_argument("--apply", action="store_true", help="Nach BOOT-Freigabe einmal per OTA übertragen")
    parser.add_argument("--firmware", type=Path, default=DEFAULT_FIRMWARE, help="OTA-Datei mit benachbarter Prüfsummendatei")
    parser.add_argument("--device-config", type=Path, help="Vorhandene Display-Konfiguration verwenden")
    args = parser.parse_args()
    try:
        update_display(Device(args.device_config or discover_config()), args.firmware, args.apply)
    except UpdateError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except (OSError, ValueError):
        print("Prüfung fehlgeschlagen: Firmwaredateien, Display-Konfiguration oder Netzwerk prüfen.", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Abgebrochen. Falls der Upload begonnen hat, zuerst den Stand mit --check prüfen.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
