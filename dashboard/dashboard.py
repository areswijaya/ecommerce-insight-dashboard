# ==========================================================
# E-COMMERCE INSIGHT DASHBOARD (OLIST MARKETPLACE)
# Author: Ilfa Antaries Yusuf Wijaya | contact.areswijaya@gmail.com
# ==========================================================
import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ----------------------------------------------------------
# PAGE CONFIGURATION
# ----------------------------------------------------------
st.set_page_config(
    page_title="E-Commerce Analytics Dashboard | Olist",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------------
# LOAD CSS STYLING
# ----------------------------------------------------------
css_path = os.path.join(os.path.dirname(__file__), "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ----------------------------------------------------------
# NUMBER FORMATTING HELPER (STANDARD ENGLISH FORMAT)
# ----------------------------------------------------------
def fmt_number(val, is_currency: bool = False, decimals: int = 0) -> str:
    """Format numbers using standard English conventions (comma thousands, dot decimal)."""
    if val is None or pd.isna(val):
        return "-"
    try:
        val_float = float(val)
    except (ValueError, TypeError):
        return str(val)
        
    if decimals == 0:
        res = f"{val_float:,.0f}"
    else:
        res = f"{val_float:,.{decimals}f}"
        
    return f"R$ {res}" if is_currency else res

# Backward-compatible alias
fmt_id = fmt_number

# ----------------------------------------------------------
# REUSABLE PLOTLY THEME HELPER
# ----------------------------------------------------------
def apply_plot_theme(fig, title="", x_title="", y_title="", margin=None):
    """Apply a consistent dark and clean layout across all Plotly charts."""
    if margin is None:
        margin = dict(l=75, r=40, t=55, b=45)
    fig.update_layout(
        title=f"<b>{title}</b>" if title else "",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=margin,
        font=dict(color="#F8FAFC", family="Inter, sans-serif"),
        hoverlabel=dict(bgcolor="#1E293B", font_color="#F8FAFC", font_size=12)
    )
    fig.update_xaxes(title_text=x_title, showgrid=True, gridcolor="rgba(148, 163, 184, 0.15)", automargin=True)
    fig.update_yaxes(title_text=y_title, showgrid=True, gridcolor="rgba(148, 163, 184, 0.15)", automargin=True)
    return fig

# ----------------------------------------------------------
# DATA LOADER (WITH CACHING & PRE-CALCULATED DATES)
# ----------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_data():
    possible_paths = [
        os.path.join("data", "clean_orders.csv"),
        os.path.join("..", "data", "clean_orders.csv"),
        os.path.join(os.path.dirname(__file__), "..", "data", "clean_orders.csv"),
        "clean_orders.csv"
    ]
    file_path = None
    for p in possible_paths:
        if os.path.exists(p):
            file_path = p
            break
            
    if not file_path:
        return None
        
    df = pd.read_csv(file_path)
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    df["order_purchase_date"] = df["order_purchase_timestamp"].dt.date
    df["order_delivered_customer_date"] = pd.to_datetime(df["order_delivered_customer_date"])
    df["order_estimated_delivery_date"] = pd.to_datetime(df["order_estimated_delivery_date"])
    df["is_delayed"] = df["is_delayed"].astype(bool)
    return df

with st.spinner("Loading analytical dataset..."):
    df_raw = load_data()

if df_raw is None:
    st.error("⚠️ Dataset file `clean_orders.csv` was not found. Please ensure the file exists in the `data/` folder.")
    st.stop()

# ----------------------------------------------------------
# SIDEBAR CONTROLS & GLOBAL FILTERS
# ----------------------------------------------------------
st.sidebar.title("⚙️ Dashboard Filters")

# 1. Date Range Filter
min_date = df_raw["order_purchase_date"].min()
max_date = df_raw["order_purchase_date"].max()

st.sidebar.subheader("🗓️ Date Range")
period_preset = st.sidebar.selectbox(
    "Select Analysis Period:",
    options=[
        "All Time (Jan 2017 - Aug 2018)",
        "Year 2017 (Expansion & Black Friday Peak)",
        "Year 2018 (Market Maturity)",
        "Custom Date Range"
    ],
    index=0,
    help="Use a quick preset or select 'Custom Date Range' to pick specific dates."
)

if period_preset == "Year 2017 (Expansion & Black Friday Peak)":
    start_date = pd.to_datetime("2017-01-01").date()
    end_date = pd.to_datetime("2017-12-31").date()
    st.sidebar.caption(f"📅 Selected: **{start_date.strftime('%b %d, %Y')}** to **{end_date.strftime('%b %d, %Y')}**")
elif period_preset == "Year 2018 (Market Maturity)":
    start_date = pd.to_datetime("2018-01-01").date()
    end_date = pd.to_datetime("2018-08-31").date()
    st.sidebar.caption(f"📅 Selected: **{start_date.strftime('%b %d, %Y')}** to **{end_date.strftime('%b %d, %Y')}**")
elif period_preset == "Custom Date Range":
    date_selection = st.sidebar.date_input(
        "Pick Custom Date Range:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        help="Data covers the core 20-month window from Jan 1, 2017 to Aug 31, 2018."
    )
    if isinstance(date_selection, (tuple, list)):
        if len(date_selection) == 2:
            start_date, end_date = date_selection
        elif len(date_selection) == 1:
            start_date = end_date = date_selection[0]
            st.sidebar.info("💡 Single date selected. Showing orders for this day.")
        else:
            start_date, end_date = min_date, max_date
    else:
        start_date = end_date = date_selection
else:  # All Time Default
    start_date = min_date
    end_date = max_date
    st.sidebar.caption(f"📅 Selected: **{start_date.strftime('%b %d, %Y')}** to **{end_date.strftime('%b %d, %Y')}** (Full 20 Months)")

# 2. Product Category Filter
all_categories = sorted(df_raw["product_category_name_english"].dropna().unique().tolist())

st.sidebar.subheader("📦 Product Categories")
all_categories_mode = st.sidebar.checkbox(f"All Categories ({len(all_categories)} Active)", value=True)
if all_categories_mode:
    selected_categories = all_categories
    st.sidebar.caption(f"✅ Showing all {len(all_categories)} active categories.")
else:
    top_default = ["health_beauty", "watches_gifts", "bed_bath_table", "sports_leisure", "computers_accessories"]
    selected_categories = st.sidebar.multiselect(
        "Select Specific Categories:",
        options=all_categories,
        default=top_default,
        help="Select one or more categories for focused comparison."
    )

st.sidebar.markdown("---")

# Author Credit and Dataset Information
st.sidebar.subheader("👤 Author Credit")
st.sidebar.markdown(
    "**Ilfa Antaries Yusuf Wijaya**  \n"
    "✉️ [contact.areswijaya@gmail.com](mailto:contact.areswijaya@gmail.com)"
)

st.sidebar.subheader("📊 Dataset Information")
st.sidebar.markdown(
    "**Source:** [Olist Brazilian E-Commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) on Kaggle  \n"
    "**Description:** 100,000 real anonymized customer orders made between 2016 and 2018 across Brazilian marketplaces, covering order status, delivery timelines, product categories, pricing, and customer review scores."
)

# ----------------------------------------------------------
# APPLY FILTERS
# ----------------------------------------------------------
mask_date = (df_raw["order_purchase_date"] >= start_date) & (df_raw["order_purchase_date"] <= end_date)
mask_cat = df_raw["product_category_name_english"].isin(selected_categories)

df_filtered = df_raw[mask_date & mask_cat].copy()

# Order-level dataframe for logistics and customer review metrics
df_orders = df_filtered.drop_duplicates(subset=["order_id"]).copy()

# ----------------------------------------------------------
# HEADER BANNER
# ----------------------------------------------------------
st.markdown("""
<div class="main-banner">
    <h1>🛍️ E-Commerce Performance Dashboard</h1>
    <p>Sales Trends, Product Category Pareto (80/20), and Delivery Impact on Customer Satisfaction (Olist Marketplace)</p>
</div>
""", unsafe_allow_html=True)

if df_filtered.empty or df_orders.empty:
    st.warning("⚠️ No orders match your selected filters. Please adjust the date range or category filters in the sidebar.")
    st.stop()

# ----------------------------------------------------------
# EXECUTIVE KPI RIBBON (5 MAIN METRICS)
# ----------------------------------------------------------
# Item-level metrics
total_revenue = df_filtered["total_order_value"].sum()
total_orders = df_orders["order_id"].nunique()
aov = total_revenue / total_orders if total_orders > 0 else 0

# Order-level metrics (accurate without multi-item duplicate weighting)
avg_delivery_days = df_orders["actual_delivery_days"].mean() if not df_orders.empty else None
median_delivery_days = df_orders["actual_delivery_days"].median() if not df_orders.empty else None
on_time_pct = ((~df_orders["is_delayed"]).mean() * 100) if not df_orders.empty else 0

df_reviewed = df_orders.dropna(subset=["review_score"]).copy()
avg_review_score = df_reviewed["review_score"].mean() if not df_reviewed.empty else None

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric(
    "💰 Total Net Revenue", 
    fmt_id(total_revenue, is_currency=True),
    help="Total realized revenue on delivered orders, including product price and freight."
)
kpi2.metric(
    "📦 Delivered Orders", 
    fmt_id(total_orders),
    help=f"Total unique delivered customer orders ({fmt_id(len(df_filtered))} individual items sold)."
)
kpi3.metric(
    "🏷️ Average Order Value", 
    fmt_id(aov, is_currency=True, decimals=2),
    help="Average spend per delivered order (AOV = Total Net Revenue / Total Unique Orders)."
)
kpi4.metric(
    "🚚 Avg Delivery Time", 
    f"{fmt_id(avg_delivery_days, decimals=1)} Days" if avg_delivery_days is not None else "-",
    help=f"Average actual delivery duration from purchase to doorstep. Median duration: {fmt_id(median_delivery_days, decimals=1)} days."
)
kpi5.metric(
    "⭐ Avg Review Score", 
    f"{fmt_id(avg_review_score, decimals=2)} / 5.0" if avg_review_score is not None else "-",
    help=f"Average customer review rating on a 1-5 scale (On-time delivery rate: {fmt_id(on_time_pct, decimals=1)}%)."
)

# Secondary Metadata Strip
st.markdown(f"""
<div style="display: flex; gap: 1.5rem; justify-content: space-around; background: #1E293B; padding: 0.65rem 1.2rem; border-radius: 8px; border: 1px solid #334155; margin-top: 0.5rem; font-size: 0.88rem; color: #94A3B8;">
    <span>📊 <b>Median Delivery Time:</b> <span style="color: #F8FAFC;">{fmt_id(median_delivery_days, decimals=1)} Days</span></span>
    <span>🚚 <b>On-Time Delivery Rate:</b> <span style="color: #34D399;">{fmt_id(on_time_pct, decimals=1)}%</span></span>
    <span>📦 <b>Total Items Sold:</b> <span style="color: #F8FAFC;">{fmt_id(len(df_filtered))} Items</span></span>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr style='margin: 1.5rem 0; border: none; height: 1px; background-color: #334155;'/>", unsafe_allow_html=True)

# ----------------------------------------------------------
# SECTION 1: MONTHLY SALES & MOM GROWTH DYNAMICS
# ----------------------------------------------------------
st.subheader("📈 1. Monthly Revenue & Growth Dynamics")
st.caption("Addressing Question 1: Tracking monthly sales volume, month-over-month growth rates, and seasonal shopping spikes.")

# Monthly aggregation
monthly_agg = df_filtered.groupby("order_year_month").agg(
    revenue=("total_order_value", "sum"),
    orders=("order_id", "nunique")
).reset_index()

monthly_agg["mom_growth"] = monthly_agg["revenue"].pct_change() * 100
monthly_agg["aov"] = monthly_agg["revenue"] / monthly_agg["orders"]

col1, col2 = st.columns([7, 5])

with col1:
    tab_trend, tab_aov_trend = st.tabs(["📊 Revenue & Order Volume", "🏷️ Average Order Value (AOV)"])
    
    with tab_trend:
        # Dual-axis chart: Revenue vs Total Orders
        fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig_trend.add_trace(
            go.Scatter(
                x=monthly_agg["order_year_month"],
                y=monthly_agg["revenue"],
                name="Net Revenue (BRL)",
                mode="lines+markers",
                line=dict(color="#38BDF8", width=3),
                marker=dict(size=7, color="#38BDF8"),
                hovertemplate="Month: %{x}<br>Revenue: R$ %{y:,.2f}<extra></extra>"
            ),
            secondary_y=False
        )
        
        fig_trend.add_trace(
            go.Scatter(
                x=monthly_agg["order_year_month"],
                y=monthly_agg["orders"],
                name="Delivered Orders",
                mode="lines+markers",
                line=dict(color="#34D399", width=2, dash="dash"),
                marker=dict(size=6, symbol="square", color="#34D399"),
                hovertemplate="Month: %{x}<br>Orders: %{y:,}<extra></extra>"
            ),
            secondary_y=True
        )
        
        # Dynamic annotation for Black Friday Nov 2017 peak
        if "2017-11" in monthly_agg["order_year_month"].values:
            bf_row = monthly_agg[monthly_agg["order_year_month"] == "2017-11"].iloc[0]
            bf_rev_str = f"R$ {fmt_id(bf_row['revenue'] / 1e6, decimals=2)}M"
            bf_mom_val = bf_row["mom_growth"]
            bf_mom_str = f"+{fmt_id(bf_mom_val, decimals=1)}% MoM" if pd.notna(bf_mom_val) else ""
            
            fig_trend.add_annotation(
                x="2017-11",
                y=bf_row["revenue"],
                text=f"<b>Black Friday Peak (Nov 2017)</b><br>{bf_rev_str} ({bf_mom_str})",
                showarrow=True,
                arrowhead=2,
                arrowcolor="#EF4444",
                arrowsize=1,
                arrowwidth=2,
                ax=-70,
                ay=-55,
                bgcolor="#1E293B",
                bordercolor="#EF4444",
                borderwidth=1.5,
                font=dict(color="#F8FAFC", size=10)
            )
        
        apply_plot_theme(fig_trend, title="Monthly Net Revenue vs Order Volume", x_title="Order Month", y_title="Net Revenue (BRL)")
        fig_trend.update_layout(
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig_trend.update_yaxes(title_text="Total Orders", secondary_y=True, showgrid=False, automargin=True)
        st.plotly_chart(fig_trend, width="stretch")
        
    with tab_aov_trend:
        # AOV Monthly Trend Line Chart
        fig_aov_trend = go.Figure()
        fig_aov_trend.add_trace(
            go.Scatter(
                x=monthly_agg["order_year_month"],
                y=monthly_agg["aov"],
                name="Average Order Value",
                mode="lines+markers",
                line=dict(color="#38BDF8", width=2.5),
                marker=dict(size=6, color="#38BDF8"),
                hovertemplate="Month: %{x}<br>AOV: R$ %{y:,.2f}<extra></extra>"
            )
        )
        if not monthly_agg.empty:
            mean_aov_val = monthly_agg["aov"].mean()
            fig_aov_trend.add_hline(
                y=mean_aov_val, 
                line_dash="dash", 
                line_color="#94A3B8", 
                line_width=1.5,
                annotation_text=f"Average: {fmt_id(mean_aov_val, is_currency=True, decimals=1)}", 
                annotation_position="bottom right"
            )
        apply_plot_theme(fig_aov_trend, title="Monthly Average Order Value (AOV) Stability", x_title="Order Month", y_title="AOV (BRL)")
        fig_aov_trend.update_layout(hovermode="x unified")
        st.plotly_chart(fig_aov_trend, width="stretch")
        st.caption("ℹ️ The dashed line indicates the overall average AOV. Consistent AOV values demonstrate that revenue growth was primarily driven by increasing order volumes rather than price inflation.")

with col2:
    # MoM Growth % Bar Chart with neutral handling for baseline month
    mom_display = monthly_agg.copy()
    mom_vals = mom_display["mom_growth"]
    
    colors_mom = []
    hover_texts = []
    for idx, val in enumerate(mom_vals):
        if idx == 0 or pd.isna(val):
            colors_mom.append("#64748B")
            hover_texts.append("Baseline Month")
        elif val >= 0:
            colors_mom.append("#34D399")
            hover_texts.append(f"+{fmt_id(val, decimals=2)}%")
        else:
            colors_mom.append("#EF4444")
            hover_texts.append(f"{fmt_id(val, decimals=2)}%")
            
    fig_mom = go.Figure()
    fig_mom.add_trace(go.Bar(
        x=mom_display["order_year_month"],
        y=mom_vals.fillna(0),
        marker_color=colors_mom,
        customdata=hover_texts,
        hovertemplate="Month: %{x}<br>MoM Growth: %{customdata}<extra></extra>"
    ))
    
    fig_mom.add_hline(y=0, line_dash="solid", line_color="#94A3B8", line_width=1)
    apply_plot_theme(fig_mom, title="Month-over-Month Growth (MoM %)", x_title="Order Month", y_title="MoM Growth (%)", margin=dict(l=65, r=30, t=55, b=45))
    st.plotly_chart(fig_mom, width="stretch")
    st.caption("ℹ️ The first month serves as the neutral baseline. If the selected date range starts mid-month, that month's growth rate reflects partial data.")

# Dynamic metrics for Section 1 insight card
if not monthly_agg.empty:
    peak_row = monthly_agg.loc[monthly_agg["revenue"].idxmax()]
    peak_month = peak_row["order_year_month"]
    peak_rev = fmt_id(peak_row["revenue"], is_currency=True)
    first_month = monthly_agg.iloc[0]["order_year_month"]
    first_rev = fmt_id(monthly_agg.iloc[0]["revenue"], is_currency=True)
    avg_aov_range = f"{fmt_id(monthly_agg['aov'].min(), is_currency=True, decimals=0)} to {fmt_id(monthly_agg['aov'].max(), is_currency=True, decimals=0)}"
else:
    peak_month, peak_rev, first_month, first_rev, avg_aov_range = "-", "-", "-", "-", "-"

# Insight Box Section 1
st.markdown(f"""
<div class="insight-card">
    <div class="insight-card-title">💡 Key Insights: Sales Growth and Seasonal Patterns</div>
    <div class="insight-card-body">
        <ul>
            <li><b>Expanding Sales Volume:</b> Monthly revenue started at <b>{first_rev}</b> ({first_month}) and climbed to a peak of <b>{peak_rev}</b> in {peak_month}.</li>
            <li><b>Seasonal Demand Spikes:</b> The sharp rise in November 2017 reflects the annual Black Friday shopping event, followed by standard post-holiday normalization.</li>
            <li><b>Stable Shopping Basket Size:</b> Average Order Value remained consistent across months, staying within <b>{avg_aov_range}</b>. This indicates that sales expansion was largely fueled by increasing customer order volumes.</li>
        </ul>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr style='margin: 1.5rem 0; border: none; height: 1px; background-color: #334155;'/>", unsafe_allow_html=True)

# ----------------------------------------------------------
# SECTION 2: PRODUCT CATEGORY PARETO 80/20 & AOV
# ----------------------------------------------------------
st.subheader("📦 2. Product Category Portfolio: 80/20 Pareto Analysis")
st.caption("Addressing Question 2: Identifying the core product categories generating 80% of total revenue and comparing their Average Order Values.")

cat_agg = df_filtered.groupby("product_category_name_english").agg(
    total_revenue=("total_order_value", "sum"),
    total_orders=("order_id", "nunique"),
    total_items=("product_id", "count")
).reset_index()

cat_agg["aov"] = cat_agg["total_revenue"] / cat_agg["total_orders"]
cat_agg = cat_agg.sort_values(by="total_revenue", ascending=False).reset_index(drop=True)
cat_agg["cum_revenue"] = cat_agg["total_revenue"].cumsum()
cat_agg["cum_pct"] = (cat_agg["cum_revenue"] / cat_agg["total_revenue"].sum()) * 100

total_cats_count = len(cat_agg)
core_cats_count = (cat_agg["cum_pct"] <= 80).sum() + 1 if total_cats_count > 0 else 0

col_p1, col_p2 = st.columns([7, 5])

with col_p1:
    # Crash-safe Pareto slider
    if total_cats_count <= 1:
        top_n = total_cats_count
        st.info(f"Showing 1 selected category: **{cat_agg.iloc[0]['product_category_name_english']}**")
    elif total_cats_count <= 5:
        top_n = total_cats_count
        st.caption(f"Showing all {total_cats_count} selected categories.")
    else:
        slider_max = min(30, total_cats_count)
        slider_default = min(15, total_cats_count)
        top_n = st.slider("Display Top N Categories:", min_value=1, max_value=slider_max, value=slider_default)
        
    df_pareto_display = cat_agg.head(top_n).copy()
    
    # Pareto Plot
    fig_pareto = make_subplots(specs=[[{"secondary_y": True}]])
    colors_pareto = ["#3B82F6" if i < core_cats_count else "#64748B" for i in range(len(df_pareto_display))]
    
    fig_pareto.add_trace(
        go.Bar(
            x=df_pareto_display["product_category_name_english"],
            y=df_pareto_display["total_revenue"],
            name="Revenue (BRL)",
            marker_color=colors_pareto,
            hovertemplate="Category: %{x}<br>Revenue: R$ %{y:,.2f}<extra></extra>"
        ),
        secondary_y=False
    )
    
    fig_pareto.add_trace(
        go.Scatter(
            x=df_pareto_display["product_category_name_english"],
            y=df_pareto_display["cum_pct"],
            name="Cumulative (%)",
            mode="lines+markers",
            line=dict(color="#F87171", width=2.5),
            marker=dict(size=6, color="#F87171"),
            hovertemplate="Category: %{x}<br>Cumulative: %{y:.1f}%<extra></extra>"
        ),
        secondary_y=True
    )
    
    fig_pareto.add_hline(y=80, line_dash="dash", line_color="#F87171", secondary_y=True, annotation_text="80% Pareto Cutoff", annotation_position="bottom right")
    
    apply_plot_theme(fig_pareto, title=f"Top {top_n} Product Categories by Revenue (Pareto Curve)", y_title="Revenue (BRL)")
    fig_pareto.update_layout(
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig_pareto.update_xaxes(tickangle=-45)
    fig_pareto.update_yaxes(title_text="Cumulative (%)", secondary_y=True, range=[0, 105], showgrid=False, automargin=True)
    
    st.plotly_chart(fig_pareto, width="stretch")

with col_p2:
    top_cat_name = cat_agg.iloc[0]["product_category_name_english"] if total_cats_count > 0 else "-"
    top_cat_rev = fmt_id(cat_agg.iloc[0]["total_revenue"], is_currency=True) if total_cats_count > 0 else "-"
    core_pct_str = f"{(core_cats_count/total_cats_count)*100:.1f}%" if total_cats_count > 0 else "-"
    
    st.markdown(f"""
    <div style="background-color: #1E293B; border: 1px solid #334155; border-radius: 10px; padding: 1.2rem; margin-bottom: 1rem;">
        <h4 style="margin: 0; color: #60A5FA;">📊 Pareto Principle Summary</h4>
        <p style="margin: 0.5rem 0 0 0; color: #CBD5E1; font-size: 0.92rem; line-height: 1.5;">
            Exactly <b>{core_cats_count} out of {total_cats_count} categories ({core_pct_str})</b> generate <b>80% of total revenue</b> in the selected data.<br/>
            Top revenue category: <b>{top_cat_name}</b> ({top_cat_rev}).
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # AOV Bar Chart across Top Categories
    fig_aov = px.bar(
        df_pareto_display.sort_values(by="aov", ascending=True),
        x="aov",
        y="product_category_name_english",
        orientation="h",
        labels={"aov": "AOV (BRL)", "product_category_name_english": "Product Category"},
        color="aov",
        color_continuous_scale="Blues"
    )
    apply_plot_theme(fig_aov, title=f"Average Order Value by Category (Top {top_n})", x_title="AOV (BRL)", margin=dict(l=85, r=30, t=55, b=45))
    fig_aov.update_layout(coloraxis_showscale=False)
    
    st.plotly_chart(fig_aov, width="stretch")

# Determine top 3 categories dynamically
top_3_names = ", ".join([f"<code>{cat}</code>" for cat in cat_agg.head(3)["product_category_name_english"].tolist()]) if total_cats_count >= 3 else top_cat_name

# Insight Box Section 2
st.markdown(f"""
<div class="insight-card">
    <div class="insight-card-title">💡 Key Insights: Product Portfolio Optimization</div>
    <div class="insight-card-body">
        <ul>
            <li><b>Revenue Concentration:</b> Across the {total_cats_count} active product categories, just <b>{core_cats_count} core categories ({core_pct_str})</b> drive 80% of total revenue, led by {top_3_names}.</li>
            <li><b>Different Category Roles:</b> Order values vary widely by category. High-ticket items (e.g., computers and watches) drive higher spend per transaction, whereas high-volume essentials (e.g., bed & bath, health & beauty) deliver consistent order frequency.</li>
            <li><b>Strategic Recommendation:</b> Protect inventory and priority marketing visibility for core revenue drivers, while bundling popular everyday items with higher-margin products.</li>
        </ul>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr style='margin: 1.5rem 0; border: none; height: 1px; background-color: #334155;'/>", unsafe_allow_html=True)

# ----------------------------------------------------------
# SECTION 3: DELIVERY DURATION & SATISFACTION GAP (ORDER LEVEL)
# ----------------------------------------------------------
st.subheader("🚚 3. Delivery Performance & Customer Satisfaction")
st.caption("Addressing Question 3: Evaluating how actual delivery duration and calendar delays impact customer review ratings on unique orders.")

ontime_df = df_reviewed[~df_reviewed["is_delayed"]]
late_df = df_reviewed[df_reviewed["is_delayed"]]

on_time_avg = ontime_df["review_score"].mean() if not ontime_df.empty else None
late_avg = late_df["review_score"].mean() if not late_df.empty else None
satisfaction_gap = (on_time_avg - late_avg) if (on_time_avg is not None and late_avg is not None) else None

# Statistical correlation (Pearson & Spearman rank correlation)
corr_pearson = df_reviewed["actual_delivery_days"].corr(df_reviewed["review_score"], method="pearson") if len(df_reviewed) > 1 else None
corr_spearman = df_reviewed["actual_delivery_days"].rank().corr(df_reviewed["review_score"].rank()) if len(df_reviewed) > 1 else None

col_d1, col_d2 = st.columns([6, 6])

with col_d1:
    tab_rating, tab_prop, tab_dist = st.tabs([
        "⭐ Average Review Score", 
        "🚨 1-Star Review Rate",
        "📊 Rating Distribution (1 to 5 ⭐)"
    ])
    
    n_ontime = len(ontime_df)
    n_late = len(late_df)
    
    with tab_rating:
        # Bar Chart: Satisfaction Gap (On-Time vs Late)
        gap_labels = [f"On-Time or Early\n({fmt_id(n_ontime)} orders)", f"Delayed Past Estimate\n({fmt_id(n_late)} orders)"]
        gap_values = [on_time_avg if on_time_avg is not None else 0, late_avg if late_avg is not None else 0]
        gap_texts = [f"{fmt_id(on_time_avg, decimals=2)} ⭐" if on_time_avg is not None else "No Data",
                     f"{fmt_id(late_avg, decimals=2)} ⭐" if late_avg is not None else "No Data"]
                     
        gap_data = pd.DataFrame({
            "Delivery Status": gap_labels,
            "Average Rating": gap_values,
            "Text": gap_texts
        })
        
        fig_gap = px.bar(
            gap_data,
            x="Delivery Status",
            y="Average Rating",
            text="Text",
            color="Delivery Status",
            color_discrete_sequence=["#10B981", "#EF4444"]
        )
        fig_gap.update_traces(textposition="outside", width=0.45)
        apply_plot_theme(fig_gap, title="Customer Ratings: On-Time vs Delayed Deliveries", y_title="Average Rating (1-5 Stars)", margin=dict(l=65, r=30, t=55, b=45))
        fig_gap.update_layout(yaxis_range=[0, 5.3], showlegend=False)
        fig_gap.update_xaxes(showgrid=False)
        st.plotly_chart(fig_gap, width="stretch")
        
    with tab_prop:
        # Bar Chart: 1-Star Review Share
        p_ontime_1_val = (ontime_df["review_score"] == 1).mean() * 100 if not ontime_df.empty else 0
        p_late_1_val = (late_df["review_score"] == 1).mean() * 100 if not late_df.empty else 0
        
        prop_labels = [f"On-Time\n({fmt_id(n_ontime)} orders)", f"Delayed\n({fmt_id(n_late)} orders)"]
        prop_vals = [p_ontime_1_val, p_late_1_val]
        prop_texts = [f"{fmt_id(p_ontime_1_val, decimals=1)}%", f"{fmt_id(p_late_1_val, decimals=1)}%"]
        
        df_prop = pd.DataFrame({
            "Delivery Status": prop_labels,
            "1-Star Review Share (%)": prop_vals,
            "Text": prop_texts
        })
        
        fig_prop = px.bar(
            df_prop,
            x="Delivery Status",
            y="1-Star Review Share (%)",
            text="Text",
            color="Delivery Status",
            color_discrete_sequence=["#10B981", "#EF4444"]
        )
        fig_prop.update_traces(textposition="outside", width=0.45)
        apply_plot_theme(fig_prop, title="Share of 1-Star Reviews by Delivery Status", y_title="Orders with 1-Star Review (%)", margin=dict(l=65, r=30, t=55, b=45))
        fig_prop.update_layout(yaxis_range=[0, max(65, p_late_1_val * 1.15)], showlegend=False)
        fig_prop.update_xaxes(showgrid=False)
        st.plotly_chart(fig_prop, width="stretch")
        st.caption("ℹ️ Missing the estimated delivery date drastically increases the risk of a 1-star negative review by more than 8x.")

    with tab_dist:
        # Grouped Bar Chart: Full Rating Distribution 1 to 5 Stars
        dist_data = []
        for status_label, sub_df in [("On-Time", ontime_df), ("Delayed", late_df)]:
            if not sub_df.empty:
                counts = sub_df["review_score"].round().value_counts(normalize=True) * 100
                for score in [1, 2, 3, 4, 5]:
                    pct_val = counts.get(float(score), 0.0)
                    dist_data.append({
                        "Delivery Status": status_label,
                        "Star Rating": f"{score} ⭐",
                        "Percentage": round(pct_val, 1),
                        "Label Text": f"{pct_val:.1f}%"
                    })
        
        df_chart_dist = pd.DataFrame(dist_data)
        if not df_chart_dist.empty:
            fig_dist = px.bar(
                df_chart_dist,
                x="Star Rating",
                y="Percentage",
                color="Delivery Status",
                barmode="group",
                color_discrete_map={"On-Time": "#10B981", "Delayed": "#EF4444"},
                text="Label Text",
                labels={"Percentage": "Share of Orders (%)", "Star Rating": "Review Rating"}
            )
            fig_dist.update_traces(textposition="outside")
            apply_plot_theme(fig_dist, title="Full Review Rating Breakdown: On-Time vs Delayed", y_title="Share of Orders (%)", margin=dict(l=65, r=30, t=55, b=45))
            max_p = df_chart_dist["Percentage"].max() if not df_chart_dist.empty else 60
            fig_dist.update_layout(yaxis_range=[0, max(75, max_p * 1.18)], legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            st.plotly_chart(fig_dist, width="stretch")
            st.caption("ℹ️ On-time deliveries are heavily weighted toward 5 stars (62.2%), whereas delayed orders drop predominantly to 1 star (53.7%).")

with col_d2:
    # Boxplot of Delivery Days by Review Score (0-45 day window to highlight quartiles)
    fig_box = px.box(
        df_reviewed,
        x="review_score",
        y="actual_delivery_days",
        labels={"review_score": "Review Score (1 to 5)", "actual_delivery_days": "Actual Delivery Time (Days)"},
        points=False  # Hide extreme outliers to keep box shapes informative
    )
    fig_box.update_traces(marker_color="#38BDF8")
    apply_plot_theme(fig_box, title="Delivery Days Distribution across Review Scores", x_title="Customer Review Score (1 to 5)", y_title="Delivery Time (Days)", margin=dict(l=65, r=30, t=55, b=45))
    fig_box.update_layout(yaxis_range=[0, 45], showlegend=False)
    
    st.plotly_chart(fig_box, width="stretch")
    st.caption("ℹ️ Y-axis is scaled to 0-45 days (covering over 95% of orders) to maintain clear quartile comparisons.")

# Metrics Highlight for Section 3
c_m1, c_m2, c_m3 = st.columns(3)
c_m1.metric(
    "📉 Satisfaction Gap", 
    f"-{fmt_id(satisfaction_gap, decimals=2)} ⭐" if satisfaction_gap is not None else "-",
    help="Difference in average review rating between on-time orders and delayed orders."
)
c_m2.metric(
    "🔗 Delivery vs Rating Correlation", 
    f"r = {fmt_id(corr_pearson, decimals=3)}" if corr_pearson is not None else "-",
    help=f"Pearson r = {fmt_id(corr_pearson, decimals=3)} | Spearman r_s = {fmt_id(corr_spearman, decimals=3)} (Sample size n = {fmt_id(len(df_reviewed))} unique orders)."
)
c_m3.metric(
    "🚨 Delivery Performance", 
    f"{fmt_id((~df_orders['is_delayed']).mean()*100, decimals=1)}% On-Time",
    help=f"Out of {fmt_id(len(df_orders))} unique orders, {fmt_id((df_orders['is_delayed']).sum())} orders ({fmt_id(df_orders['is_delayed'].mean()*100, decimals=1)}%) arrived after the estimated delivery date."
)

# Calculate 1-star proportions dynamically
ontime_1star = fmt_id((ontime_df["review_score"] == 1).mean() * 100, decimals=1) if not ontime_df.empty else "0"
late_1star = fmt_id((late_df["review_score"] == 1).mean() * 100, decimals=1) if not late_df.empty else "0"

# Insight Box Section 3
st.markdown(f"""
<div class="insight-card">
    <div class="insight-card-title">💡 Key Insights: Delivery Timelines and Customer Satisfaction</div>
    <div class="insight-card-body">
        <ul>
            <li><b>Major Satisfaction Penalty:</b> Orders delivered on time earned an average rating of <b>{fmt_id(on_time_avg, decimals=2)} ⭐</b>, whereas delayed orders plunged to <b>{fmt_id(late_avg, decimals=2)} ⭐</b> (a satisfaction gap of <b>-{fmt_id(satisfaction_gap, decimals=2)} stars</b>).</li>
            <li><b>Surge in Negative Reviews:</b> The share of 1-star negative reviews escalates from <b>{ontime_1star}%</b> for on-time orders to <b>{late_1star}%</b> when shipments miss their estimated delivery date.</li>
            <li><b>Delivery Promises Anchor Expectations:</b> Customers judge delivery success against the promised arrival date. Missing that deadline correlates strongly with poor ratings (Pearson r = {fmt_id(corr_pearson, decimals=3)}, Spearman r_s = {fmt_id(corr_spearman, decimals=3)}).</li>
        </ul>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr style='margin: 1.5rem 0; border: none; height: 1px; background-color: #334155;'/>", unsafe_allow_html=True)

# ----------------------------------------------------------
# SECTION 4: STRATEGIC ACTION PLAYBOOK (TAKEAWAYS)
# ----------------------------------------------------------
st.subheader("🎯 4. Actionable Business Recommendations")
st.caption("Practical action points synthesized for Commercial, Merchandising, and Logistics teams.")

col_a1, col_a2, col_a3 = st.columns(3)

with col_a1:
    st.markdown(f"""
    <div class="playbook-card commercial">
        <h4 class="playbook-title commercial">🚀 Commercial & Growth Strategy</h4>
        <ul class="playbook-list">
            <li><b>Early Holiday Preparation:</b> Launch pre-promotional campaigns in October to build early demand and prevent courier bottlenecks during the November Black Friday peak.</li>
            <li><b>Focus on Order Volume:</b> With average order value remaining stable (~{fmt_id(aov, is_currency=True, decimals=0)}), business revenue growth depends primarily on acquiring new orders and customers.</li>
            <li><b>Post-Peak Customer Retention:</b> Implement targeted re-engagement campaigns in December and January to convert seasonal holiday shoppers into repeat buyers.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col_a2:
    st.markdown("""
    <div class="playbook-card merchandising">
        <h4 class="playbook-title merchandising">📦 Product Portfolio & Merchandising</h4>
        <ul class="playbook-list">
            <li><b>Protect Core Drivers:</b> Prioritize inventory and premium digital shelf space for the core categories that drive 80% of sales.</li>
            <li><b>Smart Product Bundling:</b> Pair high-volume everyday essentials with higher-margin specialty products to increase average cart values.</li>
            <li><b>Catalog Streamlining:</b> Review low-turnover, long-tail categories to optimize catalog maintenance without impacting top-line revenue.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col_a3:
    st.markdown("""
    <div class="playbook-card logistics">
        <h4 class="playbook-title logistics">🚚 Logistics & Customer Experience</h4>
        <ul class="playbook-list">
            <li><b>Realistic Delivery Windows:</b> Incorporate a 2 to 3 day safety buffer for long-distance routes to prevent ratings from falling due to missed arrival promises.</li>
            <li><b>Proactive Delay Alerts:</b> Trigger automated notifications with real-time updates and goodwill discounts as soon as shipping exceptions are detected.</li>
            <li><b>Seller SLA Accountability:</b> Regularly audit fulfillment partners and merchant dispatch times with high delay rates to maintain high delivery standards.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='margin: 1.5rem 0; border: none; height: 1px; background-color: #334155;'/>", unsafe_allow_html=True)

# ----------------------------------------------------------
# SECTION 5: DATA DRILLDOWN & AUDIT TRAIL
# ----------------------------------------------------------
st.subheader("🔍 5. Data Exploration & Export")
st.caption("Inspect transaction samples, review aggregated summary tables, and download filtered datasets in CSV format.")

with st.expander("📂 Open Data Exploration Panel & Download CSVs", expanded=False):
    tab_sample, tab_cat_table, tab_monthly_table = st.tabs([
        "📋 Transaction Sample (10 Rows)", 
        "📦 Category Summary Table", 
        "📈 Monthly Trends Table"
    ])
    
    with tab_sample:
        display_cols = [
            "order_id", "order_purchase_timestamp", "product_category_name_english",
            "price", "freight_value", "total_order_value", "actual_delivery_days",
            "is_delayed", "review_score"
        ]
        st.dataframe(df_filtered[display_cols].head(10), hide_index=True)
        csv_sample = df_filtered[display_cols].to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered Transactions (CSV)",
            data=csv_sample,
            file_name="filtered_ecommerce_transactions.csv",
            mime="text/csv",
            help="Download filtered transaction data based on the active date and category filters."
        )
        
    with tab_cat_table:
        cat_export = cat_agg[["product_category_name_english", "total_revenue", "total_orders", "total_items", "aov", "cum_pct"]].copy()
        cat_export.columns = ["Product Category", "Total Revenue (BRL)", "Total Orders", "Total Items", "AOV (BRL)", "Cumulative (%)"]
        st.dataframe(cat_export.head(30), hide_index=True)
        csv_cat = cat_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Category Pareto Summary (CSV)",
            data=csv_cat,
            file_name="category_pareto_summary.csv",
            mime="text/csv"
        )
        
    with tab_monthly_table:
        monthly_export = monthly_agg[["order_year_month", "revenue", "orders", "aov", "mom_growth"]].copy()
        monthly_export.columns = ["Year-Month", "Net Revenue (BRL)", "Total Orders", "AOV (BRL)", "MoM Growth (%)"]
        st.dataframe(monthly_export, hide_index=True)
        csv_monthly = monthly_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Monthly Trends Summary (CSV)",
            data=csv_monthly,
            file_name="monthly_revenue_trend.csv",
            mime="text/csv"
        )

# ----------------------------------------------------------
# SECTION 6: AUTHOR CREDITS & FOOTER
# ----------------------------------------------------------
st.markdown("""
<div class="credit-container">
    <div>
        <div class="credit-author">👤 Ilfa Antaries Yusuf Wijaya</div>
        <div class="credit-role">E-Commerce Analytics Project</div>
    </div>
    <div class="credit-contact">
        <span style="color: #94A3B8; font-size: 0.9rem;">Contact Email:</span>
        <a href="mailto:contact.areswijaya@gmail.com" class="credit-email">✉️ contact.areswijaya@gmail.com</a>
    </div>
</div>
""", unsafe_allow_html=True)

st.caption("© 2026 E-Commerce Insight Dashboard. Built with Python, Streamlit & Plotly.")
