import os
import sys
import glob
import time
import random
import threading
import signal
import subprocess
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
monitoring_dir = os.path.join(root_dir, "monitoring")
loadgen_dir = os.path.join(root_dir, "loadgen")

if monitoring_dir not in sys.path:
    sys.path.insert(0, monitoring_dir)
if loadgen_dir not in sys.path:
    sys.path.insert(0, loadgen_dir)

import queue_manager
import submitter

# -----------------------------------------------------------------------------
# Configuração da página Streamlit
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="JAMS: Helium Benchmark Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# Helpers de Ícones SVG Acessíveis (Substituição Completa de Emojis em UI)
# -----------------------------------------------------------------------------
SVG_ICONS = {
    "zap": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
    "play": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polygon points="5 3 19 12 5 21 5 3"/></svg>',
    "stop": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="6" y="6" width="12" height="12" rx="2"/></svg>',
    "trash": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>',
    "clock": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
    "users": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    "check-circle": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
    "x-circle": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
    "alert-triangle": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    "info": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>',
    "search": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
    "eye": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>',
    "code": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>',
    "server": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="2" width="20" height="8" rx="2" ry="2"/><rect x="2" y="14" width="20" height="8" rx="2" ry="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/></svg>',
    "send": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>',
    "refresh-cw": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>'
}

def render_svg_icon(name, size=18, color="currentColor", aria_hidden=True):
    template = SVG_ICONS.get(name, SVG_ICONS["info"])
    return template.format(size=size, color=color)

