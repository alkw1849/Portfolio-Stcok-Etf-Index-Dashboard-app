import streamlit as st

st.title("new dashboard")

"""
╔══════════════════════════════════════════════════════════╗
║          📊 MARKET MONITOR — Personal Dashboard          ║
║     Any stock · ETF · Index · Crypto via yFinance        ║
╚══════════════════════════════════════════════════════════╝

Usage:
    pip install -r requirements.txt
    streamlit run dashboard.py
"""

import warnings
warnings.filterwarnings("ignore")

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Market Monitor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .stMetric { background: rgba(255,255,255,0.05); border-radius: 8px; padding: 8px; }
    .block-container { padding-top: 1rem; }
    div[data-testid="stDataFrame"] { border-radius: 8px; }
    .tag-pill {
        display: inline-block;
        background: rgba(255,255,255,0.1);
        border-radius: 20px;
        padding: 2px 10px;
        margin: 2px;
        font-size: 0.82em;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DEFAULT WATCHLIST  (user can replace / extend)
# ─────────────────────────────────────────────
DEFAULT_WATCHLIST = [
    # ── Équities FR ──
    {"ticker": "SAF.PA",    "name": "Safran",              "group": "PEA", "sector": "Aerospace / Defence",   "flag": "🇫🇷"},
    {"ticker": "SU.PA",     "name": "Schneider Electric",  "group": "PEA", "sector": "Energy / AI Datacenter","flag": "🇫🇷"},
    {"ticker": "STM.PA",    "name": "STMicroelectronics",  "group": "PEA", "sector": "Semiconductors",        "flag": "🇫🇷"},
    {"ticker": "AI.PA",     "name": "Air Liquide",         "group": "PEA", "sector": "Industrial Chemicals",  "flag": "🇫🇷"},
    {"ticker": "HO.PA",     "name": "Thales",              "group": "PEA", "sector": "Defence / Cyber",       "flag": "🇫🇷"},
    {"ticker": "MC.PA",     "name": "LVMH",                "group": "PEA", "sector": "Luxury",                "flag": "🇫🇷"},
    {"ticker": "AM.PA",     "name": "Dassault Aviation",   "group": "PEA", "sector": "Aerospace / Defence",   "flag": "🇫🇷"},
    {"ticker": "RMS.PA",    "name": "Hermès",              "group": "PEA", "sector": "Ultra-Premium Luxury",  "flag": "🇫🇷"},
    {"ticker": "NOVO-B.CO", "name": "Novo Nordisk",        "group": "PEA", "sector": "Health / GLP-1",        "flag": "🇩🇰"},
    # ── Équities US ──
    {"ticker": "NVDA",  "name": "NVIDIA",        "group": "CTO", "sector": "Semiconductors / AI", "flag": "🇺🇸"},
    {"ticker": "META",  "name": "Meta Platforms", "group": "CTO", "sector": "Tech / Social / AI",  "flag": "🇺🇸"},
    {"ticker": "AMD",   "name": "AMD",            "group": "CTO", "sector": "Semiconductors",      "flag": "🇺🇸"},
    {"ticker": "TSLA",  "name": "Tesla",          "group": "CTO", "sector": "EV / Mobility",       "flag": "🇺🇸"},
    {"ticker": "MSFT",  "name": "Microsoft",      "group": "CTO", "sector": "Tech / Cloud / AI",   "flag": "🇺🇸"},
    {"ticker": "PLTR",  "name": "Palantir",       "group": "CTO", "sector": "AI / Data Analytics", "flag": "🇺🇸"},
    {"ticker": "AMZN",  "name": "Amazon",         "group": "CTO", "sector": "Tech / Cloud / AWS",  "flag": "🇺🇸"},
    {"ticker": "AAPL",  "name": "Apple",          "group": "CTO", "sector": "Tech / Consumer",     "flag": "🇺🇸"},
    {"ticker": "PEP",   "name": "PepsiCo",        "group": "CTO", "sector": "Defensive Consumer",  "flag": "🇺🇸"},
    {"ticker": "MA",    "name": "Mastercard",     "group": "CTO", "sector": "Fintech / Payments",  "flag": "🇺🇸"},
    {"ticker": "GOOGL", "name": "Alphabet",       "group": "CTO", "sector": "Tech / Search / AI",  "flag": "🇺🇸"},
    {"ticker": "NFLX",  "name": "Netflix",        "group": "CTO", "sector": "Streaming",           "flag": "🇺🇸"},
    {"ticker": "ORCL",  "name": "Oracle",         "group": "CTO", "sector": "Tech / Cloud / DB",   "flag": "🇺🇸"},
    {"ticker": "KO",    "name": "Coca-Cola",      "group": "CTO", "sector": "Defensive Consumer",  "flag": "🇺🇸"},
    {"ticker": "BLK",   "name": "BlackRock",      "group": "CTO", "sector": "Finance / ETF",       "flag": "🇺🇸"},
    {"ticker": "WMT",   "name": "Walmart",        "group": "CTO", "sector": "Retail / Tech",       "flag": "🇺🇸"},
    # ── Asia ──
    {"ticker": "1211.HK","name": "BYD",           "group": "CTO", "sector": "EV / Batteries",      "flag": "🇨🇳"},
    {"ticker": "1810.HK","name": "Xiaomi",        "group": "CTO", "sector": "Tech / EV / IoT",     "flag": "🇨🇳"},
]

BENCHMARKS = {
    "S&P 500":    "^GSPC",
    "NASDAQ 100": "^NDX",
    "CAC 40":     "^FCHI",
    "Euro Stoxx": "^STOXX50E",
}

FLAG_MAP = {
    ".PA": "🇫🇷", ".CO": "🇩🇰", ".AS": "🇳🇱", ".DE": "🇩🇪", ".MI": "🇮🇹",
    ".MC": "🇪🇸", ".L": "🇬🇧", ".HK": "🇨🇳", ".T": "🇯🇵", ".AX": "🇦🇺",
    ".TO": "🇨🇦", ".SW": "🇨🇭",
}

PERIODS = {"6M": "6mo", "1Y": "1y", "2Y": "2y", "5Y": "5y", "10Y": "10y"}

# ─────────────────────────────────────────────
# SESSION STATE — persistent watchlist
# ─────────────────────────────────────────────
if "watchlist" not in st.session_state:
    st.session_state.watchlist = DEFAULT_WATCHLIST.copy()

def guess_flag(ticker: str) -> str:
    for suffix, flag in FLAG_MAP.items():
        if ticker.upper().endswith(suffix.upper()):
            return flag
    return "🌍"

def add_to_watchlist(ticker: str, name: str, group: str, sector: str):
    ticker = ticker.upper().strip()
    existing = [e["ticker"] for e in st.session_state.watchlist]
    if ticker in existing:
        return False, "Already in watchlist."
    flag = guess_flag(ticker)
    st.session_state.watchlist.append({
        "ticker": ticker, "name": name or ticker,
        "group": group, "sector": sector or "—",
        "flag": flag,
    })
    return True, f"✅ {ticker} added!"

def remove_from_watchlist(ticker: str):
    st.session_state.watchlist = [
        e for e in st.session_state.watchlist if e["ticker"] != ticker
    ]

# ─────────────────────────────────────────────
# DATA LAYER  (cache 1h)
# ─────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def load_history(ticker: str, period: str) -> pd.DataFrame:
    try:
        df = yf.Ticker(ticker).history(period=period, auto_adjust=True)
        if df.empty:
            return pd.DataFrame()
        df.index = pd.to_datetime(df.index).tz_localize(None)
        return df
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=3600, show_spinner=False)
def load_info(ticker: str) -> dict:
    try:
        info = yf.Ticker(ticker).info
        return info if info else {}
    except Exception:
        return {}

