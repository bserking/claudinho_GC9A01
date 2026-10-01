#!/usr/bin/env bash
# Configura o Wi-Fi do Claudinho pela USB pedindo a senha AQUI, no terminal,
# escondida: ela nao passa pela conversa com o Claude, nao aparece na linha de
# comando e so fica gravada na placa. Gera o segredo do PC, espera a placa
# entrar no Wi-Fi e grava IP, segredo e MAC no computador.
# Uso (num terminal de verdade): wifi.sh PORTA "NOME DA REDE"
# Sem terminal, le a senha da primeira linha da entrada padrao.
source "$(dirname "$0")/comum.sh"
DIR="$(dirname "$0")"
PORTA="${1:-}"; SSID="${2:-}"
[ -n "$PORTA" ] && [ -n "$SSID" ] || { echo "usage: wifi.sh PORT \"NETWORK NAME\"" >&2; exit 1; }
# Windows pode anunciar python3/python pelos aliases vazios da Microsoft
# Store. Nao basta achar o comando: executa cada candidato e so aceita um
# interpretador Python 3 real. Em Git Bash, o Python instalado costuma se
# chamar "python"; por isso ele vem primeiro.
PYTHON=()
for candidato in python python3; do
  if "$candidato" -c 'import sys;raise SystemExit(0 if sys.version_info.major == 3 else 1)' >/dev/null 2>&1; then
    PYTHON=("$candidato"); break
  fi
done
if [ ${#PYTHON[@]} -eq 0 ] && py -3 -c 'import sys' >/dev/null 2>&1; then PYTHON=(py -3); fi
[ ${#PYTHON[@]} -gt 0 ] || { echo "Python 3 was not found" >&2; exit 1; }
if [ -t 0 ]; then
  IFS= read -r -s -p "Wi-Fi password for \"$SSID\" (hidden while you type): " SENHA; echo
else
  IFS= read -r SENHA          # sem terminal: primeira linha da entrada padrao
fi
[ -n "$SENHA" ] || { echo "empty password; nothing was sent" >&2; exit 1; }
TOKEN=$("${PYTHON[@]}" -c 'import secrets;print(secrets.token_hex(24))')

# A linha CFG vai por pipe direto para a serial: a senha nao toca o disco nem
# aparece em argumentos (passa ao Python pelo ambiente, que so o dono le).
echo "sending configuration over USB..."
if ! SSID="$SSID" SENHA="$SENHA" TOKEN="$TOKEN" "${PYTHON[@]}" -c 'import json,os
print("CFG " + json.dumps({"ssid": os.environ["SSID"], "senha": os.environ["SENHA"], "token": os.environ["TOKEN"]}))' \
    | bash "$DIR/serial.sh" "$PORTA" - "CFG OK" "" 20 >/dev/null; then
  unset SENHA; echo "the board did not acknowledge (CFG OK). Check the port and try again." >&2; exit 1
fi
unset SENHA

echo "ok. Waiting for the board to connect to Wi-Fi (up to 1 minute)..."
L=""
for i in 1 2 3; do
  L=$(bash "$DIR/serial.sh" "$PORTA" INFO 'CLAUDINHO {' "" 25 | tail -1)
  case "$L" in *'"wifi":"conectado"'*) break ;; esac
done
case "$L" in
  *'"wifi":"conectado"'*) ;;
  *) echo "the board did not connect to Wi-Fi: check the password and use a 2.4 GHz network. Try again." >&2; exit 1 ;;
esac
IP=$(printf '%s' "${L#CLAUDINHO }" | "${PYTHON[@]}" -c 'import json,sys;print(json.load(sys.stdin)["ip"])')
MAC=$(printf '%s' "${L#CLAUDINHO }" | "${PYTHON[@]}" -c 'import json,sys;print(json.load(sys.stdin)["mac"])')
grava_config CLAUDINHO_IP "$IP"; grava_config CLAUDINHO_TOKEN "$TOKEN"; grava_config CLAUDINHO_MAC "$MAC"
echo "Done! Claudinho is connected to Wi-Fi."
echo "  IP:  $IP"
echo "  MAC: $MAC"
echo "Reserve this IP on your router (DHCP reservation), then return to Claude."
