#!/usr/bin/env bash
# Network maintenance after Claudinho has been configured.
#   claudinho.sh info                 current status (GET /mini.json)
#   claudinho.sh log                  device log
#   claudinho.sh cara <type> [mood]   show a face (inicio, prompt, ferramenta, erro, parou, atencao, compact, fim, dormir)
#   claudinho.sh cor                  open palette (legacy touch hardware only)
#   claudinho.sh cor R G B [salvar]   exact face color ("salvar" saves it on the board)
#   claudinho.sh reiniciar
#   claudinho.sh atualizar [file.bin] firmware over the network; requires pressing BOOT
#   claudinho.sh tela <file.tft>      legacy Nextion compatibility only; supply your own file
#   claudinho.sh consumo [seconds]    show usage screen now (default: 20 s)
#   claudinho.sh velha                tic-tac-toe (legacy touch hardware only)
#   claudinho.sh genius               memory game (legacy touch hardware only)
#   claudinho.sh bambu IP | desligar  connect Bambu printer; access code is entered privately
#   claudinho.sh painel               show printer dashboard
#   claudinho.sh cena <type>          test a scene: codando, terminal, lendo, agente
#   claudinho.sh alerta [bom|ruim|filamento|hms]  show a sample printer alert
# O segredo nunca vai na linha de comando (ver curl_claudinho no comum.sh).
source "$(dirname "$0")/comum.sh"
IP=$(le_config CLAUDINHO_IP)
[ -n "$IP" ] || { echo "Claudinho is not configured yet (run /claudinho:configurar)" >&2; exit 1; }
PYTHON=python3
[ "$(ambiente)" = windows ] && PYTHON=python
J=(-H 'Content-Type: application/json')
uso() { sed -n '2,17p' "$0"; exit 1; }
num() { case "$1" in ''|*[!0-9]*) return 1 ;; esac; }
palavra() { case "$1" in *[!a-z]*) return 1 ;; esac; }      # so letras minusculas (ou vazio)
cmd() { curl_claudinho -s -m 10 "${J[@]}" -X POST "http://$IP/cmd" -d "$1"; }
mini() { curl_claudinho -s -m 5 "http://$IP/mini.json"; }

# Firmware e tela pela rede exigem alguem na frente do Claudinho: pede o
# toque e espera a placa liberar (firmware anterior a 1.0.9 nao pede).
libera() {
  local m i
  m=$(mini); case "$m" in *'"manut"'*) ;; *) return 0 ;; esac
  cmd '{"manutencao":true}' >/dev/null || { echo "Claudinho did not respond" >&2; return 1; }
  case "$m" in
    *'"display":"gc9a01-240x240"'*) echo "Press BOOT on the board to allow the update..." ;;
    *) echo "Tap the Claudinho screen or press BOOT on the board to allow the update..." ;;
  esac
  for i in $(seq 35); do
    sleep 2; m=$(mini)
    case "$m" in *'"manut":"liberada"'*) echo "approved."; return 0 ;; esac
    case "$m" in *'"manut":""'*) [ "$i" -gt 3 ] && break ;; esac
  done
  echo "approval timed out; nothing was sent" >&2; return 1
}

