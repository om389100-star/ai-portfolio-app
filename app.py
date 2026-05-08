from db import save_portfolio, get_portfolios, init_db
from auth import login, check_auth
from payments import create_checkout_session

import streamlit as st
import requests
import pandas as pd
import plotly.express as px

init_db()

if "paid" not in st.session_state:
    st.session_state["paid"] = False

# ---------------------------
# CONFIG
# ---------------------------
API_URL = "https://ai-portfolio-backend.onrender.com/optimize"

query_params = st.query_params

if "success" in query_params:
    st.session_state["paid"] = True
    st.success("✅ Payment successful! Premium unlocked.")

st.set_page_config(
    page_title="AI Portfolio Optimizer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------
# AI EXPLANATION FUNCTION
# ---------------------------
def generate_explanation(data, risk_level):
    weights = data["weights"]
    sharpe = data["sharpe_ratio"]
    volatility = data["expected_volatility"]
    expected_return = data["expected_return"]

    top_stock = max(weights, key=weights.get)

    if sharpe > 1:
        sharpe_text = "strong"
    elif sharpe > 0.5:
        sharpe_text = "moderate"
    else:
        sharpe_text = "weak"

    if volatility < 0.2:
        risk_text = "low risk and stable"
    elif volatility < 0.4:
        risk_text = "moderately risky"
    else:
        risk_text = "highly volatile"

    explanation = f"""
### 🧠 AI Portfolio Analysis

This portfolio is optimized for a **{risk_level.upper()} risk strategy**.

- 📌 Highest allocation: **{top_stock}**
- 📈 Expected return: **{expected_return*100:.2f}%**
- ⚖️ Sharpe Ratio: **{sharpe:.2f}** ({sharpe_text})
- 📉 Risk level: **{risk_text}** ({volatility*100:.2f}% volatility)

### 📊 Summary
Balanced portfolio optimized for risk-return efficiency.
"""
    return explanation


# ---------------------------
# HEADER
# ---------------------------
st.markdown("""
# 💼 AI Portfolio Optimizer
### 📊 Institutional-grade portfolio intelligence powered by AI
---
""")

colA, colB = st.columns([4, 1])

with colB:
    if not st.session_state["paid"]:
        if st.button("💰 Upgrade Pro", key="upgrade_btn"):

            checkout_url = create_checkout_session()

            st.markdown(
                f"[👉 Click Here to Complete Payment]({checkout_url})"
            )

# ---------------------------
# AUTH
# ---------------------------
login()

if not check_auth():
    st.warning("🔐 Please login to use the app")
    st.stop()

# ---------------------------
# SIDEBAR
# ---------------------------
with st.sidebar:
    theme = st.selectbox("🎨 Theme", ["Dark", "Light"])

    st.markdown("---")

    st.subheader("👤 Account")

    if st.session_state.get("paid"):
       st.success("💎 PRO Member")
    else:
       st.warning("🆓 Free Plan")

    st.markdown("---")

    menu = st.radio(
        "Navigation",
        [
            "📊 Dashboard",
            "📂 Portfolio History",
            "🧠 AI Insights",
            "⚙️ Settings"
        ]
    )

    st.title("⚙️ Portfolio Settings")

    tickers_input = st.text_input(
        "Stock Tickers",
        placeholder="AAPL, MSFT, TSLA"
    )

    risk_level = st.selectbox(
        "Risk Level",
        ["low", "medium", "high"]
    )

    if st.button("📊 Try Demo Portfolio", key="demo_btn"):
        tickers_input = "AAPL, MSFT, TSLA"

    run_btn = st.button("🚀 Optimize", key="optimize_btn")


# ---------------------------
# THEME STYLING
# ---------------------------
if theme == "Dark":
    st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
        color: white;
    }
    [data-testid="metric-container"] {
        background-color: #1c1f26;
        border-radius: 10px;
        padding: 15px;
    }
    section[data-testid="stSidebar"] {
        background-color: #111827;
    }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    .stApp {
        background-color: #f9fafb;
        color: black;
    }
    [data-testid="metric-container"] {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #e5e7eb;
    }
    section[data-testid="stSidebar"] {
        background-color: #f3f4f6;
    }
    </style>
    """, unsafe_allow_html=True)


# ---------------------------
# EMPTY STATE
# ---------------------------
if not run_btn:
    st.info("👈 Configure your portfolio settings and click Optimize to begin")


# ---------------------------
# MAIN LOGIC
# ---------------------------
if run_btn:

    if not tickers_input:
        st.warning("Please enter stock tickers")
        st.stop()

    tickers = [t.strip().upper() for t in tickers_input.split(",")]

    if len(tickers) < 2:
        st.warning("Enter at least 2 stocks")
        st.stop()

    # API CALL
    with st.status("🔍 AI analyzing portfolio...", expanded=True):
        try:
            response = requests.post(
                API_URL,
                json={
                    "tickers": tickers,
                    "risk_level": risk_level
                }
            )
            data = response.json()
        except Exception as e:
            st.error(f"Error: {e}")
            st.stop()

    if "weights" not in data:
        st.error("Invalid response from backend")
        st.stop()

    st.success("✅ Portfolio Optimized")

    # Save portfolio
    save_portfolio(
        st.session_state["user_id"],
        tickers,
        risk_level,
        data["expected_return"],
        data["sharpe_ratio"]
    )

    # ---------------------------
    # LAYOUT
    # ---------------------------
    col1, col2 = st.columns([1.2, 0.8])

    # Allocation
    with col1:
        st.markdown("---")
        st.subheader("📊 Portfolio Allocation")

        weights = data["weights"]

        df_weights = pd.DataFrame(
            weights.items(),
            columns=["Stock", "Weight"]
        )

        df_weights["Weight %"] = df_weights["Weight"] * 100

        st.dataframe(df_weights[["Stock", "Weight %"]], use_container_width=True)
        st.bar_chart(df_weights.set_index("Stock")["Weight %"])

        fig_pie = px.pie(
            df_weights,
            values="Weight %",
            names="Stock",
            title="Portfolio Allocation Breakdown",
            hole=0.45
        )

        fig_pie.update_traces(
        textposition="inside",
        textinfo="percent+label"
        )

        st.plotly_chart(fig_pie, use_container_width=True)

    # Metrics
    with col2:
        st.markdown("---")
        st.subheader("📊 Key Metrics")

        colA, colB, colC = st.columns(3)

        colA.metric("📈 Expected Return", f"{data['expected_return']*100:.2f}%")
        colB.metric("⚠️ Volatility", f"{data['expected_volatility']*100:.2f}%")
        colC.metric("⚖️ Sharpe Ratio", f"{data['sharpe_ratio']:.2f}")

    # Chart
    st.markdown("---")
    st.subheader("📉 Portfolio Growth")

    history = pd.DataFrame(data["price_history"])
    history["Date"] = pd.to_datetime(history["Date"])
    history.set_index("Date", inplace=True)

    fig = px.line(
        history,
        x=history.index,
        y=history.columns,
        title="Portfolio Performance Over Time"
    )

    fig.update_layout(
        template="plotly_dark" if theme == "Dark" else "plotly_white",
        xaxis_title="Date",
        yaxis_title="Price",
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

    # AI Insights
    explanation = generate_explanation(data, risk_level)

    if st.session_state["paid"]:

        with st.expander("🧠 AI Insights", expanded=True):
            st.markdown(explanation)

    else:
        st.warning("🔒 Upgrade to Pro to unlock AI Insights")

    # ---------------------------
    # ANALYTICS DASHBOARD
    # ---------------------------

    st.markdown("---")
    st.subheader("📈 SaaS Analytics Dashboard")

    history_db = get_portfolios(st.session_state["user_id"])

    total_portfolios = len(history_db)

    if total_portfolios > 0:

        returns = [row[3] for row in history_db]
        sharpes = [row[4] for row in history_db]

        avg_return = sum(returns) / len(returns)
        best_sharpe = max(sharpes)

    else:
        avg_return = 0
        best_sharpe = 0

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "📂 Total Portfolios",
        total_portfolios
    )

    col2.metric(
        "📈 Avg Return",
        f"{avg_return*100:.2f}%"
    )

    col3.metric(
    "⚖️ Best Sharpe",
    f"{best_sharpe:.2f}"
    )
# --------------------------
# SAVED PORTFOLIOS
# ---------------------------
st.markdown("---")
st.subheader("📂 Saved Portfolios")

history_db = get_portfolios(st.session_state["user_id"])

if history_db:
    df_history = pd.DataFrame(
        history_db,
        columns=["ID", "Tickers", "Risk", "Return", "Sharpe"]
    )
    st.dataframe(df_history, use_container_width=True)
else:
    st.info("No saved portfolios yet")