# -----------------------------------------------------------------------------
# Design System Tokens & Estilização CSS Global (WCAG AA & a11y)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Reset Global e Design Tokens */
    *, *::before, *::after {
        box-sizing: border-box;
    }

    :root {
        /* Paleta Semântica de Cores */
        --color-bg-main: #0d1117;
        --color-bg-card: #161b22;
        --color-bg-card-hover: #21262d;
        --color-border: #30363d;
        --color-border-hover: #8b949e;
        
        --color-text-primary: #f0f6fc;
        --color-text-secondary: #8b949e;
        --color-text-muted: #6e7681;
        
        --color-boca: #e3b341;
        --color-boca-bg: #271e05;
        --color-boca-border: #d29922;
        
        --color-helium: #58a6ff;
        --color-helium-bg: #0d2d17;
        --color-helium-border: #388bfd;
        
        --color-success: #3fb950;
        --color-success-bg: #0d2d17;
        --color-success-border: #238636;
        
        --color-error: #f85149;
        --color-error-bg: #3d1214;
        --color-error-border: #da3633;
        
        --color-warning: #d29922;
        --color-warning-bg: #271e05;
        --color-warning-border: #9e6a03;
        
        --color-info: #58a6ff;
        --color-info-bg: #0c2d6b;
        --color-info-border: #1f6beb;
        
        --color-focus: #58a6ff;

        /* Tokens de Espaçamento */
        --space-1: 4px;
        --space-2: 8px;
        --space-3: 12px;
        --space-4: 16px;
        --space-6: 24px;
        --space-8: 32px;

        /* Tokens de Radius */
        --radius-sm: 4px;
        --radius-md: 8px;
        --radius-lg: 12px;
        --radius-full: 9999px;

        /* Tokens de Tipografia */
        --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        --font-mono: "JetBrains Mono", "Fira Code", SFMono-Regular, Consolas, monospace;
        
        --font-size-xs: 0.75rem;
        --font-size-sm: 0.875rem;
        --font-size-base: 1rem;
        --font-size-lg: 1.25rem;
        --font-size-xl: 1.5rem;
        --font-size-2xl: 2rem;

        --line-height-heading: 1.25;
        --line-height-body: 1.5;
    }

    /* Container Principal */
    .main {
        background-color: var(--color-bg-main);
        color: var(--color-text-primary);
        font-family: var(--font-sans);
        line-height: var(--line-height-body);
    }

    /* Acessibilidade: Foco de Teclado Visível */
    *:focus-visible {
        outline: 2px solid var(--color-focus) !important;
        outline-offset: 2px !important;
    }

    /* Suporte a Prefers Reduced Motion */
    @media (prefers-reduced-motion: reduce) {
        *, ::before, ::after {
            animation-duration: 0.01ms !important;
            transition-duration: 0.01ms !important;
        }
    }

    /* Estilização de Containers Semânticos */
    header, main, section, article, aside, nav {
        max-width: 100%;
        overflow-x: auto;
    }

    .stMetric, div[data-testid="stMetric"], div[data-testid="metric-container"] {
        background-color: var(--color-bg-card);
        border: 1px solid var(--color-border);
        border-radius: var(--radius-md);
        padding: var(--space-3);
        height: 100%;
        min-height: 110px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    div[data-testid="stMetricValue"] {
        font-size: var(--font-size-xl);
        font-weight: 700;
        color: var(--color-text-primary);
        font-family: var(--font-mono);
    }

    /* Cabeçalhos dos Sistemas */
    .boca-header {
        color: var(--color-boca);
        font-weight: 700;
        font-size: var(--font-size-lg);
        border-bottom: 2px solid var(--color-boca);
        padding-bottom: var(--space-1);
        margin-top: var(--space-4);
        margin-bottom: var(--space-3);
        display: flex;
        align-items: center;
        gap: var(--space-2);
    }

    .helium-header {
        color: var(--color-helium);
        font-weight: 700;
        font-size: var(--font-size-lg);
        border-bottom: 2px solid var(--color-helium);
        padding-bottom: var(--space-1);
        margin-top: var(--space-4);
        margin-bottom: var(--space-3);
        display: flex;
        align-items: center;
        gap: var(--space-2);
    }

    /* Banners de Status de Leitura */
    .status-banner-off {
        background-color: var(--color-error-bg);
        border: 1px solid var(--color-error-border);
        color: var(--color-error);
        padding: var(--space-3) var(--space-4);
        border-radius: var(--radius-md);
        font-weight: 600;
        margin-bottom: var(--space-4);
        display: flex;
        align-items: center;
        gap: var(--space-2);
    }

    .status-banner-on {
        background-color: var(--color-success-bg);
        border: 1px solid var(--color-success-border);
        color: var(--color-success);
        padding: var(--space-3) var(--space-4);
        border-radius: var(--radius-md);
        font-weight: 600;
        margin-bottom: var(--space-4);
        display: flex;
        align-items: center;
        gap: var(--space-2);
    }

    .status-banner-paused {
        background-color: var(--color-warning-bg);
        border: 1px solid var(--color-warning-border);
        color: var(--color-warning);
        padding: var(--space-3) var(--space-4);
        border-radius: var(--radius-md);
        font-weight: 600;
        margin-bottom: var(--space-4);
        display: flex;
        align-items: center;
        gap: var(--space-2);
    }

    /* Cards de Requisição da Fila */
    .queue-card {
        background-color: var(--color-bg-card);
        border-radius: var(--radius-md);
        padding: var(--space-3);
        margin-bottom: var(--space-2);
        display: flex;
        flex-direction: column;
        gap: var(--space-1);
        transition: background-color 0.2s ease;
    }

    .queue-card:hover {
        background-color: var(--color-bg-card-hover);
    }

    .queue-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: var(--space-2);
    }

    .queue-card-title {
        font-weight: 700;
        color: var(--color-text-primary);
        font-family: var(--font-mono);
        font-size: var(--font-size-sm);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 65%;
    }

    .queue-card-badge {
        font-weight: 700;
        font-size: var(--font-size-xs);
        padding: var(--space-1) var(--space-2);
        border-radius: var(--radius-sm);
        display: inline-flex;
        align-items: center;
        gap: var(--space-1);
        white-space: nowrap;
        font-family: var(--font-mono);
    }

    .queue-card-meta {
        font-size: var(--font-size-xs);
        color: var(--color-text-secondary);
        display: flex;
        flex-wrap: wrap;
        gap: var(--space-3);
        align-items: center;
    }

    /* Target de toque adequado (44px+) */
    .stButton button {
        min-height: 44px;
        border-radius: var(--radius-md);
        font-weight: 600;
    }

    /* Media Queries Responsivos */
    @media (max-width: 768px) {
        div[data-testid="stMetricValue"] {
            font-size: var(--font-size-lg);
        }
        .queue-card-meta {
            flex-direction: column;
            align-items: flex-start;
            gap: var(--space-1);
        }
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Inicialização do Session State
# -----------------------------------------------------------------------------
if "is_running" not in st.session_state:
    st.session_state["is_running"] = False

if "spawned_pids" not in st.session_state:
    st.session_state["spawned_pids"] = []

if "df_boca" not in st.session_state:
    st.session_state["df_boca"] = None

if "df_helium" not in st.session_state:
    st.session_state["df_helium"] = None

# -----------------------------------------------------------------------------
# Funções Auxiliares de Telemetria 100% Real
# -----------------------------------------------------------------------------

def get_real_resting_telemetry(target_system="helium"):
    containers = {
        "helium-webserver", "helium-app", "helium-autojudge", "helium-redis", "helium-db",
        "microhelium-webserver", "microhelium-app", "microhelium-autojudge", "microhelium-redis", "microhelium-db"
    }
    cmds = [
        "docker stats --no-stream --format \"{{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\"",
        "sg docker -c '\''docker stats --no-stream --format \"{{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\"'\''",
        "sudo -n docker stats --no-stream --format \"{{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\""
    ]
    out = ""
    for cmd in cmds:
        try:
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=4)
            if res.returncode == 0 and res.stdout:
                out = res.stdout
                break
        except Exception:
            pass

    if out:
        total_cpu = 0.0
        total_ram_mb = 0.0
        found = False
        for line in out.strip().splitlines():
            parts = line.split("\t")
            if len(parts) >= 3 and parts[0] in containers:
                found = True
                try:
                    cpu_val = float(parts[1].replace("%", "").strip())
                    total_cpu += cpu_val
                except Exception:
                    pass
                try:
                    mem_str = parts[2].split("/")[0].strip()
                    if "GiB" in mem_str:
                        val = float(mem_str.replace("GiB", "").strip()) * 1024.0
                    elif "MiB" in mem_str:
                        val = float(mem_str.replace("MiB", "").strip())
                    elif "KiB" in mem_str:
                        val = float(mem_str.replace("KiB", "").strip()) / 1024.0
                    elif "B" in mem_str:
                        val = float(mem_str.replace("B", "").strip()) / (1024.0 * 1024.0)
                    else:
                        val = 0.0
                    total_ram_mb += val
                except Exception:
                    pass
        if found:
            return {
                "online": True,
                "cpu_user": round(total_cpu, 2),
                "cpu_system": 0.0,
                "ram_used_mb": round(total_ram_mb, 1)
            }

    return {"online": False, "cpu_user": 0.0, "cpu_system": 0.0, "ram_used_mb": 0.0}

