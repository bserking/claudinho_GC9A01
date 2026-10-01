---
name: configurar
description: "Configure Claudinho for ESP32-C3 Super Mini and the round GC9A01 SPI display: firmware, Wi-Fi, Claude Code status line, diagnostics, OTA updates, and optional Bambu Lab monitoring."
---

# Configure Claudinho

This package targets **ESP32-C3 Super Mini + GC9A01 240x240 SPI**. The ESP32
draws the interface directly; no separate display upload is needed.

| GC9A01 | ESP32-C3 Super Mini |
| --- | --- |
| VDD | 3.3V |
| GND | GND |
| SCL/SCK | GPIO 4 |
| SDA/MOSI | GPIO 5 |
| CS | GPIO 6 |
| DC | GPIO 7 |
| RST | GPIO 10 |

There is no touch controller or MISO wire in this setup. **BOOT** approves an
update, acknowledges an alert, and cycles face → usage → printer (if configured)
→ face. The display asks **Press BOOT** when approval is required. Touch-only
games and the visual color palette are disabled. Set an exact face color with
`claudinho.sh cor R G B salvar`.

Guide the user through one step at a time. Explain each command before running
it and inspect its output before continuing. Never claim success without the
corresponding acknowledgement. A successful build does not prove that the
display wiring or a newly connected board works.

**Never ask for the Wi-Fi password or Bambu printer access code in the chat.**
The user enters these privately in a terminal. Respect restrictions on the
computer: use existing tools and do not install packages, change system
settings, or request administrator access. If an upload tool is unavailable,
explain the prerequisite before proceeding. The `esptool.sh` download fallback
must not be used when downloading programs is prohibited.

For every command, use the variables provided by Claude Code:

```bash
export R="${CLAUDE_PLUGIN_ROOT}"; export CLAUDINHO_DADOS="${CLAUDE_PLUGIN_DATA}"
```

Scripts support Linux, macOS, WSL, and Windows with Git Bash. Under WSL and
Windows, USB ports belong to Windows, for example `COM6`. To inspect the
environment:

```bash
bash -c 'source "$R/scripts/comum.sh"; ambiente'
```

The ESP32-C3 firmware has been built and the connected GC9A01 has been used in
this project. Other boards, wiring, and operating systems still need their own
hardware test. If a command fails, inspect the cause instead of repeating it
blindly. Ask the user to handle physical actions such as connecting a data
cable or pressing BOOT.

## Update process

- A new or unconfigured board needs its first firmware upload over USB.
- Later updates use `claudinho.sh atualizar`, which posts the firmware directly
  to the board over the local network. There is no cloud server in this path.
- Tell the user before starting: **Press BOOT** on the board when prompted.
  Approval expires after about one minute. No upload starts without approval.
- The ESP32 writes to its spare partition and switches only after verification.
  An interrupted transfer keeps the old firmware active.
- If Wi-Fi is unavailable, the IP changed, the device secret differs, or the
  board no longer runs compatible firmware, use USB setup and diagnostics.

## 0. Check whether it is configured

```bash
bash "$R/scripts/claudinho.sh" info
```

A JSON reply containing `"versao"` confirms that the device is reachable.
Continue with the user's request: diagnostics in step 7 or an OTA update with
`claudinho.sh atualizar`. If it reports that the device is not configured or
does not respond, continue with step 1.

## 1. Connect the hardware

Confirm the wiring table above. **VDD connects to 3.3 V.** Power the assembly
through the ESP32 USB connector, with the display supplied by the board.
Use a **USB data cable**; a charging-only cable cannot configure the board.

If an OTA update returns an empty response, check Wi-Fi signal and power using
`claudinho.sh log`. An incomplete transfer is discarded. Investigate repeated
failures; `claudinho.sh reiniciar` reconnects the board to Wi-Fi.

## 2. Find the USB port

```bash
bash "$R/scripts/porta.sh"
```

Keep the printed port, such as `COM6`, `/dev/ttyACM0`, or `/dev/cu.usbmodem101`.
If detection fails, check the cable and try connecting USB while holding
**BOOT**. If access is blocked by the computer's permissions, explain that
limitation; do not change administrator or system permissions.

## 3. Upload firmware over USB

Run this only when firmware upload is needed and existing upload tooling is
available:

```bash
bash "$R/scripts/gravar.sh" PORT
```

Replace `PORT` with the detected port. If the output contains `PRECISA_BOOT`,
ask the user to **hold BOOT, unplug and reconnect USB, then release BOOT**.
Detect the port again if its number changes, then retry.

Wait for `Hash of data verified`. The full USB upload may erase the board's
previous configuration. Ask what appears on the display. If it stays black or
white, stop and check power, SCL/SCK, SDA/MOSI, CS, DC, and RST.

## 4. Configure Wi-Fi and the device secret

