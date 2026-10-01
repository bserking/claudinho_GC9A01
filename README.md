# Claudinho GC9A01

Firmware and Claude Code plugin for an ESP32-C3 Super Mini with a round
240 x 240 GC9A01 display. The LCD, local web dashboard, command-line messages
and Bambu Lab printer alerts use English. Installation guidance for this
project is in `INSTALL-GC9A01-DE.md`.

The computer sends Claude Code hook events and optional usage measurements
directly to the device over the local network. The accompanying
`claude-app-integration/` Python MCP server sends Claude App and Cowork
task states. Neither path needs an external service or Anthropic credentials.
The App skill reports its own state; it does not measure account limits or
guarantee that every chat action produces a tool call.

The GC9A01 build supports faces, usage, work scenes, BOOT navigation, local
Wi-Fi setup, firmware OTA and optional Bambu printer status and alerts.
Touch-only games and the visual palette are excluded from this build.
Color can be set using `claudinho.sh cor R G B salvar`.

Missing or expired usage is unavailable (`--` on the LCD, `Unavailable` in
the web dashboard and JSON `null`). The activity indicator remains usable
when the computer only reports task events. Usage supplied by Claude Code
is shared display data and is not a measurement of the Claude App account.

`firmware/bin/` contains only the current ESP32-C3 GC9A01 release and its
SHA-256 manifest. Use the `-ota.bin` image for network updates. The
`-completo.bin` image is for initial USB flashing with existing tooling.

Existing event names, routes, serial responses and configuration keys are
retained for compatibility. The legacy Nextion source backend is available
at compile time; this package contains no Nextion screen files or binaries.

Source builds require an existing Arduino CLI environment with ESP32 core
3.3.12, ArduinoJson 7.4.3, Adafruit GC9A01A 1.1.1, Adafruit GFX 1.12.6 and
Adafruit BusIO 1.17.4. End users can apply the supplied OTA image using only
Python 3.10+ and its standard library. The HMS generator is offline and
documented in `firmware/hms/README.md`.

Based on [Claudinho by Argeu Thiesen](https://github.com/argeuthiesen/claudinho).
The original MIT license is in `LICENSE`.
