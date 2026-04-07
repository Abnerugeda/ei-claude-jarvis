#!/usr/bin/env python3
"""
JARVIS v4 — Wake Word "Jarvis" via Porcupine (Picovoice)
Fale "Jarvis" para ativar as ações configuradas.

Uso:
  python3 jarvis.py

Configuração:
  Defina a variável PORCUPINE_ACCESS_KEY no ambiente ou em .env:
    export PORCUPINE_ACCESS_KEY="sua-chave-aqui"

  Obtenha sua chave gratuita em: https://console.picovoice.ai/
"""

import os
import sys
import subprocess
import webbrowser
import threading
import time
import struct
from datetime import datetime

import pvporcupine
import pyaudio


# ============================================================
#  CONFIGURAÇÕES
# ============================================================

COOLDOWN = 4.0  # segundos entre ativações


# ============================================================
#  AÇÕES — edite aqui o que acontece ao falar "Jarvis"
# ============================================================

def executar_acoes():
    jarvis_diz("Ativando sistemas, senhor.")

    abrir_url("https://www.youtube.com/watch?v=5RdmcuQm6EU&list=RD5RdmcuQm6EU&start_radio=1")
    abrir_programa(["code"])
    abrir_terminal_com_comando("claude")



# ============================================================
#  UTILITÁRIOS
# ============================================================

def jarvis_diz(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"\n  [{ts}] JARVIS » {msg}")


def abrir_url(url: str):
    try:
        webbrowser.open(url)
        jarvis_diz(f"Navegador → {url}")
    except Exception as e:
        jarvis_diz(f"Erro ao abrir URL: {e}")


def abrir_programa(cmd: list):
    try:
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, start_new_session=True)
        jarvis_diz(f"Iniciando: {' '.join(cmd)}")
    except FileNotFoundError:
        jarvis_diz(f"Não encontrado: {cmd[0]}")
    except Exception as e:
        jarvis_diz(f"Erro: {e}")


def abrir_terminal_com_comando(cmd: str):
    try:
        subprocess.Popen(
            ["gnome-terminal", "--", "bash", "-c", f"{cmd}; exec bash"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        jarvis_diz(f"Terminal: {cmd}")
    except FileNotFoundError:
        try:
            subprocess.Popen(["xterm", "-e", f"bash -c '{cmd}; exec bash'"],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             start_new_session=True)
        except Exception as e:
            jarvis_diz(f"Erro ao abrir terminal: {e}")


def executar_comando(cmd: list):
    try:
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, start_new_session=True)
    except Exception as e:
        jarvis_diz(f"Erro: {e}")


# ============================================================
#  CARREGA ACCESS KEY
# ============================================================

def carregar_access_key() -> str:
    # 1. Variável de ambiente
    key = os.environ.get("PORCUPINE_ACCESS_KEY", "").strip()
    if key:
        return key

    # 2. Arquivo .env no mesmo diretório
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("PORCUPINE_ACCESS_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if key:
                        return key

    print("\n  ERRO: Access Key da Porcupine não encontrada.")
    print("  1. Crie sua chave gratuita em: https://console.picovoice.ai/")
    print("  2. Defina no terminal:  export PORCUPINE_ACCESS_KEY=\"sua-chave\"")
    print("     ou crie o arquivo .env com:  PORCUPINE_ACCESS_KEY=sua-chave")
    sys.exit(1)


# ============================================================
#  DETECTOR DE WAKE WORD
# ============================================================

def main():
    print("""
  ╔══════════════════════════════════════════════╗
  ║           J A R V I S   v4.0                ║
  ║      Wake Word "Jarvis" via Porcupine        ║
  ╠══════════════════════════════════════════════╣
  ║  • Fale "Jarvis" para ativar                 ║
  ║  • Ctrl+C para encerrar                      ║
  ╚══════════════════════════════════════════════╝""")

    access_key = carregar_access_key()

    try:
        porcupine = pvporcupine.create(
            access_key=access_key,
            keyword_paths=["Ei-claude_pt_linux_v4_0_0.ppn"],
            model_path="porcupine_params_pt.pv",
        )
    except pvporcupine.PorcupineInvalidArgumentError:
        print("\n  ERRO: Access Key inválida.")
        print("  Verifique sua chave em: https://console.picovoice.ai/")
        sys.exit(1)
    except pvporcupine.PorcupineActivationError:
        print("\n  ERRO: Access Key expirada ou sem cota.")
        sys.exit(1)
    except Exception as e:
        print(f"\n  ERRO ao inicializar Porcupine: {e}")
        sys.exit(1)

    pa = pyaudio.PyAudio()
    audio_stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length,
    )

    jarvis_diz("Sistemas online. Aguardando wake word...")
    print("  [·] Ouvindo... (fale 'Ei Claude')", end="", flush=True)

    ultima_ativacao = 0.0

    try:
        while True:
            pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            keyword_index = porcupine.process(pcm)

            if keyword_index >= 0:
                agora = time.monotonic()
                if agora - ultima_ativacao >= COOLDOWN:
                    ultima_ativacao = agora
                    threading.Thread(target=executar_acoes, daemon=True).start()
                    print(f"\r  [·] Ouvindo... (fale 'Jarvis')", end="", flush=True)

    except KeyboardInterrupt:
        jarvis_diz("Encerrando. Até logo, senhor.")
    finally:
        audio_stream.stop_stream()
        audio_stream.close()
        pa.terminate()
        porcupine.delete()


if __name__ == "__main__":
    main()