List visible networks; the ESP32 uses 2.4 GHz:

```bash
bash "$R/scripts/serial.sh" PORT SCAN REDE "SCAN FIM" 40
```

Ask only for the **network name**. Resolve `$R` and `$CLAUDINHO_DADOS` to actual
paths before showing the command. Ask the user to run it in a terminal
**outside Claude Code**, using Git Bash or WSL on Windows:

```bash
CLAUDINHO_DADOS="<data-directory>" bash "<plugin-root>/scripts/wifi.sh" PORT "NETWORK NAME"
```

The script asks for a hidden password, generates the local device secret,
sends configuration over USB, and stores the device IP, secret, and MAC on the
computer. The Wi-Fi password stays on the board. Wait for **Done!**, the IP,
and the MAC. If it fails, ask for the error message without any password or
secret. Check the password locally and ensure the network is 2.4 GHz.

Verify from Claude Code:

```bash
bash "$R/scripts/claudinho.sh" info
```

USB acknowledgements and machine-readable fields retain their existing names:
`CFG OK`, `"wifi":"conectado"`, and `"manut":"liberada"`. These protocol
values are intentional even though user-facing messages are English.

Tell the user the IP and MAC and recommend a DHCP reservation on the router.
If the IP changes, the stored configuration must be updated.

## 5. Check the display

The GC9A01 interface is included in the ESP32 firmware. After the greeting or
face appears, continue to the status line. No additional screen file is needed.

## 6. Enable the Claude Code status line

Plugin hooks report work events. The status line also sends the usage numbers
provided by Claude Code. The setup script backs up settings and preserves an
existing status line:

```bash
python "$R/scripts/instalar-statusline.py" "$CLAUDINHO_DADOS"
```

Use the existing Python executable; on Linux or macOS it may be `python3`.
No Python package installation is needed. This integrates Claude Code usage;
the separate Claude App skill reports task states and does not measure plan
limits.

## 7. Test and diagnose

```bash
bash "$R/scripts/claudinho.sh" cara prompt feliz
bash "$R/scripts/claudinho.sh" info
```

Ask whether the happy face with narrowed eyes appeared. `info` should show
`"local":true`. Usage values arrive after Claude Code supplies its next status
line update. Read diagnostics without USB using `claudinho.sh log`.

## Optional Bambu Lab printer

Use this section only when the user asks to connect a printer. The original
integration was tested on a P2S with AMS. Other Bambu models with local network
access need their own test; do not claim compatibility was verified.

The device connects directly to the printer on the local network. Its dashboard
shows progress, time remaining, layers, temperatures, and AMS information.
During printing it appears periodically. Press **BOOT** to cycle screens or
acknowledge an alert. Informational alerts clear automatically; action alerts
remain until acknowledged. Preview an alert using
`claudinho.sh alerta bom|ruim|filamento|hms`.

1. On the printer, open Settings → Network/WLAN and note the **IP** and
   **access code**. Recommend reserving its IP on the router. Local access may
   require the printer's LAN or developer mode, depending on its firmware.
2. Ask the user to enter the access code privately in a terminal outside
   Claude Code. Resolve the directory paths in this command first:

   ```bash
   CLAUDINHO_DADOS="<data-directory>" bash "<plugin-root>/scripts/claudinho.sh" bambu PRINTER_IP
   ```

   The hidden code is sent to and stored on the board. The computer does not
   keep it.
3. Inspect `bash "$R/scripts/claudinho.sh" log` for printer connection and
   authentication results. A refused code may mean a wrong code or disabled
   local access. If there is no connection, check power, IP, and network.
4. Show the printer dashboard immediately with `claudinho.sh painel`.

To disable the integration and delete the code from the board, use
`claudinho.sh bambu desligar`. Configuration travels over local HTTP with the
device secret; the connection is not encrypted.

## Tool scenes

While Claude Code uses tools, the screen can show an editor, terminal, reading
animation, or agent diagram. Hooks send only a fixed category, never file names
or command contents. Explain that the scene is a decorative indication of the
category. To preview one:

```bash
bash "$R/scripts/claudinho.sh" cena codando
```

Other supported categories are `terminal`, `lendo`, and `agente`.

## Command reference

Command names retain their existing Portuguese identifiers for compatibility:

```text
claudinho.sh info | log | cara <type> [mood] | cor R G B [salvar]
claudinho.sh bambu IP|desligar | painel | alerta [type] | cena <type>
claudinho.sh reiniciar | consumo [seconds] | atualizar [firmware.bin]
```

Face events: `inicio`, `prompt`, `ferramenta`, `erro`, `parou`, `atencao`,
`compact`, `fim`, `dormir`. Prompt moods: `feliz`, `preocupado`, `susto`.
The legacy commands `tela`, `velha`, `genius`, and the touch palette do not apply
to this GC9A01 setup.
