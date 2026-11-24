import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="E-Commerce Analytics Dashboard | Olist",
    layout="wide",
    initial_sidebar_state="expanded",
)

css_path = os.path.join(os.path.dirname(__file__), "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def fmt_number(val, is_currency: bool = False, decimals: int = 0) -> str:
    """Format numeric values with comma thousands separators and optional BRL prefix."""
    if val is None or pd.isna(val):
        return "-"
    try:
        val_float = float(val)
    except (ValueError, TypeError):
        return str(val)

    res = f"{val_float:,.0f}" if decimals == 0 else f"{val_float:,.{decimals}f}"
    return f"R$ {res}" if is_currency else res


def apply_plot_theme(fig, title="", x_title="", y_title="", margin=None):
    """Apply transparent dark-theme layout and typography to a Plotly figure."""
    if margin is None:
        margin = dict(l=75, r=40, t=55, b=45)
    fig.update_layout(
        title=f"<b>{title}</b>" if title else "",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=margin,
        font=dict(color="#F8FAFC", family="Inter, sans-serif"),
        hoverlabel=dict(bgcolor="#1E293B", bordercolor="#334155", font_color="#F8FAFC", font_size=12),
    )
    fig.update_xaxes(title_text=x_title, showgrid=True, gridcolor="rgba(148, 163, 184, 0.15)", automargin=True)
    fig.update_yaxes(title_text=y_title, showgrid=True, gridcolor="rgba(148, 163, 184, 0.15)", automargin=True)
    return fig


@st.cache_data(show_spinner=False)
def load_data():
    """Load clean_orders.csv from standard repository working directories."""
    possible_paths = [
        os.path.join("data", "clean_orders.csv"),
        os.path.join("..", "data", "clean_orders.csv"),
        os.path.join(os.path.dirname(__file__), "..", "data", "clean_orders.csv"),
        "clean_orders.csv",
    ]
    file_path = next((p for p in possible_paths if os.path.exists(p)), None)
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
    st.error("Dataset file `clean_orders.csv` was not found. Ensure it exists in the `data/` folder.")
    st.stop()

st.sidebar.title("Dashboard Filters")

min_date = df_raw["order_purchase_date"].min()
max_date = df_raw["order_purchase_date"].max()

st.sidebar.subheader("Date Range")
period_preset = st.sidebar.selectbox(
    "Analysis Period",
    options=[
        "All Time (Jan 2017 - Aug 2018)",
        "Year 2017 (Expansion & Black Friday Peak)",
        "Year 2018 (Market Maturity)",
        "Custom Date Range",
    ],
    index=0,
    help="Select a preset period or switch to Custom Date Range.",
)

if period_preset == "Year 2017 (Expansion & Black Friday Peak)":
    start_date = pd.to_datetime("2017-01-01").date()
    end_date = pd.to_datetime("2017-12-31").date()
    st.sidebar.caption(f"Selected: **{start_date.strftime('%b %d, %Y')}** to **{end_date.strftime('%b %d, %Y')}**")
elif period_preset == "Year 2018 (Market Maturity)":
    start_date = pd.to_datetime("2018-01-01").date()
    end_date = pd.to_datetime("2018-08-31").date()
    st.sidebar.caption(f"Selected: **{start_date.strftime('%b %d, %Y')}** to **{end_date.strftime('%b %d, %Y')}**")
elif period_preset == "Custom Date Range":
    date_selection = st.sidebar.date_input(
        "Custom Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        help="Dataset covers Jan 1, 2017 to Aug 31, 2018.",
    )
    if isinstance(date_selection, (tuple, list)):
        if len(date_selection) == 2:
            start_date, end_date = date_selection
        elif len(date_selection) == 1:
            start_date = end_date = date_selection[0]
            st.sidebar.info("Single date selected. Showing orders for this day.")
        else:
            start_date, end_date = min_date, max_date
    else:
        start_date = end_date = date_selection
else:
    start_date = min_date
    end_date = max_date
    st.sidebar.caption(
        f"Selected: **{start_date.strftime('%b %d, %Y')}** to **{end_date.strftime('%b %d, %Y')}** (20 Months)"
    )

all_categories = sorted(df_raw["product_category_name_english"].dropna().unique().tolist())

st.sidebar.subheader("Product Categories")
all_categories_mode = st.sidebar.checkbox(f"All Categories ({len(all_categories)} Active)", value=True)
if all_categories_mode:
    selected_categories = all_categories
    st.sidebar.caption(f"Showing all {len(all_categories)} active categories.")
else:
    top_default = ["health_beauty", "watches_gifts", "bed_bath_table", "sports_leisure", "computers_accessories"]
    selected_categories = st.sidebar.multiselect(
        "Select Categories",
        options=all_categories,
        default=top_default,
        help="Pick one or more product categories to compare.",
    )

st.sidebar.markdown("---")

st.sidebar.subheader("Author")
st.sidebar.markdown(
    "**Ilfa Antaries Yusuf Wijaya**  \n"
    "[contact.areswijaya@gmail.com](mailto:contact.areswijaya@gmail.com)"
)

st.sidebar.subheader("Dataset")
st.sidebar.markdown(
    "**Source:** [Olist Brazilian E-Commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) (Kaggle)  \n"
    "**Scope:** Delivered orders from Jan 2017 to Aug 2018 (109,872 line items across 96,203 orders)."
)

mask_date = (df_raw["order_purchase_date"] >= start_date) & (df_raw["order_purchase_date"] <= end_date)
mask_cat = df_raw["product_category_name_english"].isin(selected_categories)
df_filtered = df_raw[mask_date & mask_cat].copy()

# Deduplicate to order level so multi-item orders do not skew delivery or review metrics.
df_orders = df_filtered.drop_duplicates(subset=["order_id"]).copy()

st.markdown(
    """
<div class="main-banner">
    <h1>E-Commerce Performance Dashboard</h1>
    <p>Sales trends, product category Pareto (80/20), and delivery impact on customer satisfaction across Olist Marketplace.</p>
</div>
""",
    unsafe_allow_html=True,
)

if df_filtered.empty or df_orders.empty:
    st.warning("No orders match the active filters. Adjust the date range or product categories in the sidebar.")
    st.stop()

total_revenue = df_filtered["total_order_value"].sum()
total_orders = df_orders["order_id"].nunique()
aov = total_revenue / total_orders if total_orders > 0 else 0

avg_delivery_days = df_orders["actual_delivery_days"].mean()
median_delivery_days = df_orders["actual_delivery_days"].median()
on_time_pct = (~df_orders["is_delayed"]).mean() * 100

df_reviewed = df_orders.dropna(subset=["review_score"]).copy()
avg_review_score = df_reviewed["review_score"].mean() if not df_reviewed.empty else None

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric(
    "Total Net Revenue",
    fmt_number(total_revenue, is_currency=True),
    help="Sum of product price and freight across delivered items.",
)
kpi2.metric(
    "Delivered Orders",
    fmt_number(total_orders),
    help=f"Unique delivered orders ({fmt_number(len(df_filtered))} line items).",
)
kpi3.metric(
    "Average Order Value",
    fmt_number(aov, is_currency=True, decimals=2),
    help="Total net revenue divided by unique delivered orders.",
)
kpi4.metric(
    "Avg Delivery Time",
    f"{fmt_number(avg_delivery_days, decimals=1)} Days" if pd.notna(avg_delivery_days) else "-",
    help=f"Mean purchase-to-delivery duration. Median: {fmt_number(median_delivery_days, decimals=1)} days.",
)
kpi5.metric(
    "Avg Review Score",
    f"{fmt_number(avg_review_score, decimals=2)} / 5.0" if avg_review_score is not None else "-",
    help=f"Mean customer rating on a 1 to 5 scale ({fmt_number(on_time_pct, decimals=1)}% delivered on time).",
)

st.markdown(
    f"""
<div class="metadata-strip">
    <span><strong>Median Delivery Time:</strong> {fmt_number(median_delivery_days, decimals=1)} Days</span>
    <span><strong>On-Time Delivery Rate:</strong> <span class="text-ontime">{fmt_number(on_time_pct, decimals=1)}%</span></span>
    <span><strong>Total Items Sold:</strong> {fmt_number(len(df_filtered))} Items</span>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)

st.subheader("1. Monthly Revenue and Growth Dynamics")
st.caption("Monthly net revenue, delivered order count, and month-over-month growth rates.")

monthly_agg = (
    df_filtered.groupby("order_year_month")
    .agg(revenue=("total_order_value", "sum"), orders=("order_id", "nunique"))
    .reset_index()
)
monthly_agg["mom_growth"] = monthly_agg["revenue"].pct_change() * 100
monthly_agg["aov"] = monthly_agg["revenue"] / monthly_agg["orders"]

col1, col2 = st.columns([7, 5])

with col1:
    tab_trend, tab_aov_trend = st.tabs(["Revenue & Order Volume", "Average Order Value (AOV)"])

    with tab_trend:
        fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
        fig_trend.add_trace(
            go.Scatter(
                x=monthly_agg["order_year_month"],
                y=monthly_agg["revenue"],
                name="Net Revenue (BRL)",
                mode="lines+markers",
                line=dict(color="#38BDF8", width=3),
                marker=dict(size=7, color="#38BDF8"),
                hovertemplate="Month: %{x}<br>Revenue: R$ %{y:,.2f}<extra></extra>",
            ),
            secondary_y=False,
        )
        fig_trend.add_trace(
            go.Scatter(
                x=monthly_agg["order_year_month"],
                y=monthly_agg["orders"],
                name="Delivered Orders",
                mode="lines+markers",
                line=dict(color="#34D399", width=2, dash="dash"),
                marker=dict(size=6, symbol="square", color="#34D399"),
                hovertemplate="Month: %{x}<br>Orders: %{y:,}<extra></extra>",
            ),
            secondary_y=True,
        )

        if "2017-11" in monthly_agg["order_year_month"].values:
            bf_row = monthly_agg[monthly_agg["order_year_month"] == "2017-11"].iloc[0]
            bf_rev_str = f"R$ {fmt_number(bf_row['revenue'] / 1e6, decimals=2)}M"
            bf_mom_val = bf_row["mom_growth"]
            bf_mom_str = f" (+{fmt_number(bf_mom_val, decimals=1)}% MoM)" if pd.notna(bf_mom_val) else ""

            fig_trend.add_annotation(
                x="2017-11",
                y=bf_row["revenue"],
                text=f"<b>Black Friday Peak (Nov 2017)</b><br>{bf_rev_str}{bf_mom_str}",
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
                font=dict(color="#F8FAFC", size=10),
            )

        apply_plot_theme(fig_trend, title="Monthly Net Revenue vs Order Volume", x_title="Order Month", y_title="Net Revenue (BRL)")
        fig_trend.update_layout(
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        fig_trend.update_yaxes(title_text="Total Orders", secondary_y=True, showgrid=False, automargin=True)
        st.plotly_chart(fig_trend, width="stretch")

    with tab_aov_trend:
        fig_aov_trend = go.Figure()
        fig_aov_trend.add_trace(
            go.Scatter(
                x=monthly_agg["order_year_month"],
                y=monthly_agg["aov"],
                name="Average Order Value",
                mode="lines+markers",
                line=dict(color="#38BDF8", width=2.5),
                marker=dict(size=6, color="#38BDF8"),
                hovertemplate="Month: %{x}<br>AOV: R$ %{y:,.2f}<extra></extra>",
            )
        )
        if not monthly_agg.empty:
            mean_aov_val = monthly_agg["aov"].mean()
            fig_aov_trend.add_hline(
                y=mean_aov_val,
                line_dash="dash",
                line_color="#94A3B8",
                line_width=1.5,
                annotation_text=f"Mean: {fmt_number(mean_aov_val, is_currency=True, decimals=1)}",
                annotation_position="bottom right",
            )
        apply_plot_theme(fig_aov_trend, title="Monthly Average Order Value (AOV)", x_title="Order Month", y_title="AOV (BRL)")
        fig_aov_trend.update_layout(hovermode="x unified")
        st.plotly_chart(fig_aov_trend, width="stretch")
        st.caption("Dashed line marks the period mean AOV. Flat AOV indicates revenue growth came from order volume rather than price increases.")

with col2:
    mom_vals = monthly_agg["mom_growth"]
    colors_mom = []
    hover_texts = []
    for idx, val in enumerate(mom_vals):
        if idx == 0 or pd.isna(val):
            colors_mom.append("#64748B")
            hover_texts.append("Baseline Month")
        elif val >= 0:
            colors_mom.append("#34D399")
            hover_texts.append(f"+{fmt_number(val, decimals=2)}%")
        else:
            colors_mom.append("#EF4444")
            hover_texts.append(f"{fmt_number(val, decimals=2)}%")

    fig_mom = go.Figure()
    fig_mom.add_trace(
        go.Bar(
            x=monthly_agg["order_year_month"],
            y=mom_vals.fillna(0),
            marker_color=colors_mom,
            customdata=hover_texts,
            hovertemplate="Month: %{x}<br>MoM Growth: %{customdata}<extra></extra>",
        )
    )
    fig_mom.add_hline(y=0, line_dash="solid", line_color="#94A3B8", line_width=1)
    apply_plot_theme(
        fig_mom,
        title="Month-over-Month Growth (MoM %)",
        x_title="Order Month",
        y_title="MoM Growth (%)",
        margin=dict(l=65, r=30, t=55, b=45),
    )
    st.plotly_chart(fig_mom, width="stretch")
    st.caption("First month acts as the baseline. Mid-month filter cutoffs reflect partial volume in the opening month.")

peak_row = monthly_agg.loc[monthly_agg["revenue"].idxmax()]
peak_month = peak_row["order_year_month"]
peak_rev = fmt_number(peak_row["revenue"], is_currency=True)
first_month = monthly_agg.iloc[0]["order_year_month"]
first_rev = fmt_number(monthly_agg.iloc[0]["revenue"], is_currency=True)
avg_aov_range = f"{fmt_number(monthly_agg['aov'].min(), is_currency=True)} to {fmt_number(monthly_agg['aov'].max(), is_currency=True)}"

st.markdown(
    f"""
<div class="insight-card">
    <div class="insight-card-title">Key Insights: Sales Growth and Seasonal Patterns</div>
    <div class="insight-card-body">
        <ul>
            <li>Monthly revenue grew from <b>{first_rev}</b> ({first_month}) to a peak of <b>{peak_rev}</b> in {peak_month}.</li>
            <li>The November 2017 spike reflects Black Friday demand, followed by post-holiday normalization in December.</li>
            <li>Average Order Value held between <b>{avg_aov_range}</b> across months, showing that higher order counts drove expansion.</li>
        </ul>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)

st.subheader("2. Product Category Portfolio: 80/20 Pareto Analysis")
st.caption("Identifies the core categories contributing 80% of cumulative revenue and compares their AOV.")

cat_agg = (
    df_filtered.groupby("product_category_name_english")
    .agg(
        total_revenue=("total_order_value", "sum"),
        total_orders=("order_id", "nunique"),
        total_items=("product_id", "count"),
    )
    .reset_index()
)
cat_agg["aov"] = cat_agg["total_revenue"] / cat_agg["total_orders"]
cat_agg = cat_agg.sort_values(by="total_revenue", ascending=False).reset_index(drop=True)
cat_agg["cum_revenue"] = cat_agg["total_revenue"].cumsum()
cat_agg["cum_pct"] = (cat_agg["cum_revenue"] / cat_agg["total_revenue"].sum()) * 100

total_cats_count = len(cat_agg)
core_cats_count = (cat_agg["cum_pct"] <= 80).sum() + 1 if total_cats_count > 0 else 0

col_p1, col_p2 = st.columns([7, 5])

with col_p1:
    # Bypass slider when 5 or fewer categories are active to prevent Streamlit min/max errors.
    if total_cats_count <= 1:
        top_n = total_cats_count
        st.info(f"Showing 1 selected category: **{cat_agg.iloc[0]['product_category_name_english']}**")
    elif total_cats_count <= 5:
        top_n = total_cats_count
        st.caption(f"Showing all {total_cats_count} selected categories.")
    else:
        slider_max = min(30, total_cats_count)
        slider_default = min(15, total_cats_count)
        top_n = st.slider("Display Top N Categories", min_value=1, max_value=slider_max, value=slider_default)

    df_pareto_display = cat_agg.head(top_n).copy()
    colors_pareto = ["#3B82F6" if i < core_cats_count else "#64748B" for i in range(len(df_pareto_display))]

    fig_pareto = make_subplots(specs=[[{"secondary_y": True}]])
    fig_pareto.add_trace(
        go.Bar(
            x=df_pareto_display["product_category_name_english"],
            y=df_pareto_display["total_revenue"],
            name="Revenue (BRL)",
            marker_color=colors_pareto,
            hovertemplate="Category: %{x}<br>Revenue: R$ %{y:,.2f}<extra></extra>",
        ),
        secondary_y=False,
    )
    fig_pareto.add_trace(
        go.Scatter(
            x=df_pareto_display["product_category_name_english"],
            y=df_pareto_display["cum_pct"],
            name="Cumulative (%)",
            mode="lines+markers",
            line=dict(color="#F87171", width=2.5),
            marker=dict(size=6, color="#F87171"),
            hovertemplate="Category: %{x}<br>Cumulative: %{y:.1f}%<extra></extra>",
        ),
        secondary_y=True,
    )
    fig_pareto.add_hline(
        y=80,
        line_dash="dash",
        line_color="#F87171",
        secondary_y=True,
        annotation_text="80% Pareto Cutoff",
        annotation_position="bottom right",
    )

    apply_plot_theme(fig_pareto, title=f"Top {top_n} Product Categories by Revenue (Pareto Curve)", y_title="Revenue (BRL)")
    fig_pareto.update_layout(
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig_pareto.update_xaxes(tickangle=-45)
    fig_pareto.update_yaxes(title_text="Cumulative (%)", secondary_y=True, range=[0, 105], showgrid=False, automargin=True)
    st.plotly_chart(fig_pareto, width="stretch")

with col_p2:
    top_cat_name = cat_agg.iloc[0]["product_category_name_english"] if total_cats_count > 0 else "-"
    top_cat_rev = fmt_number(cat_agg.iloc[0]["total_revenue"], is_currency=True) if total_cats_count > 0 else "-"
    core_pct_str = f"{(core_cats_count / total_cats_count) * 100:.1f}%" if total_cats_count > 0 else "-"

    st.markdown(
        f"""
    <div class="summary-card">
        <h4>Pareto Principle Summary</h4>
        <p>
            <b>{core_cats_count} of {total_cats_count} categories ({core_pct_str})</b> generate <b>80% of total revenue</b> in the current selection.<br/>
            Top category: <b>{top_cat_name}</b> ({top_cat_rev}).
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    fig_aov = px.bar(
        df_pareto_display.sort_values(by="aov", ascending=True),
        x="aov",
        y="product_category_name_english",
        orientation="h",
        labels={"aov": "AOV (BRL)", "product_category_name_english": "Product Category"},
        color="aov",
        color_continuous_scale="Blues",
    )
    apply_plot_theme(
        fig_aov,
        title=f"Average Order Value by Category (Top {top_n})",
        x_title="AOV (BRL)",
        margin=dict(l=85, r=30, t=55, b=45),
    )
    fig_aov.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig_aov, width="stretch")

top_3_names = (
    ", ".join([f"<code>{cat}</code>" for cat in cat_agg.head(3)["product_category_name_english"].tolist()])
    if total_cats_count >= 3
    else f"<code>{top_cat_name}</code>"
)

st.markdown(
    f"""
<div class="insight-card">
    <div class="insight-card-title">Key Insights: Product Portfolio</div>
    <div class="insight-card-body">
        <ul>
            <li>Across {total_cats_count} active categories, <b>{core_cats_count} categories ({core_pct_str})</b> generate 80% of revenue, led by {top_3_names}.</li>
            <li>Order values differ across categories: higher-priced items such as watches and computers lift spend per order, while household staples such as bed, bath, and table drive purchase frequency.</li>
            <li>Prioritize stock availability and campaign placement for these core categories, and bundle everyday staples with higher-priced items.</li>
        </ul>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)

st.subheader("3. Delivery Performance and Customer Satisfaction")
st.caption("Evaluates how delivery duration and calendar delays relate to review scores on unique orders.")

ontime_df = df_reviewed[~df_reviewed["is_delayed"]]
late_df = df_reviewed[df_reviewed["is_delayed"]]

on_time_avg = ontime_df["review_score"].mean() if not ontime_df.empty else None
late_avg = late_df["review_score"].mean() if not late_df.empty else None
satisfaction_gap = (on_time_avg - late_avg) if (on_time_avg is not None and late_avg is not None) else None

corr_pearson = df_reviewed["actual_delivery_days"].corr(df_reviewed["review_score"], method="pearson") if len(df_reviewed) > 1 else None
corr_spearman = df_reviewed["actual_delivery_days"].rank().corr(df_reviewed["review_score"].rank()) if len(df_reviewed) > 1 else None

col_d1, col_d2 = st.columns([6, 6])

with col_d1:
    tab_rating, tab_prop, tab_dist = st.tabs([
        "Average Review Score",
        "1-Star Review Rate",
        "Rating Distribution (1 to 5)",
    ])

    n_ontime = len(ontime_df)
    n_late = len(late_df)

    with tab_rating:
        gap_labels = [
            f"On-Time or Early\n({fmt_number(n_ontime)} orders)",
            f"Delayed Past Estimate\n({fmt_number(n_late)} orders)",
        ]
        gap_values = [on_time_avg if on_time_avg is not None else 0, late_avg if late_avg is not None else 0]
        gap_texts = [
            f"{fmt_number(on_time_avg, decimals=2)} / 5.0" if on_time_avg is not None else "No Data",
            f"{fmt_number(late_avg, decimals=2)} / 5.0" if late_avg is not None else "No Data",
        ]

        gap_data = pd.DataFrame({
            "Delivery Status": gap_labels,
            "Average Rating": gap_values,
            "Text": gap_texts,
        })
        fig_gap = px.bar(
            gap_data,
            x="Delivery Status",
            y="Average Rating",
            text="Text",
            color="Delivery Status",
            color_discrete_sequence=["#10B981", "#EF4444"],
        )
        fig_gap.update_traces(textposition="outside", width=0.45)
        apply_plot_theme(
            fig_gap,
            title="Customer Ratings: On-Time vs Delayed Deliveries",
            y_title="Average Rating (1-5 Stars)",
            margin=dict(l=65, r=30, t=55, b=45),
        )
        fig_gap.update_layout(yaxis_range=[0, 5.4], showlegend=False)
        fig_gap.update_xaxes(showgrid=False)
        st.plotly_chart(fig_gap, width="stretch")

    with tab_prop:
        p_ontime_1_val = (ontime_df["review_score"] == 1).mean() * 100 if not ontime_df.empty else 0.0
        p_late_1_val = (late_df["review_score"] == 1).mean() * 100 if not late_df.empty else 0.0

        df_prop = pd.DataFrame({
            "Delivery Status": [
                f"On-Time\n({fmt_number(n_ontime)} orders)",
                f"Delayed\n({fmt_number(n_late)} orders)",
            ],
            "1-Star Review Share (%)": [p_ontime_1_val, p_late_1_val],
            "Text": [f"{fmt_number(p_ontime_1_val, decimals=1)}%", f"{fmt_number(p_late_1_val, decimals=1)}%"],
        })
        fig_prop = px.bar(
            df_prop,
            x="Delivery Status",
            y="1-Star Review Share (%)",
            text="Text",
            color="Delivery Status",
            color_discrete_sequence=["#10B981", "#EF4444"],
        )
        fig_prop.update_traces(textposition="outside", width=0.45)
        apply_plot_theme(
            fig_prop,
            title="Share of 1-Star Reviews by Delivery Status",
            y_title="Orders with 1-Star Review (%)",
            margin=dict(l=65, r=30, t=55, b=45),
        )
        fig_prop.update_layout(yaxis_range=[0, max(65, p_late_1_val * 1.15)], showlegend=False)
        fig_prop.update_xaxes(showgrid=False)
        st.plotly_chart(fig_prop, width="stretch")
        if p_ontime_1_val > 0 and p_late_1_val > 0:
            st.caption(
                f"Delayed orders receive 1-star reviews at {p_late_1_val / p_ontime_1_val:.1f}x the rate of on-time orders "
                f"({fmt_number(p_late_1_val, decimals=1)}% vs {fmt_number(p_ontime_1_val, decimals=1)}%)."
            )
        elif not late_df.empty:
            st.caption(f"Delayed orders record a {fmt_number(p_late_1_val, decimals=1)}% 1-star review rate.")

    with tab_dist:
        dist_data = []
        for status_label, sub_df in [("On-Time", ontime_df), ("Delayed", late_df)]:
            if not sub_df.empty:
                counts = sub_df["review_score"].round().value_counts(normalize=True) * 100
                for score in [1, 2, 3, 4, 5]:
                    pct_val = counts.get(float(score), 0.0)
                    dist_data.append({
                        "Delivery Status": status_label,
                        "Star Rating": f"{score} Star" if score == 1 else f"{score} Stars",
                        "Percentage": round(pct_val, 1),
                        "Label Text": f"{pct_val:.1f}%",
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
                labels={"Percentage": "Share of Orders (%)", "Star Rating": "Review Rating"},
            )
            fig_dist.update_traces(textposition="outside")
            apply_plot_theme(
                fig_dist,
                title="Review Rating Breakdown: On-Time vs Delayed",
                y_title="Share of Orders (%)",
                margin=dict(l=65, r=30, t=55, b=45),
            )
            max_p = df_chart_dist["Percentage"].max()
            fig_dist.update_layout(
                yaxis_range=[0, max(75, max_p * 1.18)],
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            )
            st.plotly_chart(fig_dist, width="stretch")
            ontime_5star = (ontime_df["review_score"].round() == 5).mean() * 100 if not ontime_df.empty else 0.0
            late_1star_dist = (late_df["review_score"].round() == 1).mean() * 100 if not late_df.empty else 0.0
            st.caption(
                f"On-time deliveries earn 5 stars in {fmt_number(ontime_5star, decimals=1)}% of orders, "
                f"whereas delayed deliveries fall to 1 star in {fmt_number(late_1star_dist, decimals=1)}%."
            )
        else:
            st.info("No review ratings available for the current filter selection.")

with col_d2:
    if not df_reviewed.empty:
        # Cap y-axis at 45 days (covers >95% of orders) to keep quartiles readable.
        fig_box = px.box(
            df_reviewed,
            x="review_score",
            y="actual_delivery_days",
            labels={"review_score": "Review Score (1 to 5)", "actual_delivery_days": "Actual Delivery Time (Days)"},
            points=False,
        )
        fig_box.update_traces(marker_color="#38BDF8")
        apply_plot_theme(
            fig_box,
            title="Delivery Days Distribution by Review Score",
            x_title="Customer Review Score (1 to 5)",
            y_title="Delivery Time (Days)",
            margin=dict(l=65, r=30, t=55, b=45),
        )
        fig_box.update_layout(yaxis_range=[0, 45], showlegend=False)
        st.plotly_chart(fig_box, width="stretch")
        st.caption("Y-axis capped at 45 days (covering over 95% of orders) to keep quartile comparisons readable.")
    else:
        st.info("No review data available to plot delivery duration quartiles.")

c_m1, c_m2, c_m3 = st.columns(3)
c_m1.metric(
    "Satisfaction Gap",
    f"-{fmt_number(satisfaction_gap, decimals=2)} stars" if satisfaction_gap is not None else "-",
    help="Difference in mean review rating between on-time and delayed orders.",
)
c_m2.metric(
    "Delivery vs Rating Correlation",
    f"r = {fmt_number(corr_pearson, decimals=3)}" if corr_pearson is not None else "-",
    help=(
        f"Pearson r = {fmt_number(corr_pearson, decimals=3)} | "
        f"Spearman r_s = {fmt_number(corr_spearman, decimals=3)} "
        f"(n = {fmt_number(len(df_reviewed))} unique orders)."
    ) if corr_pearson is not None else "Insufficient reviewed orders to compute correlation.",
)
c_m3.metric(
    "Delivery Performance",
    f"{fmt_number(on_time_pct, decimals=1)}% On-Time",
    help=(
        f"Out of {fmt_number(len(df_orders))} unique orders, {fmt_number(df_orders['is_delayed'].sum())} "
        f"({fmt_number(df_orders['is_delayed'].mean() * 100, decimals=1)}%) arrived past the estimated date."
    ),
)

on_time_str = f"{fmt_number(on_time_avg, decimals=2)} / 5.0" if on_time_avg is not None else "N/A"
late_str = f"{fmt_number(late_avg, decimals=2)} / 5.0" if late_avg is not None else "N/A"
gap_str = f"-{fmt_number(satisfaction_gap, decimals=2)} stars" if satisfaction_gap is not None else "N/A"
ontime_1star = fmt_number((ontime_df["review_score"] == 1).mean() * 100, decimals=1) if not ontime_df.empty else "0.0"
late_1star = fmt_number((late_df["review_score"] == 1).mean() * 100, decimals=1) if not late_df.empty else "0.0"
corr_p_str = fmt_number(corr_pearson, decimals=3) if corr_pearson is not None else "N/A"
corr_s_str = fmt_number(corr_spearman, decimals=3) if corr_spearman is not None else "N/A"

st.markdown(
    f"""
<div class="insight-card">
    <div class="insight-card-title">Key Insights: Delivery Timelines and Customer Satisfaction</div>
    <div class="insight-card-body">
        <ul>
            <li>On-time orders average <b>{on_time_str}</b> compared to <b>{late_str}</b> for delayed orders (a gap of <b>{gap_str}</b>).</li>
            <li>The 1-star review rate climbs from <b>{ontime_1star}%</b> on time to <b>{late_1star}%</b> when an order passes its estimated delivery date.</li>
            <li>Longer delivery times correlate with lower ratings (Pearson r = {corr_p_str}, Spearman r_s = {corr_s_str}), with the promised arrival date acting as the main customer threshold.</li>
        </ul>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)

st.subheader("4. Business Recommendations")
st.caption("Operational priorities for commercial, merchandising, and logistics teams.")

col_a1, col_a2, col_a3 = st.columns(3)

with col_a1:
    st.markdown(
        f"""
    <div class="playbook-card">
        <h4 class="playbook-title">Commercial & Growth</h4>
        <ul class="playbook-list">
            <li>Launch pre-holiday promotions in October to build early demand and ease November Black Friday courier bottlenecks.</li>
            <li>Focus revenue growth on customer acquisition and order volume, since AOV remains steady near {fmt_number(aov, is_currency=True, decimals=0)}.</li>
            <li>Run re-engagement offers in December and January to convert first-time seasonal buyers into repeat customers.</li>
        </ul>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col_a2:
    st.markdown(
        """
    <div class="playbook-card">
        <h4 class="playbook-title">Product Portfolio & Merchandising</h4>
        <ul class="playbook-list">
            <li>Protect inventory availability and primary storefront visibility for the core categories driving 80% of revenue.</li>
            <li>Bundle high-frequency everyday items with higher-priced products to lift average basket value.</li>
            <li>Audit low-turnover long-tail categories periodically to trim catalog overhead without affecting revenue.</li>
        </ul>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col_a3:
    st.markdown(
        """
    <div class="playbook-card">
        <h4 class="playbook-title">Logistics & Customer Experience</h4>
        <ul class="playbook-list">
            <li>Add a 2 to 3 day buffer to delivery estimates on long-distance routes so promised arrival dates remain realistic.</li>
            <li>Send proactive delay alerts with updated tracking and goodwill credits as soon as transit exceptions occur.</li>
            <li>Track merchant dispatch times and carrier SLA performance on high-delay corridors.</li>
        </ul>
    </div>
    """,
        unsafe_allow_html=True,
    )

st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)

st.subheader("5. Data Exploration and Export")
st.caption("Inspect transaction samples, review summary tables, and download filtered CSV files.")

with st.expander("Open Data Exploration and CSV Export", expanded=False):
    tab_sample, tab_cat_table, tab_monthly_table = st.tabs([
        "Transaction Sample (10 Rows)",
        "Category Summary",
        "Monthly Trends",
    ])

    with tab_sample:
        display_cols = [
            "order_id",
            "order_purchase_timestamp",
            "product_category_name_english",
            "price",
            "freight_value",
            "total_order_value",
            "actual_delivery_days",
            "is_delayed",
            "review_score",
        ]
        st.dataframe(df_filtered[display_cols].head(10), hide_index=True)
        csv_sample = df_filtered[display_cols].to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Filtered Transactions (CSV)",
            data=csv_sample,
            file_name="filtered_ecommerce_transactions.csv",
            mime="text/csv",
            help="Download filtered line items matching the active sidebar filters.",
        )

    with tab_cat_table:
        cat_export = cat_agg[["product_category_name_english", "total_revenue", "total_orders", "total_items", "aov", "cum_pct"]].copy()
        cat_export.columns = ["Product Category", "Total Revenue (BRL)", "Total Orders", "Total Items", "AOV (BRL)", "Cumulative (%)"]
        st.dataframe(cat_export.head(30), hide_index=True)
        csv_cat = cat_export.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Category Pareto Summary (CSV)",
            data=csv_cat,
            file_name="category_pareto_summary.csv",
            mime="text/csv",
        )

    with tab_monthly_table:
        monthly_export = monthly_agg[["order_year_month", "revenue", "orders", "aov", "mom_growth"]].copy()
        monthly_export.columns = ["Year-Month", "Net Revenue (BRL)", "Total Orders", "AOV (BRL)", "MoM Growth (%)"]
        st.dataframe(monthly_export, hide_index=True)
        csv_monthly = monthly_export.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Monthly Trends (CSV)",
            data=csv_monthly,
            file_name="monthly_revenue_trend.csv",
            mime="text/csv",
        )

st.markdown(
    """
<div class="credit-container">
    <div>
        <div class="credit-author">Ilfa Antaries Yusuf Wijaya</div>
        <div class="credit-role">E-Commerce Analytics Project</div>
    </div>
    <div class="credit-contact">
        <span>Contact:</span>
        <a href="mailto:contact.areswijaya@gmail.com" class="credit-email">contact.areswijaya@gmail.com</a>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

st.caption("2026 E-Commerce Insight Dashboard. Built with Python, Streamlit, and Plotly.")