def load_real_metrics(target_system, scenario):
    results_dir = os.path.join(root_dir, "results", target_system, scenario)
    sar_file = os.path.join(results_dir, "sar_metrics.csv")
    raw_log = os.path.join(results_dir, "sar_raw.txt")

    if os.path.exists(raw_log):
        try:
            from parse_sar import parse_sar_raw
            parse_sar_raw(raw_log, sar_file)
        except Exception:
            pass

    if os.path.exists(sar_file):
        try:
            df_sar = pd.read_csv(sar_file)
            if not df_sar.empty and "cpu_user" in df_sar.columns:
                return df_sar
        except Exception:
            pass

    return None

def get_locust_executable():
    venv_locust = os.path.abspath(os.path.join(root_dir, "venv", "bin", "locust"))
    if os.path.exists(venv_locust):
        return venv_locust
    return "locust"

def start_real_load_and_telemetry_session(scenario, sampling_interval, user_count, enabled_verdicts):
    sar_script = os.path.join(root_dir, "monitoring", "sar-collect.sh")
    proc_sar_helium = subprocess.Popen([sar_script, "helium", scenario, str(sampling_interval)], cwd=root_dir)
    st.session_state["spawned_pids"].append(proc_sar_helium.pid)

    venv_python = os.path.abspath(os.path.join(root_dir, "venv", "bin", "python"))
    python_bin = venv_python if os.path.exists(venv_python) else sys.executable
    verdicts_str = ",".join(enabled_verdicts) if enabled_verdicts else "AC"

    locust_bin = get_locust_executable()
    locust_file = os.path.join(root_dir, "loadgen", "locustfile.py")
    env_helium = os.environ.copy()
    env_helium["TARGET_SYSTEM"] = "helium"
    env_helium["ENABLED_VERDICTS"] = verdicts_str
    env_helium["WAIT_INTERVAL"] = str(sampling_interval)
    env_helium["SCENARIO"] = scenario
    helium_host = os.getenv("HELIUM_HOST", "http://127.0.0.10:8000")
    proc_locust_helium = subprocess.Popen([
        locust_bin, "-f", locust_file,
        "--host", helium_host,
        "--headless", "-u", str(user_count), "-r", str(user_count)
    ], cwd=root_dir, env=env_helium)
    st.session_state["spawned_pids"].append(proc_locust_helium.pid)

def stop_real_load_session():
    for pid in st.session_state.get("spawned_pids", []):
        try:
            os.kill(pid, signal.SIGTERM)
        except Exception:
            pass
        try:
            os.kill(pid, signal.SIGKILL)
        except Exception:
            pass
    st.session_state["spawned_pids"] = []

def clear_all_records():
    stop_real_load_session()
    st.session_state["df_boca"] = None
    st.session_state["df_helium"] = None
    st.session_state["is_running"] = False
    queue_manager.clear_queue()
    
    results_dir = os.path.join(root_dir, "results")
    try:
        for root_path, dirs, files in os.walk(results_dir):
            for file in files:
                os.remove(os.path.join(root_path, file))
    except Exception:
        pass

# -----------------------------------------------------------------------------
# Verificação de Saúde (Health Check)
# -----------------------------------------------------------------------------
import requests
def check_helium_status():
    helium_host = os.getenv("HELIUM_HOST", "http://127.0.0.10:8000")
    try:
        requests.get(helium_host, timeout=1)
        return True
    except Exception:
        return False

# -----------------------------------------------------------------------------
# Modal Dialog Acessível para Código Fonte
# -----------------------------------------------------------------------------
@st.dialog("Código Fonte da Submissão")
def render_code_modal(sub):
    target_name = "BOCA" if sub["target"] == "boca" else "Helium"
    verdict = sub.get("verdict") or "PENDING"
    status = sub.get("status") or "pending"
    
    st.markdown(f"### {render_svg_icon('code', 20, 'var(--color-text-primary)')} Submissão #{sub['id']} — {target_name}", unsafe_allow_html=True)
    
    m1, m2 = st.columns(2)
    with m1:
        st.markdown(f"**Equipe:** {sub.get('team', '-')}")
        st.markdown(f"**Linguagem:** {str(sub.get('language', '-')).upper()}")
    with m2:
        st.markdown(f"**Status:** {status.upper()}")
        st.markdown(f"**Veredito:** {verdict}")

    sub_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(sub.get('submitted_at', time.time())))
    st.markdown(f"**Arquivo:** `{sub.get('filename', 'exercise.cpp')}` | **Problema:** `{sub.get('problem', 'A')}` | **Horário:** `{sub_time_str}`")
    
    if sub.get("http_latency_ms") or sub.get("judge_latency_ms"):
        st.info(f"Latência HTTP: {sub.get('http_latency_ms', 0):.1f} ms | Latência de Julgamento: {sub.get('judge_latency_ms', 0):.1f} ms")

    st.markdown("#### Código Fonte Enviado:")
    lang_str = str(sub.get("language", "cpp")).lower()
    code_lang = "python" if "py" in lang_str else "cpp"
    
    st.code(sub.get("source_code", "// Nenhum código-fonte encontrado"), language=code_lang, line_numbers=True)

    if sub.get("error_message"):
        with st.expander("Detalhes do Erro / Feedback de Execução", expanded=True):
            st.error(sub["error_message"])

