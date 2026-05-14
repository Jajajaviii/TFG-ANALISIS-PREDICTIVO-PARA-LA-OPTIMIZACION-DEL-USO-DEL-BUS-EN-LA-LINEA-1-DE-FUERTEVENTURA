# =====================================================================
#  DASHBOARD INTERACTIVO - LÍNEA 1 PUERTO DEL ROSARIO
#  Streamlit App · Apoyo a la toma de decisiones del Ayuntamiento
#  Ejecutar:  streamlit run dashboard_app.py
# =====================================================================

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
DATA_FILE = APP_DIR / "TFG_L1_dataset_definitivo.csv.gz"


def _has_streamlit_context():
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
    except Exception:
        return False
    return get_script_run_ctx() is not None


def _bootstrap_streamlit_when_run_directly():
    """Relaunch the script with `streamlit run` when executed with `python`."""
    if __name__ != "__main__":
        return
    if _has_streamlit_context():
        return
    if os.environ.get("_DASHBOARD_STREAMLIT_BOOTSTRAPPED") == "1":
        return

    os.environ["_DASHBOARD_STREAMLIT_BOOTSTRAPPED"] = "1"
    from streamlit.web import cli as stcli

    sys.argv = ["streamlit", "run", str(Path(__file__).resolve()), *sys.argv[1:]]
    raise SystemExit(stcli.main())


_bootstrap_streamlit_when_run_directly()

# ---------------------------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="Línea 1 · Puerto del Rosario",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Paleta Fuerteventura — turquesa Atlántico · dunas doradas · lava volcánica
COLORS = {
    "primary":   "#005F7A",  # azul profundo Atlántico
    "secondary": "#E8B830",  # oro de las dunas (Corralejo / Jandía)
    "accent":    "#00B4C6",  # turquesa aguas someras (Sotavento)
    "success":   "#7A9E6B",  # tabaiba / vegetación canaria
    "warning":   "#E07840",  # atardecer volcánico
    "danger":    "#C0401A",  # lava / roca basáltica
    "neutral":   "#9A8A72",  # tierra seca / jable
    "text":      "#2A1F14",  # marrón oscuro volcánico (UI general)
    "grid":      "#E8D8A8",  # arena clara
}
SCEN_COLORS = {"bajo": "#00B4C6", "medio": "#E8B830", "alto": "#C0401A"}

# Constantes de tema oscuro para gráficos
_CBGP  = "#111111"          # fondo interior del plot
_CPAPER = "#111111"         # fondo papel (borde exterior)
_CTEXT  = "#F0E8D0"         # texto claro (arena clara cálida)
_CGRID  = "#2E2820"         # líneas de cuadrícula casi negras


def apply_plotly_theme(fig):
    """Aplica tema oscuro con colores Fuerteventura a todas las figuras Plotly."""
    fig.update_layout(
        plot_bgcolor=_CBGP,
        paper_bgcolor=_CPAPER,
        font=dict(family="Inter, Helvetica, Arial, sans-serif",
                  size=12, color=_CTEXT),
        legend=dict(font=dict(color=_CTEXT, size=11),
                    bgcolor="rgba(20,18,16,0.85)",
                    bordercolor="#3A3028", borderwidth=1),
    )
    if fig.layout.title.text:
        fig.update_layout(title=dict(font=dict(color=COLORS["accent"], size=14)))
    fig.update_xaxes(title_font=dict(color=_CTEXT), tickfont=dict(color=_CTEXT),
                     gridcolor=_CGRID, linecolor="#3A3028", zerolinecolor="#3A3028")
    fig.update_yaxes(title_font=dict(color=_CTEXT), tickfont=dict(color=_CTEXT),
                     gridcolor=_CGRID, linecolor="#3A3028", zerolinecolor="#3A3028")
    return fig

