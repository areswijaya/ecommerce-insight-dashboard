from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
TOP_CATEGORIES_DEFAULT = [
    "health_beauty",
    "watches_gifts",
    "bed_bath_table",
    "sports_leisure",
    "computers_accessories",
]

st.set_page_config(
    page_title="E-Commerce Insight Dashboard | Olist",
    layout="wide",
    initial_sidebar_state="expanded",
)

css_path = BASE_DIR / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def fmt_number(val, is_currency: bool = False, decimals: int = 0) -> str:
    """Format angka dengan pemisah ribuan koma dan awalan R$ opsional."""
    if val is None or pd.isna(val):
        return "-"
    try:
        val_float = float(val)
    except (ValueError, TypeError):
        return str(val)

    res = f"{val_float:,.0f}" if decimals == 0 else f"{val_float:,.{decimals}f}"
    return f"R$ {res}" if is_currency else res


def apply_plot_theme(fig, title="", x_title="", y_title="", margin=None):
    """Terapkan tata letak gelap transparan dan tipografi seragam pada grafik Plotly."""
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
    """Muat clean_orders.csv dari lokasi standar proyek."""
    candidates = [
        BASE_DIR.parent / "data" / "clean_orders.csv",
        Path("data") / "clean_orders.csv",
        Path("clean_orders.csv"),
    ]
    file_path = next((p for p in candidates if p.exists()), None)
    if not file_path:
        return None

    df = pd.read_csv(file_path)
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    df["order_purchase_date"] = df["order_purchase_timestamp"].dt.date
    df["order_delivered_customer_date"] = pd.to_datetime(df["order_delivered_customer_date"])
    df["order_estimated_delivery_date"] = pd.to_datetime(df["order_estimated_delivery_date"])
    df["is_delayed"] = df["is_delayed"].astype(bool)
    return df


def reset_filters():
    """Kembalikan seluruh filter sidebar ke pilihan awal."""
    prev = st.session_state.get("filter_reset_gen", 0)
    for prefix in ("filter_period_", "filter_dates_", "filter_all_cats_", "filter_cats_"):
        st.session_state.pop(f"{prefix}{prev}", None)
    st.session_state["filter_reset_gen"] = prev + 1


with st.spinner("Memuat dataset transaksi..."):
    df_raw = load_data()

if df_raw is None:
    st.error("File `data/clean_orders.csv` tidak ditemukan. Pastikan dataset bersih sudah dibuat oleh `notebook.ipynb`.")
    st.stop()

min_date = df_raw["order_purchase_date"].min()
max_date = df_raw["order_purchase_date"].max()
all_categories = sorted(df_raw["product_category_name_english"].dropna().unique().tolist())
total_orders_all = df_raw["order_id"].nunique()

gen = st.session_state.get("filter_reset_gen", 0)
st.sidebar.header("Filter Data")
st.sidebar.caption("Berlaku pada seluruh metrik dan grafik di dashboard.")

period_preset = st.sidebar.selectbox(
    "Periode Analisis",
    options=[
        "Semua Periode (Jan 2017 - Agu 2018)",
        "Tahun 2017 (Ekspansi & Puncak Black Friday)",
        "Tahun 2018 (Fase Stabil)",
        "Pilih Rentang Tanggal",
    ],
    index=0,
    key=f"filter_period_{gen}",
    help="Pilih periode cepat atau tentukan tanggal awal dan akhir sendiri.",
)

if period_preset == "Tahun 2017 (Ekspansi & Puncak Black Friday)":
    start_date = pd.to_datetime("2017-01-01").date()
    end_date = pd.to_datetime("2017-12-31").date()
    st.sidebar.caption(f"Periode: **{start_date.strftime('%d %b %Y')}** - **{end_date.strftime('%d %b %Y')}**")
elif period_preset == "Tahun 2018 (Fase Stabil)":
    start_date = pd.to_datetime("2018-01-01").date()
    end_date = pd.to_datetime("2018-08-31").date()
    st.sidebar.caption(f"Periode: **{start_date.strftime('%d %b %Y')}** - **{end_date.strftime('%d %b %Y')}**")