# -----------------------------------------------------------------------------
# Barra Lateral (Sidebar) - Painel de Controle Master com Imagem Otimizada / Alt
# -----------------------------------------------------------------------------
st.sidebar.markdown(f"""
<aside aria-label="Painel de Controle Master">
    <div style="display: flex; align-items: center; gap: var(--space-2); margin-bottom: var(--space-3);">
        <img src="https://img.icons8.com/color/96/000000/dashboard.png" alt="Logo JAMS Benchmark Dashboard" loading="lazy" width="48" height="48" style="object-fit: contain;" />
        <h2 style="margin: 0; font-size: var(--font-size-lg); color: var(--color-text-primary);">JAMS Control</h2>
    </div>
</aside>
""", unsafe_allow_html=True)

col_btn1, col_btn2 = st.sidebar.columns(2)

with col_btn1:
    if st.sidebar.button("LIGAR", disabled=st.session_state["is_running"], type="primary", use_container_width=True):
        st.session_state["is_running"] = True
        st.rerun()

with col_btn2:
    if st.sidebar.button("DESLIGAR", disabled=not st.session_state["is_running"], use_container_width=True):
        stop_real_load_session()
        st.session_state["is_running"] = False
        st.rerun()

if st.sidebar.button("Limpar Registros", use_container_width=True):
    clear_all_records()
    st.sidebar.success("Registros e filas limpos com sucesso!")
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown(f"<h3 style='font-size: var(--font-size-sm); color: var(--color-text-secondary);'>CONFIGURAÇÕES DE TESTE</h3>", unsafe_allow_html=True)

sampling_interval = st.sidebar.slider(
    "Frequência de Amostragem (segundos)",
    min_value=1, max_value=10, value=1, step=1,
    help="Altera o intervalo de amostragem de dados em tempo de execução."
)

user_count = st.sidebar.slider(
    "Usuários Simultâneos (N Users)",
    min_value=1, max_value=100, value=5, step=1,
    help="Número de usuários virtuais enviando submissões HTTP concorrentes."
)

st.sidebar.markdown("**Checklist de Vereditos:**")
verdict_ac = st.sidebar.checkbox("ACCEPTED (AC)", value=True)
verdict_wa = st.sidebar.checkbox("WRONG ANSWER (WA)", value=True)
verdict_tle = st.sidebar.checkbox("TIME LIMIT EXCEEDED (TLE)", value=True)
verdict_ce = st.sidebar.checkbox("COMPILATION ERROR (CE)", value=True)

enabled_verdicts = []
if verdict_ac: enabled_verdicts.append("AC")
if verdict_wa: enabled_verdicts.append("WA")
if verdict_tle: enabled_verdicts.append("TLE")
if verdict_ce: enabled_verdicts.append("CE")

import json
config_path = os.path.join(root_dir, "results", "locust_config.json")
os.makedirs(os.path.dirname(config_path), exist_ok=True)
try:
    with open(config_path, "w") as f:
        json.dump({"enabled_verdicts": enabled_verdicts}, f)
except Exception:
    pass