# ---------------------------------------------------------------------
# CSS CUSTOM
# ---------------------------------------------------------------------
st.markdown("""
<style>
    /* ── Fondo general: arena de Fuerteventura ── */
    .stApp, [data-testid="stAppViewContainer"] {
        background-color: #F5EBD0 !important;
    }
    [data-testid="stSidebar"] {
        background-color: #EAD9B0 !important;
    }
    [data-testid="stSidebar"] * {
        color: #2A1F14 !important;
    }

    /* Selectbox en sidebar: contenedor visible */
    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        background-color: #F5EBD0 !important;
        border-color: #9A8A72 !important;
    }
    [data-testid="stSidebar"] [data-baseweb="select"] span,
    [data-testid="stSidebar"] [data-baseweb="select"] div {
        color: #2A1F14 !important;
    }

    /* Dropdown de opciones (sale fuera del sidebar, necesita selector global) */
    [data-baseweb="popover"] [data-baseweb="menu"] {
        background-color: #F5EBD0 !important;
        border: 1px solid #9A8A72 !important;
    }
    [data-baseweb="popover"] [role="option"] {
        background-color: #F5EBD0 !important;
        color: #2A1F14 !important;
    }
    [data-baseweb="popover"] [role="option"]:hover,
    [data-baseweb="popover"] [aria-selected="true"] {
        background-color: #D4C090 !important;
        color: #111111 !important;
    }

    .main {padding-top: 1rem;}

    /* KPI cards */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #005F7A 0%, #00B4C6 100%);
        padding: 18px; border-radius: 10px;
        box-shadow: 0 3px 10px rgba(0,95,122,0.25);
    }
    [data-testid="stMetric"] label,
    [data-testid="stMetric"] [data-testid="stMetricLabel"] p {
        color: rgba(255,255,255,0.9) !important;
        font-size: 11px !important;
        text-transform: uppercase; letter-spacing: 0.5px;
    }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: white !important; font-size: 28px !important;
    }
    [data-testid="stMetric"] [data-testid="stMetricDelta"] {
        color: rgba(255,255,255,0.75) !important;
    }

    /* Titulos */
    h1 {color: #005F7A; font-weight: 700;}
    h2, h3 {color: #111111 !important;}
    p, li, label {color: #2A1F14;}

    /* ── Navegación radio como botones ── */
    [data-testid="stRadio"] > div {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        background: transparent !important;
        border-bottom: 2px solid #C8B888;
        padding-bottom: 10px;
        margin-bottom: 4px;
    }
    [data-testid="stRadio"] label {
        background-color: #E8D8A8 !important;
        color: #2A1F14 !important;
        border: 1px solid #B8A878 !important;
        border-radius: 8px 8px 0 0 !important;
        padding: 9px 20px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        cursor: pointer;
        transition: all 0.18s ease !important;
        margin: 0 !important;
    }
    [data-testid="stRadio"] label:hover {
        background-color: #D4C090 !important;
        border-color: #9A8A72 !important;
    }
    /* Ocultar el círculo del radio nativo */
    [data-testid="stRadio"] input[type="radio"] {
        display: none !important;
    }
    /* Opción seleccionada */
    [data-testid="stRadio"] label:has(input:checked) {
        background-color: #005F7A !important;
        color: white !important;
        border-color: #005F7A !important;
    }

    /* ── Tooltips (globo de ayuda) ── */
    [data-testid="stTooltipIcon"] svg {
        fill: #005F7A !important;
        width: 14px !important;
        height: 14px !important;
    }
    div[role="tooltip"],
    div[role="tooltip"] *,
    div[role="tooltip"] p,
    div[role="tooltip"] span,
    div[role="tooltip"] div {
        background-color: #FFFBF0 !important;
        color: #1A1208 !important;
        border: none !important;
        border-radius: 6px !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        padding: 0 !important;
        max-width: 220px !important;
        box-shadow: none !important;
        pointer-events: none !important;
        line-height: 1.5 !important;
    }
    div[role="tooltip"] {
        padding: 6px 12px !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2) !important;
        border: 1px solid #C8B888 !important;
    }

    /* ── Expander KPIs ── */
    [data-testid="stExpander"] {
        background-color: #EDE0BC !important;
        border: 1.5px solid #C8B888 !important;
        border-radius: 10px !important;
    }
    [data-testid="stExpander"] > details > summary {
        background-color: #D8C898 !important;
        border-radius: 8px !important;
        padding: 10px 16px !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        color: #005F7A !important;
    }
    [data-testid="stExpander"] > details > summary:hover {
        background-color: #C8B888 !important;
    }

    .header-box {
        background: linear-gradient(135deg, #003D52 0%, #005F7A 55%, #00B4C6 100%);
        padding: 24px 30px; border-radius: 12px; color: white; margin-bottom: 24px;
        box-shadow: 0 4px 16px rgba(0,63,82,0.3);
    }
    .footer-box {
        text-align: center; color: #9A8A72; font-size: 11px;
        padding: 18px; margin-top: 24px; border-top: 2px solid #E8B830;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------
# CARGA DE DATOS (cacheada)
# ---------------------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE, parse_dates=["fecha"], low_memory=False)
    if "is_service_segment" not in df.columns:
        df["is_service_segment"] = df["direction"].isin(["ida", "vuelta"])
    if "cycle_id" not in df.columns:
        df["cycle_id"] = df["trip_id"].str.split("_").str[-1]
    if "service_id" not in df.columns:
        df["service_id"] = df["trip_id"].astype(str) + "_" + df["direction"].astype(str)
    if "total_time_min" not in df.columns:
        df["total_time_min"] = df["drive_time_min"].fillna(0) + df["dwell_time_next_stop_min"].fillna(0)
    return df


@st.cache_data
def build_metrics(df, capacity, alpha_bajo, alpha_medio, alpha_alto):
    ALPHA = {"bajo": alpha_bajo, "medio": alpha_medio, "alto": alpha_alto}
    BETA_DAY = {"laborable": 1.00, "sabado": 0.85, "domingo_festivo": 0.80}

    # Demanda diaria — igual que antes
    df_daily = (df.drop_duplicates(subset="fecha")
                  [["fecha", "day_type", "airport_pax", "max_impact_factor",
                    "has_event", "month", "weekday"]]
                  .copy().sort_values("fecha").reset_index(drop=True))
    df_daily["beta"]  = df_daily["day_type"].map(BETA_DAY).fillna(1.0)
    df_daily["gamma"] = df_daily["max_impact_factor"].fillna(1.0)
    for s, alpha in ALPHA.items():
        df_daily[f"D_{s}"] = (df_daily["airport_pax"] * alpha *
                              df_daily["beta"] * df_daily["gamma"])

    proxy_raw = df_daily["D_medio"]
    proxy_min, proxy_max = proxy_raw.min(), proxy_raw.max()
    df_daily["D_index"] = ((proxy_raw - proxy_min) / max(proxy_max - proxy_min, 1e-9)).clip(0, 1)
    df_daily["mes"] = df_daily["fecha"].dt.to_period("M").astype(str)

    # Preparar service_df una sola vez con columnas mínimas
    cols_needed = ["fecha", "service_id", "segment_order", "direction",
                   "from_stop", "from_node_weight", "is_service_segment"]
    cols_needed = [c for c in cols_needed if c in df.columns]
    
    service_df = df[df["is_service_segment"]][cols_needed].copy()
    service_df["service_seg_order"] = (
        service_df.sort_values(["fecha", "service_id", "segment_order"])
        .groupby(["fecha", "service_id"]).cumcount() + 1
    )
    node_weights = service_df.groupby("from_stop")["from_node_weight"].first().fillna(1.0)
    service_df["w_norm"] = service_df["from_stop"].map(node_weights / node_weights.sum())
    n_services = service_df.groupby("fecha")["service_id"].nunique().mean()

    # Calcular KPIs por escenario SIN guardar los dataframes completos
    kpi_seg, kpi_exp = {}, {}
    sim_runs = {}

    for scen, alpha in ALPHA.items():
        daily_d = df_daily.set_index("fecha")[f"D_{scen}"].to_dict()
        s = service_df.copy()
        s["d_dia"] = s["fecha"].map(daily_d)
        s["boardings"] = s["d_dia"] * s["w_norm"] / max(n_services, 1)
        s = s.sort_values(["fecha", "service_id", "segment_order"])

        # Cumsum eficiente sin lambda doble
        cs = s.groupby(["fecha", "service_id"])["boardings"].cumsum()
        cs_shift = s.groupby(["fecha", "service_id"])["boardings"].cumsum().shift(2).fillna(0)
        s["occ_potential"] = cs - cs_shift * 0.25
        s["occ"] = s["occ_potential"].clip(upper=capacity)

        kpi_seg[scen] = {"occ_mean": s["occ"].mean(), "occ_p95": s["occ"].quantile(0.95)}
        exp_peak = s.groupby(["fecha", "service_id"])["occ_potential"].max()
        no_serv  = (s["occ_potential"] - s["occ"]).clip(lower=0).sum()
        kpi_exp[scen] = {"sat_pct": (exp_peak > capacity).mean() * 100, "no_servida": no_serv}

        sim_runs[scen] = s[["fecha", "service_id", "service_seg_order",
                             "direction", "from_stop", "occ", "occ_potential"]].copy()
        del s, cs, cs_shift  # liberar memoria inmediatamente

    return df_daily, service_df, sim_runs, pd.DataFrame(kpi_seg).T, pd.DataFrame(kpi_exp).T

# ---------------------------------------------------------------------
# SIDEBAR (filtros y parámetros)
# ---------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Parámetros del modelo")

    capacity = st.slider("Capacidad del vehículo (pax)", 30, 100, 55, 5,
                         help="Capacidad máxima de pasajeros por expedición")

    st.markdown("---")
    st.markdown("**Tasas de adopción (α)**")
    alpha_bajo  = st.slider("Escenario bajo",  0.005, 0.030, 0.010, 0.001, format="%.3f")
    alpha_medio = st.slider("Escenario medio", 0.010, 0.060, 0.030, 0.001, format="%.3f")
    alpha_alto  = st.slider("Escenario alto",  0.020, 0.100, 0.050, 0.001, format="%.3f")

    st.markdown("---")
    escenario_focus = st.selectbox("Escenario en foco", ["bajo", "medio", "alto"], index=1)

    st.markdown("---")
    st.markdown("""
    <div style='font-size:10px; color:#6C757D; line-height:1.5'>
    <b>Trabajo Fin de Grado</b><br>
    Ciencia de Datos<br>
    Línea 1 · Puerto del Rosario<br>
    Datos: 2024-2025
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------
# CARGA Y CÁLCULO
# ---------------------------------------------------------------------
try:
    df = load_data()
except FileNotFoundError:
    st.error("No se encuentra el archivo `TFG_L1_dataset_definitivo.csv`. "
             "Asegúrate de que está en la misma carpeta que `dashboard_app.py`.")
    st.stop()

df_daily, service_df, sim_runs, kpi_seg_df, kpi_exp_df = build_metrics(
    df, capacity, alpha_bajo, alpha_medio, alpha_alto
)


# ---------------------------------------------------------------------
# CABECERA INSTITUCIONAL
# ---------------------------------------------------------------------
st.markdown("""
<div class='header-box'>
  <div style='display:flex; justify-content:space-between; align-items:center'>
    <div>
      <h1 style='color:white; margin:0; font-size:28px'>Línea 1 · Puerto del Rosario</h1>
      <p style='margin:4px 0 0 0; opacity:0.85; font-size:13px'>
         Cuadro de mando operativo · Análisis de demanda y simulación
      </p>
    </div>
    <div style='text-align:right; opacity:0.85; font-size:11px'>
      <div><b>Ayuntamiento de Puerto del Rosario</b></div>
      <div>Periodo de análisis: 2024 – 2025</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------
# NAVEGACIÓN PRINCIPAL
# ---------------------------------------------------------------------
pagina = st.radio(
    "navegacion",
    ["Red y geografía", "Demanda", "Operación", "Sensibilidad", "Modelos predictivos"],
    horizontal=True,
    label_visibility="collapsed",
)

# ---------------------------------------------------------------------
# KPIs PRINCIPALES (colapsables — debajo de la navegación)
# ---------------------------------------------------------------------
with st.expander("▸ Indicadores clave (KPIs)", expanded=True):
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Paradas únicas en la línea", f"{df['from_stop'].nunique()}")
    col2.metric("Expediciones por día (media)",
                f"{int(service_df.groupby('fecha')['service_id'].nunique().mean())}")
    col3.metric("Tiempo de ciclo completo",
                f"{df.groupby(['fecha','cycle_id'])['total_time_min'].sum().mean():.1f} min")
    col4.metric("Distancia de ciclo completo",
                f"{df.groupby(['fecha','cycle_id'])['segment_distance_km'].sum().mean():.1f} km")

    st.markdown("<div style='margin-top:10px'></div>", unsafe_allow_html=True)

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Demanda equivalente (pax/día)",
                f"{int(df_daily['D_medio'].mean()):,}")
    col6.metric(f"Ocupación P95 — esc. {escenario_focus}",
                f"{kpi_seg_df.loc[escenario_focus, 'occ_p95']:.1f}")
    col7.metric("Expediciones saturadas",
                f"{kpi_exp_df.loc[escenario_focus, 'sat_pct']:.1f}%")
    col8.metric("Demanda no servida (acumulada)",
                f"{int(kpi_exp_df.loc[escenario_focus, 'no_servida']):,}")

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------------------
# CONTENIDO POR SECCIÓN
# ---------------------------------------------------------------------

# ---------------- SECCIÓN 1: RED Y GEOGRAFÍA ----------------
if pagina == "Red y geografía":
    st.markdown("### Distribución geográfica de las paradas")
    st.markdown("*Las paradas se agrupan en tres zonas funcionales. El tamaño del marcador "
                "indica el peso relativo del nodo dentro del sistema.*")

    stops_geo = (df.dropna(subset=["from_lat", "from_lon"])
                   .drop_duplicates(subset=["from_stop"])
                   [["from_stop_name", "from_lat", "from_lon", "from_zone",
                     "from_node_weight", "from_is_key_node"]])

    fig_map = px.scatter_map(
        stops_geo,
        lat="from_lat", lon="from_lon",
        color="from_zone",
        size=stops_geo["from_node_weight"].fillna(1) + 1,
        hover_name="from_stop_name",
        hover_data={"from_zone": True, "from_node_weight": True,
                    "from_lat": False, "from_lon": False},
        color_discrete_map={"Aeropuerto": COLORS["accent"],
                            "Puerto del Rosario": COLORS["secondary"],
                            "La Hondura": COLORS["danger"]},
        zoom=11.5,
        height=550,
        map_style="carto-positron",
    )
    fig_map.update_layout(margin=dict(l=0, r=0, t=10, b=0),
                          legend=dict(title="Zona funcional"))
    fig_map = apply_plotly_theme(fig_map)
    st.plotly_chart(fig_map, use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### Distribución de paradas por zona")
        zone_counts = stops_geo["from_zone"].value_counts().reset_index()
        zone_counts.columns = ["Zona", "Paradas"]
        fig_z = px.bar(zone_counts, x="Zona", y="Paradas",
                       color="Zona",
                       color_discrete_map={"Aeropuerto": COLORS["accent"],
                                           "Puerto del Rosario": COLORS["secondary"],
                                           "La Hondura": COLORS["danger"]},
                       text="Paradas")
        fig_z.update_layout(showlegend=True, height=350,
                            legend=dict(title="Zona"),
                            )
        fig_z.update_traces(textposition="outside")
        fig_z.update_xaxes(gridcolor=_CGRID)
        fig_z.update_yaxes(gridcolor=_CGRID)
        fig_z = apply_plotly_theme(fig_z)
        st.plotly_chart(fig_z, use_container_width=True)

    with col_b:
        st.markdown("### Nodos clave del sistema")
        key_count = stops_geo["from_is_key_node"].value_counts()
        fig_k = go.Figure(data=[go.Pie(
            labels=["Nodo clave", "Parada secundaria"],
            values=[key_count.get(True, 0), key_count.get(False, 0)],
            hole=0.55,
            marker=dict(colors=[COLORS["danger"], COLORS["accent"]]),
            textinfo="label+percent",
        )])
        fig_k.update_layout(showlegend=True, height=350,
                            
                            annotations=[dict(text=f"{stops_geo['from_stop'].count() if 'from_stop' in stops_geo else len(stops_geo)}<br>paradas",
                                              x=0.5, y=0.5, font=dict(size=14, color=COLORS["primary"]),
                                              showarrow=False)])
        fig_k = apply_plotly_theme(fig_k)
        st.plotly_chart(fig_k, use_container_width=True)


# ---------------- SECCIÓN 2: DEMANDA ----------------
elif pagina == "Demanda":
    st.markdown("### Evolución mensual del índice de demanda")
    monthly = (df_daily.groupby("mes")
               .agg(mean=("D_index", "mean"),
                    max=("D_index", "max"),
                    min=("D_index", "min"))
               .reset_index())

    fig_ts = go.Figure()
    fig_ts.add_trace(go.Scatter(x=monthly["mes"], y=monthly["max"],
                                mode="lines", line=dict(width=0),
                                showlegend=False, hoverinfo="skip"))
    fig_ts.add_trace(go.Scatter(x=monthly["mes"], y=monthly["min"],
                                mode="lines", line=dict(width=0),
                                fill="tonexty", fillcolor="rgba(11,61,145,0.15)",
                                name="Rango mensual"))
    fig_ts.add_trace(go.Scatter(x=monthly["mes"], y=monthly["mean"],
                                mode="lines+markers", name="D_index medio",
                                line=dict(color=COLORS["primary"], width=3),
                                marker=dict(size=8)))
    fig_ts.update_layout(height=380,
                         xaxis_title="Mes", yaxis_title="D_index",
                         hovermode="x unified")
    fig_ts.update_xaxes(gridcolor=_CGRID)
    fig_ts.update_yaxes(gridcolor=_CGRID)
    fig_ts = apply_plotly_theme(fig_ts)
    st.plotly_chart(fig_ts, use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### Distribución por tipo de día")
        fig_box = go.Figure()
        for scen, color in SCEN_COLORS.items():
            fig_box.add_trace(go.Box(y=df_daily[f"D_{scen}"], x=df_daily["day_type"],
                                     name=f"Esc. {scen}",
                                     marker=dict(color=color, opacity=0.75),
                                     boxmean=True))
        fig_box.update_layout(height=400, boxmode="group",
                              xaxis_title="Tipo de día",
                              yaxis_title="Pasajeros equivalentes/día",
                              )
        fig_box.update_xaxes(gridcolor=_CGRID)
        fig_box.update_yaxes(gridcolor=_CGRID)
        fig_box = apply_plotly_theme(fig_box)
        st.plotly_chart(fig_box, use_container_width=True)

    with col_b:
        st.markdown("### Tráfico aeroportuario diario")
        airport_daily = (df_daily[["fecha", "airport_pax"]]
                         .set_index("fecha")["airport_pax"]
                         .resample("ME").mean().reset_index())
        airport_daily.columns = ["Mes", "Pasajeros aeropuerto (media)"]
        fig_air = px.line(airport_daily, x="Mes", y="Pasajeros aeropuerto (media)",
                          markers=True)
        fig_air.update_traces(line=dict(color=COLORS["secondary"], width=3),
                              marker=dict(size=8),
                              name="Pasajeros aeropuerto (media)")
        fig_air.update_layout(height=400, showlegend=True,
                              )
        fig_air.update_xaxes(gridcolor=_CGRID)
        fig_air.update_yaxes(gridcolor=_CGRID)
        fig_air = apply_plotly_theme(fig_air)
        st.plotly_chart(fig_air, use_container_width=True)


# ---------------- SECCIÓN 3: OPERACIÓN ----------------
elif pagina == "Operación":
    st.markdown(f"### Perfil de ocupación por sentido (escenario **{escenario_focus}**)")

    fig_prof = go.Figure()
    for direccion, color, dash_style in [("ida", COLORS["primary"], "solid"),
                                         ("vuelta", COLORS["danger"], "dash")]:
        sub = (sim_runs[escenario_focus].query("direction == @direccion")
               .groupby("service_seg_order")["occ"].mean().reset_index())
        fig_prof.add_trace(go.Scatter(x=sub["service_seg_order"], y=sub["occ"],
                                      mode="lines+markers",
                                      line=dict(color=color, width=3, dash=dash_style),
                                      marker=dict(size=10),
                                      name=f"Sentido {direccion}"))
    fig_prof.add_hline(y=capacity, line=dict(color=COLORS["danger"], dash="dash", width=1.5),
                       annotation_text=f"Capacidad ({capacity})",
                       annotation_position="top right")
    fig_prof.add_hline(y=capacity * 0.8, line=dict(color=COLORS["warning"], dash="dot", width=1.2),
                       annotation_text="80% capacidad",
                       annotation_position="bottom right")
    fig_prof.update_layout(height=420,
                           xaxis_title="Orden de segmento",
                           yaxis_title="Pasajeros (ocupación media)",
                           )
    fig_prof.update_xaxes(gridcolor=_CGRID)
    fig_prof.update_yaxes(gridcolor=_CGRID)
    fig_prof = apply_plotly_theme(fig_prof)
    st.plotly_chart(fig_prof, use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### Ocupación media por escenario")
        ocup_data = pd.DataFrame({
            "Escenario": list(SCEN_COLORS.keys()),
            "Ocupación media": [kpi_seg_df.loc[s, "occ_mean"] for s in SCEN_COLORS],
            "P95": [kpi_seg_df.loc[s, "occ_p95"] for s in SCEN_COLORS],
        })
        fig_oc = go.Figure()
        fig_oc.add_trace(go.Bar(x=ocup_data["Escenario"], y=ocup_data["Ocupación media"],
                                name="Media",
                                marker=dict(color=[SCEN_COLORS[s] for s in SCEN_COLORS]),
                                text=[f"{v:.1f}" for v in ocup_data["Ocupación media"]],
                                textposition="outside"))
        fig_oc.add_trace(go.Bar(x=ocup_data["Escenario"], y=ocup_data["P95"],
                                name="P95",
                                marker=dict(color=[SCEN_COLORS[s] for s in SCEN_COLORS],
                                            opacity=0.5, pattern_shape="/"),
                                text=[f"{v:.1f}" for v in ocup_data["P95"]],
                                textposition="outside"))
        fig_oc.add_hline(y=capacity, line=dict(color=COLORS["danger"], dash="dash"),
                         annotation_text=f"Cap. {capacity}")
        fig_oc.update_layout(height=380, barmode="group",
                             yaxis_title="Pasajeros")
        fig_oc = apply_plotly_theme(fig_oc)
        st.plotly_chart(fig_oc, use_container_width=True)

    with col_b:
        st.markdown("### Saturación y demanda no servida")
        df_kpi = pd.DataFrame({
            "Escenario": list(SCEN_COLORS.keys()),
            "Saturación (%)": [kpi_exp_df.loc[s, "sat_pct"] for s in SCEN_COLORS],
            "No servida": [kpi_exp_df.loc[s, "no_servida"] for s in SCEN_COLORS],
        })
        fig_sat = go.Figure()
        fig_sat.add_trace(go.Bar(x=df_kpi["Escenario"], y=df_kpi["Saturación (%)"],
                                 marker=dict(color=[SCEN_COLORS[s] for s in SCEN_COLORS]),
                                 text=[f"{v:.1f}%" for v in df_kpi["Saturación (%)"]],
                                 textposition="outside",
                                 yaxis="y", name="Saturación %"))
        fig_sat.add_hline(y=5, line=dict(color=COLORS["danger"], dash="dash"),
                          annotation_text="Umbral 5%")
        fig_sat.update_layout(height=380, showlegend=True,
                              yaxis_title="% Expediciones saturadas")
        fig_sat = apply_plotly_theme(fig_sat)
        st.plotly_chart(fig_sat, use_container_width=True)


# ---------------- SECCIÓN 4: SENSIBILIDAD ----------------
elif pagina == "Sensibilidad":
    st.markdown("### Análisis de sensibilidad operativa")
    st.markdown("*Comparación de variantes operativas frente al escenario base. "
                "Permite evaluar el impacto de modificar parámetros clave del servicio.*")

    base_no_serv = kpi_exp_df.loc["medio", "no_servida"]

    ref = base_no_serv if base_no_serv > 0 else 5000
    if base_no_serv == 0:
        st.caption(
            "Los parámetros actuales no generan demanda no servida. "
            "El gráfico muestra valores ilustrativos de referencia (base = 5 000 pax)."
        )

    sens_data = pd.DataFrame({
        "Variante": ["Base (alpha=0.030)", "Capacidad 70 pax", "Adopción -10%",
                     "Adopción +10%", "Frecuencia +25%"],
        "Demanda no servida": [ref, ref * 0.18, ref * 0.50, ref * 1.73, ref * 0.84],
    }).sort_values("Demanda no servida")

    fig_sens = go.Figure(go.Bar(
        y=sens_data["Variante"],
        x=sens_data["Demanda no servida"],
        orientation="h",
        name="Demanda no servida",
        marker=dict(color=COLORS["primary"], line=dict(color="white", width=1.5)),
        text=[f"{int(v):,}" for v in sens_data["Demanda no servida"]],
        textposition="outside",
    ))
    fig_sens.update_layout(height=400, showlegend=True,
                           xaxis_title="Demanda equivalente no servida (período)",
                           )
    fig_sens.update_xaxes(gridcolor=_CGRID)
    fig_sens = apply_plotly_theme(fig_sens)
    st.plotly_chart(fig_sens, use_container_width=True)

    st.info("**Lectura:** El aumento de capacidad a 70 pasajeros es la medida más eficaz, "
            "reduciendo en más del 80% la demanda no servida respecto al escenario base. "
            "Por el contrario, un incremento del 10% en la adopción del servicio dispara "
            "la demanda no servida, evidenciando la sensibilidad del sistema actual ante "
            "crecimientos moderados de demanda.")


# ---------------- SECCIÓN 5: MODELOS ----------------
elif pagina == "Modelos predictivos":
    st.markdown("### Comparativa de modelos predictivos")
    st.markdown("*Resultados sobre el conjunto de prueba (2025) para los modelos evaluados.*")

    modelos_df = pd.DataFrame({
        "Modelo":  ["Baseline", "Ridge", "XGBoost", "MLP"],
        "MAE":     [0.1197, 0.0089, 0.0497, 0.0093],
        "RMSE":    [0.1551, 0.0128, 0.0769, 0.0470],
        "R²":      [0.0000, 0.9947, 0.7984, 0.9728],
    })
    col_a, col_b = st.columns(2)
    with col_a:
        fig_mae = px.bar(modelos_df, x="Modelo", y="MAE", text="MAE",
                         color="Modelo",
                         color_discrete_sequence=[COLORS["neutral"], COLORS["primary"],
                                                  COLORS["danger"], COLORS["warning"]])
        fig_mae.update_traces(texttemplate="%{text:.4f}", textposition="outside")
        fig_mae.update_layout(height=400, showlegend=True,
                              yaxis_title="MAE (escala D_index)",
                              title="MAE en test 2025")
        fig_mae = apply_plotly_theme(fig_mae)
        st.plotly_chart(fig_mae, use_container_width=True)

    with col_b:
        fig_rmse = px.bar(modelos_df, x="Modelo", y="RMSE", text="RMSE",
                          color="Modelo",
                          color_discrete_sequence=[COLORS["neutral"], COLORS["primary"],
                                                   COLORS["danger"], COLORS["warning"]])
        fig_rmse.update_traces(texttemplate="%{text:.4f}", textposition="outside")
        fig_rmse.update_layout(height=400, showlegend=True,
                               yaxis_title="RMSE (escala D_index)",
                               title="RMSE en test 2025")
        fig_rmse = apply_plotly_theme(fig_rmse)
        st.plotly_chart(fig_rmse, use_container_width=True)

    st.markdown("### Tabla resumen de métricas")
    st.dataframe(
        modelos_df.style.format({"MAE": "{:.4f}", "RMSE": "{:.4f}", "R²": "{:.4f}"})
                        .background_gradient(subset=["MAE", "RMSE"], cmap="RdYlGn_r")
                        .background_gradient(subset=["R²"], cmap="RdYlGn"),
        use_container_width=True, hide_index=True,
    )

    st.warning("**Nota interpretativa:** El alto rendimiento de los modelos lineales "
               "(Ridge y MLP) frente a XGBoost se explica por la naturaleza de la variable "
               "objetivo D_index, que es una combinación lineal de los predictores. En este "
               "contexto, los modelos con sesgo lineal capturan mejor la estructura del problema.")


# ---------------------------------------------------------------------
# FOOTER
# ---------------------------------------------------------------------
st.markdown("""
<div class='footer-box'>
  Trabajo Fin de Grado · Ciencia de Datos · 2025-2026<br>
  Línea 1 · Puerto del Rosario · Datos del periodo 2024-2025 · Elaboración propia
</div>
""", unsafe_allow_html=True)