elif period_preset == "Pilih Rentang Tanggal":
    date_selection = st.sidebar.date_input(
        "Rentang Tanggal",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key=f"filter_dates_{gen}",
        help="Cakupan data: 1 Jan 2017 - 31 Agu 2018.",
    )
    if isinstance(date_selection, (tuple, list)):
        if len(date_selection) == 2:
            start_date, end_date = date_selection
        elif len(date_selection) == 1:
            start_date = end_date = date_selection[0]
            st.sidebar.info("Satu tanggal dipilih. Menampilkan transaksi pada hari tersebut.")
        else:
            start_date, end_date = min_date, max_date
    else:
        start_date = end_date = date_selection
else:
    start_date = min_date
    end_date = max_date
    st.sidebar.caption(
        f"Periode: **{start_date.strftime('%d %b %Y')}** - **{end_date.strftime('%d %b %Y')}** (20 Bulan)"
    )

all_categories_mode = st.sidebar.checkbox(
    f"Semua Kategori ({len(all_categories)} Aktif)",
    value=True,
    key=f"filter_all_cats_{gen}",
)
if all_categories_mode:
    selected_categories = all_categories
else:
    selected_categories = st.sidebar.multiselect(
        "Pilih Kategori Produk",
        options=all_categories,
        default=TOP_CATEGORIES_DEFAULT,
        key=f"filter_cats_{gen}",
        help="Pilih satu atau beberapa kategori untuk dibandingkan.",
    )

st.sidebar.button(
    "Reset Filter",
    on_click=reset_filters,
    key="reset_filters_btn",
    width="stretch",
)

mask_date = (df_raw["order_purchase_date"] >= start_date) & (df_raw["order_purchase_date"] <= end_date)
mask_cat = df_raw["product_category_name_english"].isin(selected_categories)
df_filtered = df_raw[mask_date & mask_cat].copy()

# Deduplikasi ke tingkat order_id agar pesanan multi-item tidak membobot ganda durasi kirim atau rating.
df_orders = df_filtered.drop_duplicates(subset=["order_id"]).copy()

st.sidebar.markdown(
    f'<div class="filter-status-box">Menampilkan <b>{len(df_orders):,}</b> '
    f'dari <b>{total_orders_all:,}</b> pesanan terkirim</div>',
    unsafe_allow_html=True,
)
st.sidebar.markdown(
    """
<div class="author-card">
<div class="author-label">Dibuat oleh</div>
<div class="author-name">Ilfa Antaries Yusuf Wijaya</div>
<div class="author-links">
<a href="mailto:contact.areswijaya@gmail.com" target="_blank" rel="noopener noreferrer">Email</a>
<a href="https://www.linkedin.com/in/areswijaya" target="_blank" rel="noopener noreferrer">LinkedIn</a>
<a href="https://github.com/areswijaya" target="_blank" rel="noopener noreferrer">GitHub</a>
</div>
</div>
    """,
    unsafe_allow_html=True,
)

filter_note_html = ""
if len(df_orders) != total_orders_all:
    filter_note_html = (
        f'<div class="header-filter-note">'
        f'Filter aktif: menampilkan {len(df_orders):,} dari {total_orders_all:,} pesanan terkirim.'
        f'</div>'
    )

st.markdown(
    f"""
<div class="main-banner">
    <h1>E-Commerce Insight Dashboard</h1>
    <p>Tren pendapatan bulanan, konsentrasi kategori Pareto (80/20), dan dampak ketepatan pengiriman terhadap rating pelanggan pada dataset Olist Marketplace (Jan 2017 - Agu 2018).</p>
    {filter_note_html}
</div>
""",
    unsafe_allow_html=True,
)

if df_filtered.empty or df_orders.empty:
    st.warning("Tidak ada pesanan yang cocok dengan filter aktif. Klik 'Reset Filter' atau ubah pilihan di sidebar.")
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
    "Total Pendapatan Bersih",
    fmt_number(total_revenue, is_currency=True),
    help="Total harga produk ditambah biaya kirim pada pesanan berstatus delivered.",
)
kpi2.metric(
    "Pesanan Terkirim",
    fmt_number(total_orders),
    help=f"Jumlah order_id unik ({fmt_number(len(df_filtered))} baris item terjual).",
)
kpi3.metric(
    "Rata-Rata Nilai Pesanan (AOV)",
    fmt_number(aov, is_currency=True, decimals=2),
    help="Total pendapatan bersih dibagi jumlah pesanan unik.",
)
kpi4.metric(
    "Rata-Rata Durasi Kirim",
    f"{fmt_number(avg_delivery_days, decimals=1)} Hari" if pd.notna(avg_delivery_days) else "-",
    help=f"Rata-rata waktu dari pembelian hingga diterima pelanggan. Median: {fmt_number(median_delivery_days, decimals=1)} hari.",
)
kpi5.metric(
    "Rata-Rata Skor Ulasan",
    f"{fmt_number(avg_review_score, decimals=2)} / 5.0" if avg_review_score is not None else "-",
    help=f"Rata-rata rating pelanggan skala 1-5 ({fmt_number(on_time_pct, decimals=1)}% pesanan tepat waktu).",
)