scenario = st.sidebar.selectbox(
    "Cenário de Estresse:",
    options=["burst", "baseline", "steady", "ramp", "endurance"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"""
<div style="font-size: var(--font-size-xs); color: var(--color-text-secondary);">
    <p style="margin: var(--space-1) 0;"><strong>Helium Stack:</strong> <code>127.0.0.10:8000</code></p>
    <p style="margin: var(--space-1) 0;"><strong>Ambiente:</strong> Docker Compose (Paridade 2 vCPU / 2GB)</p>
</div>
""", unsafe_allow_html=True)

if st.session_state["is_running"] and not st.session_state.get("spawned_pids"):
    start_real_load_and_telemetry_session(scenario, sampling_interval, user_count, enabled_verdicts)

# -----------------------------------------------------------------------------
# Cabeçalho Principal e Banner de Estado Semânticos (a11y)
# -----------------------------------------------------------------------------
st.markdown(f"""
<header role="banner">
    <h1 style="display: flex; align-items: center; gap: var(--space-3); font-size: var(--font-size-2xl); margin-bottom: var(--space-2);">
        {render_svg_icon('zap', 32, 'var(--color-helium)')}
        JAMS — Judge Assessment & Metrics Suite
    </h1>
</header>
""", unsafe_allow_html=True)

has_stored_data = st.session_state.get("df_helium") is not None and not st.session_state["df_helium"].empty

helium_online = check_helium_status()

if not helium_online:
    st.markdown(f"""
    <div class="status-banner-off" role="status" aria-live="polite">
        {render_svg_icon('x-circle', 20, 'var(--color-error)')}
        <span>HELIUM OFFLINE: Não foi possível conectar ao servidor Helium. Por favor, certifique-se de que ele esteja rodando externamente.</span>
    </div>
    """, unsafe_allow_html=True)
    if st.session_state["is_running"]:
        stop_real_load_session()
        st.session_state["is_running"] = False
        st.rerun()
elif st.session_state["is_running"]:
    st.markdown(f"""
    <div class="status-banner-on" role="status" aria-live="polite">
        {render_svg_icon('check-circle', 20, 'var(--color-success)')}
        <span>LEITURA DE DADOS EM TEMPO REAL ATIVA: A amostragem de telemetria está atualizando os gráficos em tempo real.</span>
    </div>
    """, unsafe_allow_html=True)
elif has_stored_data:
    st.markdown(f"""
    <div class="status-banner-paused" role="status" aria-live="polite">
        {render_svg_icon('alert-triangle', 20, 'var(--color-warning)')}
        <span>LEITURA PAUSADA (DADOS FIXADOS NA TELA): Os registros acumulados permanecem visíveis para análise. Clique em "LIGAR" para retomar.</span>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="status-banner-off" role="status" aria-live="polite">
        {render_svg_icon('info', 20, 'var(--color-text-secondary)')}
        <span>MODO DE OBSERVAÇÃO EM REPOUSO (STANDBY): Clique em "LIGAR" para iniciar a leitura de dados novos ou execute testes via CLI.</span>
    </div>
    """, unsafe_allow_html=True)

st.caption(f"Cenário: **{scenario.upper()}** | Usuários Simultâneos: **{user_count}** | Amostragem: **{sampling_interval}s** | Estado: **{'LIGADO (Leitura Ativa)' if st.session_state['is_running'] else ('PAUSADO (Dados Fixados)' if has_stored_data else 'STANDBY')}**")

# -----------------------------------------------------------------------------
# Carregamento e Acumulação de Dados de Telemetria
# -----------------------------------------------------------------------------
if st.session_state["is_running"]:
    new_helium = load_real_metrics("helium", scenario)
    if new_helium is not None and not new_helium.empty:
        if st.session_state.get("df_helium") is not None and not st.session_state["df_helium"].empty:
            combined = pd.concat([st.session_state["df_helium"], new_helium], ignore_index=True)
            st.session_state["df_helium"] = combined.drop_duplicates(subset=["timestamp"], keep="last").reset_index(drop=True)
        else:
            st.session_state["df_helium"] = new_helium

df_boca = None
df_helium = st.session_state.get("df_helium")

idle_boca = None
idle_helium = None
if (df_helium is None or df_helium.empty) and not st.session_state["is_running"]:
    with st.spinner("Lendo telemetria REAL de repouso dos containers via Docker stats..."):
        idle_helium = get_real_resting_telemetry("helium")

# -----------------------------------------------------------------------------
# Widget de Disparo de Submissão de Teste Rápido
# -----------------------------------------------------------------------------
with st.expander("Disparar Exercício de Teste Rápido (Submissão Pontual)", expanded=False):
    st.markdown("Envie uma requisição de avaliação individual para observar a chegada na fila correspondente e a transição de estado em tempo real.")
    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        target_choice = st.selectbox(
            "Sistema Alvo:", 
            ["helium"], 
            format_func=lambda x: "Helium"
        )
    with col_t2:
        lang_choice = st.selectbox("Linguagem:", ["cpp", "py"], format_func=lambda x: "C++17 (g++)" if x == "cpp" else "Python 3")
    with col_t3:
        preset_choice = st.selectbox("Template de Exercício:", ["ac_sum", "wa_sum", "tle_loop", "ce_syntax", "custom"], format_func=lambda x: f"{x}.{lang_choice}")
    
    if preset_choice == "custom":
        default_code = '#include <iostream>\nusing namespace std;\nint main() {\n    cout << "Hello from Antigravity!" << endl;\n    return 0;\n}' if lang_choice == "cpp" else 'print("Hello from Antigravity!")'
        custom_code = st.text_area("Código-Fonte Customizado:", value=default_code, height=120)
    else:
        custom_code = None

    if st.button("Enviar Requisição para a Fila", type="primary", use_container_width=True):
        filename_val = f"{preset_choice}.{lang_choice}"
        team_id = f"team{random.randint(1, 100)}"
        t = threading.Thread(
            target=submitter.submit_test_run,
            kwargs={
                "target": target_choice,
                "filename": filename_val,
                "custom_code": custom_code,
                "team": team_id,
                "lang": lang_choice
            },
            daemon=True
        )
        t.start()
        st.success(f"Submissão enfileirada com sucesso como {team_id}! Acompanhe o veredito no card abaixo.")
        time.sleep(0.3)
        st.rerun()

# -----------------------------------------------------------------------------
# Renderização da Fila de Requisições Semântica e Acessível
# -----------------------------------------------------------------------------
def get_verdict_badge_data(status, verdict):
    verdict = (verdict or "PENDING").upper()
    status = (status or "pending").lower()
    
    if status == "error" or verdict in ["CE", "RE", "ERR"]:
        if verdict == "CE":
            return "CE", "Compilation Error", render_svg_icon("x-circle", 14, "var(--color-error)"), "var(--color-error)", "var(--color-error-bg)"
        elif verdict == "RE":
            return "RE", "Runtime Error", render_svg_icon("x-circle", 14, "var(--color-error)"), "var(--color-error)", "var(--color-error-bg)"
        else:
            return "ERR", "Erro no Sistema", render_svg_icon("x-circle", 14, "var(--color-error)"), "var(--color-error)", "var(--color-error-bg)"
    elif status == "judged":
        if verdict == "AC":
            return "AC", "Accepted", render_svg_icon("check-circle", 14, "var(--color-success)"), "var(--color-success)", "var(--color-success-bg)"
        elif verdict == "WA":
            return "WA", "Wrong Answer", render_svg_icon("x-circle", 14, "var(--color-error)"), "var(--color-error)", "var(--color-error-bg)"
        elif verdict == "TLE":
            return "TLE", "Time Limit Exceeded", render_svg_icon("clock", 14, "var(--color-warning)"), "var(--color-warning)", "var(--color-warning-bg)"
        else:
            return verdict[:3], f"Validada ({verdict})", render_svg_icon("info", 14, "var(--color-text-secondary)"), "var(--color-border)", "var(--color-bg-card-hover)"
    elif status == "judging":
        return "JUD", "Validando / Julgando...", render_svg_icon("refresh-cw", 14, "var(--color-warning)"), "var(--color-warning)", "var(--color-warning-bg)"
    else:
        return "PEN", "Aguardando na Fila", render_svg_icon("clock", 14, "var(--color-info)"), "var(--color-info)", "var(--color-info-bg)"

def render_submission_card(sub, target_system, key_prefix="main", idx=0):
    sub_id = sub["id"]
    status = sub["status"]
    verdict = sub.get("verdict") or "PENDING"
    filename = sub["filename"]
    team = sub["team"]
    lang = str(sub["language"]).upper()
    sub_time = time.strftime('%H:%M:%S', time.localtime(sub["submitted_at"]))
    target_title = "BOCA" if target_system == "boca" else "Helium"
    
    acronym, full_text, badge_icon, border_color, badge_bg = get_verdict_badge_data(status, verdict)
    
    import urllib.parse
    eye_svg = SVG_ICONS["eye"].format(size=20, color="#f0f6fc")
    eye_svg_hover = SVG_ICONS["eye"].format(size=20, color="#58a6ff")
    enc_eye = urllib.parse.quote(eye_svg)
    enc_hover = urllib.parse.quote(eye_svg_hover)
    
    with st.container():
        st.markdown(f"""
        <div id="rel-wrapper-{key_prefix}-{sub_id}" style="display: none;"></div>
        <article class="queue-card" style="border-left: 4px solid {border_color}; margin-bottom: 0; padding-right: 50px;" tabindex="0">
            <div class="queue-card-header">
                <span class="queue-card-title" title="#Run {sub_id} — {filename}">#Run {sub_id} — {filename}</span>
                <span class="queue-card-badge" title="{full_text}" style="background-color: {badge_bg}; color: {border_color}; border: 1px solid {border_color};">
                    {badge_icon} [{acronym}]
                </span>
            </div>
            <div class="queue-card-meta">
                <span>Equipe: <strong>{team}</strong></span>
                <span>Linguagem: <strong>{lang}</strong></span>
                <span>Horário: <strong>{sub_time}</strong></span>
                <span>HTTP: <strong>{sub['http_latency_ms']:.0f}ms</strong></span>
                <span>Juiz: <strong>{sub['judge_latency_ms']:.0f}ms</strong></span>
            </div>
        </article>
        <style>
            /* 1. Make the Streamlit vertical block of THIS container relative */
            div[data-testid="stVerticalBlock"]:has(> div.element-container div#rel-wrapper-{key_prefix}-{sub_id}) {{
                position: relative;
                margin-bottom: var(--space-2);
            }}
            /* 2. Make the LAST element-container (the button) absolutely positioned at top-right */
            div[data-testid="stVerticalBlock"]:has(> div.element-container div#rel-wrapper-{key_prefix}-{sub_id}) > div.element-container:last-child {{
                position: absolute;
                top: 15px;
                right: 15px;
                width: 32px;
                z-index: 10;
            }}
            /* 3. Style the button to show the SVG */
            div[data-testid="stVerticalBlock"]:has(> div.element-container div#rel-wrapper-{key_prefix}-{sub_id}) > div.element-container:last-child button {{
                background-color: transparent !important;
                border: none !important;
                box-shadow: none !important;
                color: transparent !important;
                width: 32px;
                height: 32px;
                background-image: url("data:image/svg+xml;utf8,{enc_eye}");
                background-repeat: no-repeat;
                background-position: center;
                padding: 0;
                min-height: 0;
                transition: transform 0.2s;
            }}
            div[data-testid="stVerticalBlock"]:has(> div.element-container div#rel-wrapper-{key_prefix}-{sub_id}) > div.element-container:last-child button:hover {{
                background-image: url("data:image/svg+xml;utf8,{enc_hover}");
                transform: scale(1.1);
            }}
            div[data-testid="stVerticalBlock"]:has(> div.element-container div#rel-wrapper-{key_prefix}-{sub_id}) > div.element-container:last-child button p {{
                display: none;
            }}
        </style>
        """, unsafe_allow_html=True)
        
        if st.button("view", key=f"{key_prefix}_btn_card_{target_system}_{sub_id}_{idx}", help=f"Ver Código (Run #{sub_id} - {target_title})"):
            render_code_modal(sub)

@st.dialog("Fila Completa de Requisições")
def render_full_queue_modal(target_system):
    target_title = "BOCA" if target_system == "boca" else "Helium"
    st.markdown(f"### {render_svg_icon('server', 20, 'var(--color-text-primary)')} Fila Completa — {target_title}", unsafe_allow_html=True)
    
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        status_filter = st.selectbox(
            f"Filtro Status ({target_title}):",
            options=["Todas", "Aguardando / Validando", "Já Validadas", "Com Erro", "AC", "WA", "TLE", "CE"],
            key=f"modal_status_filter_{target_system}"
        )
    with f_col2:
        lang_filter = st.selectbox(
            f"Filtro Linguagem ({target_title}):",
            options=["Todas", "C++ (.cpp)", "Python (.py)"],
            key=f"modal_lang_filter_{target_system}"
        )
    
    search_term = st.text_input(f"Buscar ({target_title}):", key=f"modal_search_{target_system}", placeholder="Filtrar por equipe ou arquivo...", label_visibility="visible")

    submissions = queue_manager.fetch_queue(
        target=target_system,
        status_filter=status_filter,
        lang_filter=lang_filter,
        search=search_term,
        limit=100
    )
    
    if not submissions:
        st.info(f"Nenhuma requisição na fila do {target_title} para os filtros selecionados.")
        return

    st.markdown(f"**Exibindo {len(submissions)} requisição(ões) encontradas:**")
    for idx, sub in enumerate(submissions):
        render_submission_card(sub, target_system, key_prefix="modal", idx=idx)

# -----------------------------------------------------------------------------
# Renderização da Fila de Requisições Semântica e Acessível
# -----------------------------------------------------------------------------
def render_request_queue(target_system, header_class):
    target_title = "BOCA" if target_system == "boca" else "Helium"
    header_color = "var(--color-boca)" if target_system == "boca" else "var(--color-helium)"
    
    st.markdown(f"""
    <section aria-label="Fila de Requisições {target_title}">
        <h3 class="{header_class}">
            {render_svg_icon('server', 20, header_color)}
            Fila de Requisições: {target_title}
        </h3>
    </section>
    """, unsafe_allow_html=True)
    
    summary = queue_manager.get_queue_summary(target_system)
    q1, q2, q3, q4 = st.columns(4)
    q1.metric("Total Fila", summary["total"])
    q2.metric("Aguardando", summary["pending"] + summary["judging"])
    q3.metric("Já Validadas", summary["judged"])
    q4.metric("Com Erro", summary["error"])

    f_col1, f_col2 = st.columns([3, 1])
    with f_col2:
        filter_err = st.checkbox("Apenas Erros", key=f"main_err_filter_{target_system}")

    status_filter = "Com Erro" if filter_err else None
    initial_limit = 5
    submissions = queue_manager.fetch_queue(
        target=target_system,
        status_filter=status_filter,
        limit=initial_limit
    )
    queue_manager.log_event(f"[DASHBOARD] Render main queue summary for {target_title} (Found {len(submissions)} / Total {summary['total']})")

    if not submissions:
        st.info(f"Nenhuma requisição na fila do {target_title}.")
    else:
        with f_col1:
            st.markdown(f"**Últimas {len(submissions)} de {summary['total']} requisições efetuadas:**")
        for idx, sub in enumerate(submissions):
            render_submission_card(sub, target_system, key_prefix="main", idx=idx)

    if st.button(f"Ver Fila Completa ({summary['total']} itens - {target_title})", key=f"btn_full_queue_{target_system}", use_container_width=True):
        render_full_queue_modal(target_system)

# -----------------------------------------------------------------------------
# Seção de Métricas do Sistema
# -----------------------------------------------------------------------------
def render_system_metrics(system_name, df_sar, idle_info, header_class):
    color_theme = "#e3b341" if system_name == "BOCA" else "#58a6ff"
    
    st.markdown(f"""
    <section aria-label="Métricas de Sistema {system_name}">
        <h3 class="{header_class}">
            {render_svg_icon('zap', 20, color_theme)}
            {system_name} System Metrics
        </h3>
    </section>
    """, unsafe_allow_html=True)
    
    if df_sar is not None and not df_sar.empty:
        status_text = "Leitura Ativa" if st.session_state["is_running"] else "Leitura Pausada"
        st.caption(f"Status: **{status_text}** | Registros: **{len(df_sar)} pontos**")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("CPU Load Avg", f"{df_sar['cpu_user'].mean():.1f}%", delta=f"{df_sar['cpu_user'].iloc[-1] - df_sar['cpu_user'].iloc[0]:.1f}%")
        with col2:
            ram_val = df_sar['ram_used_mb'].iloc[-1] if 'ram_used_mb' in df_sar.columns else 0
            st.metric("RAM Utilizada", f"{ram_val:.0f} MB", delta="2048 MB Max")
        with col3:
            http_lat = df_sar['http_latency_ms'].dropna() if 'http_latency_ms' in df_sar.columns else []
            val_http = float(pd.Series(http_lat).quantile(0.95)) if len(http_lat) > 0 else 0
            st.metric("HTTP Latency (p95)", f"{val_http:.0f} ms")
        with col4:
            judge_lat = df_sar['judge_latency_ms'].dropna() if 'judge_latency_ms' in df_sar.columns else []
            val_judge = float(pd.Series(judge_lat).mean()) if len(judge_lat) > 0 else 0
            st.metric("Judge Latency Avg", f"{val_judge:.0f} ms")

        fig_cpu = px.line(
            df_sar, x="timestamp", y=["cpu_user", "cpu_system"],
            labels={"value": "Uso de CPU (%)", "timestamp": "Tempo"},
            title=f"Uso de CPU - {system_name}",
            color_discrete_sequence=[color_theme, "#f85149"]
        )
        fig_cpu.update_layout(template="plotly_dark", height=280, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_cpu, use_container_width=True)

        if "http_latency_ms" in df_sar.columns and "judge_latency_ms" in df_sar.columns:
            fig_lat = px.line(
                df_sar, x="timestamp", y=["http_latency_ms", "judge_latency_ms"],
                labels={"value": "Latência (ms)", "timestamp": "Tempo"},
                title=f"Latência HTTP vs Julgamento - {system_name}",
                color_discrete_sequence=[color_theme, "#a5d6ff"]
            )
            fig_lat.update_layout(template="plotly_dark", height=280, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_lat, use_container_width=True)

    elif st.session_state["is_running"]:
        st.warning(f"Aguardando primeiros dados de telemetria real do {system_name}...")

    else:
        if idle_info and idle_info.get("online"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Status da Stack", "ONLINE (Repouso)", delta="Sem requisições")
            with col2:
                st.metric("CPU em Repouso (%user)", f"{idle_info['cpu_user']:.1f}%")
            with col3:
                st.metric("RAM em Repouso", f"{idle_info['ram_used_mb']:.0f} MB")
            
            st.info(f"{system_name} está pronto. Clique em 'LIGAR' para iniciar a amostragem e leitura de dados.")
        else:
            st.error(f"Stack {system_name} inacessível ou desligada. Execute 'make up' (ou 'make {system_name.lower()}-up') para iniciá-la.")


# -----------------------------------------------------------------------------
# Exibição de Fila e Métricas Focadas no Helium
# -----------------------------------------------------------------------------
st.markdown("<main role='main'>", unsafe_allow_html=True)

render_system_metrics("Helium", df_helium, idle_helium, "helium-header")
st.markdown("---")
render_request_queue("helium", "helium-header")

st.markdown("</main>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Painel de Vereditos (Exibe sempre que houver dados acumulados)
# -----------------------------------------------------------------------------
if has_stored_data:
    st.markdown("---")
    st.subheader("Distribuição de Vereditos Reais")
    
    col_v1, col_v2 = st.columns(2)
    
    with col_v1:
        categories = enabled_verdicts if enabled_verdicts else ["AC"]
        helium_ac = df_helium["ac_count"].sum() if df_helium is not None and "ac_count" in df_helium.columns else 0
        helium_wa = df_helium["wa_count"].sum() if df_helium is not None and "wa_count" in df_helium.columns else 0
        helium_tle = df_helium["tle_count"].sum() if df_helium is not None and "tle_count" in df_helium.columns else 0

        helium_vals = [helium_ac if "AC" in categories else 0, helium_wa if "WA" in categories else 0, helium_tle if "TLE" in categories else 0]

        fig_verdicts = go.Figure(data=[
            go.Bar(name="Helium", x=categories[:len(helium_vals)], y=helium_vals, marker_color="#58a6ff")
        ])
        fig_verdicts.update_layout(barmode="group", template="plotly_dark", title="Vereditos de Teste Filtrados (Helium)", height=300)
        st.plotly_chart(fig_verdicts, use_container_width=True)

    with col_v2:
        fig_comp_cpu = go.Figure()
        if df_helium is not None and "cpu_user" in df_helium.columns:
            fig_comp_cpu.add_trace(go.Scatter(x=df_helium["timestamp"], y=df_helium["cpu_user"], name="Helium CPU %", line=dict(color="#58a6ff")))
        fig_comp_cpu.update_layout(template="plotly_dark", title="Evolução de Carga de CPU (%user) - Helium", height=300)
        st.plotly_chart(fig_comp_cpu, use_container_width=True)

# Auto-refresh em runtime quando LIGADO ou quando houver submissões ativas pendentes
if st.session_state["is_running"]:
    time.sleep(sampling_interval)
    st.rerun()
else:
    try:
        summary = queue_manager.get_queue_summary("helium")
        if summary.get("pending", 0) > 0 or summary.get("judging", 0) > 0:
            time.sleep(1.5)
            st.rerun()
    except Exception:
        pass
