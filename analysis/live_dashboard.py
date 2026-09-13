import os
import glob
import time
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Configuração da página Streamlit
st.set_page_config(
    page_title="JAMS: BOCA vs Helium Benchmark Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS personalizada (Dark Mode GitHub/Monitoring Style)
st.markdown("""
<style>
    .main {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    .stMetric {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 12px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
    }
    .boca-header {
        color: #e3b341;
        font-weight: 700;
        border-bottom: 2px solid #e3b341;
        padding-bottom: 4px;
    }
    .helium-header {
        color: #58a6ff;
        font-weight: 700;
        border-bottom: 2px solid #58a6ff;
        padding-bottom: 4px;
    }
    .status-banner-off {
        background-color: #3d1214;
        border: 1px solid #f85149;
        color: #ff7b72;
        padding: 12px 16px;
        border-radius: 8px;
        font-weight: 600;
        margin-bottom: 16px;
    }
    .status-banner-on {
        background-color: #0d2d17;
        border: 1px solid #238636;
        color: #7ee787;
        padding: 12px 16px;
        border-radius: 8px;
        font-weight: 600;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Inicialização do Session State (Padrão: DESLIGADO / False)
# -----------------------------------------------------------------------------
if "is_running" not in st.session_state:
    st.session_state["is_running"] = False

# -----------------------------------------------------------------------------
# Função Helper: Carregar ou Simular Dados de Telemetria
# -----------------------------------------------------------------------------
def load_metrics(target_system, scenario, user_count, sampling_interval):
    """
    Carrega ou gera simulação dinâmica baseada no número de Usuários N e Intervalo em Runtime.
    """
    results_dir = os.path.join("..", "results", target_system, scenario)
    sar_file = os.path.join(results_dir, "sar_metrics.csv")

    timestamps = pd.date_range(end=pd.Timestamp.now(), periods=60, freq=f"{sampling_interval}s")

    if os.path.exists(sar_file):
        try:
            df_sar = pd.read_csv(sar_file)
            return df_sar
        except Exception:
            pass

    # Simulação realista proporcional a N usuários e tipo de sistema
    base_cpu = (40 if target_system == "boca" else 25) + (user_count * 0.4)
    base_ram = (900 if target_system == "boca" else 650) + (user_count * 5)
    base_latency = (60 if target_system == "boca" else 20) + (user_count * 0.8)

    np.random.seed(42 if target_system == "boca" else 84)
    df_sar = pd.DataFrame({
        "timestamp": timestamps,
        "cpu_user": np.clip(base_cpu + np.random.normal(0, 6, 60), 0, 100),
        "cpu_system": np.clip(10 + np.random.normal(0, 2, 60), 0, 100),
        "ram_used_mb": np.clip(base_ram + np.cumsum(np.random.normal(1, 3, 60)), 200, 2048),
        "http_latency_ms": np.clip(base_latency + np.random.normal(0, 10, 60), 5, 1000),
        "judge_latency_ms": np.clip((base_latency * 2.5) + np.random.normal(0, 30, 60), 20, 5000),
        "ac_count": np.random.randint(10, 30, 60),
        "wa_count": np.random.randint(1, 6, 60),
        "tle_count": np.random.randint(0, 4, 60)
    })

    return df_sar


# -----------------------------------------------------------------------------
# Barra Lateral (Sidebar) - Botões de Controle e Configurações em Standby
# -----------------------------------------------------------------------------
st.sidebar.image("https://img.icons8.com/color/96/000000/dashboard.png", width=64)
st.sidebar.title("⚡ Painel de Controle Master")

# Botões de Ação Proeminentes (LIGAR / DESLIGAR)
col_btn1, col_btn2 = st.sidebar.columns(2)

with col_btn1:
    if st.button("▶️ LIGAR", disabled=st.session_state["is_running"], type="primary", use_container_width=True):
        st.session_state["is_running"] = True
        st.rerun()

with col_btn2:
    if st.button("⏹️ DESLIGAR", disabled=not st.session_state["is_running"], use_container_width=True):
        st.session_state["is_running"] = False
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("🛠️ Configurações (Editáveis em Standby)")

# 1. Seletor Principal de Modo de Visão (Target Selector)
view_mode = st.sidebar.radio(
    "Modo de Visão / Sistema:",
    options=["⚔️ Comparativo Lado a Lado", "🟢 Apenas BOCA", "🔵 Apenas Helium"],
    index=0
)

# 2. Runtime Slider: Frequência de Amostragem (sar interval)
sampling_interval = st.sidebar.slider(
    "⏱️ Frequência de Amostragem (segundos)",
    min_value=1, max_value=10, value=1, step=1,
    help="Altera a frequência de amostragem de dados em tempo de execução."
)

# 3. Runtime Slider: Quantidade de Usuários Concorrentes (N Users)
user_count = st.sidebar.slider(
    "👥 Usuários Simultâneos (N Users)",
    min_value=1, max_value=100, value=1, step=1,
    help="Simula a carga proporcional no dashboard para 1 até 100 usuários."
)

# 4. Checklist de Vereditos Habilitados
st.sidebar.markdown("**📋 Checklist de Vereditos:**")
verdict_ac = st.sidebar.checkbox("ACCEPTED (AC)", value=True)
verdict_wa = st.sidebar.checkbox("WRONG ANSWER (WA)", value=True)
verdict_tle = st.sidebar.checkbox("TIME LIMIT EXCEEDED (TLE)", value=True)
verdict_ce = st.sidebar.checkbox("COMPILATION ERROR (CE)", value=True)

# 5. Cenário do Locust
scenario = st.sidebar.selectbox(
    "Cenário de Estresse:",
    options=["burst", "baseline", "steady", "ramp", "endurance"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Conexão com VMs:**")
st.sidebar.markdown("🟢 **BOCA VM**: `192.168.56.11` (Vagrant SSH)")
st.sidebar.markdown("🔵 **Helium VM**: `192.168.56.10` (Vagrant SSH)")

# -----------------------------------------------------------------------------
# Cabeçalho Principal e Banner de Estado (ON / OFF)
# -----------------------------------------------------------------------------
st.title("⚡ JAMS — Judge Assessment & Metrics Suite (BOCA vs Helium)")

if st.session_state["is_running"]:
    st.markdown("""
    <div class="status-banner-on">
        🟢 SISTEMA EM EXECUÇÃO: O monitoramento e a coleta de telemetria estão ativos em tempo real.
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="status-banner-off">
        🔴 SISTEMA DESLIGADO (STANDBY): O sistema está pausado e nenhuma requisição está sendo enviada. Configure os parâmetros desejados na barra lateral e clique em "▶️ LIGAR" para iniciar.
    </div>
    """, unsafe_allow_html=True)

st.caption(f"Cenário: **{scenario.upper()}** | Usuários Simultâneos: **{user_count}** | Amostragem: **{sampling_interval}s** | Estado: **{'🟢 LIGADO' if st.session_state['is_running'] else '🔴 DESLIGADO'}**")

# Carrega os dados considerando as configs de runtime
df_boca = load_metrics("boca", scenario, user_count, sampling_interval)
df_helium = load_metrics("helium", scenario, user_count, sampling_interval)


# -----------------------------------------------------------------------------
# Renderização da UI por Modo de Visão
# -----------------------------------------------------------------------------

def render_system_metrics(system_name, df, header_class):
    color_theme = "#e3b341" if system_name == "BOCA" else "#58a6ff"
    
    st.markdown(f"<h3 class='{header_class}'>{system_name} System ({user_count} Usuários)</h3>", unsafe_allow_html=True)
    
    # Cards de Métricas Rápidas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("CPU Load Avg", f"{df['cpu_user'].mean():.1f}%", delta=f"{df['cpu_user'].iloc[-1] - df['cpu_user'].iloc[0]:.1f}%")
    with col2:
        st.metric("RAM Utilizada", f"{df['ram_used_mb'].iloc[-1]:.0f} MB", delta="2048 MB Max")
    with col3:
        st.metric("HTTP Latency (p95)", f"{np.percentile(df['http_latency_ms'], 95):.0f} ms")
    with col4:
        st.metric("Judge Latency Avg", f"{df['judge_latency_ms'].mean():.0f} ms")

    # Gráfico de Uso de CPU e Memória
    fig_cpu = px.line(
        df, x="timestamp", y=["cpu_user", "cpu_system"],
        labels={"value": "Uso de CPU (%)", "timestamp": "Tempo"},
        title=f"Uso de CPU - {system_name}",
        color_discrete_sequence=[color_theme, "#ff7b72"]
    )
    fig_cpu.update_layout(template="plotly_dark", height=280, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_cpu, use_container_width=True)

    # Gráfico de Latência (HTTP vs Judge)
    fig_lat = px.line(
        df, x="timestamp", y=["http_latency_ms", "judge_latency_ms"],
        labels={"value": "Latência (ms)", "timestamp": "Tempo"},
        title=f"Latência HTTP vs Julgamento - {system_name}",
        color_discrete_sequence=[color_theme, "#a5d6ff"]
    )
    fig_lat.update_layout(template="plotly_dark", height=280, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_lat, use_container_width=True)


if view_mode == "⚔️ Comparativo Lado a Lado":
    col_left, col_right = st.columns(2)
    with col_left:
        render_system_metrics("BOCA", df_boca, "boca-header")
    with col_right:
        render_system_metrics("Helium", df_helium, "helium-header")

elif view_mode == "🟢 Apenas BOCA":
    render_system_metrics("BOCA", df_boca, "boca-header")

elif view_mode == "🔵 Apenas Helium":
    render_system_metrics("Helium", df_helium, "helium-header")

# -----------------------------------------------------------------------------
# Painel de Vereditos e Comparativo Direto
# -----------------------------------------------------------------------------
st.markdown("---")
st.subheader("📊 Distribuição de Vereditos e Throughput Total")

col_v1, col_v2 = st.columns(2)

with col_v1:
    categories = []
    if verdict_ac: categories.append("AC")
    if verdict_wa: categories.append("WA")
    if verdict_tle: categories.append("TLE")
    if not categories: categories = ["AC"]

    boca_vals = [df_boca["ac_count"].sum() if "AC" in categories else 0,
                 df_boca["wa_count"].sum() if "WA" in categories else 0,
                 df_boca["tle_count"].sum() if "TLE" in categories else 0]
    
    helium_vals = [df_helium["ac_count"].sum() if "AC" in categories else 0,
                   df_helium["wa_count"].sum() if "WA" in categories else 0,
                   df_helium["tle_count"].sum() if "TLE" in categories else 0]

    fig_verdicts = go.Figure(data=[
        go.Bar(name="BOCA", x=categories, y=boca_vals[:len(categories)], marker_color="#e3b341"),
        go.Bar(name="Helium", x=categories, y=helium_vals[:len(categories)], marker_color="#58a6ff")
    ])
    fig_verdicts.update_layout(barmode="group", template="plotly_dark", title="Vereditos Filtrados pelo Checklist", height=300)
    st.plotly_chart(fig_verdicts, use_container_width=True)

with col_v2:
    fig_comp_cpu = go.Figure()
    fig_comp_cpu.add_trace(go.Scatter(x=df_boca["timestamp"], y=df_boca["cpu_user"], name="BOCA CPU %", line=dict(color="#e3b341")))
    fig_comp_cpu.add_trace(go.Scatter(x=df_helium["timestamp"], y=df_helium["cpu_user"], name="Helium CPU %", line=dict(color="#58a6ff")))
    fig_comp_cpu.update_layout(template="plotly_dark", title="Comparativo Direto de CPU Load (%user)", height=300)
    st.plotly_chart(fig_comp_cpu, use_container_width=True)

# Auto-refresh em runtime apenas quando LIGADO (is_running == True)
if st.session_state["is_running"]:
    time.sleep(sampling_interval)
    st.rerun()