st.markdown(
    f"""
<div class="metadata-strip">
    <span><strong>Median Durasi Kirim:</strong> {fmt_number(median_delivery_days, decimals=1)} Hari</span>
    <span><strong>Ketepatan Pengiriman:</strong> <span class="text-ontime">{fmt_number(on_time_pct, decimals=1)}%</span></span>
    <span><strong>Total Item Terjual:</strong> {fmt_number(len(df_filtered))} Item</span>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)

st.subheader("1. Dinamika Pendapatan & Pertumbuhan Bulanan")
st.caption("Pergerakan pendapatan bersih bulanan, jumlah pesanan terkirim, dan laju pertumbuhan MoM.")

monthly_agg = (
    df_filtered.groupby("order_year_month")
    .agg(revenue=("total_order_value", "sum"), orders=("order_id", "nunique"))
    .reset_index()
)
monthly_agg["mom_growth"] = monthly_agg["revenue"].pct_change() * 100
monthly_agg["aov"] = monthly_agg["revenue"] / monthly_agg["orders"]

col1, col2 = st.columns([7, 5])

with col1:
    tab_trend, tab_aov_trend = st.tabs(["Pendapatan & Volume Pesanan", "Rata-Rata Nilai Pesanan (AOV)"])

    with tab_trend:
        fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
        fig_trend.add_trace(
            go.Scatter(
                x=monthly_agg["order_year_month"],
                y=monthly_agg["revenue"],
                name="Pendapatan Bersih (BRL)",
                mode="lines+markers",
                line=dict(color="#38BDF8", width=3),
                marker=dict(size=7, color="#38BDF8"),
                hovertemplate="Bulan: %{x}<br>Pendapatan: R$ %{y:,.2f}<extra></extra>",
            ),
            secondary_y=False,
        )
        fig_trend.add_trace(
            go.Scatter(
                x=monthly_agg["order_year_month"],
                y=monthly_agg["orders"],
                name="Pesanan Terkirim",
                mode="lines+markers",
                line=dict(color="#34D399", width=2, dash="dash"),
                marker=dict(size=6, symbol="square", color="#34D399"),
                hovertemplate="Bulan: %{x}<br>Pesanan: %{y:,}<extra></extra>",
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
                text=f"<b>Puncak Black Friday (Nov 2017)</b><br>{bf_rev_str}{bf_mom_str}",
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

        apply_plot_theme(
            fig_trend,
            title="Pendapatan Bersih Bulanan vs Volume Pesanan",
            x_title="Bulan Pesanan",
            y_title="Pendapatan Bersih (BRL)",
        )
        fig_trend.update_layout(
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        fig_trend.update_yaxes(title_text="Jumlah Pesanan", secondary_y=True, showgrid=False, automargin=True)
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
                hovertemplate="Bulan: %{x}<br>AOV: R$ %{y:,.2f}<extra></extra>",
            )
        )
        if not monthly_agg.empty:
            mean_aov_val = monthly_agg["aov"].mean()
            fig_aov_trend.add_hline(
                y=mean_aov_val,
                line_dash="dash",
                line_color="#94A3B8",
                line_width=1.5,
                annotation_text=f"Rata-rata: {fmt_number(mean_aov_val, is_currency=True, decimals=1)}",
                annotation_position="bottom right",
            )
        apply_plot_theme(fig_aov_trend, title="Rata-Rata Nilai Pesanan (AOV) Bulanan", x_title="Bulan Pesanan", y_title="AOV (BRL)")
        fig_aov_trend.update_layout(hovermode="x unified")
        st.plotly_chart(fig_aov_trend, width="stretch")
        st.caption("Garis putus-putus menandai rata-rata AOV periode aktif. AOV yang datar menunjukkan pertumbuhan omset berasal dari jumlah pesanan, bukan kenaikan harga.")

with col2:
    mom_vals = monthly_agg["mom_growth"]
    colors_mom = []
    hover_texts = []
    for idx, val in enumerate(mom_vals):
        if idx == 0 or pd.isna(val):
            colors_mom.append("#64748B")
            hover_texts.append("Bulan Dasar")
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
            hovertemplate="Bulan: %{x}<br>Pertumbuhan MoM: %{customdata}<extra></extra>",
        )
    )
    fig_mom.add_hline(y=0, line_dash="solid", line_color="#94A3B8", line_width=1)
    apply_plot_theme(
        fig_mom,
        title="Pertumbuhan Bulanan (MoM %)",
        x_title="Bulan Pesanan",
        y_title="Pertumbuhan MoM (%)",
        margin=dict(l=65, r=30, t=55, b=45),
    )
    st.plotly_chart(fig_mom, width="stretch")
    st.caption("Bulan pertama menjadi acuan dasar. Jika filter dimulai di tengah bulan, angka bulan awal hanya mencerminkan transaksi parsial.")

peak_row = monthly_agg.loc[monthly_agg["revenue"].idxmax()]
peak_month = peak_row["order_year_month"]
peak_rev = fmt_number(peak_row["revenue"], is_currency=True)
first_month = monthly_agg.iloc[0]["order_year_month"]
first_rev = fmt_number(monthly_agg.iloc[0]["revenue"], is_currency=True)
avg_aov_range = f"{fmt_number(monthly_agg['aov'].min(), is_currency=True)} sampai {fmt_number(monthly_agg['aov'].max(), is_currency=True)}"

st.markdown(
    f"""
<div class="insight-card">
    <div class="insight-card-title">Ringkasan Pertumbuhan & Pola Musiman</div>
    <div class="insight-card-body">
        <ul>
            <li>Pendapatan bulanan naik dari <b>{first_rev}</b> ({first_month}) hingga puncaknya <b>{peak_rev}</b> pada {peak_month}.</li>
            <li>Lonjakan November 2017 mencerminkan permintaan Black Friday, lalu kembali melandai pada Desember.</li>
            <li>AOV bertahan di kisaran <b>{avg_aov_range}</b>, menandakan ekspansi penjualan didorong penambahan volume pesanan.</li>
        </ul>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)

