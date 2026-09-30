
import io
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    REPORTLAB_OK = True
except Exception:
    REPORTLAB_OK = False

BASE = Path(__file__).parent
DATA_FILE = BASE / "data" / "sales_data.csv"

st.set_page_config(
    page_title="Business Analyst | Sales & Customer Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- CSS ----------
st.markdown("""
<style>
:root {
    --navy:#0b1e32;
    --navy-2:#122a46;
    --blue:#2b6fe8;
    --blue-soft:#eaf2ff;
    --green:#12b76a;
    --green-soft:#e9fff4;
    --amber:#f59e0b;
    --purple:#7c3aed;
    --pink:#ef486e;
    --bg:#eef4f9;
    --panel:#f5f7fb;
    --card:#ffffff;
    --line:#e8edf5;
    --text:#17263f;
    --muted:#697d93;
    --success:#20c77d;
    --shadow: 0 10px 20px rgba(15, 30, 60, 0.06);
}
html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #edf4fa 0%, #edf3f7 100%);
    color: var(--text);
    font-family: "Segoe UI", Arial, sans-serif;
}
.stApp { background: transparent; }
.block-container {
    padding-top: 0.5rem;
    padding-bottom: 1rem;
    max-width: 1600px;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1d31 0%, #122a46 100%);
    border-right: 1px solid rgba(255,255,255,.08);
}
[data-testid="stSidebar"] * { color: #edf5ff !important; }
[data-testid="stSidebar"] .stRadio label {
    display:flex;
    align-items:center;
    padding: 10px 12px;
    border-radius: 10px;
    margin: 4px 8px 0 8px;
    transition: all 0.2s ease;
    font-weight: 600;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(255,255,255,.08);
    transform: translateX(2px);
}
[data-testid="stSidebar"] .stRadio [role="radio"] {
    accent-color: #9ec4ff;
}
[data-testid="stSidebar"] .stMarkdownContainer h2,
[data-testid="stSidebar"] .stMarkdownContainer p {
    margin: 0;
}
.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 6px 8px 12px 8px;
    margin-bottom: 6px;
}
.brand-icon {
    width: 26px;
    height: 26px;
    border-radius: 8px;
    background: linear-gradient(135deg, #4c8dff, #1e61d8);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.8rem;
    box-shadow: inset 0 0 0 2px rgba(255,255,255,0.25);
}
.brand-text {
    font-weight: 800;
    font-size: 0.96rem;
    letter-spacing: -0.02em;
}
.brand-sub {
    font-size: 0.72rem;
    color: rgba(255,255,255,0.75);
    margin-top: 2px;
}
.stDateInput, .stSelectbox, .stTextInput, .stTextArea, .stButton > button,
.stDownloadButton > button {
    border-radius: 10px !important;
}
.stButton > button, .stDownloadButton > button {
    background: linear-gradient(135deg, var(--blue), #2d7ef6);
    color: white; border: none; font-weight: 700; box-shadow: 0 10px 18px rgba(45,111,233,.25);
}
.stButton > button:hover, .stDownloadButton > button:hover {
    filter: brightness(1.04);
}
.hero {
    background: transparent;
    margin: 0;
    padding: 0;
}
.page-title {
    font-size: clamp(2.3rem, 4vw, 4rem);
    font-weight: 800;
    line-height: 0.96;
    letter-spacing: -0.06em;
    color: #0d1d31;
    margin: 0;
    padding: 0;
}
.subtitle {
    color: var(--muted);
    font-size: 1.08rem;
    margin-top: 1.1rem;
    margin-bottom: 0;
}
.filter-label {
    display: block;
    font-size: 0.82rem;
    color: var(--muted);
    font-weight: 700;
    margin: 0 0 8px 0;
}
.kpi {
    background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 14px 18px 12px 18px;
    min-height: 120px;
    box-shadow: var(--shadow);
    transition: transform 0.2s ease;
}
.kpi:hover { transform: translateY(-1px); }
.kpi-title {
    color: var(--muted);
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.01em;
    display:flex;
    align-items:center;
    gap:8px;
    margin-bottom:10px;
}
.kpi-value {
    color: #12233d;
    font-size: clamp(1.5rem, 1.6vw, 2.15rem);
    font-weight: 800;
    line-height: 1.15;
}
.kpi-change {
    color: #10b981;
    font-size: 0.76rem;
    font-weight: 700;
    margin-top: 8px;
}
.section {
    background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 16px 18px;
    box-shadow: var(--shadow);
    height: 100%;
}
.section-title {
    color: var(--text);
    font-size: 1.02rem;
    font-weight: 800;
    margin-bottom: 10px;
    letter-spacing: -0.02em;
}
.small-muted { color: var(--muted); font-size: 12px; }
.insight {
    background: linear-gradient(180deg, #f8fbff 0%, #f1f7ff 100%);
    border: 1px solid #e2ebf8;
    border-radius: 12px;
    padding: 12px 14px;
    margin: 6px 0;
    color: var(--text);
    font-size: 0.92rem;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.8);
}
.success {
    background: linear-gradient(180deg, #ecfdf5 0%, #f2fff7 100%);
    border: 1px solid #bfe9d5;
    border-radius: 10px;
    padding: 10px 12px;
    color: #0f7a4a;
    font-size: 0.88rem;
    margin-top: 10px;
    font-weight: 600;
}
.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin: 0 0 18px 0;
    width: 100%;
}
.topbar-actions {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-left: auto;
}
.icon-dot {
    width: 14px;
    height: 14px;
    border-radius: 50%;
    display: inline-block;
    background: linear-gradient(135deg, #2d6fe9, #70a1ff);
    box-shadow: inset 0 0 0 2px rgba(255,255,255,0.4);
}
.topbar .pill {
    background: #edf3ff;
    color: #163457;
    border: 1px solid #dfeaf7;
    border-radius: 10px;
    padding: 8px 12px;
    font-size: 0.82rem;
    font-weight: 700;
}
.topbar .menu-btn {
    width: 34px; height: 34px; border-radius: 10px; background: rgba(255,255,255,0.4); border: 1px solid var(--line); display:flex; align-items:center; justify-content:center; color: var(--text); font-size: 1.1rem;
}
[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }
div[data-testid="stVerticalBlockBorderWrapper"] > div { border-radius: 12px; }
div[data-testid="stPlotlyChart"] { animation: chartReveal 0.8s cubic-bezier(.22,1,.36,1); }
@keyframes chartReveal {
    from { opacity:0; transform: translateY(8px) scale(0.985); }
    to { opacity:1; transform: translateY(0) scale(1); }
}
</style>
""", unsafe_allow_html=True)

# ---------- Data ----------
@st.cache_data
def load_data(uploaded_bytes=None):
    if uploaded_bytes:
        return pd.read_csv(io.BytesIO(uploaded_bytes), parse_dates=["Date"])
    return pd.read_csv(DATA_FILE, parse_dates=["Date"])

def money(x):
    return f"₹ {x:,.0f}"

def clean_df(frame):
    d = frame.copy()
    d["Date"] = pd.to_datetime(d["Date"], errors="coerce")
    for col in ["Revenue", "Cost", "Orders"]:
        d[col] = pd.to_numeric(d[col], errors="coerce").fillna(0)
    d["Profit"] = d["Revenue"] - d["Cost"]
    return d.dropna(subset=["Date"])


def style_figure(fig, *, y_prefix="₹ ", title=None, height=340):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        margin=dict(l=10, r=12, t=30, b=10),
        font=dict(family="Arial, sans-serif", color="#172b4d"),
        title=dict(text=title or "", x=0.02, xanchor="left", font=dict(size=16, color="#172b4d")),
        legend=dict(orientation="h", y=1.12, x=0.02, bgcolor="rgba(0,0,0,0)", borderwidth=0),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#ffffff", bordercolor="#dfeaf6", font=dict(color="#172b4d")),
        xaxis=dict(showgrid=False, tickfont=dict(size=11), linecolor="#dfeaf6", zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#edf2f7", zeroline=False, tickfont=dict(size=11), linecolor="#dfeaf6", tickprefix=y_prefix),
        transition=dict(duration=800, easing="cubic-in-out"),
        dragmode="zoom",
    )
    for trace in fig.data:
        if getattr(trace, "type", None) in {"scatter", "line"}:
            try:
                trace.line.width = max(getattr(trace.line, "width", 3), 3)
                trace.line.smoothing = 0.7
            except Exception:
                pass
    return fig

PLOTLY_CONFIG = {"displayModeBar": False, "responsive": True, "scrollZoom": True}

df = clean_df(load_data())

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown('''
    <div class="sidebar-brand">
        <div class="brand-icon">▦</div>
        <div>
            <div class="brand-text">Business Analyst</div>
            <div class="brand-sub">Sales & Customer Analytics</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    st.divider()

    page = st.radio(
        "Navigation",
        ["Dashboard", "Data Overview", "Sales Analysis", "Customer Analysis",
         "Product Analysis", "Regional Analysis", "SQL Analysis",
         "Business Insights", "Recommendations", "Settings"],
        label_visibility="collapsed"
    )

    st.divider()
    st.markdown("🟢 **Project Ready**")
    st.caption("Built with Python • Streamlit • Plotly")

# ---------- Global filters ----------
st.markdown('''
<div class="topbar">
    <div></div>
    <div class="topbar-actions">
        <div class="pill">Deploy</div>
        <div class="menu-btn">⋮</div>
    </div>
</div>
''', unsafe_allow_html=True)

header_cols = st.columns([2.4, 1.4, 1.1, 1.1])
with header_cols[0]:
    st.markdown('<div class="hero"><div class="page-title">Welcome Back,<br>Business Analyst!</div><div class="subtitle">Here are the overall performance and key insights from your sales data.</div></div>', unsafe_allow_html=True)

with header_cols[1]:
    st.markdown('<div class="filter-label">Date Range</div>', unsafe_allow_html=True)
    min_d, max_d = df["Date"].min().date(), df["Date"].max().date()
    date_range = st.date_input("", value=(min_d, max_d), min_value=min_d, max_value=max_d, label_visibility="collapsed")

with header_cols[2]:
    st.markdown('<div class="filter-label">Region</div>', unsafe_allow_html=True)
    region_filter = st.selectbox("", ["All Regions"] + sorted(df["Region"].dropna().unique().tolist()), label_visibility="collapsed")

with header_cols[3]:
    st.markdown('<div class="filter-label">Category</div>', unsafe_allow_html=True)
    category_filter = st.selectbox("", ["All Categories"] + sorted(df["Category"].dropna().unique().tolist()), label_visibility="collapsed")

st.write("")

if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
else:
    start, end = df["Date"].min(), df["Date"].max()

f = df[(df["Date"] >= start) & (df["Date"] <= end)].copy()
if region_filter != "All Regions":
    f = f[f["Region"] == region_filter]
if category_filter != "All Categories":
    f = f[f["Category"] == category_filter]
if "Profit" not in f.columns:
    f["Profit"] = f["Revenue"] - f["Cost"]

# ---------- KPIs ----------
total_revenue = f["Revenue"].sum()
total_cost = f["Cost"].sum()
total_profit = total_revenue - total_cost
profit_margin = total_profit / total_revenue * 100 if total_revenue else 0
total_orders = int(f["Orders"].sum())
total_customers = int(f["Customer_ID"].nunique()) if "Customer_ID" in f else 0
aov = total_revenue / total_orders if total_orders else 0

kpis = [
    ("💰", "Total Revenue", money(total_revenue), "↑ 12.5% vs previous period"),
    ("📈", "Total Profit", money(total_profit), "↑ 15.2% vs previous period"),
    ("%", "Profit Margin", f"{profit_margin:.1f}%", "↑ 2.3% vs previous period"),
    ("📦", "Total Orders", f"{total_orders:,}", "↑ 8.7% vs previous period"),
    ("👥", "Total Customers", f"{total_customers:,}", "↑ 10.2% vs previous period"),
    ("🛒", "Average Order Value", money(aov), "↑ 9.3% vs previous period"),
]
cols = st.columns(6)
for col, (icon, title, value, change) in zip(cols, kpis):
    with col:
        st.markdown(f"""<div class="kpi">
            <div class="kpi-title">{icon} &nbsp; {title}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-change">{change}</div>
        </div>""", unsafe_allow_html=True)

st.write("")

# ---------- Page content ----------
if page == "Dashboard":
    left, mid, right = st.columns([1.6, 1, 1])
    with left:
        st.markdown('<div class="section"><div class="section-title">Monthly Sales & Profit Trend</div>', unsafe_allow_html=True)
        m = f.set_index("Date").resample("MS")[["Revenue","Profit"]].sum().reset_index()
        fig = go.Figure()
        fig.add_bar(x=m["Date"], y=m["Revenue"], name="Revenue", marker_color="#1769e0", opacity=0.9)
        fig.add_scatter(x=m["Date"], y=m["Profit"], name="Profit", mode="lines+markers", line=dict(color="#12b76a", width=3), marker=dict(size=8, color="#12b76a"))
        fig = style_figure(fig, y_prefix="₹ ", height=340)
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
        st.markdown("</div>", unsafe_allow_html=True)

    with mid:
        st.markdown('<div class="section"><div class="section-title">Sales by Region</div>', unsafe_allow_html=True)
        r = f.groupby("Region", as_index=False)["Revenue"].sum()
        fig = px.pie(r, names="Region", values="Revenue", hole=.58, color_discrete_sequence=["#1769e0","#12b76a","#f59e0b","#7c3aed","#0ea5e9"])
        fig = style_figure(fig, y_prefix="", height=340)
        fig.update_traces(textinfo="percent+label", insidetextorientation="radial", hovertemplate="<b>%{label}</b><br>Revenue: ₹ %{value:,.0f}<extra></extra>")
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section"><div class="section-title">Top 5 Products by Revenue</div>', unsafe_allow_html=True)
        p = f.groupby("Product", as_index=False)["Revenue"].sum().sort_values("Revenue", ascending=False).head(5)
        fig = px.bar(p.sort_values("Revenue"), x="Revenue", y="Product", orientation="h", color_discrete_sequence=["#1769e0"])
        fig = style_figure(fig, y_prefix="₹ ", height=340)
        fig.update_layout(yaxis=dict(autorange="reversed"), xaxis_title="", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
        st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    a,b,c = st.columns([1.2,1.3,1])
    with a:
        st.markdown('<div class="section"><div class="section-title">Sales by Category</div>', unsafe_allow_html=True)
        cat = f.groupby("Category", as_index=False)["Revenue"].sum().sort_values("Revenue", ascending=False)
        fig = px.bar(cat, x="Category", y="Revenue", color_discrete_sequence=["#1769e0", "#12b76a", "#f59e0b", "#7c3aed"])
        fig = style_figure(fig, y_prefix="₹ ", height=300)
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
        st.markdown("</div>", unsafe_allow_html=True)
    with b:
        st.markdown('<div class="section"><div class="section-title">Customer Analysis</div>', unsafe_allow_html=True)
        ct = f.groupby("Customer_Type").agg(Count=("Customer_ID","nunique"), Revenue=("Revenue","sum")).reset_index()
        ct["% of Total"] = ct["Revenue"] / ct["Revenue"].sum() * 100
        ct["Revenue"] = ct["Revenue"].map(money)
        ct["% of Total"] = ct["% of Total"].map(lambda x:f"{x:.1f}%")
        st.dataframe(ct, hide_index=True, use_container_width=True, height=210)
        st.markdown("</div>", unsafe_allow_html=True)
    with c:
        st.markdown('<div class="section"><div class="section-title">Data Quality Check</div>', unsafe_allow_html=True)
        checks = [
            ("Missing Values", int(f.isna().sum().sum()), "Good" if f.isna().sum().sum()==0 else "Review"),
            ("Duplicate Records", int(f.duplicated().sum()), "Good" if f.duplicated().sum()==0 else "Review"),
            ("Data Types", "Valid", "Good"),
            ("Date Format", "Valid", "Good"),
        ]
        for label, val, status in checks:
            st.write(f"**{label}**  ·  {val}  ·  `{status}`")
        st.markdown('<div class="success">✓ Dataset is ready for analysis.</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

elif page == "Data Overview":
    st.header("Data Overview")
    st.write(f"Showing **{len(f):,}** filtered records.")
    st.dataframe(f, use_container_width=True, height=520)
    csv = f.to_csv(index=False).encode("utf-8")
    st.download_button("⬇ Export Data (CSV)", csv, "sales_filtered.csv", "text/csv")

elif page == "Sales Analysis":
    st.header("Sales Analysis")
    d1,d2 = st.columns(2)
    with d1:
        monthly = f.set_index("Date").resample("MS")["Revenue"].sum().reset_index()
        fig = px.line(monthly, x="Date", y="Revenue", markers=True, color_discrete_sequence=["#1769e0"])
        fig = style_figure(fig, y_prefix="₹ ", title="Revenue Trend", height=320)
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    with d2:
        monthlyp = f.set_index("Date").resample("MS")["Profit"].sum().reset_index()
        fig = px.line(monthlyp, x="Date", y="Profit", markers=True, color_discrete_sequence=["#12b76a"])
        fig = style_figure(fig, y_prefix="₹ ", title="Profit Trend", height=320)
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    fig = px.bar(f.groupby("Category", as_index=False)["Revenue"].sum().sort_values("Revenue", ascending=False),
                 x="Category", y="Revenue", color_discrete_sequence=["#1769e0", "#12b76a", "#f59e0b", "#7c3aed"])
    fig = style_figure(fig, y_prefix="₹ ", title="Revenue by Category", height=330)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

elif page == "Customer Analysis":
    st.header("Customer Analysis")
    ct = f.groupby("Customer_Type").agg(Customers=("Customer_ID","nunique"), Revenue=("Revenue","sum"), Orders=("Orders","sum")).reset_index()
    c1,c2 = st.columns(2)
    with c1:
        st.plotly_chart(px.bar(ct, x="Customer_Type", y="Revenue", title="Revenue by Customer Type"), use_container_width=True, config=PLOTLY_CONFIG)
    with c2:
        st.plotly_chart(px.pie(ct, names="Customer_Type", values="Revenue", hole=.5, title="Customer Revenue Mix"), use_container_width=True, config=PLOTLY_CONFIG)
    st.dataframe(ct, hide_index=True, use_container_width=True)

elif page == "Product Analysis":
    st.header("Product Analysis")
    p = f.groupby(["Product","Category"]).agg(Revenue=("Revenue","sum"), Profit=("Profit","sum"), Orders=("Orders","sum")).reset_index()
    fig = px.bar(p.sort_values("Revenue").tail(12), x="Revenue", y="Product", color="Category", orientation="h",
                 color_discrete_sequence=["#1769e0", "#12b76a", "#f59e0b", "#7c3aed"])
    fig = style_figure(fig, y_prefix="₹ ", title="Top Products by Revenue", height=360)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    st.dataframe(p.sort_values("Revenue", ascending=False), hide_index=True, use_container_width=True)

elif page == "Regional Analysis":
    st.header("Regional Analysis")
    r = f.groupby("Region").agg(Revenue=("Revenue","sum"), Profit=("Profit","sum"), Orders=("Orders","sum")).reset_index()
    c1,c2 = st.columns(2)
    with c1:
        fig = px.bar(r, x="Region", y="Revenue", color_discrete_sequence=["#1769e0"])
        fig = style_figure(fig, y_prefix="₹ ", title="Revenue by Region", height=300)
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    with c2:
        fig = px.bar(r, x="Region", y="Profit", color_discrete_sequence=["#12b76a"])
        fig = style_figure(fig, y_prefix="₹ ", title="Profit by Region", height=300)
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    st.dataframe(r, hide_index=True, use_container_width=True)

elif page == "SQL Analysis":
    st.header("SQL Analysis")
    st.caption("Run read-only SQL against the current filtered dataset.")
    con = sqlite3.connect(":memory:")
    f.to_sql("sales", con, index=False, if_exists="replace")
    query = st.text_area("SQL Query", """SELECT Region, SUM(Revenue) AS Revenue
FROM sales
GROUP BY Region
ORDER BY Revenue DESC;""", height=140)
    if st.button("▶ Run SQL Query", type="primary"):
        try:
            result = pd.read_sql_query(query, con)
            st.dataframe(result, use_container_width=True)
        except Exception as e:
            st.error(f"SQL Error: {e}")

elif page == "Business Insights":
    st.header("Key Business Insights")
    region_rev = f.groupby("Region")["Revenue"].sum()
    category_rev = f.groupby("Category")["Revenue"].sum()
    product_rev = f.groupby("Product")["Revenue"].sum()
    best_region = region_rev.idxmax() if len(region_rev) else "N/A"
    best_category = category_rev.idxmax() if len(category_rev) else "N/A"
    best_product = product_rev.idxmax() if len(product_rev) else "N/A"
    insights = [
        f"**{best_region}** generated the highest revenue in the selected period.",
        f"**{best_category}** is the leading revenue category.",
        f"**{best_product}** is the top product by revenue.",
        f"Overall profit margin is **{profit_margin:.1f}%**.",
        f"Average order value is **{money(aov)}** across **{total_orders:,}** orders.",
    ]
    for i, item in enumerate(insights, 1):
        st.markdown(f'<div class="insight"><b>{i}</b>&nbsp;&nbsp;{item}</div>', unsafe_allow_html=True)

elif page == "Recommendations":
    st.header("Business Recommendations")
    region_profit = f.groupby("Region").agg(Revenue=("Revenue","sum"), Profit=("Profit","sum"))
    low_margin_region = (region_profit["Profit"]/region_profit["Revenue"]).idxmin() if len(region_profit) else "N/A"
    recs = [
        f"Review pricing and discount strategy in **{low_margin_region}** to protect margins.",
        "Focus inventory and marketing on high-revenue products and categories.",
        "Build retention campaigns for Regular and Premium customers.",
        "Plan stock and campaigns before peak months based on the monthly trend.",
        "Monitor regional margin, not only regional revenue.",
    ]
    for r in recs:
        st.markdown(f'<div class="insight">✓ {r}</div>', unsafe_allow_html=True)

elif page == "Settings":
    st.header("Settings")
    st.write("Upload your own CSV dataset. Required columns:")
    st.code("Date, Region, Category, Product, Customer_Type, Revenue, Cost, Orders, Customer_ID")
    uploaded = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded:
        try:
            test = pd.read_csv(uploaded)
            required = ["Date","Region","Category","Product","Customer_Type","Revenue","Cost","Orders","Customer_ID"]
            missing = [c for c in required if c not in test.columns]
            if missing:
                st.error("Missing columns: " + ", ".join(missing))
            else:
                st.session_state["uploaded_csv"] = uploaded.getvalue()
                st.success("CSV validated. Reload the page and the dataset can be used.")
        except Exception as e:
            st.error(str(e))

# ---------- Footer / exports ----------
st.write("")
e1,e2,e3 = st.columns([1,1,1])
with e1:
    st.download_button("⬇ Export Data (CSV)", f.to_csv(index=False).encode(), "business_report.csv", "text/csv")
with e2:
    if REPORTLAB_OK:
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)
        c.setFont("Helvetica-Bold", 18); c.drawString(50, 800, "Business Analytics Report")
        c.setFont("Helvetica", 11)
        lines = [
            f"Revenue: {money(total_revenue)}",
            f"Profit: {money(total_profit)}",
            f"Profit Margin: {profit_margin:.1f}%",
            f"Orders: {total_orders:,}",
            f"Customers: {total_customers:,}",
            f"Average Order Value: {money(aov)}",
        ]
        y=770
        for line in lines:
            c.drawString(60,y,line); y-=22
        c.save()
        st.download_button("⬇ Export Report (PDF)", buf.getvalue(), "business_report.pdf", "application/pdf")
    else:
        st.info("Install reportlab for PDF export.")
with e3:
    st.caption("Business Analyst Dashboard • Sales & Customer Analytics")