@st.cache_data(ttl=3600, show_spinner=False)
def load_benchmark(ticker: str, period: str) -> pd.DataFrame:
    try:
        df = yf.download(ticker, period=period, auto_adjust=True, progress=False)
        if df.empty:
            return pd.DataFrame()
        df.index = pd.to_datetime(df.index).tz_localize(None)
        return df
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=3600, show_spinner=False)
def validate_ticker(ticker: str) -> tuple[bool, str]:
    """Quick validation: returns (is_valid, display_name)."""
    try:
        info = yf.Ticker(ticker).info
        name = info.get("longName") or info.get("shortName") or ""
        if not name and info.get("regularMarketPrice") is None:
            return False, ""
        return True, name
    except Exception:
        return False, ""

# ─────────────────────────────────────────────
# TECHNICAL INDICATORS
# ─────────────────────────────────────────────
def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def macd(series: pd.Series, fast=12, slow=26, sig=9):
    m = series.ewm(span=fast, adjust=False).mean() - series.ewm(span=slow, adjust=False).mean()
    s = m.ewm(span=sig, adjust=False).mean()
    return m, s, m - s

def bollinger(series: pd.Series, period=20, k=2):
    sma = series.rolling(period).mean()
    std = series.rolling(period).std()
    return sma + k * std, sma, sma - k * std

def atr(df: pd.DataFrame, period=14) -> pd.Series:
    tr = pd.concat([
        df["High"] - df["Low"],
        (df["High"] - df["Close"].shift()).abs(),
        (df["Low"]  - df["Close"].shift()).abs(),
    ], axis=1).max(axis=1)
    return tr.rolling(period).mean()

def compute_signal(hist: pd.DataFrame) -> tuple:
    """Returns (label, hex_color, numeric_score)."""
    if hist.empty or len(hist) < 60:
        return "⚪ N/A", "#888888", 0.0

    close = hist["Close"]
    rsi_v  = rsi(close).iloc[-1]
    ma50   = close.rolling(50).mean().iloc[-1]
    ma200  = close.rolling(200).mean().iloc[-1]
    price  = close.iloc[-1]
    h52    = close.tail(252).max()
    pct_hi = (price - h52) / h52 * 100

    score = 0.0
    if rsi_v < 30:    score += 2.5
    elif rsi_v < 42:  score += 1.2
    elif rsi_v > 75:  score -= 2.5
    elif rsi_v > 65:  score -= 1.0
    if price > ma200: score += 0.5
    if price > ma50:  score += 0.5
    if ma50  > ma200: score += 0.5   # golden cross
    if pct_hi < -30:  score += 2.0
    elif pct_hi < -15: score += 1.0
    elif pct_hi > -5:  score -= 0.5

    if score >= 4:    return "🟢 BUY",       "#00c851", score
    elif score >= 2:  return "🟡 ACCUMULATE","#ffbb33", score
    elif score >= 0:  return "🟠 WATCH",     "#ff8800", score
    else:             return "🔴 WAIT",      "#ff4444", score

