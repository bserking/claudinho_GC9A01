"""Prepare the Claude MCP entry and skill ZIP; --apply merges the local app config."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import sys
import uuid
import zipfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--profile", default="claude-app")
    parser.add_argument("--config", type=Path, help="Override Claude desktop config location")
    args = parser.parse_args()
    if not args.profile.strip():
        parser.error("Use a nonempty profile")
    root = Path(__file__).resolve().parent
    entry = {"command": sys.executable,
             "args": [str(root / "server.py"), "--profile", args.profile,
                      "--data-dir", str(root / "data")]}
    snippet = {"mcpServers": {"claude-info-display": entry}}
    (root / "claude-config-entry.json").write_text(json.dumps(snippet, indent=2), encoding="utf-8")
    with zipfile.ZipFile(root / "info-display-skill.zip", "w", zipfile.ZIP_DEFLATED) as archive:
        archive.write(root / "info-display/SKILL.md", "info-display/SKILL.md")
    print("Konfigurationsvorlage und Skill-ZIP erstellt.")
    if not args.apply:
        return
    target = args.config or Path(os.environ["APPDATA"]) / "Claude/claude_desktop_config.json"
    previous = target.read_bytes() if target.exists() else None
    config = json.loads(previous.decode("utf-8-sig")) if previous is not None else {}
    if not isinstance(config, dict) or not isinstance(config.get("mcpServers", {}), dict):
        raise ValueError("Bestehende Claude-Konfiguration hat ein unerwartetes Format; nicht veraendert")
    servers = config.setdefault("mcpServers", {})
    if "claude-info-display" in servers and servers["claude-info-display"] != entry:
        raise ValueError("Abweichender claude-info-display-Eintrag vorhanden; nicht ueberschrieben")
    if servers.get("claude-info-display") == entry:
        print("Claude-Verbindung ist bereits konfiguriert.")
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    if previous is not None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        backup = target.with_name(target.name + ".before-info-display-" + stamp + "-" + uuid.uuid4().hex[:6])
        shutil.copy2(target, backup)
    servers["claude-info-display"] = entry
    temporary = target.with_name(target.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        temporary.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
        if (target.read_bytes() if target.exists() else None) != previous:
            raise ValueError("Konfiguration wurde zwischenzeitlich geaendert; bitte erneut versuchen")
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)
    print("Claude-Verbindung hinzugefuegt; vorhandene Einstellungen beibehalten. Claude neu starten.")


if __name__ == "__main__":
    main()