case "${1:-}" in
  info) mini ;;
  log)  curl_claudinho -s -m 5 "http://$IP/log" ;;
  cara)
    palavra "${2:-x}" && palavra "${3:-}" || uso
    curl_claudinho -s -m 10 "${J[@]}" -X POST "http://$IP/evento" -d "{\"tipo\":\"$2\",\"humor\":\"${3:-}\",\"sessao\":\"teste\"}" ;;
  cor)
    if [ -z "${2:-}" ]; then
      case "$(mini)" in *'"display":"gc9a01-240x240"'*) echo "This display has no touch controller. Use: cor R G B salvar" >&2; exit 1 ;; esac
      cmd '{"paleta":true}'; echo "choose a color on the Claudinho screen"; exit
    fi
    for v in "${2:-}" "${3:-}" "${4:-}"; do num "$v" && [ "$v" -le 255 ] || uso; done
    case "${5:-}" in "") S=false ;; salvar) S=true ;; *) uso ;; esac
    cmd "{\"cor\":[$2,$3,$4],\"salvar\":$S}" ;;
  reiniciar) cmd '{"reiniciar":true}' ;;
  velha|genius)
    case "$(mini)" in *'"display":"gc9a01-240x240"'*) echo "This game requires a touch controller and is disabled with this wiring." >&2; exit 1 ;; esac
    if [ "$1" = velha ]; then cmd '{"velha":true}'; echo "game opened on the Claudinho screen"; else cmd '{"genius":true}'; echo "memory game opened on the Claudinho screen"; fi ;;
  painel) cmd '{"painel":true}' ;;
  alerta) case "${2:-bom}" in bom|ruim|filamento|hms) cmd "{\"alerta\":\"${2:-bom}\"}" ;; *) uso ;; esac ;;
  cena)
    case "${2:-}" in codando|terminal|lendo|agente) ;; *) uso ;; esac
    curl_claudinho -s -m 10 "${J[@]}" -X POST "http://$IP/evento" -d "{\"tipo\":\"ferramenta\",\"acao\":\"$2\",\"forca\":true}" ;;   # sem sessao: teste nao conta como terminal aberto
  bambu)
    case "${2:-}" in
      desligar) cmd '{"bambu":{"desligar":true}}' ;;
      ""|*[!0-9.]*) uso ;;
      *)
        # o codigo vai por pipe (nunca na linha de comando) e fica gravado so na placa
        if [ -t 0 ]; then IFS= read -r -s -p "Printer access code: " CODIGO; echo; else IFS= read -r CODIGO; fi
        [ -n "$CODIGO" ] || { echo "empty access code; nothing was sent" >&2; exit 1; }
        BIP="$2" CODIGO="$CODIGO" "$PYTHON" -c 'import json,os;print(json.dumps({"bambu":{"ip":os.environ["BIP"],"codigo":os.environ["CODIGO"]}}))' \
          | curl -s -m 10 -K <(printf 'header = "Authorization: Bearer %s"\n' "$(le_config CLAUDINHO_TOKEN)") "${J[@]}" -X POST "http://$IP/cmd" --data-binary @-
        unset CODIGO ;;
    esac ;;
  consumo) S="${2:-20}"; num "$S" || uso; cmd "{\"consumo\":$S}" ;;
  atualizar)
    CHIP=$(mini | grep -o '"placa":"[^"]*"' | cut -d'"' -f4)
    ARQ="${2:-$(ls "$RAIZ"/firmware/bin/claudinho-${CHIP:-esp32c3}-*-ota.bin 2>/dev/null | sort -V | tail -1)}"
    [ -f "$ARQ" ] || { echo "firmware file was not found" >&2; exit 1; }
    libera || exit 1
    echo "sending $(basename "$ARQ") to $IP"
    curl_claudinho -s -m 180 -F "f=@$ARQ" "http://$IP/ota" ;;
  tela)
    case "$(mini)" in *'"display":"gc9a01-240x240"'*) echo "The GC9A01 interface is part of the firmware; no separate display file is required."; exit 0 ;; esac
    # Legacy Nextion backend: this package does not include a TFT file.
    ARQ="${2:-}"
    [ -f "$ARQ" ] || { echo "legacy display file was not found; supply a path after tela: $ARQ" >&2; exit 1; }
    TAM=$(wc -c < "$ARQ" | tr -d ' ')
    libera || exit 1
    echo "sending $TAM bytes to $IP (about 40 s)"
    curl_claudinho -s -m 300 -F "f=@$ARQ" "http://$IP/tft?tam=$TAM" ;;
  *) uso ;;
esac