st.subheader("2. Portofolio Kategori Produk: Analisis Pareto 80/20")
st.caption("Memetakan kategori penyumbang 80% pendapatan kumulatif beserta perbedaan AOV antar-kategori.")

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
    # Lewati slider jika kategori aktif <= 5 agar rentang min/max st.slider tetap valid.
    if total_cats_count <= 1:
        top_n = total_cats_count
        st.info(f"Menampilkan 1 kategori terpilih: **{cat_agg.iloc[0]['product_category_name_english']}**")
    elif total_cats_count <= 5:
        top_n = total_cats_count
        st.caption(f"Menampilkan seluruh {total_cats_count} kategori terpilih.")
    else:
        slider_max = min(30, total_cats_count)
        slider_default = min(15, total_cats_count)
        top_n = st.slider("Tampilkan N Kategori Teratas", min_value=1, max_value=slider_max, value=slider_default)

    df_pareto_display = cat_agg.head(top_n).copy()
    colors_pareto = ["#3B82F6" if i < core_cats_count else "#64748B" for i in range(len(df_pareto_display))]

    fig_pareto = make_subplots(specs=[[{"secondary_y": True}]])
    fig_pareto.add_trace(
        go.Bar(
            x=df_pareto_display["product_category_name_english"],
            y=df_pareto_display["total_revenue"],
            name="Pendapatan (BRL)",
            marker_color=colors_pareto,
            hovertemplate="Kategori: %{x}<br>Pendapatan: R$ %{y:,.2f}<extra></extra>",
        ),
        secondary_y=False,
    )
    fig_pareto.add_trace(
        go.Scatter(
            x=df_pareto_display["product_category_name_english"],
            y=df_pareto_display["cum_pct"],
            name="Kumulatif (%)",
            mode="lines+markers",
            line=dict(color="#F87171", width=2.5),
            marker=dict(size=6, color="#F87171"),
            hovertemplate="Kategori: %{x}<br>Kumulatif: %{y:.1f}%<extra></extra>",
        ),
        secondary_y=True,
    )
    fig_pareto.add_hline(
        y=80,
        line_dash="dash",
        line_color="#F87171",
        secondary_y=True,
        annotation_text="Batas Pareto 80%",
        annotation_position="bottom right",
    )

    apply_plot_theme(fig_pareto, title=f"Top {top_n} Kategori Produk berdasarkan Pendapatan (Kurva Pareto)", y_title="Pendapatan (BRL)")
    fig_pareto.update_layout(
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig_pareto.update_xaxes(tickangle=-45)
    fig_pareto.update_yaxes(title_text="Kumulatif (%)", secondary_y=True, range=[0, 105], showgrid=False, automargin=True)
    st.plotly_chart(fig_pareto, width="stretch")

with col_p2:
    top_cat_name = cat_agg.iloc[0]["product_category_name_english"] if total_cats_count > 0 else "-"
    top_cat_rev = fmt_number(cat_agg.iloc[0]["total_revenue"], is_currency=True) if total_cats_count > 0 else "-"
    core_pct_str = f"{(core_cats_count / total_cats_count) * 100:.1f}%" if total_cats_count > 0 else "-"

    st.markdown(
        f"""
    <div class="summary-card">
        <h4>Ringkasan Prinsip Pareto</h4>
        <p>
            <b>{core_cats_count} dari {total_cats_count} kategori ({core_pct_str})</b> menyumbang <b>80% total pendapatan</b> pada pilihan saat ini.<br/>
            Kategori teratas: <b>{top_cat_name}</b> ({top_cat_rev}).
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
        labels={"aov": "AOV (BRL)", "product_category_name_english": "Kategori Produk"},
        color="aov",
        color_continuous_scale="Blues",
    )
    apply_plot_theme(
        fig_aov,
        title=f"Rata-Rata Nilai Pesanan per Kategori (Top {top_n})",
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
    <div class="insight-card-title">Ringkasan Portofolio Produk</div>
    <div class="insight-card-body">
        <ul>
            <li>Dari {total_cats_count} kategori aktif, <b>{core_cats_count} kategori ({core_pct_str})</b> menyumbang 80% pendapatan dengan kontributor utama {top_3_names}.</li>
            <li>Nilai belanja berbeda antarsegmen: kategori seperti jam tangan dan komputer mendorong nominal per transaksi, sedangkan kebutuhan rumah tangga menopang frekuensi pesanan.</li>
            <li>Fokuskan ketersediaan stok dan slot promosi pada kategori inti, lalu padukan produk berfrekuensi tinggi dengan barang bernilai lebih tinggi.</li>
        </ul>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)

st.subheader("3. Kinerja Pengiriman & Kepuasan Pelanggan")
st.caption("Mengukur hubungan durasi pengiriman riil dan keterlambatan kalender terhadap skor ulasan pada pesanan unik.")

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
        "Rata-Rata Skor Ulasan",
        "Persentase Ulasan Bintang 1",
        "Distribusi Skor Ulasan (1-5)",
    ])

    n_ontime = len(ontime_df)
    n_late = len(late_df)

    with tab_rating:
        gap_labels = [
            f"Tepat Waktu / Lebih Awal\n({fmt_number(n_ontime)} pesanan)",
            f"Terlambat dari Estimasi\n({fmt_number(n_late)} pesanan)",
        ]
        gap_values = [on_time_avg if on_time_avg is not None else 0, late_avg if late_avg is not None else 0]
        gap_texts = [
            f"{fmt_number(on_time_avg, decimals=2)} / 5.0" if on_time_avg is not None else "Tidak Ada Data",
            f"{fmt_number(late_avg, decimals=2)} / 5.0" if late_avg is not None else "Tidak Ada Data",
        ]

        gap_data = pd.DataFrame({
            "Status Pengiriman": gap_labels,
            "Rata-Rata Rating": gap_values,
            "Label": gap_texts,
        })
        fig_gap = px.bar(
            gap_data,
            x="Status Pengiriman",
            y="Rata-Rata Rating",
            text="Label",
            color="Status Pengiriman",
            color_discrete_sequence=["#10B981", "#EF4444"],
        )
        fig_gap.update_traces(textposition="outside", width=0.45)
        apply_plot_theme(
            fig_gap,
            title="Rata-Rata Rating: Tepat Waktu vs Terlambat",
            y_title="Rata-Rata Rating (1-5 Bintang)",
            margin=dict(l=65, r=30, t=55, b=45),
        )
        fig_gap.update_layout(yaxis_range=[0, 5.4], showlegend=False)
        fig_gap.update_xaxes(showgrid=False)
        st.plotly_chart(fig_gap, width="stretch")

    with tab_prop:
        p_ontime_1_val = (ontime_df["review_score"] == 1).mean() * 100 if not ontime_df.empty else 0.0
        p_late_1_val = (late_df["review_score"] == 1).mean() * 100 if not late_df.empty else 0.0

        df_prop = pd.DataFrame({
            "Status Pengiriman": [
                f"Tepat Waktu\n({fmt_number(n_ontime)} pesanan)",
                f"Terlambat\n({fmt_number(n_late)} pesanan)",
            ],
            "Proporsi Bintang 1 (%)": [p_ontime_1_val, p_late_1_val],
            "Label": [f"{fmt_number(p_ontime_1_val, decimals=1)}%", f"{fmt_number(p_late_1_val, decimals=1)}%"],
        })
        fig_prop = px.bar(
            df_prop,
            x="Status Pengiriman",
            y="Proporsi Bintang 1 (%)",
            text="Label",
            color="Status Pengiriman",
            color_discrete_sequence=["#10B981", "#EF4444"],
        )
        fig_prop.update_traces(textposition="outside", width=0.45)
        apply_plot_theme(
            fig_prop,
            title="Proporsi Ulasan Bintang 1 menurut Status Pengiriman",
            y_title="Pesanan dengan Bintang 1 (%)",
            margin=dict(l=65, r=30, t=55, b=45),
        )
        fig_prop.update_layout(yaxis_range=[0, max(65, p_late_1_val * 1.15)], showlegend=False)
        fig_prop.update_xaxes(showgrid=False)
        st.plotly_chart(fig_prop, width="stretch")
        if p_ontime_1_val > 0 and p_late_1_val > 0:
            st.caption(
                f"Pesanan terlambat menerima ulasan bintang 1 sebesar {p_late_1_val / p_ontime_1_val:.1f}x lebih tinggi "
                f"dibanding pesanan tepat waktu ({fmt_number(p_late_1_val, decimals=1)}% vs {fmt_number(p_ontime_1_val, decimals=1)}%)."
            )
        elif not late_df.empty:
            st.caption(f"Proporsi ulasan bintang 1 pada pesanan terlambat mencapai {fmt_number(p_late_1_val, decimals=1)}%.")

    with tab_dist:
        dist_data = []
        for status_label, sub_df in [("Tepat Waktu", ontime_df), ("Terlambat", late_df)]:
            if not sub_df.empty:
                counts = sub_df["review_score"].round().value_counts(normalize=True) * 100
                for score in [1, 2, 3, 4, 5]:
                    pct_val = counts.get(float(score), 0.0)
                    dist_data.append({
                        "Status Pengiriman": status_label,
                        "Skor Bintang": f"{score} Bintang",
                        "Persentase": round(pct_val, 1),
                        "Label": f"{pct_val:.1f}%",
                    })

        df_chart_dist = pd.DataFrame(dist_data)
        if not df_chart_dist.empty:
            fig_dist = px.bar(
                df_chart_dist,
                x="Skor Bintang",
                y="Persentase",
                color="Status Pengiriman",
                barmode="group",
                color_discrete_map={"Tepat Waktu": "#10B981", "Terlambat": "#EF4444"},
                text="Label",
                labels={"Persentase": "Proporsi Pesanan (%)", "Skor Bintang": "Skor Ulasan"},
            )
            fig_dist.update_traces(textposition="outside")
            apply_plot_theme(
                fig_dist,
                title="Distribusi Skor Ulasan: Tepat Waktu vs Terlambat",
                y_title="Proporsi Pesanan (%)",
                margin=dict(l=65, r=30, t=55, b=45),
            )
            max_p = df_chart_dist["Persentase"].max()
            fig_dist.update_layout(
                yaxis_range=[0, max(75, max_p * 1.18)],
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            )
            st.plotly_chart(fig_dist, width="stretch")
            ontime_5star = (ontime_df["review_score"].round() == 5).mean() * 100 if not ontime_df.empty else 0.0
            late_1star_dist = (late_df["review_score"].round() == 1).mean() * 100 if not late_df.empty else 0.0
            st.caption(
                f"Pesanan tepat waktu memperoleh 5 bintang pada {fmt_number(ontime_5star, decimals=1)}% pesanan, "
                f"sedangkan pesanan terlambat turun ke 1 bintang pada {fmt_number(late_1star_dist, decimals=1)}%."
            )
        else:
            st.info("Tidak ada data ulasan untuk pilihan filter saat ini.")

with col_d2:
    if not df_reviewed.empty:
        # Batasi sumbu Y pada 45 hari (mencakup >95% pesanan) agar kuartil boxplot terbaca jelas.
        fig_box = px.box(
            df_reviewed,
            x="review_score",
            y="actual_delivery_days",
            labels={"review_score": "Skor Ulasan (1-5)", "actual_delivery_days": "Durasi Pengiriman Riil (Hari)"},
            points=False,
        )
        fig_box.update_traces(marker_color="#38BDF8")
        apply_plot_theme(
            fig_box,
            title="Sebaran Durasi Pengiriman per Skor Ulasan",
            x_title="Skor Ulasan Pelanggan (1-5)",
            y_title="Durasi Pengiriman (Hari)",
            margin=dict(l=65, r=30, t=55, b=45),
        )
        fig_box.update_layout(yaxis_range=[0, 45], showlegend=False)
        st.plotly_chart(fig_box, width="stretch")
        st.caption("Sumbu Y dibatasi 0-45 hari (mencakup lebih dari 95% pesanan) agar perbandingan kuartil tetap terbaca.")
    else:
        st.info("Tidak ada data ulasan untuk menampilkan sebaran durasi pengiriman.")

c_m1, c_m2, c_m3 = st.columns(3)
c_m1.metric(
    "Selisih Kepuasan (Gap)",
    f"-{fmt_number(satisfaction_gap, decimals=2)} bintang" if satisfaction_gap is not None else "-",
    help="Selisih rata-rata skor ulasan antara pesanan tepat waktu dan terlambat.",
)
c_m2.metric(
    "Korelasi Durasi vs Rating",
    f"r = {fmt_number(corr_pearson, decimals=3)}" if corr_pearson is not None else "-",
    help=(
        f"Pearson r = {fmt_number(corr_pearson, decimals=3)} | "
        f"Spearman r_s = {fmt_number(corr_spearman, decimals=3)} "
        f"(n = {fmt_number(len(df_reviewed))} pesanan unik)."
    ) if corr_pearson is not None else "Jumlah ulasan tidak cukup untuk menghitung korelasi.",
)
c_m3.metric(
    "Ketepatan Pengiriman",
    f"{fmt_number(on_time_pct, decimals=1)}% Tepat Waktu",
    help=(
        f"Dari {fmt_number(len(df_orders))} pesanan unik, {fmt_number(df_orders['is_delayed'].sum())} "
        f"({fmt_number(df_orders['is_delayed'].mean() * 100, decimals=1)}%) tiba melewati tanggal estimasi."
    ),
)

on_time_str = f"{fmt_number(on_time_avg, decimals=2)} / 5.0" if on_time_avg is not None else "N/A"
late_str = f"{fmt_number(late_avg, decimals=2)} / 5.0" if late_avg is not None else "N/A"
gap_str = f"-{fmt_number(satisfaction_gap, decimals=2)} bintang" if satisfaction_gap is not None else "N/A"
ontime_1star = fmt_number((ontime_df["review_score"] == 1).mean() * 100, decimals=1) if not ontime_df.empty else "0.0"
late_1star = fmt_number((late_df["review_score"] == 1).mean() * 100, decimals=1) if not late_df.empty else "0.0"
corr_p_str = fmt_number(corr_pearson, decimals=3) if corr_pearson is not None else "N/A"
corr_s_str = fmt_number(corr_spearman, decimals=3) if corr_spearman is not None else "N/A"

st.markdown(
    f"""
<div class="insight-card">
    <div class="insight-card-title">Ringkasan Logistik & Kepuasan Pelanggan</div>
    <div class="insight-card-body">
        <ul>
            <li>Pesanan tepat waktu mencatat rata-rata <b>{on_time_str}</b> dibanding <b>{late_str}</b> pada pesanan terlambat (selisih <b>{gap_str}</b>).</li>
            <li>Proporsi ulasan bintang 1 naik dari <b>{ontime_1star}%</b> saat tepat waktu menjadi <b>{late_1star}%</b> saat melewati tanggal estimasi.</li>
            <li>Durasi kirim yang lebih lama berkorelasi negatif dengan skor ulasan (Pearson r = {corr_p_str}, Spearman r_s = {corr_s_str}), dengan tanggal estimasi sebagai batas toleransi pelanggan.</li>
        </ul>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)

st.subheader("4. Ide Tindak Lanjut & Keterbatasan Analisis")
st.caption("Opsi tindak lanjut berbasis pola data teramati beserta batasan cakupan dataset.")

col_a1, col_a2, col_a3 = st.columns(3)

with col_a1:
    st.markdown(
        f"""
    <div class="playbook-card">
        <h4 class="playbook-title">Komersial & Musiman</h4>
        <ul class="playbook-list">
            <li>Mulai promosi lebih awal pada Oktober untuk mengurai lonjakan permintaan sebelum puncak Black Friday November.</li>
            <li>Arahkan pertumbuhan omset pada akuisisi pesanan baru karena AOV bertahan di kisaran {fmt_number(aov, is_currency=True, decimals=0)}.</li>
            <li>Uji penawaran retensi pada Desember dan Januari untuk menjaga pembeli musiman tetap berbelanja ulang.</li>
        </ul>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col_a2:
    st.markdown(
        """
    <div class="playbook-card">
        <h4 class="playbook-title">Portofolio & Merchandising</h4>
        <ul class="playbook-list">
            <li>Jaga ketersediaan stok dan penempatan utama untuk kelompok kategori inti penyumbang 80% omset.</li>
            <li>Padukan produk berfrekuensi tinggi dengan barang bernilai lebih tinggi untuk mengangkat nilai keranjang belanja.</li>
            <li>Evaluasi berkala kategori ekor panjang bervolume rendah agar pengelolaan katalog tetap efisien.</li>
        </ul>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col_a3:
    st.markdown(
        """
    <div class="playbook-card">
        <h4 class="playbook-title">Logistik & SLA Pengiriman</h4>
        <ul class="playbook-list">
            <li>Tambahkan margin 2 sampai 3 hari pada estimasi rute jarak jauh agar tanggal janji tetap realistis.</li>
            <li>Kirim pemberitahuan proaktif ketika pengiriman berisiko melewati estimasi untuk menekan keluhan bintang 1.</li>
            <li>Pantau ketepatan waktu penjual dan kurir pada jalur dengan tingkat keterlambatan tinggi.</li>
        </ul>
    </div>
    """,
        unsafe_allow_html=True,
    )

st.caption(
    "Catatan keterbatasan: dataset hanya memuat pesanan berstatus delivered (Jan 2017 - Agu 2018), tidak menyertakan "
    "customer_unique_id lintas transaksi sehingga analisis retensi/RFM tidak dilakukan, dan nilai pendapatan menggunakan "
    "angka kotor item ditambah ongkos kirim tanpa data HPP atau diskon."
)

st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)

st.subheader("5. Eksplorasi Data & Unduh CSV")
st.caption("Periksa sampel transaksi terfilter, tabel ringkasan kategori, tren bulanan, dan ekspor CSV.")

with st.expander("Buka Tabel Ringkasan & Ekspor CSV", expanded=False):
    tab_sample, tab_cat_table, tab_monthly_table = st.tabs([
        "Sampel Transaksi (10 Baris)",
        "Ringkasan Kategori",
        "Tren Bulanan",
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
            label="Unduh Transaksi Terfilter (CSV)",
            data=csv_sample,
            file_name="filtered_ecommerce_transactions.csv",
            mime="text/csv",
            help="Unduh baris item transaksi sesuai filter aktif di sidebar.",
        )

    with tab_cat_table:
        cat_export = cat_agg[["product_category_name_english", "total_revenue", "total_orders", "total_items", "aov", "cum_pct"]].copy()
        cat_export.columns = ["Kategori Produk", "Total Pendapatan (BRL)", "Jumlah Pesanan", "Jumlah Item", "AOV (BRL)", "Kumulatif (%)"]
        st.dataframe(cat_export.head(30), hide_index=True)
        csv_cat = cat_export.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Unduh Ringkasan Pareto (CSV)",
            data=csv_cat,
            file_name="category_pareto_summary.csv",
            mime="text/csv",
        )

    with tab_monthly_table:
        monthly_export = monthly_agg[["order_year_month", "revenue", "orders", "aov", "mom_growth"]].copy()
        monthly_export.columns = ["Tahun-Bulan", "Pendapatan Bersih (BRL)", "Jumlah Pesanan", "AOV (BRL)", "Pertumbuhan MoM (%)"]
        st.dataframe(monthly_export, hide_index=True)
        csv_monthly = monthly_export.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Unduh Tren Bulanan (CSV)",
            data=csv_monthly,
            file_name="monthly_revenue_trend.csv",
            mime="text/csv",
        )