# ─────────────────────────────────────────────
# BUILD LOOKUP  from current watchlist
# ─────────────────────────────────────────────
def build_lookup() -> dict:
    return {e["name"]: e for e in st.session_state.watchlist}

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")

    period_label = st.selectbox("Period", list(PERIODS.keys()), index=4)
    period       = PERIODS[period_label]

    # ── Group filter ──
    all_groups = sorted({e["group"] for e in st.session_state.watchlist})
    group_options = ["All"] + all_groups
    group_filt = st.selectbox("Filter by group", group_options)

    st.markdown("---")

    # ── ADD TICKER ──
    st.markdown("### ➕ Add to Watchlist")
    with st.form("add_form", clear_on_submit=True):
        new_tick   = st.text_input("Ticker (e.g. AAPL, ^GSPC, BTC-USD)", placeholder="TICKER")
        new_name   = st.text_input("Display name (optional)", placeholder="Apple")
        new_group  = st.text_input("Group / Account", placeholder="CTO")
        new_sector = st.text_input("Sector (optional)", placeholder="Tech / Consumer")
        submitted  = st.form_submit_button("Add ✅", use_container_width=True)
        if submitted and new_tick:
            ok, msg = add_to_watchlist(new_tick, new_name, new_group or "—", new_sector)
            if ok:
                st.success(msg)
                st.cache_data.clear()
            else:
                st.warning(msg)

    st.markdown("---")

    # ── REMOVE TICKER ──
    st.markdown("### 🗑️ Remove from Watchlist")
    names_in_watchlist = [e["name"] for e in st.session_state.watchlist]
    to_remove = st.selectbox("Select to remove", ["—"] + names_in_watchlist)
    if st.button("Remove 🗑️", use_container_width=True) and to_remove != "—":
        ticker_to_rm = next((e["ticker"] for e in st.session_state.watchlist
                             if e["name"] == to_remove), None)
        if ticker_to_rm:
            remove_from_watchlist(ticker_to_rm)
            st.cache_data.clear()
            st.rerun()

    st.markdown("---")

    # ── CACHE ──
    st.markdown("**🔄 Data Cache (1h)**")
    if st.button("♻️ Force Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    # ── WATCHLIST STATS ──
    st.markdown("---")
    n_total = len(st.session_state.watchlist)
    st.markdown(f"**📋 Watchlist:** {n_total} assets")
    for g in all_groups:
        n_g = sum(1 for e in st.session_state.watchlist if e["group"] == g)
        st.markdown(f"  · **{g}**: {n_g}")

    # Reset to default
    if st.button("🔁 Reset to default watchlist", use_container_width=True):
        st.session_state.watchlist = DEFAULT_WATCHLIST.copy()
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.caption("Data via yFinance • Not financial advice")

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.title("📊 Market Monitor")
st.markdown(
    f"*Live data via yFinance · Period: **{period_label}** · "
    f"Last refresh: {datetime.now().strftime('%d/%m/%Y %H:%M')}*"
)
st.markdown("---")

# ─────────────────────────────────────────────
# BUILD LOOKUP + FILTER HELPER
# ─────────────────────────────────────────────
LOOKUP = build_lookup()  # name → entry dict

def visible(name):
    entry = LOOKUP.get(name, {})
    return group_filt == "All" or entry.get("group") == group_filt

# ─────────────────────────────────────────────
# LOAD ALL DATA
# ─────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def load_all(tickers_key: str, period: str) -> dict:
    """tickers_key is a stable string so cache invalidates on watchlist change."""
    result = {}
    for entry in st.session_state.watchlist:
        name   = entry["name"]
        ticker = entry["ticker"]
        result[name] = {
            "hist": load_history(ticker, period),
            "info": load_info(ticker),
            "cfg":  entry,
        }
    return result

tickers_key = "|".join(sorted(e["ticker"] for e in st.session_state.watchlist))

with st.spinner("📡 Loading market data…"):
    ALL = load_all(tickers_key, period)

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tabs = st.tabs([
    "🏠 Overview",
    "📈 Technical Analysis",
    "🎯 Entry Signals",
    "🔄 Comparative Performance",
    "🌡️ Heatmap & Correlation",
    "💼 Portfolio Allocation",
    "🔍 Quick Search",
])
tab_overview, tab_tech, tab_signals, tab_compare, tab_heat, tab_portfolio, tab_search = tabs

# ══════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ══════════════════════════════════════════════
with tab_overview:

    visible_entries = [e for e in st.session_state.watchlist if visible(e["name"])]
    sectors = {e["sector"] for e in visible_entries}
    groups  = {e["group"]  for e in visible_entries}

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("📋 Assets tracked", len(st.session_state.watchlist))
    k2.metric("✅ In current filter", len(visible_entries))
    k3.metric("🏭 Sectors", len(sectors))
    k4.metric("📂 Groups", len(groups))

    st.markdown("---")

    # ── SUMMARY TABLE ────────────────────────
    rows = []
    for name, d in ALL.items():
        if not visible(name): continue
        hist = d["hist"]
        info = d["info"]
        cfg  = d["cfg"]
        if hist.empty: continue

        close = hist["Close"]
        price = close.iloc[-1]

        def safe_perf(n_days):
            if len(close) >= n_days:
                return (close.iloc[-1] / close.iloc[-n_days] - 1) * 100
            return None

        this_year = close[close.index.year == datetime.now().year]
        ytd = (price / this_year.iloc[0] - 1) * 100 if len(this_year) > 1 else None

        p1m  = safe_perf(21)
        p3m  = safe_perf(63)
        p1y  = safe_perf(252)
        p_all = (price / close.iloc[0] - 1) * 100

        # Currency formatting
        currency = info.get("currency", "")
        curr_sym = {"USD": "$", "EUR": "€", "GBP": "£", "HKD": "HK$",
                    "DKK": "DKK ", "JPY": "¥"}.get(currency, "")
        price_str = f"{curr_sym}{price:,.2f}"

        pe  = info.get("trailingPE")
        fpe = info.get("forwardPE")
        dy  = info.get("dividendYield")
        mc  = info.get("marketCap")

        signal_label, _, _ = compute_signal(hist)

        rows.append({
            " ":           cfg.get("flag", "🌍"),
            "Name":        name,
            "Ticker":      cfg["ticker"],
            "Group":       cfg.get("group", "—"),
            "Sector":      cfg.get("sector", "—"),
            "Price":       price_str,
            "YTD %":       f"{ytd:+.1f}%" if ytd is not None else "—",
            "1M %":        f"{p1m:+.1f}%" if p1m else "—",
            "3M %":        f"{p3m:+.1f}%" if p3m else "—",
            "1Y %":        f"{p1y:+.1f}%" if p1y else "—",
            f"{period_label} %": f"{p_all:+.0f}%",
            "P/E":         f"{pe:.0f}" if pe else "—",
            "P/E Fwd":     f"{fpe:.0f}" if fpe else "—",
            "Div %":       f"{dy*100:.1f}%" if dy else "—",
            "Mkt Cap":     (f"${mc/1e9:.1f}B" if mc and currency == "USD"
                            else f"{mc/1e9:.1f}B" if mc else "—"),
            "Signal":      signal_label,
        })

    df_ov = pd.DataFrame(rows)
    if not df_ov.empty:
        st.dataframe(df_ov, use_container_width=True, height=620, hide_index=True)
    else:
        st.info("No data available. Check your watchlist and internet connection.")

    # ── SECTOR + GROUP PIES ──
    st.markdown("### 🏭 Breakdown")
    pc1, pc2 = st.columns(2)

    with pc1:
        sec_df = pd.DataFrame([(e["sector"], e["group"])
                                for e in visible_entries],
                               columns=["Sector", "Group"])
        if not sec_df.empty:
            fig_sec = px.pie(sec_df, names="Sector", title="By Sector",
                             color_discrete_sequence=px.colors.qualitative.Set3,
                             hole=0.35)
            fig_sec.update_traces(textinfo="label+percent")
            fig_sec.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                                   showlegend=False, margin=dict(t=40, b=0))
            st.plotly_chart(fig_sec, use_container_width=True)

    with pc2:
        grp_df = pd.DataFrame([(e["name"], e["group"]) for e in visible_entries],
                               columns=["Name", "Group"])
        if not grp_df.empty:
            fig_grp = px.pie(grp_df, names="Group", title="By Group / Account",
                             hole=0.35,
                             color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_grp.update_traces(textinfo="label+percent+value")
            fig_grp.update_layout(paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=40, b=0))
            st.plotly_chart(fig_grp, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 2 — TECHNICAL ANALYSIS
# ══════════════════════════════════════════════
with tab_tech:

    visible_names = [e["name"] for e in st.session_state.watchlist if visible(e["name"])]

    if not visible_names:
        st.info("No assets in current filter.")
    else:
        col_s1, col_s2, col_s3 = st.columns([3, 2, 1])
        with col_s1:
            sel = st.selectbox("Asset", visible_names, key="tech_sel")
        with col_s2:
            chart_per_label = st.selectbox("Chart period", list(PERIODS.keys()), index=3,
                                           key="tech_period")
            chart_per = PERIODS[chart_per_label]
        with col_s3:
            show_bb = st.checkbox("Bollinger Bands", value=True)

        entry  = LOOKUP[sel]
        ticker = entry["ticker"]
        hist   = load_history(ticker, chart_per)
        info   = load_info(ticker)

        if hist.empty:
            st.warning(f"Could not load data for **{sel}** ({ticker}). "
                       "Check the ticker or try refreshing.")
        else:
            close  = hist["Close"]
            price  = close.iloc[-1]
            rsi_s  = rsi(close)
            ma20   = close.rolling(20).mean()
            ma50   = close.rolling(50).mean()
            ma200  = close.rolling(200).mean()
            bb_u, bb_m, bb_l = bollinger(close)
            macd_l, macd_sig, macd_hist = macd(close)
            atr_v  = atr(hist).iloc[-1]

            h52    = close.tail(252).max()
            l52    = close.tail(252).min()
            ma50v  = ma50.iloc[-1]
            ma200v = ma200.iloc[-1]
            rsi_v  = rsi_s.iloc[-1]
            beta   = info.get("beta")
            prev   = close.iloc[-2] if len(close) > 1 else price

            # ── KPI ROW ─────────────────────────
            currency = info.get("currency", "")
            curr_sym = {"USD": "$", "EUR": "€", "GBP": "£", "HKD": "HK$",
                        "DKK": "DKK ", "JPY": "¥"}.get(currency, "")

            c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
            c1.metric("Price", f"{curr_sym}{price:,.2f}",
                      f"{(price/prev-1)*100:+.2f}%")
            c2.metric("RSI 14", f"{rsi_v:.1f}",
                      "🔥 Overbought" if rsi_v > 70 else
                      ("💎 Oversold" if rsi_v < 30 else "Neutral"))
            c3.metric("MA 50",  f"{curr_sym}{ma50v:,.2f}",
                      f"{(price/ma50v-1)*100:+.1f}%")
            c4.metric("MA 200", f"{curr_sym}{ma200v:,.2f}",
                      f"{(price/ma200v-1)*100:+.1f}%")
            c5.metric("52W High", f"{curr_sym}{h52:,.2f}",
                      f"{(price/h52-1)*100:+.1f}%")
            c6.metric("52W Low",  f"{curr_sym}{l52:,.2f}",
                      f"{(price/l52-1)*100:+.1f}%")
            c7.metric("ATR 14",   f"{curr_sym}{atr_v:,.2f}" if not np.isnan(atr_v) else "—")

            # ── MAIN CHART ──────────────────────
            fig = make_subplots(
                rows=4, cols=1,
                shared_xaxes=True,
                row_heights=[0.50, 0.15, 0.17, 0.18],
                vertical_spacing=0.02,
                subplot_titles=[
                    f"{sel} ({ticker}) — Price & Moving Averages",
                    "Volume", "RSI (14)", "MACD (12, 26, 9)"],
            )

            # Candlestick
            fig.add_trace(go.Candlestick(
                x=hist.index, open=hist["Open"], high=hist["High"],
                low=hist["Low"], close=close, name="Price",
                increasing_line_color="#26a69a", decreasing_line_color="#ef5350",
            ), row=1, col=1)

            # MAs
            for ma_s, ma_c, ma_n in [
                (ma20,  "#FF9800", "MA 20"),
                (ma50,  "#2196F3", "MA 50"),
                (ma200, "#E91E63", "MA 200"),
            ]:
                fig.add_trace(go.Scatter(x=hist.index, y=ma_s, name=ma_n,
                                          line=dict(color=ma_c, width=1.5),
                                          opacity=0.85), row=1, col=1)

            # Bollinger
            if show_bb:
                fig.add_trace(go.Scatter(x=hist.index, y=bb_u,
                                          name="BB Upper", line=dict(color="#78909C", width=1, dash="dot"),
                                          opacity=0.6), row=1, col=1)
                fig.add_trace(go.Scatter(x=hist.index, y=bb_l,
                                          name="BB Lower", line=dict(color="#78909C", width=1, dash="dot"),
                                          fill="tonexty", fillcolor="rgba(120,144,156,0.08)",
                                          opacity=0.6), row=1, col=1)

            # Volume
            vol_colors = ["#26a69a" if c >= o else "#ef5350"
                          for c, o in zip(hist["Close"], hist["Open"])]
            fig.add_trace(go.Bar(x=hist.index, y=hist["Volume"], name="Volume",
                                  marker_color=vol_colors, opacity=0.7), row=2, col=1)

            # RSI
            fig.add_trace(go.Scatter(x=hist.index, y=rsi_s, name="RSI",
                                      line=dict(color="#AB47BC", width=1.5)), row=3, col=1)
            for lvl, col in [(70, "rgba(239,83,80,0.35)"), (30, "rgba(38,166,154,0.35)")]:
                fig.add_hline(y=lvl, line_dash="dash", line_color=col,
                              annotation_text=str(lvl), row=3, col=1)
            fig.add_hrect(y0=30, y1=70, fillcolor="rgba(200,200,200,0.04)",
                          line_width=0, row=3, col=1)

            # MACD
            macd_bar_colors = ["#26a69a" if v >= 0 else "#ef5350" for v in macd_hist]
            fig.add_trace(go.Bar(x=hist.index, y=macd_hist, name="MACD Hist",
                                  marker_color=macd_bar_colors, opacity=0.7), row=4, col=1)
            fig.add_trace(go.Scatter(x=hist.index, y=macd_l, name="MACD",
                                      line=dict(color="#42A5F5", width=1.5)), row=4, col=1)
            fig.add_trace(go.Scatter(x=hist.index, y=macd_sig, name="Signal",
                                      line=dict(color="#FF7043", width=1.5)), row=4, col=1)

            fig.update_layout(
                height=820,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(20,20,20,0.15)",
                xaxis_rangeslider_visible=False,
                legend=dict(orientation="h", yanchor="bottom", y=1.01, x=0),
                margin=dict(t=60, b=20),
            )
            for ax in ["xaxis", "xaxis2", "xaxis3", "xaxis4"]:
                fig.update_layout({ax: {"gridcolor": "rgba(128,128,128,0.12)"}})
            for ax in ["yaxis", "yaxis2", "yaxis3", "yaxis4"]:
                fig.update_layout({ax: {"gridcolor": "rgba(128,128,128,0.12)"}})

            st.plotly_chart(fig, use_container_width=True)

            # ── FUNDAMENTALS ────────────────────
            st.markdown("### 📊 Fundamentals")
            f1, f2, f3 = st.columns(3)

            def safe(key, pct=False, digits=2):
                v = info.get(key)
                if v is None: return "—"
                if pct: return f"{v*100:.1f}%"
                return f"{v:.{digits}f}"

            with f1:
                st.markdown("**Valuation**")
                st.markdown(f"""
| Ratio | Value |
|-------|-------|
| P/E (TTM) | {safe('trailingPE')} |
| P/E Forward | {safe('forwardPE')} |
| PEG | {safe('pegRatio')} |
| P/B | {safe('priceToBook')} |
| EV/EBITDA | {safe('enterpriseToEbitda')} |
""")
            with f2:
                st.markdown("**Growth & Profitability**")
                st.markdown(f"""
| Metric | Value |
|--------|-------|
| Revenue Growth | {safe('revenueGrowth', pct=True)} |
| EPS Growth | {safe('earningsGrowth', pct=True)} |
| Net Margin | {safe('profitMargins', pct=True)} |
| ROE | {safe('returnOnEquity', pct=True)} |
| ROA | {safe('returnOnAssets', pct=True)} |
""")
            with f3:
                mc  = info.get("marketCap")
                dy  = info.get("dividendYield")
                rec = info.get("recommendationKey", "—")
                sector_info = info.get("sector", entry.get("sector", "—"))
                st.markdown("**General**")
                st.markdown(f"""
| Metric | Value |
|--------|-------|
| Market Cap | {f"{curr_sym}{mc/1e9:.1f}B" if mc else "—"} |
| Dividend Yield | {f"{dy*100:.2f}%" if dy else "—"} |
| Beta | {safe('beta')} |
| Analyst Reco | {rec.upper()} |
| Sector | {sector_info} |
| Currency | {currency or "—"} |
""")

# ══════════════════════════════════════════════
# TAB 3 — ENTRY SIGNALS
# ══════════════════════════════════════════════
with tab_signals:
    st.info(
        "⚙️ Signals computed from: **RSI 14**, **MA50/MA200**, **distance to 52W High**. "
        "Score → 🟢 BUY / 🟡 ACCUMULATE / 🟠 WATCH / 🔴 WAIT. "
        "**Not financial advice.**"
    )

    sig_rows = []
    for name, d in ALL.items():
        if not visible(name): continue
        hist = d["hist"]
        cfg  = d["cfg"]
        if hist.empty or len(hist) < 60: continue

        close  = hist["Close"]
        rsi_v  = rsi(close).iloc[-1]
        ma50v  = close.rolling(50).mean().iloc[-1]
        ma200v = close.rolling(200).mean().iloc[-1]
        price  = close.iloc[-1]
        h52    = close.tail(252).max()
        l52    = close.tail(252).min()

        label, color, score = compute_signal(hist)
        p1y = (price / close.iloc[-252] - 1) * 100 if len(close) >= 252 else None
        ytd_c = close[close.index.year == datetime.now().year]
        ytd = (price / ytd_c.iloc[0] - 1) * 100 if len(ytd_c) > 1 else None

        sig_rows.append({
            " ":           cfg.get("flag", "🌍"),
            "Name":        name,
            "Ticker":      cfg["ticker"],
            "Group":       cfg.get("group", "—"),
            "Price":       round(price, 2),
            "RSI 14":      round(rsi_v, 1),
            "vs MA50":     f"{(price/ma50v-1)*100:+.1f}%",
            "vs MA200":    f"{(price/ma200v-1)*100:+.1f}%",
            "vs 52W High": f"{(price/h52-1)*100:+.1f}%",
            "vs 52W Low":  f"{(price/l52-1)*100:+.1f}%",
            "Golden Cross": "✅" if ma50v > ma200v else "❌",
            "YTD %":       f"{ytd:+.1f}%" if ytd is not None else "—",
            "1Y %":        f"{p1y:+.1f}%" if p1y is not None else "—",
            "Signal":      label,
            "_score":      score,
        })

    if sig_rows:
        sig_df = pd.DataFrame(sig_rows).sort_values("_score", ascending=False)
        disp_cols = [" ", "Name", "Ticker", "Group", "Price", "RSI 14",
                     "vs MA50", "vs MA200", "vs 52W High", "vs 52W Low",
                     "Golden Cross", "YTD %", "1Y %", "Signal"]
        st.dataframe(sig_df[disp_cols], use_container_width=True,
                     height=600, hide_index=True)

        # Signal distribution bar
        st.markdown("### 📊 Signal Distribution")
        cnt = sig_df["Signal"].value_counts().reset_index()
        cnt.columns = ["Signal", "Count"]
        fig_bar = px.bar(
            cnt, x="Signal", y="Count", color="Signal",
            color_discrete_map={
                "🟢 BUY":       "#00c851",
                "🟡 ACCUMULATE":"#ffbb33",
                "🟠 WATCH":     "#ff8800",
                "🔴 WAIT":      "#ff4444",
            },
            text="Count",
        )
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(20,20,20,0.15)",
            showlegend=False, height=300,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # RSI scatter
        st.markdown("### 📉 RSI vs. Distance to 52W High")
        scatter_data = []
        for _, row in sig_df.iterrows():
            try:
                dist = float(row["vs 52W High"].replace("%","").replace("+",""))
                scatter_data.append({
                    "Name": row["Name"], "RSI": row["RSI 14"],
                    "Dist 52W High %": dist, "Signal": row["Signal"],
                    "Group": row["Group"],
                })
            except Exception:
                pass
        if scatter_data:
            sc_df = pd.DataFrame(scatter_data)
            fig_sc = px.scatter(
                sc_df, x="RSI", y="Dist 52W High %",
                color="Signal", text="Name", size_max=12,
                color_discrete_map={
                    "🟢 BUY":"#00c851","🟡 ACCUMULATE":"#ffbb33",
                    "🟠 WATCH":"#ff8800","🔴 WAIT":"#ff4444"},
                hover_data=["Group"],
                title="Bottom-left = oversold + far from high (better entry zone)",
            )
            fig_sc.add_vline(x=30, line_dash="dash", line_color="rgba(38,166,154,0.5)")
            fig_sc.add_vline(x=70, line_dash="dash", line_color="rgba(239,83,80,0.5)")
            fig_sc.update_traces(textposition="top center")
            fig_sc.update_layout(
                height=500,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(20,20,20,0.15)",
            )
            st.plotly_chart(fig_sc, use_container_width=True)
    else:
        st.info("Not enough data to compute signals. Try a longer period.")

# ══════════════════════════════════════════════
# TAB 4 — COMPARATIVE PERFORMANCE
# ══════════════════════════════════════════════
with tab_compare:
    st.markdown("### 🔄 Normalized Performance (base 100)")

    visible_names_c = [e["name"] for e in st.session_state.watchlist if visible(e["name"])]
    default_sel = visible_names_c[:6]

    sel_comp = st.multiselect(
        "Choose assets", visible_names_c, default=default_sel,
    )
    inc_bench = st.checkbox("Add benchmarks (S&P500, NASDAQ, CAC40, Euro Stoxx)", value=True)

    fig_norm = go.Figure()

    for name in sel_comp:
        h = ALL[name]["hist"]
        if h.empty: continue
        norm = h["Close"] / h["Close"].iloc[0] * 100
        cfg  = LOOKUP[name]
        fig_norm.add_trace(go.Scatter(
            x=h.index, y=norm,
            name=f"{cfg.get('flag','🌍')} {name}",
            mode="lines", line=dict(width=2),
        ))

    if inc_bench:
        with st.spinner("Loading benchmarks…"):
            for label, bticker in BENCHMARKS.items():
                bh = load_benchmark(bticker, period)
                if bh.empty: continue
                if isinstance(bh.columns, pd.MultiIndex):
                    bh.columns = bh.columns.get_level_values(0)
                if "Close" not in bh.columns: continue
                norm_b = bh["Close"] / bh["Close"].iloc[0] * 100
                fig_norm.add_trace(go.Scatter(
                    x=bh.index, y=norm_b,
                    name=label, mode="lines",
                    line=dict(width=2, dash="dash"),
                ))

    fig_norm.update_layout(
        height=550,
        xaxis_title="Date", yaxis_title="Performance (base 100)",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(20,20,20,0.15)",
        xaxis=dict(gridcolor="rgba(128,128,128,0.15)"),
        yaxis=dict(gridcolor="rgba(128,128,128,0.15)"),
        legend=dict(orientation="v", x=1.02),
        margin=dict(r=180),
    )
    st.plotly_chart(fig_norm, use_container_width=True)

    # ── Ranking bar ──
    st.markdown("### 🏆 Performance Ranking")
    rank_rows = []
    for name in visible_names_c:
        h = ALL[name]["hist"]
        if h.empty or len(h) < 10: continue
        p = (h["Close"].iloc[-1] / h["Close"].iloc[0] - 1) * 100
        rank_rows.append({
            "Name": name,
            "Flag": LOOKUP[name].get("flag", "🌍"),
            "Perf %": round(p, 1),
            "Group": LOOKUP[name].get("group", "—"),
        })

    if rank_rows:
        rank_df = pd.DataFrame(rank_rows).sort_values("Perf %", ascending=True)
        rank_df["Label"] = rank_df["Flag"] + " " + rank_df["Name"]
        fig_rank = px.bar(
            rank_df, y="Label", x="Perf %", orientation="h",
            color="Perf %",
            color_continuous_scale=["#ef5350", "#ffbb33", "#26a69a"],
            text="Perf %",
            title=f"Total performance over the period ({period_label})",
        )
        fig_rank.update_traces(texttemplate="%{x:+.0f}%", textposition="outside")
        fig_rank.update_layout(
            height=max(400, len(rank_rows) * 26),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(20,20,20,0.15)",
            yaxis_title="", xaxis_title="Performance %",
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_rank, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 5 — HEATMAP & CORRELATION
# ══════════════════════════════════════════════
with tab_heat:

    # ── Annual heatmap ───────────────────────
    st.markdown("### 🌡️ Annual Performance Heatmap (%)")

    heat_data = {}
    for name, d in ALL.items():
        if not visible(name): continue
        h = d["hist"]
        if h.empty: continue
        yearly = h["Close"].resample("YE").last().pct_change() * 100
        heat_data[name] = yearly

    if heat_data:
        hdf = pd.DataFrame(heat_data)
        hdf.index = hdf.index.year
        hdf = hdf.tail(10)

        fig_heat = px.imshow(
            hdf.T.round(1),
            color_continuous_scale="RdYlGn",
            zmin=-50, zmax=100,
            text_auto=".0f",
            aspect="auto",
            title="Annual performance (%) — each cell = calendar year return",
        )
        fig_heat.update_layout(
            height=max(400, len(heat_data) * 28),
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=200, t=60, b=20),
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    st.markdown("---")

    # ── Correlation matrix ───────────────────
    st.markdown("### 🔗 Daily Returns Correlation Matrix")
    corr_names = [e["name"] for e in st.session_state.watchlist if visible(e["name"])]
    corr_sel = st.multiselect(
        "Assets for correlation",
        corr_names,
        default=corr_names[:15],
    )

    ret_dict = {}
    for name in corr_sel:
        h = ALL[name]["hist"]
        if not h.empty:
            ret_dict[name] = h["Close"].pct_change().dropna()

    if len(ret_dict) > 1:
        ret_df = pd.DataFrame(ret_dict).dropna()
        corr = ret_df.corr().round(2)

        fig_corr = px.imshow(
            corr,
            color_continuous_scale="RdBu_r",
            zmin=-1, zmax=1,
            text_auto=".2f",
            title="Correlation (1 = same direction, −1 = opposite, 0 = independent)",
            aspect="auto",
        )
        fig_corr.update_layout(
            height=max(500, len(corr_sel) * 30),
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=180, b=180, t=60),
        )
        st.plotly_chart(fig_corr, use_container_width=True)

        st.info(
            "💡 **Diversification tip:** look for low correlations (< 0.5) between positions. "
            "Assets from different geographies and sectors tend to decorrelate."
        )
    else:
        st.info("Select at least 2 assets to compute the correlation matrix.")

# ══════════════════════════════════════════════
# TAB 6 — PORTFOLIO ALLOCATION
# ══════════════════════════════════════════════
with tab_portfolio:
    st.markdown("## 💼 Portfolio Allocation Builder")
    st.info("⚠️ Suggested allocation only. Adapt to your risk profile. Not financial advice.")

    st.markdown("### ⚖️ Set weights for your assets")
    st.caption("Adjust the sliders, the pie chart updates automatically.")

    visible_names_p = [e["name"] for e in st.session_state.watchlist if visible(e["name"])]

    if not visible_names_p:
        st.info("No assets in current filter.")
    else:
        # Auto equal-weight default
        n_assets = len(visible_names_p)
        default_weight = round(100 / n_assets, 1)

        weights = {}
        cols = st.columns(2)
        for i, name in enumerate(visible_names_p):
            with cols[i % 2]:
                flag = LOOKUP[name].get("flag", "🌍")
                weights[name] = st.slider(
                    f"{flag} {name}",
                    min_value=0.0, max_value=50.0,
                    value=default_weight, step=0.5,
                    key=f"w_{name}",
                )

        total_w = sum(weights.values())
        st.markdown(f"**Total weight: {total_w:.1f}%** {'✅' if abs(total_w - 100) < 0.5 else '⚠️ (target = 100%)'}")

        alloc_rows = []
        for name, w in weights.items():
            if w == 0: continue
            entry  = LOOKUP[name]
            ticker = entry["ticker"]
            h = ALL[name]["hist"]
            p1y_str = "—"
            if not h.empty and len(h["Close"]) >= 252:
                p1y = (h["Close"].iloc[-1] / h["Close"].iloc[-252] - 1) * 100
                p1y_str = f"{p1y:+.1f}%"
            alloc_rows.append({
                " ":      entry.get("flag", "🌍"),
                "Name":   name,
                "Ticker": ticker,
                "Group":  entry.get("group", "—"),
                "Sector": entry.get("sector", "—"),
                "Weight %": w,
                "1Y %":   p1y_str,
            })

        alloc_df = pd.DataFrame(alloc_rows)
        if not alloc_df.empty:
            st.dataframe(alloc_df, use_container_width=True, hide_index=True)

            # Pie
            fig_alloc = px.pie(
                alloc_df, names="Name", values="Weight %",
                title="Allocation breakdown",
                color_discrete_sequence=px.colors.qualitative.Pastel,
                hole=0.3,
            )
            fig_alloc.update_traces(textinfo="label+percent")
            fig_alloc.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                showlegend=False, margin=dict(t=40, b=0),
            )
            st.plotly_chart(fig_alloc, use_container_width=True)

            # Group breakdown
            if "Group" in alloc_df.columns:
                grp_alloc = alloc_df.groupby("Group")["Weight %"].sum().reset_index()
                fig_grp_alloc = px.pie(
                    grp_alloc, names="Group", values="Weight %",
                    title="By group / account",
                    color_discrete_sequence=px.colors.qualitative.Set2,
                    hole=0.3,
                )
                fig_grp_alloc.update_traces(textinfo="label+percent")
                fig_grp_alloc.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    margin=dict(t=40, b=0),
                )
                st.plotly_chart(fig_grp_alloc, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 7 — QUICK SEARCH (ad-hoc lookup)
# ══════════════════════════════════════════════
with tab_search:
    st.markdown("## 🔍 Quick Ticker Lookup")
    st.markdown(
        "Search any asset not in your watchlist — stocks, ETFs, indices, crypto. "
        "Enter a valid yFinance ticker."
    )

    col_q1, col_q2, col_q3 = st.columns([2, 1, 1])
    with col_q1:
        search_ticker = st.text_input(
            "Ticker", placeholder="e.g. AAPL, ^GSPC, ETH-USD, GLD, VT",
            key="search_tick",
        )
    with col_q2:
        search_period_label = st.selectbox(
            "Period", list(PERIODS.keys()), index=3, key="search_per"
        )
        search_period = PERIODS[search_period_label]
    with col_q3:
        st.markdown("<br>", unsafe_allow_html=True)
        do_search = st.button("🔍 Search", use_container_width=True)

    if do_search and search_ticker:
        ticker_q = search_ticker.strip().upper()
        with st.spinner(f"Loading {ticker_q}…"):
            hist_q = load_history(ticker_q, search_period)
            info_q = load_info(ticker_q)

        if hist_q.empty:
            st.error(f"Could not find data for **{ticker_q}**. "
                     "Check the ticker format (e.g. BTC-USD, ^GSPC, AAPL).")
        else:
            long_name = info_q.get("longName") or info_q.get("shortName") or ticker_q
            currency  = info_q.get("currency", "")
            curr_sym  = {"USD": "$", "EUR": "€", "GBP": "£", "HKD": "HK$",
                         "DKK": "DKK ", "JPY": "¥"}.get(currency, "")

            st.success(f"**{long_name}** — {ticker_q}")
            st.markdown(f"Currency: `{currency}` · Sector: `{info_q.get('sector','—')}` · "
                        f"Exchange: `{info_q.get('exchange','—')}`")

            close_q = hist_q["Close"]
            price_q = close_q.iloc[-1]
            prev_q  = close_q.iloc[-2] if len(close_q) > 1 else price_q
            rsi_q   = rsi(close_q)
            ma50_q  = close_q.rolling(50).mean()
            ma200_q = close_q.rolling(200).mean()

            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Price", f"{curr_sym}{price_q:,.2f}", f"{(price_q/prev_q-1)*100:+.2f}%")
            m2.metric("RSI 14", f"{rsi_q.iloc[-1]:.1f}")
            m3.metric("MA 50",  f"{curr_sym}{ma50_q.iloc[-1]:,.2f}",
                      f"{(price_q/ma50_q.iloc[-1]-1)*100:+.1f}%")
            m4.metric("MA 200", f"{curr_sym}{ma200_q.iloc[-1]:,.2f}",
                      f"{(price_q/ma200_q.iloc[-1]-1)*100:+.1f}%")
            sig_q, _, _ = compute_signal(hist_q)
            m5.metric("Signal", sig_q)

            # Quick chart
            fig_q = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                   row_heights=[0.70, 0.30], vertical_spacing=0.04,
                                   subplot_titles=["Price", "Volume"])
            fig_q.add_trace(go.Candlestick(
                x=hist_q.index, open=hist_q["Open"], high=hist_q["High"],
                low=hist_q["Low"], close=close_q, name="Price",
                increasing_line_color="#26a69a", decreasing_line_color="#ef5350",
            ), row=1, col=1)
            fig_q.add_trace(go.Scatter(x=hist_q.index, y=ma50_q,
                                        name="MA50", line=dict(color="#2196F3", width=1.5)),
                             row=1, col=1)
            fig_q.add_trace(go.Scatter(x=hist_q.index, y=ma200_q,
                                        name="MA200", line=dict(color="#E91E63", width=1.5)),
                             row=1, col=1)
            vol_c = ["#26a69a" if c >= o else "#ef5350"
                     for c, o in zip(hist_q["Close"], hist_q["Open"])]
            fig_q.add_trace(go.Bar(x=hist_q.index, y=hist_q["Volume"],
                                    marker_color=vol_c, name="Volume", opacity=0.7),
                             row=2, col=1)
            fig_q.update_layout(
                height=540, paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(20,20,20,0.15)",
                xaxis_rangeslider_visible=False,
                margin=dict(t=40, b=10),
            )
            st.plotly_chart(fig_q, use_container_width=True)

            # Add-to-watchlist shortcut
            st.markdown("---")
            st.markdown("**➕ Add to watchlist?**")
            aq1, aq2, aq3 = st.columns(3)
            with aq1:
                add_name_q = st.text_input("Display name", value=long_name[:40], key="aq_name")
            with aq2:
                add_group_q = st.text_input("Group / Account", value="—", key="aq_group")
            with aq3:
                add_sector_q = st.text_input("Sector", value=info_q.get("sector","—"), key="aq_sector")
            if st.button("Add to watchlist ✅", key="aq_btn"):
                ok, msg = add_to_watchlist(ticker_q, add_name_q, add_group_q, add_sector_q)
                if ok:
                    st.success(msg)
                    st.cache_data.clear()
                else:
                    st.warning(msg)

    elif not search_ticker:
        st.markdown("""
**Examples of valid tickers:**

| Type | Examples |
|------|---------|
| US Stocks | `AAPL`, `MSFT`, `NVDA`, `BRK-B` |
| EU Stocks | `SU.PA`, `SAP.DE`, `ASML.AS` |
| ETFs | `SPY`, `QQQ`, `VT`, `IWDA.AS`, `GLD` |
| Indices | `^GSPC` (S&P500), `^NDX` (Nasdaq), `^FCHI` (CAC40) |
| Crypto | `BTC-USD`, `ETH-USD`, `SOL-USD` |
| Forex | `EURUSD=X`, `GBPUSD=X` |
| Commodities | `GC=F` (Gold), `CL=F` (Oil), `SI=F` (Silver) |
""")

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; opacity:0.4; font-size:0.8em'>"
    "📊 Personal Market Monitor · Data via yFinance (1h cache) · "
    "Not financial advice · Refresh page or use ♻️ button to force reload"
    "</div>",
    unsafe_allow_html=True,
)
