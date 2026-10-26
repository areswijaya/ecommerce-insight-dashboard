# ==========================================================
# E-COMMERCE INSIGHT DASHBOARD (OLIST MARKETPLACE)
# Junior Data Analyst Portfolio
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
# NUMBER FORMATTING HELPER (STANDARD INDONESIAN FORMAT)
# ----------------------------------------------------------
def fmt_id(val, is_currency: bool = False, decimals: int = 0) -> str:
    """Format angka standar Indonesia: pemisah ribuan titik (.), desimal koma (,)."""
    if val is None or pd.isna(val):
        return "-"
    try:
        val_float = float(val)
    except (ValueError, TypeError):
        return str(val)
        
    if decimals == 0:
        raw_str = f"{val_float:,.0f}"
    else:
        raw_str = f"{val_float:,.{decimals}f}"
        
    parts = raw_str.split(".")
    int_part = parts[0].replace(",", ".")
    if len(parts) > 1:
        res = f"{int_part},{parts[1]}"
    else:
        res = int_part
        
    return f"R$ {res}" if is_currency else res

# ----------------------------------------------------------
# REUSABLE PLOTLY THEME HELPER
# ----------------------------------------------------------
def apply_plot_theme(fig, title="", x_title="", y_title="", margin=None):
    """Menerapkan layout tema gelap/transparan yang konsisten pada semua figur Plotly."""
    if margin is None:
        margin = dict(l=75, r=40, t=55, b=45)
    fig.update_layout(
        title=f"<b>{title}</b>" if title else "",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=margin,
        font=dict(color="#F8FAFC", family="Inter, sans-serif"),
        hoverlabel=dict(bgcolor="#1E293B", font_color="#F8FAFC", font_size=12),
        separators=",."
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

with st.spinner("Memuat dataset analitis..."):
    df_raw = load_data()

if df_raw is None:
    st.error("⚠️ File dataset `clean_orders.csv` tidak ditemukan! Pastikan file berada di folder `data/`.")
    st.stop()

# ----------------------------------------------------------
# SIDEBAR CONTROLS & GLOBAL FILTERS
# ----------------------------------------------------------
st.sidebar.title("⚙️ Filter Analisis")

# 1. Filter Rentang Waktu (Preset Cepat & Proteksi Crash)
min_date = df_raw["order_purchase_date"].min()
max_date = df_raw["order_purchase_date"].max()

st.sidebar.subheader("🗓️ Periode Transaksi")
period_preset = st.sidebar.selectbox(
    "Preset Periode Analisis:",
    options=[
        "Seluruh Periode (Jan 2017 – Agu 2018)",
        "Tahun 2017 (Fase Ekspansi & Puncak Black Friday)",
        "Tahun 2018 (Fase Kematangan Pasar)",
        "Kustom (Rentang Tanggal Bebas)"
    ],
    index=0,
    help="Gunakan preset periode cepat atau pilih 'Kustom' untuk menentukan rentang tanggal manual."
)

if period_preset == "Tahun 2017 (Fase Ekspansi & Puncak Black Friday)":
    start_date = pd.to_datetime("2017-01-01").date()
    end_date = pd.to_datetime("2017-12-31").date()
    st.sidebar.caption(f"📅 Periode: **{start_date.strftime('%d %b %Y')}** s.d. **{end_date.strftime('%d %b %Y')}**")
elif period_preset == "Tahun 2018 (Fase Kematangan Pasar)":
    start_date = pd.to_datetime("2018-01-01").date()
    end_date = pd.to_datetime("2018-08-31").date()
    st.sidebar.caption(f"📅 Periode: **{start_date.strftime('%d %b %Y')}** s.d. **{end_date.strftime('%d %b %Y')}**")
elif period_preset == "Kustom (Rentang Tanggal Bebas)":
    date_selection = st.sidebar.date_input(
        "Pilih Rentang Tanggal Manual:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        help="Data dibatasi pada periode operasional stabil (2017-01-01 s.d. 2018-08-31)."
    )
    if isinstance(date_selection, (tuple, list)):
        if len(date_selection) == 2:
            start_date, end_date = date_selection
        elif len(date_selection) == 1:
            start_date = end_date = date_selection[0]
            st.sidebar.info("💡 Memilih satu tanggal. Menampilkan transaksi pada hari tersebut.")
        else:
            start_date, end_date = min_date, max_date
    else:
        start_date = end_date = date_selection
else:  # Seluruh Periode Default
    start_date = min_date
    end_date = max_date
    st.sidebar.caption(f"📅 Periode: **{start_date.strftime('%d %b %Y')}** s.d. **{end_date.strftime('%d %b %Y')}** (20 Bulan Penuh)")

# 2. Filter Kategori Produk (Mencegah Ledakan 72 Tag Chip)
all_categories = sorted(df_raw["product_category_name_english"].dropna().unique().tolist())

all_categories_mode = st.sidebar.checkbox(f"Analisis Seluruh Kategori ({len(all_categories)} Kategori)", value=True)
if all_categories_mode:
    selected_categories = all_categories
    st.sidebar.caption(f"✅ Menampilkan seluruh {len(all_categories)} kategori produk aktif.")
else:
    top_default = ["health_beauty", "watches_gifts", "bed_bath_table", "sports_leisure", "computers_accessories"]
    selected_categories = st.sidebar.multiselect(
        "Pilih Kategori Spesifik:",
        options=all_categories,
        default=top_default,
        help="Pilih satu atau beberapa kategori untuk perbandingan spesifik."
    )

st.sidebar.markdown("---")
st.sidebar.caption("👨‍💼 **Portfolio:** Junior Data Analyst  \n🎓 **Background:** Mathematics Graduate  \n📊 **Dataset:** Olist Brazilian E-Commerce")

# ----------------------------------------------------------
# APPLY FILTERS
# ----------------------------------------------------------
mask_date = (df_raw["order_purchase_date"] >= start_date) & (df_raw["order_purchase_date"] <= end_date)
mask_cat = df_raw["product_category_name_english"].isin(selected_categories)

df_filtered = df_raw[mask_date & mask_cat].copy()

# Dataframe level pesanan unik untuk metrik logistik & ulasan
df_orders = df_filtered.drop_duplicates(subset=["order_id"]).copy()

# ----------------------------------------------------------
# HEADER BANNER
# ----------------------------------------------------------
st.markdown("""
<div class="main-banner">
    <h1>🛍️ E-Commerce Insight Dashboard</h1>
    <p>Analisis Kinerja Komersial, Portofolio Produk Pareto 80/20, dan Pengaruh Logistik terhadap Kepuasan Pelanggan (Olist Marketplace)</p>
</div>
""", unsafe_allow_html=True)

if df_filtered.empty or df_orders.empty:
    st.warning("⚠️ Tidak ada data transaksi yang cocok dengan kombinasi filter yang dipilih. Silakan sesuaikan kembali filter di sidebar.")
    st.stop()

# ----------------------------------------------------------
# EXECUTIVE KPI RIBBON (5 METRIK UTAMA)
# ----------------------------------------------------------
# Item-level metrics
total_revenue = df_filtered["total_order_value"].sum()
total_orders = df_orders["order_id"].nunique()
aov = total_revenue / total_orders if total_orders > 0 else 0

# Order-level metrics (Akurat tanpa pembobotan ganda item)
avg_delivery_days = df_orders["actual_delivery_days"].mean() if not df_orders.empty else None
median_delivery_days = df_orders["actual_delivery_days"].median() if not df_orders.empty else None
on_time_pct = ((~df_orders["is_delayed"]).mean() * 100) if not df_orders.empty else 0

df_reviewed = df_orders.dropna(subset=["review_score"]).copy()
avg_review_score = df_reviewed["review_score"].mean() if not df_reviewed.empty else None

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric(
    "💰 Total Net Revenue", 
    fmt_id(total_revenue, is_currency=True),
    help="Total nilai pendapatan terealisasi pada pesanan berstatus delivered (mencakup harga produk dan ongkos kirim)."
)
kpi2.metric(
    "📦 Delivered Orders", 
    fmt_id(total_orders),
    help=f"Total pesanan unik yang berhasil terkirim ({fmt_id(len(df_filtered))} item barang terjual)."
)
kpi3.metric(
    "🏷️ Average Order Value", 
    fmt_id(aov, is_currency=True, decimals=2),
    help="Rata-rata nilai belanja per pesanan unik (AOV = Total Revenue / Total Unique Orders)."
)
kpi4.metric(
    "🚚 Avg Delivery Time", 
    f"{fmt_id(avg_delivery_days, decimals=1)} Hari" if avg_delivery_days is not None else "-",
    help=f"Rata-rata durasi pengiriman riil. Median durasi: {fmt_id(median_delivery_days, decimals=1)} hari."
)
kpi5.metric(
    "⭐ Avg Review Score", 
    f"{fmt_id(avg_review_score, decimals=2)} / 5,0" if avg_review_score is not None else "-",
    help=f"Rata-rata skor kepuasan ulasan pelanggan (Tingkat ketepatan waktu pengiriman: {fmt_id(on_time_pct, decimals=1)}%)."
)

# Pita Metadata Sekunder (Tanpa fake delta arrows)
st.markdown(f"""
<div style="display: flex; gap: 1.5rem; justify-content: space-around; background: #1E293B; padding: 0.65rem 1.2rem; border-radius: 8px; border: 1px solid #334155; margin-top: 0.5rem; font-size: 0.88rem; color: #94A3B8;">
    <span>📊 <b>Median Durasi Pengiriman:</b> <span style="color: #F8FAFC;">{fmt_id(median_delivery_days, decimals=1)} Hari</span></span>
    <span>🚚 <b>Ketepatan Waktu (On-Time):</b> <span style="color: #34D399;">{fmt_id(on_time_pct, decimals=1)}%</span></span>
    <span>📦 <b>Total Item Terjual:</b> <span style="color: #F8FAFC;">{fmt_id(len(df_filtered))} Item</span></span>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr style='margin: 1.5rem 0; border: none; height: 1px; background-color: #334155;'/>", unsafe_allow_html=True)

# ----------------------------------------------------------
# SECTION 1: MONTHLY SALES & MOM GROWTH DYNAMICS
# ----------------------------------------------------------
st.subheader("📈 1. Dinamika Pendapatan Bulanan & Laju Pertumbuhan (MoM)")
st.caption("Menjawab Pertanyaan Bisnis 1: Memahami tren omset bulanan, laju pertumbuhan relatif, serta mendeteksi momen musiman (seasonality).")

# Agregasi data bulanan
monthly_agg = df_filtered.groupby("order_year_month").agg(
    revenue=("total_order_value", "sum"),
    orders=("order_id", "nunique")
).reset_index()

monthly_agg["mom_growth"] = monthly_agg["revenue"].pct_change() * 100
monthly_agg["aov"] = monthly_agg["revenue"] / monthly_agg["orders"]

col1, col2 = st.columns([7, 5])

with col1:
    tab_trend, tab_aov_trend = st.tabs(["📊 Tren Omset & Pesanan", "🏷️ Stabilitas Nilai Keranjang (AOV)"])
    
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
                hovertemplate="Bulan: %{x}<br>Revenue: R$ %{y:,.2f}<extra></extra>"
            ),
            secondary_y=False
        )
        
        fig_trend.add_trace(
            go.Scatter(
                x=monthly_agg["order_year_month"],
                y=monthly_agg["orders"],
                name="Total Orders",
                mode="lines+markers",
                line=dict(color="#34D399", width=2, dash="dash"),
                marker=dict(size=6, symbol="square", color="#34D399"),
                hovertemplate="Bulan: %{x}<br>Orders: %{y:,}<extra></extra>"
            ),
            secondary_y=True
        )
        
        # Anotasi dinamis puncak Black Friday Nov 2017 jika masuk dalam rentang filter
        if "2017-11" in monthly_agg["order_year_month"].values:
            bf_row = monthly_agg[monthly_agg["order_year_month"] == "2017-11"].iloc[0]
            bf_rev_str = fmt_id(bf_row["revenue"] / 1e6, is_currency=True, decimals=2) + " Juta"
            bf_mom_val = bf_row["mom_growth"]
            bf_mom_str = f"+{fmt_id(bf_mom_val, decimals=1)}% MoM" if pd.notna(bf_mom_val) else ""
            
            fig_trend.add_annotation(
                x="2017-11",
                y=bf_row["revenue"],
                text=f"<b>Puncak Black Friday Nov 2017</b><br>{bf_rev_str} ({bf_mom_str})",
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
        
        apply_plot_theme(fig_trend, title="Tren Pendapatan Bersih vs Volume Pesanan", x_title="Bulan Transaksi", y_title="Net Revenue (BRL)")
        fig_trend.update_layout(
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig_trend.update_yaxes(title_text="Total Pesanan", secondary_y=True, showgrid=False, automargin=True)
        st.plotly_chart(fig_trend, width="stretch")
        
    with tab_aov_trend:
        # AOV Monthly Trend Line Chart (Item 11 Audit Fix)
        fig_aov_trend = go.Figure()
        fig_aov_trend.add_trace(
            go.Scatter(
                x=monthly_agg["order_year_month"],
                y=monthly_agg["aov"],
                name="Average Order Value",
                mode="lines+markers",
                line=dict(color="#38BDF8", width=2.5),
                marker=dict(size=6, color="#38BDF8"),
                hovertemplate="Bulan: %{x}<br>AOV: R$ %{y:,.2f}<extra></extra>"
            )
        )
        if not monthly_agg.empty:
            mean_aov_val = monthly_agg["aov"].mean()
            fig_aov_trend.add_hline(
                y=mean_aov_val, 
                line_dash="dash", 
                line_color="#94A3B8", 
                line_width=1.5,
                annotation_text=f"Rata-rata: {fmt_id(mean_aov_val, is_currency=True, decimals=1)}", 
                annotation_position="bottom right"
            )
        apply_plot_theme(fig_aov_trend, title="Stabilitas Nilai Transaksi Rata-rata (AOV Bulanan)", x_title="Bulan Transaksi", y_title="AOV (BRL)")
        fig_aov_trend.update_layout(hovermode="x unified")
        st.plotly_chart(fig_aov_trend, width="stretch")
        st.caption("ℹ️ *Verifikasi Stabilitas:* Garis putus-putus menunjukkan rata-rata AOV keseluruhan periode. Nilai AOV yang stabil membuktikan pertumbuhan pendapatan didorong oleh volume pesanan.")

with col2:
    # MoM Growth % Bar Chart dengan penanganan netral untuk bulan dasar
    mom_display = monthly_agg.copy()
    mom_vals = mom_display["mom_growth"]
    
    # Bulan pertama MoM diwarnai abu-abu netral (#64748B) sebagai baseline
    colors_mom = []
    hover_texts = []
    for idx, val in enumerate(mom_vals):
        if idx == 0 or pd.isna(val):
            colors_mom.append("#64748B")
            hover_texts.append("Bulan Dasar / Baseline")
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
        hovertemplate="Bulan: %{x}<br>MoM Growth: %{customdata}<extra></extra>"
    ))
    
    fig_mom.add_hline(y=0, line_dash="solid", line_color="#94A3B8", line_width=1)
    apply_plot_theme(fig_mom, title="Laju Pertumbuhan Bulanan (MoM Growth %)", x_title="Bulan Transaksi", y_title="Pertumbuhan MoM (%)", margin=dict(l=65, r=30, t=55, b=45))
    st.plotly_chart(fig_mom, width="stretch")
    st.caption("ℹ️ *Catatan Baseline:* Bulan pertama selalu berfungsi sebagai baseline netral. Jika filter memotong pertengahan bulan, perubahan MoM pada bulan tersebut mencerminkan data parsial.")

# Tentukan metrik dinamis untuk insight box Seksi 1
if not monthly_agg.empty:
    peak_row = monthly_agg.loc[monthly_agg["revenue"].idxmax()]
    peak_month = peak_row["order_year_month"]
    peak_rev = fmt_id(peak_row["revenue"], is_currency=True)
    first_month = monthly_agg.iloc[0]["order_year_month"]
    first_rev = fmt_id(monthly_agg.iloc[0]["revenue"], is_currency=True)
    avg_aov_range = f"{fmt_id(monthly_agg['aov'].min(), is_currency=True, decimals=0)} – {fmt_id(monthly_agg['aov'].max(), is_currency=True, decimals=0)}"
else:
    peak_month, peak_rev, first_month, first_rev, avg_aov_range = "-", "-", "-", "-", "-"

# Insight Box Section 1 (Dinamis & Bebas Klaim Kausalitas Berlebih)
st.markdown(f"""
<div class="insight-card">
    <div class="insight-card-title">💡 Insight Kunci — Dinamika Pertumbuhan & Pola Musiman</div>
    <div class="insight-card-body">
        <ul>
            <li><b>Ekspansi Skala Penjualan:</b> Pendapatan bulanan tercatat sebesar <b>{first_rev}</b> pada periode awal ({first_month}) dan mencapai puncaknya sebesar <b>{peak_rev}</b> pada {peak_month}.</li>
            <li><b>Indikasi Pola Musiman:</b> Lonjakan signifikan pada November 2017 konsisten dengan momen promosi akhir tahun (Black Friday), yang kemudian mengalami normalisasi pada bulan berikutnya.</li>
            <li><b>Karakteristik Nilai Keranjang (AOV):</b> Nilai transaksi rata-rata bergerak stabil pada kisaran <b>{avg_aov_range}</b>, mengindikasikan bahwa pertumbuhan omset lebih didorong oleh ekspansi volume pesanan daripada kenaikan harga rata-rata per transaksi.</li>
        </ul>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr style='margin: 1.5rem 0; border: none; height: 1px; background-color: #334155;'/>", unsafe_allow_html=True)

# ----------------------------------------------------------
# SECTION 2: PRODUCT CATEGORY PARETO 80/20 & AOV
# ----------------------------------------------------------
st.subheader("📦 2. Analisis Portofolio Produk & Distribusi Pareto 80/20")
st.caption("Menjawab Pertanyaan Bisnis 2: Mengidentifikasi kategori produk penggerak utama omset (Core 80%) dan mengamati sebaran Average Order Value (AOV).")

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
    # Slider Pareto yang Aman dari Crash (P0 Fix)
    if total_cats_count <= 1:
        top_n = total_cats_count
        st.info(f"Menampilkan 1 kategori terpilih: **{cat_agg.iloc[0]['product_category_name_english']}**")
    elif total_cats_count <= 5:
        top_n = total_cats_count
        st.caption(f"Menampilkan seluruh {total_cats_count} kategori terpilih.")
    else:
        slider_max = min(30, total_cats_count)
        slider_default = min(15, total_cats_count)
        top_n = st.slider("Tampilkan Top-N Kategori Teratas:", min_value=1, max_value=slider_max, value=slider_default)
        
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
            hovertemplate="Kategori: %{x}<br>Revenue: R$ %{y:,.2f}<extra></extra>"
        ),
        secondary_y=False
    )
    
    fig_pareto.add_trace(
        go.Scatter(
            x=df_pareto_display["product_category_name_english"],
            y=df_pareto_display["cum_pct"],
            name="Kumulatif (%)",
            mode="lines+markers",
            line=dict(color="#F87171", width=2.5),
            marker=dict(size=6, color="#F87171"),
            hovertemplate="Kategori: %{x}<br>Kumulatif: %{y:.1f}%<extra></extra>"
        ),
        secondary_y=True
    )
    
    fig_pareto.add_hline(y=80, line_dash="dash", line_color="#F87171", secondary_y=True, annotation_text="Batas Pareto 80%", annotation_position="bottom right")
    
    apply_plot_theme(fig_pareto, title=f"Diagram Pareto Top {top_n} Kategori Produk", y_title="Revenue (BRL)")
    fig_pareto.update_layout(
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig_pareto.update_xaxes(tickangle=-45)
    fig_pareto.update_yaxes(title_text="Kumulatif (%)", secondary_y=True, range=[0, 105], showgrid=False, automargin=True)
    
    st.plotly_chart(fig_pareto, width="stretch")

with col_p2:
    top_cat_name = cat_agg.iloc[0]["product_category_name_english"] if total_cats_count > 0 else "-"
    top_cat_rev = fmt_id(cat_agg.iloc[0]["total_revenue"], is_currency=True) if total_cats_count > 0 else "-"
    core_pct_str = f"{(core_cats_count/total_cats_count)*100:.1f}%" if total_cats_count > 0 else "-"
    
    st.markdown(f"""
    <div style="background-color: #1E293B; border: 1px solid #334155; border-radius: 10px; padding: 1.2rem; margin-bottom: 1rem;">
        <h4 style="margin: 0; color: #60A5FA;">📊 Konfirmasi Distribusi Pareto</h4>
        <p style="margin: 0.5rem 0 0 0; color: #CBD5E1; font-size: 0.92rem; line-height: 1.5;">
            Tepat <b>{core_cats_count} dari {total_cats_count} kategori ({core_pct_str})</b> menyumbang <b>80% pendapatan kumulatif</b> pada data terpilih.<br/>
            Kategori penyumbang tertinggi: <b>{top_cat_name}</b> ({top_cat_rev}).
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # AOV Bar Chart across Top Categories
    fig_aov = px.bar(
        df_pareto_display.sort_values(by="aov", ascending=True),
        x="aov",
        y="product_category_name_english",
        orientation="h",
        title=f"Average Order Value (AOV) per Kategori",
        labels={"aov": "AOV (BRL)", "product_category_name_english": "Kategori Produk"},
        color="aov",
        color_continuous_scale="Blues"
    )
    apply_plot_theme(fig_aov, title=f"AOV per Kategori (Top {top_n})", x_title="AOV (BRL)", margin=dict(l=85, r=30, t=55, b=45))
    fig_aov.update_layout(coloraxis_showscale=False)
    
    st.plotly_chart(fig_aov, width="stretch")

# Tentukan 3 kategori teratas secara dinamis
top_3_names = ", ".join([f"<code>{cat}</code>" for cat in cat_agg.head(3)["product_category_name_english"].tolist()]) if total_cats_count >= 3 else top_cat_name

# Insight Box Section 2 (Dinamis)
st.markdown(f"""
<div class="insight-card">
    <div class="insight-card-title">💡 Insight Kunci — Optimasi Portofolio Produk</div>
    <div class="insight-card-body">
        <ul>
            <li><b>Konsentrasi Omset:</b> Dari {total_cats_count} kategori produk aktif pada filter saat ini, <b>{core_cats_count} kategori inti ({core_pct_str})</b> mendominasi 80% omset bisnis, dengan kontribusi terbesar berasal dari {top_3_names}.</li>
            <li><b>Diferensiasi Nilai Keranjang:</b> Terdapat variasi AOV yang signifikan antarkategori. Beberapa kategori bertindak sebagai pendorong omset bernilai tinggi (<i>high-ticket niche</i>), sementara kategori lainnya berfungsi sebagai penarik volume pesanan massal.</li>
            <li><b>Rekomendasi Aksi:</b> Prioritaskan alokasi inventaris dan ruang etalase utama pada kategori inti, serta kembangkan strategi <i>bundling</i> antara produk bervolume tinggi dengan produk bernilai belanja tinggi.</li>
        </ul>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr style='margin: 1.5rem 0; border: none; height: 1px; background-color: #334155;'/>", unsafe_allow_html=True)

# ----------------------------------------------------------
# SECTION 3: DELIVERY DURATION & SATISFACTION GAP (ORDER LEVEL)
# ----------------------------------------------------------
st.subheader("🚚 3. Pengaruh Durasi & Keterlambatan Pengiriman terhadap Kepuasan")
st.caption("Menjawab Pertanyaan Bisnis 3: Menguji hubungan korelasi antara waktu tempuh pengiriman riil serta keterlambatan kalender terhadap rating ulasan pelanggan pada tingkat pesanan unik.")

ontime_df = df_reviewed[~df_reviewed["is_delayed"]]
late_df = df_reviewed[df_reviewed["is_delayed"]]

on_time_avg = ontime_df["review_score"].mean() if not ontime_df.empty else None
late_avg = late_df["review_score"].mean() if not late_df.empty else None
satisfaction_gap = (on_time_avg - late_avg) if (on_time_avg is not None and late_avg is not None) else None

# Korelasi statistik (Pearson & Spearman via rank correlation tanpa dependensi eksternal)
corr_pearson = df_reviewed["actual_delivery_days"].corr(df_reviewed["review_score"], method="pearson") if len(df_reviewed) > 1 else None
corr_spearman = df_reviewed["actual_delivery_days"].rank().corr(df_reviewed["review_score"].rank()) if len(df_reviewed) > 1 else None

col_d1, col_d2 = st.columns([6, 6])

with col_d1:
    tab_rating, tab_prop, tab_dist = st.tabs([
        "⭐ Rata-rata Skor Ulasan", 
        "🚨 Proporsi Ulasan Bintang 1",
        "📊 Distribusi Lengkap (1–5 ⭐)"
    ])
    
    n_ontime = len(ontime_df)
    n_late = len(late_df)
    
    with tab_rating:
        # Bar Chart: Satisfaction Gap (On-Time vs Late)
        gap_labels = [f"Tepat Waktu / Lebih Cepat\n({fmt_id(n_ontime)} pesanan)", f"Terlambat dari Estimasi\n({fmt_id(n_late)} pesanan)"]
        gap_values = [on_time_avg if on_time_avg is not None else 0, late_avg if late_avg is not None else 0]
        gap_texts = [f"{fmt_id(on_time_avg, decimals=2)} ⭐" if on_time_avg is not None else "Data Kosong",
                     f"{fmt_id(late_avg, decimals=2)} ⭐" if late_avg is not None else "Data Kosong"]
                     
        gap_data = pd.DataFrame({
            "Status Pengiriman": gap_labels,
            "Rata-rata Rating": gap_values,
            "Text": gap_texts
        })
        
        fig_gap = px.bar(
            gap_data,
            x="Status Pengiriman",
            y="Rata-rata Rating",
            text="Text",
            color="Status Pengiriman",
            color_discrete_sequence=["#10B981", "#EF4444"]
        )
        fig_gap.update_traces(textposition="outside", width=0.45)
        apply_plot_theme(fig_gap, title="Perbandingan Skor Ulasan: On-Time vs Delayed", y_title="Rating Ulasan (1-5 Bintang)", margin=dict(l=65, r=30, t=55, b=45))
        fig_gap.update_layout(yaxis_range=[0, 5.3], showlegend=False)
        fig_gap.update_xaxes(showgrid=False)
        st.plotly_chart(fig_gap, width="stretch")
        
    with tab_prop:
        # Bar Chart: Proporsi Ulasan Bintang 1 (Item 8 Audit Fix)
        p_ontime_1_val = (ontime_df["review_score"] == 1).mean() * 100 if not ontime_df.empty else 0
        p_late_1_val = (late_df["review_score"] == 1).mean() * 100 if not late_df.empty else 0
        
        prop_labels = [f"Tepat Waktu\n({fmt_id(n_ontime)} pesanan)", f"Terlambat Kalender\n({fmt_id(n_late)} pesanan)"]
        prop_vals = [p_ontime_1_val, p_late_1_val]
        prop_texts = [f"{fmt_id(p_ontime_1_val, decimals=1)}%", f"{fmt_id(p_late_1_val, decimals=1)}%"]
        
        df_prop = pd.DataFrame({
            "Status Pengiriman": prop_labels,
            "Persentase Bintang 1": prop_vals,
            "Text": prop_texts
        })
        
        fig_prop = px.bar(
            df_prop,
            x="Status Pengiriman",
            y="Persentase Bintang 1",
            text="Text",
            color="Status Pengiriman",
            color_discrete_sequence=["#10B981", "#EF4444"]
        )
        fig_prop.update_traces(textposition="outside", width=0.45)
        apply_plot_theme(fig_prop, title="Proporsi Ulasan Bintang 1 (Ulasan Buruk Ekstrem)", y_title="Persentase Pesanan Ulasan Bintang 1 (%)", margin=dict(l=65, r=30, t=55, b=45))
        fig_prop.update_layout(yaxis_range=[0, max(65, p_late_1_val * 1.15)], showlegend=False)
        fig_prop.update_xaxes(showgrid=False)
        st.plotly_chart(fig_prop, width="stretch")
        st.caption("ℹ️ *Bukti Lonjakan Ulasan Negatif:* Keterlambatan kalender meningkatkan risiko ulasan bintang 1 secara drastis (hingga >8x lipat).")

    with tab_dist:
        # Grouped Bar Chart: Distribusi Lengkap Seluruh Skor 1 s.d. 5 Bintang
        dist_data = []
        for status_label, sub_df in [("Tepat Waktu", ontime_df), ("Terlambat", late_df)]:
            if not sub_df.empty:
                counts = sub_df["review_score"].round().value_counts(normalize=True) * 100
                for score in [1, 2, 3, 4, 5]:
                    pct_val = counts.get(float(score), 0.0)
                    dist_data.append({
                        "Status Pengiriman": status_label,
                        "Skor Bintang": f"{score} ⭐",
                        "Persentase": round(pct_val, 1),
                        "Label Text": f"{pct_val:.1f}%"
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
                text="Label Text",
                labels={"Persentase": "Proporsi Pesanan (%)", "Skor Bintang": "Skor Ulasan"}
            )
            fig_dist.update_traces(textposition="outside")
            apply_plot_theme(fig_dist, title="Sebaran Seluruh Skor Ulasan (1–5 ⭐): Tepat Waktu vs Terlambat", y_title="Proporsi Pesanan (%)", margin=dict(l=65, r=30, t=55, b=45))
            max_p = df_chart_dist["Persentase"].max() if not df_chart_dist.empty else 60
            fig_dist.update_layout(yaxis_range=[0, max(75, max_p * 1.18)], legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            st.plotly_chart(fig_dist, width="stretch")
            st.caption("ℹ️ *Pergeseran Distribusi:* Pesanan tepat waktu didominasi oleh bintang 5 (62,2%), sedangkan saat pesanan melewati estimasi kalender, ulasan langsung anjlok ke bintang 1 (53,7%).")

with col_d2:
    # Boxplot of Delivery Days by Review Score (Rentang 0–45 hari untuk menyorot kuartil)
    fig_box = px.box(
        df_reviewed,
        x="review_score",
        y="actual_delivery_days",
        labels={"review_score": "Skor Ulasan (Review Score)", "actual_delivery_days": "Durasi Pengiriman (Hari)"},
        points=False # Sembunyikan pencilan ekstrem agar bentuk box/kuartil terlihat jelas
    )
    fig_box.update_traces(marker_color="#38BDF8")
    apply_plot_theme(fig_box, title="Sebaran Durasi Pengiriman per Skor Ulasan", x_title="Skor Ulasan Pelanggan (1 s.d. 5)", y_title="Durasi Pengiriman (Hari)", margin=dict(l=65, r=30, t=55, b=45))
    fig_box.update_layout(yaxis_range=[0, 45], showlegend=False)
    
    st.plotly_chart(fig_box, width="stretch")
    st.caption("ℹ️ *Catatan Sumbu:* Sumbu Y boxplot dibatasi pada 0–45 hari (mencakup >95% pesanan) untuk menjaga proporsi kuartil tetap informatif.")

# Metrics Highlight for Section 3
c_m1, c_m2, c_m3 = st.columns(3)
c_m1.metric(
    "📉 Satisfaction Gap", 
    f"-{fmt_id(satisfaction_gap, decimals=2)} ⭐" if satisfaction_gap is not None else "-",
    help="Selisih penurunan skor ulasan antara pesanan tepat waktu versus pesanan terlambat."
)
c_m2.metric(
    "🔗 Korelasi Durasi vs Rating", 
    f"r = {fmt_id(corr_pearson, decimals=3)}" if corr_pearson is not None else "-",
    help=f"Korelasi Pearson r = {fmt_id(corr_pearson, decimals=3)} | Spearman r_s = {fmt_id(corr_spearman, decimals=3)} (Sampel n = {fmt_id(len(df_reviewed))} pesanan)."
)
c_m3.metric(
    "🚨 Tingkat Keterlambatan", 
    f"{fmt_id((~df_orders['is_delayed']).mean()*100, decimals=1)}% Tepat Waktu",
    help=f"Dari total {fmt_id(len(df_orders))} pesanan unik, {fmt_id((df_orders['is_delayed']).sum())} pesanan ({fmt_id(df_orders['is_delayed'].mean()*100, decimals=1)}%) mengalami keterlambatan kalender."
)

# Hitung proporsi ulasan bintang 1 secara dinamis
ontime_1star = fmt_id((ontime_df["review_score"] == 1).mean() * 100, decimals=1) if not ontime_df.empty else "0"
late_1star = fmt_id((late_df["review_score"] == 1).mean() * 100, decimals=1) if not late_df.empty else "0"

# Insight Box Section 3 (Dinamis & Proporsional)
st.markdown(f"""
<div class="insight-card">
    <div class="insight-card-title">💡 Insight Kunci — Batas Toleransi Kepuasan Pelanggan</div>
    <div class="insight-card-body">
        <ul>
            <li><b>Kesenjangan Kepuasan Signifikan:</b> Pesanan yang tiba tepat waktu memperoleh rating rata-rata <b>{fmt_id(on_time_avg, decimals=2)} ⭐</b>, sedangkan pesanan terlambat anjlok menjadi <b>{fmt_id(late_avg, decimals=2)} ⭐</b> (Satisfaction Gap sebesar <b>-{fmt_id(satisfaction_gap, decimals=2)} bintang</b>).</li>
            <li><b>Lonjakan Ulasan Negatif:</b> Proporsi ulasan bintang 1 melonjak dari <b>{ontime_1star}%</b> pada pesanan tepat waktu menjadi <b>{late_1star}%</b> pada pesanan yang melewati tanggal estimasi.</li>
            <li><b>SLA Kalender sebagai Ekspektasi Kritis:</b> Normalisasi tanggal kalender mengonfirmasi bahwa keterlambatan melebihi hari yang dijanjikan berkorelasi kuat dengan ketidakpuasan pelanggan (Pearson r = {fmt_id(corr_pearson, decimals=3)}, Spearman r_s = {fmt_id(corr_spearman, decimals=3)}).</li>
        </ul>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr style='margin: 1.5rem 0; border: none; height: 1px; background-color: #334155;'/>", unsafe_allow_html=True)

# ----------------------------------------------------------
# SECTION 4: STRATEGIC ACTION PLAYBOOK (TAKEAWAYS)
# ----------------------------------------------------------
st.subheader("🎯 4. Rekomendasi Bisnis Terapan (Strategic Action Playbook)")
st.caption("Sintesis wawasan analitis ke dalam hipotesis tindakan bagi divisi Komersial, Merchandising, dan Operasional Logistik.")

col_a1, col_a2, col_a3 = st.columns(3)

with col_a1:
    st.markdown(f"""
    <div class="playbook-card commercial">
        <h4 class="playbook-title commercial">🚀 Strategi Komersial & Pertumbuhan</h4>
        <ul class="playbook-list">
            <li><b>Persiapan Pra-Black Friday:</b> Mulai kampanye promosi awal sejak bulan Oktober untuk mengantisipasi lonjakan permintaan musiman November.</li>
            <li><b>Fokus Akuisisi Volume:</b> Dengan stabilitas AOV (~{fmt_id(aov, is_currency=True, decimals=0)}), strategi pertumbuhan omset paling efektif difokuskan pada penambahan volume transaksi baru.</li>
            <li><b>Evaluasi Efektivitas Promo:</b> Audit penurunan penjualan pasca-peak season untuk menjaga kesinambungan arus transaksi kuartal berikutnya.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col_a2:
    st.markdown("""
    <div class="playbook-card merchandising">
        <h4 class="playbook-title merchandising">📦 Optimasi Portofolio Produk</h4>
        <ul class="playbook-list">
            <li><b>Fokus Alokasi Sumber Daya:</b> Prioritaskan anggaran pemasaran dan ruang etalase pada kategori inti kontributor 80% omset bisnis.</li>
            <li><b>Bundling Produk:</b> Kembangkan paket bundling antara kategori bervolume tinggi dengan produk bernilai tinggi untuk mendorong rata-rata nilai transaksi.</li>
            <li><b>Rasionalisasi Katalog:</b> Tinjau efisiensi inventaris pada kategori ekor panjang (<i>long-tail</i>) dengan kontribusi omset marjinal.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col_a3:
    st.markdown("""
    <div class="playbook-card logistics">
        <h4 class="playbook-title logistics">🚚 Keunggulan Logistik & Retensi</h4>
        <ul class="playbook-list">
            <li><b>SLA Buffer Realistis:</b> Terapkan buffer estimasi pengiriman 2–3 hari pada rute jarak jauh guna menghindari kepuasan anjlok saat pesanan melewati estimasi.</li>
            <li><b>Notifikasi Proaktif:</b> Otomasi komunikasi peringatan dini beserta kompensasi sebelum barang tiba saat terdeteksi keterlambatan ekspedisi.</li>
            <li><b>Prioritas Penanganan Seller:</b> Lakukan audit berkala pada mitra kurir dan penjual dengan tingkat keterlambatan pengiriman tertinggi.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='margin: 1.5rem 0; border: none; height: 1px; background-color: #334155;'/>", unsafe_allow_html=True)

# ----------------------------------------------------------
# SECTION 5: DATA DRILLDOWN & AUDIT TRAIL
# ----------------------------------------------------------
st.subheader("🔍 5. Eksplorasi & Audit Data Terfilter (Data Drilldown)")
st.caption("Inspeksi granularitas data transaksi, ringkasan tabel agregasi analitis, dan unduh dataset terfilter dalam format CSV.")

with st.expander("📂 Buka Panel Eksplorasi Data & Unduh CSV", expanded=False):
    tab_sample, tab_cat_table, tab_monthly_table = st.tabs([
        "📋 Sampel Transaksi (10 Baris)", 
        "📦 Tabel Agregasi Kategori Produk", 
        "📈 Tabel Agregasi Bulanan"
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
            label="📥 Unduh Data Transaksi Terfilter (CSV)",
            data=csv_sample,
            file_name="filtered_ecommerce_transactions.csv",
            mime="text/csv",
            help="Unduh data transaksi terfilter berdasarkan rentang tanggal dan kategori yang dipilih."
        )
        
    with tab_cat_table:
        cat_export = cat_agg[["product_category_name_english", "total_revenue", "total_orders", "total_items", "aov", "cum_pct"]].copy()
        cat_export.columns = ["Kategori Produk", "Total Revenue (BRL)", "Total Pesanan", "Total Item", "AOV (BRL)", "Kumulatif (%)"]
        st.dataframe(cat_export.head(30), hide_index=True)
        csv_cat = cat_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Unduh Ringkasan Kategori Pareto (CSV)",
            data=csv_cat,
            file_name="category_pareto_summary.csv",
            mime="text/csv"
        )
        
    with tab_monthly_table:
        monthly_export = monthly_agg[["order_year_month", "revenue", "orders", "aov", "mom_growth"]].copy()
        monthly_export.columns = ["Tahun-Bulan", "Net Revenue (BRL)", "Total Pesanan", "AOV (BRL)", "MoM Growth (%)"]
        st.dataframe(monthly_export, hide_index=True)
        csv_monthly = monthly_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Unduh Ringkasan Tren Bulanan (CSV)",
            data=csv_monthly,
            file_name="monthly_revenue_trend.csv",
            mime="text/csv"
        )

# ----------------------------------------------------------
# SECTION 6: PROFESSIONAL AUTHOR CREDITS (FOOTER)
# ----------------------------------------------------------
st.markdown("""
<div class="credit-container">
    <div>
        <div class="credit-author">👤 Ilfa Antaries Yusuf Wijaya</div>
        <div class="credit-role">Junior Data Analyst Portfolio • Mathematics Graduate</div>
    </div>
    <div class="credit-contact">
        <span style="color: #94A3B8; font-size: 0.9rem;">Email Kontak:</span>
        <a href="mailto:contact.areswijaya@gmail.com" class="credit-email">✉️ contact.areswijaya@gmail.com</a>
    </div>
</div>
""", unsafe_allow_html=True)

st.caption("© 2026 E-Commerce Insight Dashboard — Junior Data Analyst Portfolio. Dibangun dengan Python, Pandas, Streamlit & Plotly.")
