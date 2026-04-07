#!/usr/bin/env bash
# =============================================================
#  JARVIS — Instalador v4
#  Instala dependências e configura inicialização automática
# =============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JARVIS_PY="$SCRIPT_DIR/jarvis.py"
VENV_DIR="$SCRIPT_DIR/venv"
VENV_PYTHON="$VENV_DIR/bin/python"
AUTOSTART_DIR="$HOME/.config/autostart"
DESKTOP_FILE="$AUTOSTART_DIR/jarvis.desktop"
ENV_FILE="$SCRIPT_DIR/.env"

echo ""
echo "  ╔═══════════════════════════════════╗"
echo "  ║   JARVIS v4 — Instalação          ║"
echo "  ╚═══════════════════════════════════╝"
echo ""

# ── 1. Dependências Python ────────────────────────────────────
echo "  [1/4] Instalando dependências Python..."

# Criar virtualenv se não existir
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    echo "        Virtualenv criado em: $VENV_DIR"
fi

"$VENV_PYTHON" -m pip install --quiet pvporcupine pyaudio
echo "        pvporcupine e pyaudio instalados."

# ── 2. Configurar Access Key ──────────────────────────────────
echo ""
echo "  [2/4] Configurando Access Key da Porcupine..."

if [ -z "$PORCUPINE_ACCESS_KEY" ]; then
    if [ -f "$ENV_FILE" ] && grep -q "PORCUPINE_ACCESS_KEY=" "$ENV_FILE"; then
        echo "        Chave encontrada em .env — OK"
    else
        echo ""
        echo "  ╔══════════════════════════════════════════════════════╗"
        echo "  ║  Obtenha sua chave gratuita em:                      ║"
        echo "  ║    https://console.picovoice.ai/                     ║"
        echo "  ╚══════════════════════════════════════════════════════╝"
        echo ""
        read -rp "  Cole sua Porcupine Access Key: " ACCESS_KEY
        if [ -n "$ACCESS_KEY" ]; then
            echo "PORCUPINE_ACCESS_KEY=$ACCESS_KEY" > "$ENV_FILE"
            echo "        Chave salva em: $ENV_FILE"
        else
            echo "        AVISO: Nenhuma chave fornecida. Configure depois em $ENV_FILE"
        fi
    fi
else
    echo "        Variável PORCUPINE_ACCESS_KEY já definida no ambiente — OK"
fi

# ── 3. Permissão de execução ──────────────────────────────────
echo ""
chmod +x "$JARVIS_PY"
echo "  [3/4] Permissão de execução configurada."

# ── 4. Autostart no GNOME ─────────────────────────────────────
echo ""
echo "  [4/4] Configurando inicialização automática..."

mkdir -p "$AUTOSTART_DIR"

cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Type=Application
Name=JARVIS
Comment=Assistente de voz - wake word "Jarvis"
Exec=bash -c 'sleep 5 && $VENV_PYTHON $JARVIS_PY'
Terminal=false
Hidden=false
X-GNOME-Autostart-enabled=true
EOF

echo "        Arquivo criado em: $DESKTOP_FILE"

# ── Resumo ────────────────────────────────────────────────────
echo ""
echo "  ╔═══════════════════════════════════════════════════╗"
echo "  ║  Instalação concluída!                            ║"
echo "  ║                                                   ║"
echo "  ║  Para iniciar agora:                              ║"
echo "  ║    $VENV_PYTHON $JARVIS_PY"
echo "  ║                                                   ║"
echo "  ║  Fale 'Jarvis' para ativar.                       ║"
echo "  ║                                                   ║"
echo "  ║  O JARVIS vai iniciar automaticamente no          ║"
echo "  ║  próximo login do GNOME.                          ║"
echo "  ╚═══════════════════════════════════════════════════╝"
echo ""
