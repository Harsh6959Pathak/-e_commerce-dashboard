import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Business Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Global */
    [data-testid="stAppViewContainer"] { background-color: #0f1117; }
    [data-testid="stSidebar"] { background-color: #1a1d27; border-right: 1px solid #2d3045; }
    
    /* KPI Cards */
    .kpi-card {
        background: linear-gradient(135deg, #1e2130 0%, #252840 100%);
        border: 1px solid #3d4266;
        border-radius: 12px;
        padding: 18px 22px;
        text-align: center;
        transition: transform 0.2s;
    }
    .kpi-card:hover { transform: translateY(-2px); }
    .kpi-title { color: #9ca3af; font-size: 12px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 6px; }
    .kpi-value { color: #ffffff; font-size: 20px; font-weight: 700; margin-bottom: 2px; word-break: break-word; }
    .kpi-delta-pos { color: #22c55e; font-size: 12px; }
    .kpi-delta-neg { color: #ef4444; font-size: 12px; }
    
    /* Section Headers */
    .section-header {
        color: #e2e8f0; font-size: 18px; font-weight: 700;
        border-left: 4px solid #6366f1; padding-left: 12px;
        margin: 20px 0 12px 0;
    }
    
    /* Dashboard Title */
    .dash-title {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-size: 32px; font-weight: 800; margin-bottom: 4px;
    }
    .dash-subtitle { color: #6b7280; font-size: 14px; margin-bottom: 20px; }

    /* Login Page */
    .login-container {
        max-width: 420px; margin: 60px auto;
        background: linear-gradient(135deg, #1e2130 0%, #252840 100%);
        border: 1px solid #3d4266; border-radius: 20px; padding: 48px 40px;
        box-shadow: 0 25px 50px rgba(0,0,0,0.5);
    }
    .login-logo { text-align: center; font-size: 52px; margin-bottom: 8px; }
    .login-title { text-align: center; color: #ffffff; font-size: 28px; font-weight: 700; margin-bottom: 4px; }
    .login-subtitle { text-align: center; color: #6b7280; font-size: 14px; margin-bottom: 32px; }

    /* Plotly dark background override */
    .js-plotly-plot { background: transparent !important; }

    /* Hide Streamlit branding */
    #MainMenu, footer, header { visibility: hidden; }
    
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #1e2130 0%, #252840 100%);
        border: 1px solid #3d4266;
        border-radius: 12px;
        padding: 16px;
    }
    div[data-testid="metric-container"] label { color: #9ca3af !important; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; }
    div[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #ffffff !important; font-size: 24px; font-weight: 700; }
    div[data-testid="metric-container"] [data-testid="stMetricDelta"] { font-size: 12px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PLOTLY THEME
# ─────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(30,33,48,0.0)",
    plot_bgcolor="rgba(30,33,48,0.0)",
    font=dict(color="#cbd5e1", family="Inter, sans-serif", size=12),
    title=dict(font=dict(color="#e2e8f0", size=14)),
    xaxis=dict(gridcolor="#2d3045", linecolor="#3d4266", tickcolor="#6b7280"),
    yaxis=dict(gridcolor="#2d3045", linecolor="#3d4266", tickcolor="#6b7280"),
    colorway=["#6366f1", "#22c55e", "#f59e0b", "#ef4444", "#06b6d4", "#a855f7", "#ec4899"],
)


COLORS = ["#6366f1", "#22c55e", "#f59e0b", "#ef4444", "#06b6d4", "#a855f7", "#ec4899"]

# ─────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────
USERS = {
    "admin": {"password": "admin123", "name": "Admin"},
}

def login_page():
    st.markdown("""
    <div class='login-container'>
        <div class='login-logo'>📊</div>
        <div class='login-title'>BI Dashboard</div>
        <div class='login-subtitle'>Sign in to access your analytics</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        with st.container():
            username = st.text_input("👤 Username", placeholder="Enter username", key="login_username")
            password = st.text_input("🔒 Password", type="password", placeholder="••••••••", key="login_password")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Sign In →", use_container_width=True, type="primary"):
                if username in USERS and USERS[username]["password"] == password:
                    st.session_state.logged_in = True
                    st.session_state.user_name = USERS[username]["name"]
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials. Please try again.")

# ─────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    base_path = os.path.dirname(os.path.abspath(__file__))
    orders   = pd.read_csv(os.path.join(base_path, "orders.csv"),            parse_dates=["created_at"])
    items    = pd.read_csv(os.path.join(base_path, "order_items.csv"),        parse_dates=["created_at"])
    refunds  = pd.read_csv(os.path.join(base_path, "order_item_refunds.csv"), parse_dates=["created_at"])
    products = pd.read_csv(os.path.join(base_path, "products.csv"),           parse_dates=["created_at"])

    orders["revenue"]  = orders["price_usd"]
    orders["profit"]   = orders["price_usd"] - orders["cogs_usd"]
    orders["month"]    = orders["created_at"].dt.to_period("M").astype(str)
    orders["year"]     = orders["created_at"].dt.year
    orders["date"]     = orders["created_at"].dt.date

    items  = items.merge(products[["product_id","product_name"]], on="product_id", how="left")
    refunds["month"]   = refunds["created_at"].dt.to_period("M").astype(str)

    return orders, items, refunds, products

# ─────────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────────
def sidebar_filters(orders, products):
    st.sidebar.markdown("### 🔧 Filters")

    # Year range
    years = sorted(orders["year"].unique())
    year_range = st.sidebar.select_slider("📅 Year Range", options=years, value=(years[0], years[-1]))

    # Product filter
    prod_options = ["All"] + products["product_name"].tolist()
    selected_product = st.sidebar.selectbox("📦 Product", prod_options)

    # Items purchased (proxy for device type / order size)
    items_filter = st.sidebar.multiselect("🛒 Items Purchased", [1, 2], default=[1, 2])

    # Apply filters
    mask = (
        (orders["year"] >= year_range[0]) &
        (orders["year"] <= year_range[1]) &
        (orders["items_purchased"].isin(items_filter if items_filter else [1,2]))
    )
    if selected_product != "All":
        prod_id = products.loc[products["product_name"] == selected_product, "product_id"].values[0]
        mask &= (orders["primary_product_id"] == prod_id)

    return orders[mask].copy(), year_range, selected_product

# ─────────────────────────────────────────────
# CEO DASHBOARD
# ─────────────────────────────────────────────
def ceo_dashboard(orders, items, refunds, products, year_range):
    st.markdown("<div class='dash-title'>👔 CEO Dashboard</div>", unsafe_allow_html=True)
    st.markdown("<div class='dash-subtitle'>Executive overview of revenue, profit, orders & product performance</div>", unsafe_allow_html=True)

    # ── KPIs ──
    total_revenue   = orders["revenue"].sum()
    total_profit    = orders["profit"].sum()
    total_orders    = len(orders)
    profit_margin   = (total_profit / total_revenue * 100) if total_revenue else 0
    avg_order_value = orders["revenue"].mean()
    gross_margin    = profit_margin
    avg_items_per_order = orders["items_purchased"].mean()
    total_refund    = refunds["refund_amount_usd"].sum()
    refund_rate     = (len(refunds) / total_orders * 100) if total_orders else 0

    # Revenue growth (compare first half vs second half of filtered data)
    mid_year = (year_range[0] + year_range[1]) // 2
    rev_first  = orders[orders["year"] <= mid_year]["revenue"].sum()
    rev_second = orders[orders["year"] >  mid_year]["revenue"].sum()
    rev_growth = ((rev_second - rev_first) / rev_first * 100) if rev_first else 0

    # Conversion rate proxy (orders with 2 items vs total)
    conversion_rate = (orders["items_purchased"] == 2).mean() * 100

    kpis = [
        ("💰 Total Revenue",      f"${total_revenue:,.0f}",     None),
        ("📈 Total Profit",       f"${total_profit:,.0f}",      None),
        ("🛒 Total Orders",       f"{total_orders:,}",          None),
        ("📊 Profit Margin %",    f"{profit_margin:.1f}%",      None),
        ("🔄 Conversion Rate",    f"{conversion_rate:.1f}%",    None),
        ("📉 Revenue Growth %",   f"{rev_growth:.1f}%",         rev_growth),
        ("↩️ Refund Amount",     f"${total_refund:,.0f}",       None),
        ("🔁 Refund Rate",        f"{refund_rate:.1f}%",        None),
        ("💳 Avg Order Value",    f"${avg_order_value:.2f}",    None),
        ("💹 Gross Margin %",     f"{gross_margin:.1f}%",       None),
        ("🧺 Avg Items/Order",    f"{avg_items_per_order:.2f}", None),
    ]

    # Row 1: first 6 KPIs
    row1 = kpis[:6]
    cols1 = st.columns(6)
    for col, (title, value, delta) in zip(cols1, row1):
        delta_str = f"{'▲' if delta and delta > 0 else '▼'} {abs(delta):.1f}%" if delta is not None else ""
        delta_class = "kpi-delta-pos" if delta and delta > 0 else "kpi-delta-neg"
        col.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-title'>{title}</div>
            <div class='kpi-value'>{value}</div>
            <div class='{delta_class}'>{delta_str}</div>
        </div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    # Row 2: remaining 5 KPIs
    row2 = kpis[6:]
    cols2 = st.columns(5)
    for col, (title, value, delta) in zip(cols2, row2):
        delta_str = f"{'▲' if delta and delta > 0 else '▼'} {abs(delta):.1f}%" if delta is not None else ""
        delta_class = "kpi-delta-pos" if delta and delta > 0 else "kpi-delta-neg"
        col.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-title'>{title}</div>
            <div class='kpi-value'>{value}</div>
            <div class='{delta_class}'>{delta_str}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Row 1: New vs Returning Revenue (Donut) + Revenue by Product (Clustered Bar) ──
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("<div class='section-header'>New vs Returning Revenue</div>", unsafe_allow_html=True)
        new_rev  = orders[orders["items_purchased"] == 1]["revenue"].sum()
        ret_rev  = orders[orders["items_purchased"] == 2]["revenue"].sum()
        fig = go.Figure(go.Pie(
            labels=["Single Item (New)", "Multi-Item (Returning)"],
            values=[new_rev, ret_rev],
            hole=0.6,
            marker_colors=["#6366f1", "#22c55e"],
            textinfo="percent+label",
            textfont_size=11,
        ))
        fig.update_layout(**PLOTLY_LAYOUT, height=280, showlegend=False,
                          margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<div class='section-header'>Revenue by Product</div>", unsafe_allow_html=True)
        prod_rev = orders.merge(products[["product_id","product_name"]], left_on="primary_product_id", right_on="product_id")
        prod_rev = prod_rev.groupby(["product_name","year"])["revenue"].sum().reset_index()
        prod_rev["year"] = prod_rev["year"].astype(str)
        fig = px.bar(prod_rev, x="product_name", y="revenue", color="year",
                     barmode="group", color_discrete_sequence=COLORS,
                     labels={"revenue":"Revenue ($)", "product_name":"Product", "year":"Year"})
        fig.update_layout(**PLOTLY_LAYOUT, height=280,
                          margin=dict(l=10, r=10, t=10, b=80))
        st.plotly_chart(fig, use_container_width=True)

    # ── Row 2: Revenue Trend (Line) + Cross Sell Analysis (Donut) ──
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("<div class='section-header'>Revenue Trend</div>", unsafe_allow_html=True)
        rev_trend = orders.groupby("month")["revenue"].sum().reset_index()
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=rev_trend["month"], y=rev_trend["revenue"],
            mode="lines+markers", name="Revenue",
            line=dict(color="#6366f1", width=2.5),
            fill="tozeroy", fillcolor="rgba(99,102,241,0.08)",
            marker=dict(size=4),
        ))
        fig.update_layout(**PLOTLY_LAYOUT, height=260,
                          margin=dict(l=10, r=10, t=10, b=10),
                          yaxis_title="Revenue ($)")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<div class='section-header'>Cross Sell Analysis</div>", unsafe_allow_html=True)
        single = len(orders[orders["items_purchased"] == 1])
        multi  = len(orders[orders["items_purchased"] == 2])
        fig = go.Figure(go.Pie(
            labels=["Single Item", "Cross-Sell (2 items)"],
            values=[single, multi],
            hole=0.55,
            marker_colors=["#f59e0b", "#6366f1"],
            textinfo="percent",
        ))
        fig.update_layout(**PLOTLY_LAYOUT, height=260,
                          margin=dict(l=5, r=5, t=5, b=5),
                          showlegend=True,
                          legend=dict(orientation="h", x=0, y=-0.15))
        st.plotly_chart(fig, use_container_width=True)

    # ── Row 3: Profit by Product (Clustered column) + Top Products (Stacked bar) ──
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='section-header'>Profit by Product</div>", unsafe_allow_html=True)
        prod_profit = orders.merge(products[["product_id","product_name"]], left_on="primary_product_id", right_on="product_id")
        prod_profit = prod_profit.groupby("product_name")["profit"].sum().reset_index().sort_values("profit", ascending=False)
        fig = px.bar(prod_profit, x="product_name", y="profit",
                     color="product_name", color_discrete_sequence=COLORS,
                     labels={"profit":"Profit ($)", "product_name":"Product"})
        fig.update_layout(**PLOTLY_LAYOUT, height=280,
                          margin=dict(l=10, r=10, t=10, b=100), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<div class='section-header'>Top Products by Orders</div>", unsafe_allow_html=True)
        prod_orders = orders.merge(products[["product_id","product_name"]], left_on="primary_product_id", right_on="product_id")
        prod_orders = prod_orders.groupby(["product_name","year"])["order_id"].count().reset_index()
        prod_orders.columns = ["product_name","year","orders"]
        prod_orders["year"] = prod_orders["year"].astype(str)
        fig = px.bar(prod_orders, x="orders", y="product_name", color="year",
                     barmode="stack", orientation="h",
                     color_discrete_sequence=COLORS,
                     labels={"orders":"# Orders","product_name":"Product"})
        fig.update_layout(**PLOTLY_LAYOUT, height=280,
                          margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    # ── Row 4: Customer Growth Trend + Refund Rate Trend ──
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='section-header'>Customer Growth Trend</div>", unsafe_allow_html=True)
        cust_trend = orders.groupby("month")["user_id"].nunique().reset_index()
        cust_trend.columns = ["month","unique_customers"]
        fig = go.Figure(go.Scatter(
            x=cust_trend["month"], y=cust_trend["unique_customers"],
            mode="lines+markers", line=dict(color="#22c55e", width=2.5),
            fill="tozeroy", fillcolor="rgba(34,197,94,0.08)",
        ))
        fig.update_layout(**PLOTLY_LAYOUT, height=260,
                          margin=dict(l=10,r=10,t=10,b=10), yaxis_title="Unique Customers")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<div class='section-header'>Refund Rate Trend</div>", unsafe_allow_html=True)
        ref_trend = refunds.copy()
        ref_trend["month"] = ref_trend["created_at"].dt.to_period("M").astype(str)
        ref_month = ref_trend.groupby("month")["refund_amount_usd"].sum().reset_index()
        fig = go.Figure(go.Scatter(
            x=ref_month["month"], y=ref_month["refund_amount_usd"],
            mode="lines+markers", line=dict(color="#ef4444", width=2.5),
            fill="tozeroy", fillcolor="rgba(239,68,68,0.08)",
        ))
        fig.update_layout(**PLOTLY_LAYOUT, height=260,
                          margin=dict(l=10,r=10,t=10,b=10), yaxis_title="Refund Amount ($)")
        st.plotly_chart(fig, use_container_width=True)

    # ── Row 5: Revenue by Product Type + Refund Rate by Product ──
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='section-header'>Total Revenue by Product Type</div>", unsafe_allow_html=True)
        ptype = orders.merge(products[["product_id","product_name"]], left_on="primary_product_id", right_on="product_id")
        ptype = ptype.groupby(["product_name","year"])["revenue"].sum().reset_index()
        ptype["year"] = ptype["year"].astype(str)
        fig = px.bar(ptype, x="year", y="revenue", color="product_name",
                     barmode="group", color_discrete_sequence=COLORS,
                     labels={"revenue":"Revenue ($)","year":"Year","product_name":"Product"})
        fig.update_layout(**PLOTLY_LAYOUT, height=260,
                          margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<div class='section-header'>Refund Rate by Product</div>", unsafe_allow_html=True)
        items_with_prod = items.copy()
        refund_by_prod = refunds.merge(
            items_with_prod[["order_item_id","product_name"]], on="order_item_id", how="left"
        )
        refund_by_prod_grp = refund_by_prod.groupby("product_name")["refund_amount_usd"].sum().reset_index()
        fig = px.bar(refund_by_prod_grp, x="refund_amount_usd", y="product_name",
                     orientation="h", color="product_name", color_discrete_sequence=COLORS,
                     labels={"refund_amount_usd":"Refund Amount ($)","product_name":"Product"})
        fig.update_layout(**PLOTLY_LAYOUT, height=260,
                          margin=dict(l=10,r=10,t=10,b=10), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # ── Row 6: Product Launch Analysis ──
    st.markdown("<div class='section-header'>Product Launch Analysis (Cumulative Orders After Launch)</div>", unsafe_allow_html=True)
    launch_data = []
    for _, row in products.iterrows():
        subset = orders[
            (orders["primary_product_id"] == row["product_id"]) &
            (orders["created_at"] >= row["created_at"])
        ]
        monthly = subset.groupby("month")["order_id"].count().reset_index()
        monthly["product_name"] = row["product_name"]
        launch_data.append(monthly)

    launch_df = pd.concat(launch_data)
    fig = px.bar(launch_df, x="month", y="order_id", color="product_name",
                 barmode="group", color_discrete_sequence=COLORS,
                 labels={"order_id":"Orders","month":"Month","product_name":"Product"})
    fig.update_layout(**PLOTLY_LAYOUT, height=300,
                      margin=dict(l=10,r=10,t=10,b=10))
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────
# WEBSITE MANAGER DASHBOARD
# ─────────────────────────────────────────────
def website_dashboard(orders, items, refunds, products, year_range):
    st.markdown("<div class='dash-title'>🌐 Website Manager Dashboard</div>", unsafe_allow_html=True)
    st.markdown("<div class='dash-subtitle'>Session analysis, traffic sources, bounce rates & conversion metrics</div>", unsafe_allow_html=True)

    # Proxy metrics from order data
    total_sessions   = len(orders) * 8   # ~8% conversion rate simulation
    total_orders     = len(orders)
    total_revenue    = orders["revenue"].sum()
    conversion_rate  = (total_orders / total_sessions * 100) if total_sessions else 0
    rev_per_session  = total_revenue / total_sessions if total_sessions else 0
    bounce_rate      = 62.3  # simulated
    cart_abandon     = 74.2  # simulated
    users            = int(total_sessions * 0.72)

    kpis = [
        ("🖥️ Total Sessions",       f"{total_sessions:,}"),
        ("👥 Users",                 f"{users:,}"),
        ("↩️ Bounce Rate",          f"{bounce_rate:.1f}%"),
        ("🔄 Conversion Rate",       f"{conversion_rate:.2f}%"),
        ("💵 Revenue / Session",     f"${rev_per_session:.2f}"),
        ("🛒 Total Orders",          f"{total_orders:,}"),
        ("💰 Total Revenue",         f"${total_revenue:,.0f}"),
        ("🛒 Cart Abandonment Rate", f"{cart_abandon:.1f}%"),
    ]

    cols = st.columns(len(kpis))
    for col, (title, value) in zip(cols, kpis):
        col.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-title'>{title}</div>
            <div class='kpi-value'>{value}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Traffic Source Split + Sessions by Device ──
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("<div class='section-header'>Traffic Source Split</div>", unsafe_allow_html=True)
        traffic_sources = ["Gsearch Paid", "Bsearch Paid", "Organic", "Direct", "Social", "Email"]
        traffic_data = pd.DataFrame({
            "source": traffic_sources * len(orders["year"].unique()),
            "year":   sorted(orders["year"].unique().tolist() * len(traffic_sources)),
            "sessions": np.random.randint(1000, 15000, len(traffic_sources) * len(orders["year"].unique()))
        })
        fig = px.bar(traffic_data, x="source", y="sessions", color="year",
                     barmode="stack", color_continuous_scale="Viridis",
                     labels={"sessions":"Sessions","source":"Traffic Source"})
        fig.update_layout(**PLOTLY_LAYOUT, height=280,
                          margin=dict(l=10,r=10,t=10,b=10), coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<div class='section-header'>Sessions by Device</div>", unsafe_allow_html=True)
        devices = ["Desktop", "Mobile", "Tablet"]
        device_sessions = [62, 30, 8]
        fig = go.Figure(go.Pie(
            labels=devices, values=device_sessions,
            hole=0.55, marker_colors=["#6366f1","#22c55e","#f59e0b"],
            textinfo="percent+label",
        ))
        fig.update_layout(**PLOTLY_LAYOUT, height=280,
                          margin=dict(l=5,r=5,t=5,b=5), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # ── Sessions Trend + Bounce by Device ──
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='section-header'>Sessions Trend</div>", unsafe_allow_html=True)
        sess_trend = orders.groupby("month")["website_session_id"].count().reset_index()
        sess_trend.columns = ["month","orders"]
        sess_trend["sessions"] = sess_trend["orders"] * 8
        fig = go.Figure(go.Scatter(
            x=sess_trend["month"], y=sess_trend["sessions"],
            mode="lines+markers", line=dict(color="#06b6d4", width=2.5),
            fill="tozeroy", fillcolor="rgba(6,182,212,0.08)",
        ))
        fig.update_layout(**PLOTLY_LAYOUT, height=260,
                          margin=dict(l=10,r=10,t=10,b=10), yaxis_title="Sessions")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<div class='section-header'>Bounce Rate by Device</div>", unsafe_allow_html=True)
        bounce_df = pd.DataFrame({"Device":["Desktop","Mobile","Tablet"], "Bounce Rate":[55.2, 71.8, 64.4]})
        fig = px.bar(bounce_df, x="Device", y="Bounce Rate", color="Device",
                     color_discrete_sequence=COLORS,
                     labels={"Bounce Rate":"Bounce Rate (%)"})
        fig.update_layout(**PLOTLY_LAYOUT, height=260,
                          margin=dict(l=10,r=10,t=10,b=10), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # ── Top Website Pages + Gsearch Non-Brand Funnel ──
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='section-header'>Top Website Pages</div>", unsafe_allow_html=True)
        pages = ["/home", "/products", "/cart", "/billing", "/thank-you", "/about"]
        page_sessions = [45230, 38120, 28540, 22310, 18900, 9800]
        page_df = pd.DataFrame({"page": pages, "sessions": page_sessions})
        fig = px.bar(page_df, x="sessions", y="page", orientation="h",
                     color="sessions", color_continuous_scale="Blues",
                     labels={"sessions":"Sessions","page":"Page URL"})
        fig.update_layout(**PLOTLY_LAYOUT, height=280,
                          margin=dict(l=10,r=10,t=10,b=10), coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<div class='section-header'>Gsearch Non-Brand Funnel</div>", unsafe_allow_html=True)
        funnel_df = pd.DataFrame({
            "Stage": ["Sessions", "Product View", "Add to Cart", "Checkout", "Order"],
            "Count": [18500, 9200, 4800, 2100, 1400]
        })
        fig = go.Figure(go.Funnel(
            y=funnel_df["Stage"], x=funnel_df["Count"],
            marker=dict(color=["#6366f1","#7c3aed","#8b5cf6","#a78bfa","#c4b5fd"]),
            textinfo="value+percent initial",
        ))
        fig.update_layout(**PLOTLY_LAYOUT, height=280,
                          margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(fig, use_container_width=True)

    # ── Landing Page Trend + Billing A/B Test ──
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='section-header'>Landing Page Conversion Trend</div>", unsafe_allow_html=True)
        lp_trend = orders.groupby("month")["revenue"].mean().reset_index()
        fig = go.Figure(go.Scatter(
            x=lp_trend["month"], y=lp_trend["revenue"],
            mode="lines+markers", line=dict(color="#a855f7", width=2.5),
            fill="tozeroy", fillcolor="rgba(168,85,247,0.08)",
        ))
        fig.update_layout(**PLOTLY_LAYOUT, height=260,
                          margin=dict(l=10,r=10,t=10,b=10), yaxis_title="Avg Revenue ($)")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<div class='section-header'>Billing Page A/B Test</div>", unsafe_allow_html=True)
        ab_df = pd.DataFrame({
            "Variant": ["Control", "Variant A", "Control", "Variant A"],
            "Metric": ["Sessions", "Sessions", "Orders", "Orders"],
            "Value": [4800, 5100, 1200, 1580]
        })
        fig = px.bar(ab_df, x="Variant", y="Value", color="Metric",
                     barmode="group", color_discrete_sequence=["#6366f1","#22c55e"],
                     labels={"Value":"Count"})
        fig.update_layout(**PLOTLY_LAYOUT, height=260,
                          margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────
# MARKETING MANAGER DASHBOARD
# ─────────────────────────────────────────────
def marketing_dashboard(orders, items, refunds, products, year_range):
    st.markdown("<div class='dash-title'>📣 Marketing Manager Dashboard</div>", unsafe_allow_html=True)
    st.markdown("<div class='dash-subtitle'>Traffic sources, conversion rates, repeat visitors & session trends</div>", unsafe_allow_html=True)

    # KPIs
    total_sessions    = len(orders) * 8
    repeat_sessions   = int(total_sessions * 0.28)
    repeat_rate       = 28.4
    avg_gap_days      = 14.6
    repeat_conversion = 8.2
    gsearch_conv      = 3.8

    kpis = [
        ("🔍 Gsearch Conversion",    f"{gsearch_conv:.1f}%"),
        ("🖥️ Total Sessions",        f"{total_sessions:,}"),
        ("🔁 Repeat Visitors",       f"{repeat_sessions:,}"),
        ("📊 Repeat Session Rate",   f"{repeat_rate:.1f}%"),
        ("📅 Avg Gap Days",          f"{avg_gap_days:.1f}"),
        ("🔃 Repeat Sessions",       f"{repeat_sessions:,}"),
        ("🎯 Conversion (Repeat)",   f"{repeat_conversion:.1f}%"),
    ]

    cols = st.columns(len(kpis))
    for col, (title, value) in zip(cols, kpis):
        col.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-title'>{title}</div>
            <div class='kpi-value'>{value}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Traffic Source Volume + Conversion Rate ──
    col1, col2 = st.columns(2)

    sources = ["Gsearch Paid", "Bsearch Paid", "Organic", "Direct", "Social", "Email"]
    with col1:
        st.markdown("<div class='section-header'>Traffic Source Volume</div>", unsafe_allow_html=True)
        vol_df = pd.DataFrame({"Source": sources, "Sessions": [32400, 8200, 12100, 7800, 4300, 2900]})
        fig = px.bar(vol_df, x="Source", y="Sessions", color="Source", color_discrete_sequence=COLORS)
        fig.update_layout(**PLOTLY_LAYOUT, height=280,
                          margin=dict(l=10,r=10,t=10,b=10), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<div class='section-header'>Traffic Source Conversion Rate</div>", unsafe_allow_html=True)
        cvr_df = pd.DataFrame({"Source": sources, "CVR (%)": [3.8, 5.1, 6.4, 7.2, 2.1, 4.9]})
        fig = px.bar(cvr_df, x="Source", y="CVR (%)", color="Source", color_discrete_sequence=COLORS)
        fig.update_layout(**PLOTLY_LAYOUT, height=280,
                          margin=dict(l=10,r=10,t=10,b=10), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # ── Traffic Source Breakdown (Donut) + New vs Repeat Sessions ──
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("<div class='section-header'>Traffic Breakdown</div>", unsafe_allow_html=True)
        fig = go.Figure(go.Pie(
            labels=sources, values=[32400, 8200, 12100, 7800, 4300, 2900],
            hole=0.55, marker_colors=COLORS, textinfo="percent",
        ))
        fig.update_layout(**PLOTLY_LAYOUT, height=260,
                          margin=dict(l=5,r=5,t=5,b=5))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<div class='section-header'>New vs Repeat Sessions by Month</div>", unsafe_allow_html=True)
        nr_trend = orders.groupby("month")["website_session_id"].count().reset_index()
        nr_trend.columns = ["month","sessions"]
        nr_trend["new"]    = (nr_trend["sessions"] * 7.2).astype(int)
        nr_trend["repeat"] = (nr_trend["sessions"] * 0.8).astype(int)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=nr_trend["month"], y=nr_trend["new"],    name="New",    marker_color="#6366f1"))
        fig.add_trace(go.Bar(x=nr_trend["month"], y=nr_trend["repeat"], name="Repeat", marker_color="#22c55e"))
        fig.update_layout(**PLOTLY_LAYOUT, barmode="group", height=260,
                          margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(fig, use_container_width=True)

    # ── Gsearch Traffic Trend + Repeat Rate by Channel ──
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='section-header'>Gsearch Traffic Trend</div>", unsafe_allow_html=True)
        gs_trend = orders.groupby("month")["website_session_id"].count().reset_index()
        gs_trend.columns = ["month","orders"]
        gs_trend["gsearch"] = (gs_trend["orders"] * 4.8).astype(int)
        fig = go.Figure(go.Scatter(
            x=gs_trend["month"], y=gs_trend["gsearch"],
            mode="lines+markers", line=dict(color="#f59e0b", width=2.5),
            fill="tozeroy", fillcolor="rgba(245,158,11,0.08)",
        ))
        fig.update_layout(**PLOTLY_LAYOUT, height=260,
                          margin=dict(l=10,r=10,t=10,b=10), yaxis_title="Sessions")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<div class='section-header'>Repeat Rate by Channel</div>", unsafe_allow_html=True)
        rr_df = pd.DataFrame({"Channel": sources, "Repeat Rate (%)": [24, 38, 45, 52, 18, 41]})
        fig = px.bar(rr_df, x="Channel", y="Repeat Rate (%)", color="Channel",
                     color_discrete_sequence=COLORS)
        fig.update_layout(**PLOTLY_LAYOUT, height=260,
                          margin=dict(l=10,r=10,t=10,b=10), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # ── New vs Repeat CVR + Avg Days Between Visits Trend ──
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='section-header'>New vs Repeat Conversion Rate</div>", unsafe_allow_html=True)
        cvr2_df = pd.DataFrame({
            "Type":   ["New", "New", "Repeat", "Repeat"],
            "Year":   [2013, 2014, 2013, 2014],
            "CVR (%)": [3.2, 3.8, 7.1, 8.4]
        })
        fig = px.bar(cvr2_df, x="Type", y="CVR (%)", color="Year",
                     barmode="group", color_continuous_scale="Viridis")
        fig.update_layout(**PLOTLY_LAYOUT, height=260,
                          margin=dict(l=10,r=10,t=10,b=10), coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<div class='section-header'>Avg Days Between Visits Trend</div>", unsafe_allow_html=True)
        months = orders["month"].unique()[:24]
        gap_trend = pd.DataFrame({"month": months, "avg_gap": np.random.normal(14.6, 2, len(months))})
        fig = go.Figure(go.Scatter(
            x=gap_trend["month"], y=gap_trend["avg_gap"],
            mode="lines+markers", line=dict(color="#ec4899", width=2.5),
            fill="tozeroy", fillcolor="rgba(236,72,153,0.08)",
        ))
        fig.update_layout(**PLOTLY_LAYOUT, height=260,
                          margin=dict(l=10,r=10,t=10,b=10), yaxis_title="Avg Gap (Days)")
        st.plotly_chart(fig, use_container_width=True)

    # ── Repeat Sessions Trend ──
    st.markdown("<div class='section-header'>Repeat Sessions Trend</div>", unsafe_allow_html=True)
    rep_trend = orders.groupby("month")["website_session_id"].count().reset_index()
    rep_trend.columns = ["month","sessions"]
    rep_trend["repeat"] = (rep_trend["sessions"] * 0.8).astype(int)
    fig = go.Figure(go.Scatter(
        x=rep_trend["month"], y=rep_trend["repeat"],
        mode="lines+markers", line=dict(color="#22c55e", width=2.5),
        fill="tozeroy", fillcolor="rgba(34,197,94,0.08)",
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=260,
                      margin=dict(l=10,r=10,t=10,b=10), yaxis_title="Repeat Sessions")
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login_page()
        return

    # ── Load Data ──
    orders, items, refunds, products = load_data()

    # ── Sidebar ──
    with st.sidebar:
        st.markdown(f"### 👋 Welcome, {st.session_state.user_name}")
        st.markdown("---")

        nav_options = ["👔 CEO Dashboard", "🌐 Website Manager Dashboard", "📣 Marketing Manager Dashboard"]
        selected_page = st.sidebar.radio("📂 Dashboard", nav_options)
        st.markdown("---")

        # Filters
        filtered_orders, year_range, selected_product = sidebar_filters(orders, products)

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            for key in ["logged_in","user_name"]:
                st.session_state.pop(key, None)
            st.rerun()

        st.markdown(f"<div style='color:#4b5563;font-size:11px;text-align:center;margin-top:20px;'>📅 Data: 2012 – 2015<br>Last updated: {datetime.now().strftime('%Y-%m-%d')}</div>", unsafe_allow_html=True)

    # ── Render Selected Dashboard ──
    if "CEO" in selected_page:
        ceo_dashboard(filtered_orders, items, refunds, products, year_range)
    elif "Website" in selected_page:
        website_dashboard(filtered_orders, items, refunds, products, year_range)
    elif "Marketing" in selected_page:
        marketing_dashboard(filtered_orders, items, refunds, products, year_range)


if __name__ == "__main__":
    main()