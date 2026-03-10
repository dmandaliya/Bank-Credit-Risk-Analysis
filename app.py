"""
app.py — Bank Credit Risk Intelligence Platform
Run: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Wedge
import matplotlib.ticker as mticker
import seaborn as sns
import warnings, sys, os

warnings.filterwarnings("ignore")

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Credit Risk Intelligence",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Design Tokens ──────────────────────────────────────────────────────────────
NAVY      = "#0D1B2A"
NAVY_MID  = "#1B3A5C"
NAVY_LITE = "#2C5282"
GOLD      = "#C9A84C"
GOLD_LITE = "#E8D5A3"
BG        = "#F0F4F8"
CARD      = "#FFFFFF"
TEXT      = "#0D1B2A"
MUTED     = "#64748B"
BORDER    = "#DDE3EA"

RISK_C = {"Low": "#1A6B3C", "Medium": "#B5883E", "High": "#8B1A1A"}
RISK_L = {"Low": "#D1FAE5", "Medium": "#FEF3C7", "High": "#FEE2E2"}
RISK_M = {0: "Low", 1: "Medium", 2: "High"}

FICO_BANDS = [
    (300, 499, "#8B1A1A", "Very Poor"),
    (499, 579, "#C0392B", "Poor"),
    (579, 669, "#D97706", "Fair"),
    (669, 739, "#B45309", "Good"),
    (739, 799, "#2D6A4F", "Very Good"),
    (799, 850, "#1A6B3C", "Exceptional"),
]

def fico_label(score):
    for lo, hi, color, label in FICO_BANDS:
        if lo <= score <= hi:
            return label, color
    return "Unknown", MUTED

def credit_grade(score):
    if score >= 800: return "A+"
    if score >= 740: return "A"
    if score >= 670: return "B"
    if score >= 580: return "C"
    if score >= 500: return "D"
    return "F"

# ── Chart defaults ─────────────────────────────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor": CARD, "axes.facecolor": "#FAFBFC",
    "axes.edgecolor": BORDER, "axes.labelcolor": TEXT,
    "axes.titlecolor": NAVY, "axes.titlesize": 12, "axes.titleweight": "bold",
    "axes.labelsize": 10, "axes.grid": True,
    "grid.color": "#E8ECF0", "grid.linewidth": 0.5,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "xtick.labelsize": 9, "ytick.labelsize": 9,
    "legend.fontsize": 9, "legend.framealpha": 0.9,
    "legend.edgecolor": BORDER, "figure.dpi": 130,
})

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown(f"""<style>
[data-testid="stAppViewContainer"] {{ background:{BG}; }}
[data-testid="stSidebar"] {{
    background: linear-gradient(175deg,{NAVY} 0%,{NAVY_MID} 100%);
    border-right: 1px solid {NAVY_MID};
}}
[data-testid="stSidebar"] * {{ color:#E8EDF2 !important; }}
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {{
    color:{GOLD_LITE} !important; font-size:11px !important;
    font-weight:600 !important; letter-spacing:.5px;
}}
[data-testid="stSidebar"] hr {{ border-color:rgba(201,168,76,.25) !important; }}

.main-header {{
    background:linear-gradient(135deg,{NAVY} 0%,{NAVY_MID} 100%);
    padding:26px 34px; border-radius:14px; margin-bottom:20px;
    border-left:5px solid {GOLD};
    box-shadow:0 4px 24px rgba(13,27,42,.18);
}}
.main-header h1 {{ color:#fff; margin:0; font-size:24px; font-weight:700; letter-spacing:.4px; }}
.main-header p  {{ color:{GOLD_LITE}; margin:5px 0 0; font-size:12px; letter-spacing:.3px; }}

.kpi-card {{
    background:{CARD}; border-radius:12px; padding:16px 18px;
    border-top:3px solid {GOLD}; box-shadow:0 2px 12px rgba(13,27,42,.08);
    text-align:center; margin-bottom:6px;
}}
.kpi-label {{ color:{MUTED}; font-size:10px; font-weight:700; letter-spacing:1px; text-transform:uppercase; }}
.kpi-value {{ color:{NAVY}; font-size:22px; font-weight:800; line-height:1.1; margin:4px 0; }}
.kpi-sub   {{ color:{MUTED}; font-size:10px; }}

.sec {{ color:{NAVY}; font-size:15px; font-weight:700;
        border-left:4px solid {GOLD}; padding-left:10px;
        margin:18px 0 12px; letter-spacing:.2px; }}

[data-testid="stTabs"] [data-baseweb="tab-list"] {{
    background:{CARD}; border-radius:10px; padding:4px; gap:2px;
    box-shadow:0 1px 8px rgba(13,27,42,.07);
}}
[data-testid="stTabs"] [data-baseweb="tab"] {{
    border-radius:8px; color:{MUTED} !important; font-weight:600;
    font-size:13px; padding:8px 18px;
}}
[data-testid="stTabs"] [aria-selected="true"] {{
    background:{NAVY} !important; color:#fff !important;
}}

.rec-card {{
    border-radius:12px; padding:20px; text-align:center;
    box-shadow:0 4px 18px rgba(0,0,0,.12);
}}
.info-row {{
    display:flex; justify-content:space-between; align-items:center;
    padding:9px 0; border-bottom:1px solid {BORDER};
}}
.info-label {{ font-size:12px; color:{MUTED}; }}
.info-value {{ font-size:13px; color:{NAVY}; font-weight:700; }}
.flag-box {{
    background:#FEF3C7; border-left:4px solid {GOLD};
    border-radius:0 8px 8px 0; padding:9px 13px; margin:5px 0;
    font-size:12px; color:#78350F;
}}
.clear-box {{
    background:#D1FAE5; border-left:4px solid #1A6B3C;
    border-radius:0 8px 8px 0; padding:9px 13px;
    font-size:12px; color:#064E3B;
}}
[data-testid="stDataFrame"] {{ border-radius:10px; overflow:hidden; box-shadow:0 2px 10px rgba(13,27,42,.07); }}
[data-testid="stMetric"]    {{ background:{CARD}; padding:14px; border-radius:10px; box-shadow:0 2px 10px rgba(13,27,42,.07); }}
</style>""", unsafe_allow_html=True)


# ── Data & Model ───────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    path = os.path.join(os.path.dirname(__file__), "data", "credit_data_clean.csv")
    if not os.path.exists(path):
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
        import generate_data; import cleaning; cleaning.run()  # noqa
    return pd.read_csv(path)

@st.cache_resource
def train_model(df):
    from sklearn.preprocessing import LabelEncoder
    from sklearn.model_selection import train_test_split
    from imblearn.over_sampling import SMOTE
    from xgboost import XGBClassifier

    le = LabelEncoder()
    df = df.copy()
    df["employment_encoded"] = le.fit_transform(df["employment_status"])
    FEAT = ["age","income","loan_amount","loan_tenure","credit_score",
            "credit_utilization","repayment_history","num_defaults",
            "debt_to_income_ratio","monthly_emi","emi_to_income_ratio","employment_encoded"]
    X, y = df[FEAT], df["risk_score_numeric"]
    X_tr, _, y_tr, _ = train_test_split(X, y, test_size=.2, random_state=42, stratify=y)
    X_r, y_r = SMOTE(random_state=42).fit_resample(X_tr, y_tr)
    m = XGBClassifier(n_estimators=50, learning_rate=.1, max_depth=4,
                      eval_metric="mlogloss",
                      random_state=42, n_jobs=1)
    m.fit(X_r, y_r)
    return m, FEAT, le

df   = load_data()
model, FEATURES, le = train_model(df)


# ── Gauge chart ────────────────────────────────────────────────────────────────
def draw_gauge(score):
    fig, ax = plt.subplots(figsize=(5, 2.8))
    fig.patch.set_facecolor(CARD)
    ax.set_facecolor(CARD)
    total = 550  # 850-300

    for lo, hi, color, _ in FICO_BANDS:
        a1 = 180 - (lo - 300) / total * 180
        a2 = 180 - (hi - 300) / total * 180
        ax.add_patch(Wedge((0, 0), 1.0, a2, a1, width=0.28, color=color, zorder=2))

    # Needle
    ang = np.radians(180 - (score - 300) / total * 180)
    ax.annotate("", xy=(.82*np.cos(ang), .82*np.sin(ang)), xytext=(0, 0),
                arrowprops=dict(arrowstyle="->", color=NAVY, lw=2.5))
    ax.add_patch(plt.Circle((0,0), .07, color=NAVY, zorder=6))

    # Labels
    ax.text(0, -.18, f"{score}", ha="center", fontsize=22, fontweight="800", color=NAVY)
    fl, fc = fico_label(score)
    ax.text(0, -.34, fl, ha="center", fontsize=10, fontweight="600", color=fc)
    ax.text(-1.15, -.05, "300", ha="center", fontsize=8, color=MUTED)
    ax.text( 1.15, -.05, "850", ha="center", fontsize=8, color=MUTED)

    # FICO band ticks
    for score_tick in [300, 499, 579, 669, 739, 799, 850]:
        ta = np.radians(180 - (score_tick - 300) / total * 180)
        ax.plot([.72*np.cos(ta), .75*np.cos(ta)],
                [.72*np.sin(ta), .75*np.sin(ta)], color="white", lw=1.2, zorder=5)

    ax.set_xlim(-1.35, 1.35); ax.set_ylim(-.45, 1.1)
    ax.set_aspect("equal"); ax.axis("off")
    plt.tight_layout(pad=0)
    return fig


# ── Radar chart ────────────────────────────────────────────────────────────────
def draw_radar(values_norm, labels):
    N = len(labels)
    angles = [n / N * 2 * np.pi for n in range(N)] + [0]
    vals   = list(values_norm) + [values_norm[0]]

    fig, ax = plt.subplots(figsize=(4.5, 4.5), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor(CARD)
    ax.set_facecolor("#FAFBFC")

    ax.plot(angles, vals, color=GOLD, linewidth=2.2, zorder=3)
    ax.fill(angles, vals, color=GOLD, alpha=0.22)

    # Reference ring at 0.5
    ref = [0.5] * (N + 1)
    ax.plot(angles, ref, color=BORDER, linewidth=1, linestyle="--", zorder=2)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, size=9, color=NAVY, fontweight="600")
    ax.set_ylim(0, 1)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["25%", "50%", "75%", "100%"], size=7, color=MUTED)
    ax.grid(color=BORDER, linewidth=0.6)
    ax.spines["polar"].set_color(BORDER)
    ax.set_title("Risk Factor Profile", fontsize=11, fontweight="bold", color=NAVY, pad=15)
    plt.tight_layout()
    return fig


# ── Sidebar ────────────────────────────────────────────────────────────────────
st.sidebar.markdown(f"""
<div style='text-align:center;padding:18px 0 10px'>
    <div style='font-size:34px'>🏦</div>
    <div style='font-size:15px;font-weight:800;color:#fff;letter-spacing:2px'>CREDIT RISK</div>
    <div style='font-size:10px;color:{GOLD_LITE};letter-spacing:3px;margin-top:2px'>INTELLIGENCE PLATFORM</div>
</div>
<hr/>
<div style='font-size:10px;color:{GOLD_LITE};letter-spacing:1.5px;font-weight:700;margin-bottom:8px'>
    ◈ CUSTOMER PROFILE INPUT
</div>""", unsafe_allow_html=True)

age          = st.sidebar.slider("Age", 21, 65, 35)
income       = st.sidebar.number_input("Annual Income ($)", 10000, 300000, 60000, step=1000)
loan_amount  = st.sidebar.number_input("Loan Amount ($)", 5000, 150000, 30000, step=1000)
loan_tenure  = st.sidebar.selectbox("Loan Tenure (months)", [12,24,36,48,60,84,120], index=2)
credit_score = st.sidebar.slider("Credit Score (FICO)", 300, 850, 680)
credit_util  = st.sidebar.slider("Credit Utilization", 0.0, 1.0, 0.28, step=0.01)
repayment    = st.sidebar.slider("On-Time Payments (of last 24)", 0, 24, 20)
num_defaults = st.sidebar.selectbox("Historical Defaults", [0,1,2,3,4,5])
emp_status   = st.sidebar.selectbox("Employment Status",
                 ["Employed","Self-Employed","Unemployed","Retired"])

dti           = round(loan_amount / income, 4)
monthly_emi   = round(loan_amount / loan_tenure, 2)
emi_to_income = round(monthly_emi / (income / 12), 4)
emp_encoded   = le.transform([emp_status])[0]

inp = pd.DataFrame([dict(age=age, income=income, loan_amount=loan_amount,
    loan_tenure=loan_tenure, credit_score=credit_score,
    credit_utilization=credit_util, repayment_history=repayment,
    num_defaults=num_defaults, debt_to_income_ratio=dti,
    monthly_emi=monthly_emi, emi_to_income_ratio=emi_to_income,
    employment_encoded=emp_encoded)])

pred_class = model.predict(inp)[0]
pred_proba = model.predict_proba(inp)[0]
risk_label = RISK_M[pred_class]
risk_color = RISK_C[risk_label]
fl, fc     = fico_label(credit_score)
grade      = credit_grade(credit_score)

ICONS = {"Low": "✅", "Medium": "⚠️", "High": "🔴"}

# Sidebar prediction panel
st.sidebar.markdown("<hr/>", unsafe_allow_html=True)
st.sidebar.markdown(f"""
<div style='background:linear-gradient(135deg,{risk_color}CC,{risk_color});
     border-radius:12px;padding:16px;text-align:center;
     border:1px solid rgba(255,255,255,.12);box-shadow:0 4px 14px rgba(0,0,0,.22)'>
  <div style='font-size:24px'>{ICONS[risk_label]}</div>
  <div style='color:rgba(255,255,255,.7);font-size:9px;letter-spacing:2px;font-weight:700'>RISK VERDICT</div>
  <div style='color:#fff;font-size:22px;font-weight:800;margin:2px 0'>{risk_label.upper()} RISK</div>
  <div style='color:rgba(255,255,255,.82);font-size:11px'>P(Default) = {pred_proba[2]*100:.1f}%</div>
</div>
<div style='margin-top:10px;padding:0 2px'>
  <div style='font-size:9px;color:{GOLD_LITE};letter-spacing:1.5px;font-weight:700;margin-bottom:6px'>PROBABILITY SPLIT</div>
  {''.join([f"""
  <div style='display:flex;justify-content:space-between;align-items:center;margin:4px 0'>
    <span style='font-size:11px;color:#ccc'>{l}</span>
    <div style='flex:1;margin:0 8px;background:rgba(255,255,255,.15);border-radius:3px;height:5px'>
      <div style='background:{RISK_C[l]};width:{pred_proba[i]*100:.1f}%;height:5px;border-radius:3px'></div>
    </div>
    <span style='font-size:11px;color:#fff;font-weight:600;min-width:38px;text-align:right'>{pred_proba[i]*100:.1f}%</span>
  </div>""" for i, l in enumerate(["Low","Medium","High"])])}
</div>
<div style='margin-top:10px;padding:8px;background:rgba(255,255,255,.08);border-radius:8px;text-align:center'>
  <div style='font-size:9px;color:{GOLD_LITE};letter-spacing:1.5px'>CREDIT GRADE</div>
  <div style='font-size:26px;font-weight:900;color:#fff'>{grade}</div>
  <div style='font-size:10px;color:rgba(255,255,255,.7)'>{fl} ({credit_score})</div>
</div>""", unsafe_allow_html=True)


# ── Loan recommendation logic ──────────────────────────────────────────────────
def loan_recommendation(score, util, defaults, high_prob, dti_val, emi_ratio):
    if score >= 700 and high_prob < 0.15 and defaults == 0 and util < 0.4 and dti_val < 1.0:
        return "APPROVED", "#1A6B3C", "#D1FAE5", "✅", \
               "Strong credit profile. Standard interest rate applies.", \
               ["Credit score is in Good-Exceptional range",
                "Clean default history", "Credit utilization is healthy",
                "Debt-to-income ratio is manageable"]
    elif score >= 580 and high_prob < 0.50 and dti_val < 2.0:
        rate_adj = "+1.5% to +3.5% above base rate"
        return "CONDITIONAL", "#B5883E", "#FEF3C7", "⚠️", \
               f"Approval with conditions. Interest rate adjustment: {rate_adj}.", \
               ["Moderate credit profile — requires risk-adjusted pricing",
                "Consider requesting 6-month bank statements",
                "Recommend lower loan amount or longer tenure",
                "Co-signer may strengthen the application"]
    else:
        return "DECLINED", "#8B1A1A", "#FEE2E2", "❌", \
               "Application does not meet minimum credit policy thresholds.", \
               ["Credit score below minimum threshold (580)",
                "High predicted default probability",
                "Recommend credit improvement plan",
                "Re-apply after 6 months with improved profile"]

rec_status, rec_color, rec_bg, rec_icon, rec_note, rec_reasons = \
    loan_recommendation(credit_score, credit_util, num_defaults,
                        pred_proba[2], dti, emi_to_income)


# ── Main ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class='main-header'>
  <h1>🏦 Bank Credit Risk Intelligence Platform</h1>
  <p>Enterprise-grade credit analytics &nbsp;·&nbsp; 4,850 Customers &nbsp;·&nbsp;
     EDA &nbsp;·&nbsp; Statistical Testing &nbsp;·&nbsp; XGBoost · SMOTE · Real-time Scoring</p>
</div>""", unsafe_allow_html=True)

# KPIs
k1,k2,k3,k4,k5 = st.columns(5)
for col, lbl, val, sub in [
    (k1, "TOTAL CUSTOMERS",     f"{len(df):,}",                         "records analyzed"),
    (k2, "AVG CREDIT SCORE",    f"{df['credit_score'].mean():.0f}",     "FICO score"),
    (k3, "AVG ANNUAL INCOME",   f"${df['income'].mean()/1000:.0f}K",    "per customer"),
    (k4, "HIGH RISK CUSTOMERS", f"{(df['risk_label']=='High').sum():,}", f"{(df['risk_label']=='High').mean()*100:.1f}% of portfolio"),
    (k5, "TOTAL LOAN EXPOSURE", f"${df['loan_amount'].sum()/1e6:.1f}M", "outstanding portfolio"),
]:
    col.markdown(f"""<div class='kpi-card'>
        <div class='kpi-label'>{lbl}</div>
        <div class='kpi-value'>{val}</div>
        <div class='kpi-sub'>{sub}</div></div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "  📊  Exploratory Analysis  ",
    "  📈  Risk Segmentation  ",
    "  🤖  Model Performance  ",
    "  🏦  Credit Assessment  ",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — EDA
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("<div class='sec'>Risk Overview</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        fig, ax = plt.subplots(figsize=(6, 4))
        rc = df["risk_label"].value_counts().reindex(["Low","Medium","High"])
        bars = ax.bar(rc.index, rc.values,
                      color=[RISK_C[l] for l in rc.index],
                      width=.55, edgecolor="white", lw=1.2, zorder=3)
        ax.set_title("Customer Risk Distribution"); ax.set_ylabel("Customers")
        ax.spines[["top","right"]].set_visible(False)
        for b in bars:
            ax.text(b.get_x()+b.get_width()/2, b.get_height()+18,
                    f"{int(b.get_height()):,}", ha="center", fontsize=10,
                    fontweight="bold", color=NAVY)
        plt.tight_layout(); st.pyplot(fig); plt.close()

    with c2:
        fig, ax = plt.subplots(figsize=(6, 4))
        for lbl in ["Low","Medium","High"]:
            ax.hist(df[df["risk_label"]==lbl]["credit_score"], bins=28,
                    alpha=.72, label=lbl, color=RISK_C[lbl], edgecolor="white", lw=.5, zorder=3)
        ax.set_title("Credit Score Distribution by Risk Tier")
        ax.set_xlabel("Credit Score"); ax.set_ylabel("Count")
        ax.spines[["top","right"]].set_visible(False)
        ax.legend(title="Risk")
        plt.tight_layout(); st.pyplot(fig); plt.close()

    st.markdown("<div class='sec'>Feature Distributions</div>", unsafe_allow_html=True)
    c3, c4 = st.columns(2)

    with c3:
        fig, ax = plt.subplots(figsize=(6, 4))
        boxes = [df[df["risk_label"]==l]["credit_utilization"].values for l in ["Low","Medium","High"]]
        bp = ax.boxplot(boxes, patch_artist=True, labels=["Low","Medium","High"],
                        medianprops=dict(color=GOLD, lw=2),
                        whiskerprops=dict(color=MUTED), capprops=dict(color=MUTED),
                        flierprops=dict(marker="o", ms=3, alpha=.4))
        for patch, lbl in zip(bp["boxes"], ["Low","Medium","High"]):
            patch.set_facecolor(RISK_L[lbl]); patch.set_edgecolor(RISK_C[lbl]); patch.set_lw(1.5)
        ax.set_title("Credit Utilization by Risk Tier"); ax.set_ylabel("Utilization")
        ax.spines[["top","right"]].set_visible(False)
        plt.tight_layout(); st.pyplot(fig); plt.close()

    with c4:
        ncols = ["credit_score","income","credit_utilization","repayment_history","num_defaults","debt_to_income_ratio"]
        corr = df[ncols].corr()
        mask = np.triu(np.ones_like(corr, dtype=bool))
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.heatmap(corr, mask=mask, annot=True, fmt=".2f",
                    cmap=sns.diverging_palette(220,10,as_cmap=True),
                    center=0, ax=ax, linewidths=.8, linecolor="#F0F4F8",
                    vmin=-1, vmax=1, annot_kws={"size":8,"weight":"bold"},
                    cbar_kws={"shrink":.8})
        ax.set_title("Feature Correlation Matrix")
        plt.tight_layout(); st.pyplot(fig); plt.close()

    st.markdown("<div class='sec'>Income vs Loan Amount by Risk</div>", unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(12, 4))
    for lbl in ["Low","Medium","High"]:
        s = df[df["risk_label"]==lbl]
        ax.scatter(s["income"], s["loan_amount"], label=lbl,
                   alpha=.3, s=10, color=RISK_C[lbl], zorder=3)
    ax.set_xlabel("Annual Income ($)"); ax.set_ylabel("Loan Amount ($)")
    ax.set_title("Income vs Loan Amount — Risk Stratified")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"${x/1000:.0f}K"))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"${x/1000:.0f}K"))
    ax.spines[["top","right"]].set_visible(False)
    ax.legend(title="Risk", title_fontsize=9)
    plt.tight_layout(); st.pyplot(fig); plt.close()

    st.markdown("<div class='sec'>Dataset Preview</div>", unsafe_allow_html=True)
    st.dataframe(df.head(100), use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — RISK SEGMENTATION
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("<div class='sec'>Segmentation by Demographics</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        ct = pd.crosstab(df["employment_status"], df["risk_label"], normalize="index")*100
        fig, ax = plt.subplots(figsize=(6,4))
        ct[["Low","Medium","High"]].plot(kind="bar", stacked=True, ax=ax,
            color=[RISK_C["Low"],RISK_C["Medium"],RISK_C["High"]], edgecolor="white", lw=.8, zorder=3)
        ax.set_title("Risk by Employment Status (%)"); ax.set_xlabel("")
        ax.set_ylabel("Percentage (%)"); ax.spines[["top","right"]].set_visible(False)
        ax.legend(title="Risk", bbox_to_anchor=(1,1), title_fontsize=9)
        plt.xticks(rotation=20, ha="right"); plt.tight_layout()
        st.pyplot(fig); plt.close()

    with c2:
        df["age_group"] = pd.cut(df["age"], bins=[20,30,40,50,65],
                                  labels=["21–30","31–40","41–50","51+"])
        ct2 = pd.crosstab(df["age_group"], df["risk_label"], normalize="index")*100
        fig, ax = plt.subplots(figsize=(6,4))
        ct2[["Low","Medium","High"]].plot(kind="bar", stacked=True, ax=ax,
            color=[RISK_C["Low"],RISK_C["Medium"],RISK_C["High"]], edgecolor="white", lw=.8, zorder=3)
        ax.set_title("Risk by Age Group (%)"); ax.set_xlabel("Age Group")
        ax.set_ylabel("Percentage (%)"); ax.spines[["top","right"]].set_visible(False)
        ax.legend(title="Risk", bbox_to_anchor=(1,1), title_fontsize=9)
        plt.xticks(rotation=0); plt.tight_layout()
        st.pyplot(fig); plt.close()

    st.markdown("<div class='sec'>Credit Score Bands — Default Behavior</div>", unsafe_allow_html=True)
    df["credit_band"] = pd.cut(df["credit_score"],
        bins=[299,499,579,669,739,799,851],
        labels=["Very Poor\n<500","Poor\n500–579","Fair\n580–669","Good\n670–739","Very Good\n740–799","Exceptional\n800+"])
    band_df = df.groupby("credit_band", observed=True).agg(
        avg_defaults=("num_defaults","mean"),
        high_risk_pct=("risk_label", lambda x:(x=="High").mean()*100),
        count=("customer_id","count")
    ).reset_index()

    fig, ax1 = plt.subplots(figsize=(12,4))
    ax2 = ax1.twinx()
    bcolors = [c for _,_,c,_ in FICO_BANDS]
    ax1.bar(band_df["credit_band"], band_df["avg_defaults"],
            color=bcolors, width=.5, alpha=.85, label="Avg Defaults", zorder=3)
    ax2.plot(band_df["credit_band"], band_df["high_risk_pct"],
             color=GOLD, marker="o", lw=2.5, ms=7,
             markerfacecolor=GOLD, markeredgecolor="white", markeredgewidth=1.5,
             label="High Risk %", zorder=4)
    ax1.set_title("Credit Score Bands — Defaults & High-Risk Rate")
    ax1.set_ylabel("Avg Defaults", color=NAVY)
    ax2.set_ylabel("High Risk %", color=GOLD); ax2.tick_params(axis="y", colors=GOLD)
    ax1.spines[["top"]].set_visible(False); ax2.spines[["top"]].set_visible(False)
    h1,l1 = ax1.get_legend_handles_labels(); h2,l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1+h2, l1+l2, loc="upper right", fontsize=9)
    plt.tight_layout(); st.pyplot(fig); plt.close()

    st.markdown("<div class='sec'>Risk Tier Summary Table</div>", unsafe_allow_html=True)
    summary = df.groupby("risk_label").agg(
        Customers=("customer_id","count"),
        Avg_Credit_Score=("credit_score","mean"),
        Avg_Income=("income","mean"),
        Avg_Utilization=("credit_utilization","mean"),
        Avg_Defaults=("num_defaults","mean"),
        Total_Loan_Exposure=("loan_amount","sum"),
    ).round(2).loc[["Low","Medium","High"]]
    st.dataframe(summary.style
        .background_gradient(cmap="RdYlGn_r", subset=["Avg_Defaults"])
        .format({"Avg_Income":"${:,.0f}","Total_Loan_Exposure":"${:,.0f}","Avg_Utilization":"{:.2%}"}),
        use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — MODEL PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, roc_auc_score, roc_curve, confusion_matrix

    df_ml = df.copy(); df_ml["employment_encoded"] = le.transform(df_ml["employment_status"])
    X_all, y_all = df_ml[FEATURES], df_ml["risk_score_numeric"]
    _, X_test, _, y_test = train_test_split(X_all, y_all, test_size=.2, random_state=42, stratify=y_all)
    y_pred = model.predict(X_test); y_prob = model.predict_proba(X_test)
    auc_ovr = roc_auc_score(y_test, y_prob, multi_class="ovr")

    st.markdown("<div class='sec'>Model Summary</div>", unsafe_allow_html=True)
    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Algorithm", "XGBoost")
    m2.metric("ROC-AUC (OvR)", f"{auc_ovr:.4f}")
    m3.metric("Test Samples", f"{len(y_test):,}")
    m4.metric("Class Balancing", "SMOTE")

    st.markdown("<div class='sec'>Feature Importance & ROC Curves</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        imp = pd.Series(model.feature_importances_, index=FEATURES).sort_values()
        imp_colors = [GOLD if v == imp.max() else NAVY_MID for v in imp.values]
        fig, ax = plt.subplots(figsize=(6,5))
        ax.barh(imp.index, imp.values, color=imp_colors, edgecolor="white", lw=.8, zorder=3)
        ax.set_title("Feature Importance (XGBoost)"); ax.set_xlabel("Score")
        ax.spines[["top","right"]].set_visible(False)
        for i, (feat, val) in enumerate(imp.items()):
            ax.text(val+.001, i, f"{val:.3f}", va="center", fontsize=8, color=NAVY)
        plt.tight_layout(); st.pyplot(fig); plt.close()

    with c2:
        fig, ax = plt.subplots(figsize=(6,5))
        for i, (cls, color) in enumerate(zip(["Low","Medium","High"], [RISK_C["Low"],RISK_C["Medium"],RISK_C["High"]])):
            fpr, tpr, _ = roc_curve((y_test==i).astype(int), y_prob[:,i])
            auc_v = roc_auc_score((y_test==i).astype(int), y_prob[:,i])
            ax.plot(fpr, tpr, color=color, lw=2.5, label=f"{cls}  (AUC = {auc_v:.3f})")
        ax.fill_between([0,1],[0,1], alpha=.05, color=MUTED)
        ax.plot([0,1],[0,1],"--",color=MUTED,lw=1)
        ax.set_xlabel("False Positive Rate"); ax.set_ylabel("True Positive Rate")
        ax.set_title("ROC-AUC Curves (One-vs-Rest)"); ax.spines[["top","right"]].set_visible(False)
        ax.legend(title="Risk Tier", title_fontsize=9)
        plt.tight_layout(); st.pyplot(fig); plt.close()

    st.markdown("<div class='sec'>Confusion Matrix</div>", unsafe_allow_html=True)
    cm = confusion_matrix(y_test, y_pred)
    fig, ax = plt.subplots(figsize=(5,4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=["Low","Medium","High"], yticklabels=["Low","Medium","High"],
                linewidths=1, linecolor="#F0F4F8",
                annot_kws={"size":14,"weight":"bold"}, ax=ax)
    ax.set_xlabel("Predicted", fontsize=11); ax.set_ylabel("Actual", fontsize=11)
    ax.set_title("Confusion Matrix — XGBoost")
    col_cm, _ = st.columns([1,1])
    with col_cm: st.pyplot(fig); plt.close()

    st.markdown("<div class='sec'>Classification Report</div>", unsafe_allow_html=True)
    rpt = pd.DataFrame(classification_report(y_test, y_pred,
          target_names=["Low","Medium","High"], output_dict=True)).T.round(3)
    st.dataframe(rpt.style.background_gradient(cmap="Blues", subset=["precision","recall","f1-score"]),
                 use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — CREDIT ASSESSMENT (Live Prediction)
# ══════════════════════════════════════════════════════════════════════════════
with tab4:

    # ── Row A: Gauge | Verdict | Loan Decision ─────────────────────────────────
    st.markdown("<div class='sec'>Credit Score & Risk Assessment</div>", unsafe_allow_html=True)
    ca, cb, cc = st.columns([1.1, 1, 1.1])

    with ca:
        st.markdown(f"<div style='text-align:center;font-size:11px;color:{MUTED};font-weight:700;letter-spacing:1px;margin-bottom:4px'>FICO CREDIT SCORE GAUGE</div>", unsafe_allow_html=True)
        st.pyplot(draw_gauge(credit_score)); plt.close()
        # FICO band legend
        st.markdown(f"""
        <div style='display:flex;flex-wrap:wrap;gap:4px;justify-content:center;margin-top:4px'>
          {''.join([f'<span style="background:{c};color:#fff;font-size:9px;font-weight:600;padding:2px 7px;border-radius:10px">{l}</span>' for _,_,c,l in FICO_BANDS])}
        </div>""", unsafe_allow_html=True)

    with cb:
        st.markdown(f"<div style='text-align:center;font-size:11px;color:{MUTED};font-weight:700;letter-spacing:1px;margin-bottom:4px'>RISK CLASSIFICATION</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,{risk_color}D0,{risk_color});
             border-radius:14px;padding:22px 16px;text-align:center;
             box-shadow:0 4px 18px rgba(0,0,0,.14)'>
          <div style='font-size:30px;margin-bottom:6px'>{ICONS[risk_label]}</div>
          <div style='color:rgba(255,255,255,.75);font-size:9px;letter-spacing:2px;font-weight:700'>RISK LEVEL</div>
          <div style='color:#fff;font-size:28px;font-weight:900;letter-spacing:1px'>{risk_label.upper()}</div>
          <div style='color:rgba(255,255,255,.85);font-size:12px;margin-top:4px'>
            Default Probability: <b>{pred_proba[2]*100:.1f}%</b>
          </div>
          <hr style='border-color:rgba(255,255,255,.2);margin:10px 0'/>
          {''.join([f"""
          <div style='display:flex;justify-content:space-between;margin:3px 0'>
            <span style='color:rgba(255,255,255,.75);font-size:11px'>{l}</span>
            <span style='color:#fff;font-size:11px;font-weight:700'>{pred_proba[i]*100:.1f}%</span>
          </div>""" for i,l in enumerate(["Low Risk","Medium Risk","High Risk"])])}
        </div>""", unsafe_allow_html=True)

    with cc:
        st.markdown(f"<div style='text-align:center;font-size:11px;color:{MUTED};font-weight:700;letter-spacing:1px;margin-bottom:4px'>LOAN DECISION</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style='background:{rec_bg};border:2px solid {rec_color};
             border-radius:14px;padding:18px;text-align:center;
             box-shadow:0 4px 18px rgba(0,0,0,.08)'>
          <div style='font-size:28px;margin-bottom:4px'>{rec_icon}</div>
          <div style='color:{rec_color};font-size:11px;letter-spacing:2px;font-weight:700'>DECISION</div>
          <div style='color:{rec_color};font-size:22px;font-weight:900'>{rec_status}</div>
          <div style='color:#444;font-size:11px;margin-top:8px'>{rec_note}</div>
          <hr style='border-color:{rec_color}40;margin:10px 0'/>
          {''.join([f'<div style="font-size:11px;color:#555;text-align:left;margin:4px 0">• {r}</div>' for r in rec_reasons])}
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row B: Customer Profile | Radar | Position in Portfolio ───────────────
    st.markdown("<div class='sec'>Customer Analysis</div>", unsafe_allow_html=True)
    r1, r2, r3 = st.columns([1, 1, 1.2])

    with r1:
        st.markdown(f"<div style='font-size:11px;color:{MUTED};font-weight:700;letter-spacing:1px;margin-bottom:8px'>CUSTOMER PROFILE</div>", unsafe_allow_html=True)
        rows = [
            ("Age",               f"{age} yrs"),
            ("Annual Income",     f"${income:,}"),
            ("Loan Amount",       f"${loan_amount:,}"),
            ("Loan Tenure",       f"{loan_tenure} months"),
            ("Credit Score",      f"{credit_score} / 850"),
            ("FICO Grade",        f"{grade}  —  {fl}"),
            ("Credit Utilization",f"{credit_util*100:.0f}%"),
            ("On-Time Payments",  f"{repayment} / 24"),
            ("Defaults",          f"{num_defaults}"),
            ("Employment",        emp_status),
            ("Debt-to-Income",    f"{dti:.3f}"),
            ("Monthly EMI",       f"${monthly_emi:,.0f}"),
            ("EMI / Income",      f"{emi_to_income*100:.1f}%"),
        ]
        for lbl, val in rows:
            st.markdown(f"""
            <div class='info-row'>
              <span class='info-label'>{lbl}</span>
              <span class='info-value'>{val}</span>
            </div>""", unsafe_allow_html=True)

    with r2:
        # Radar chart — normalize each factor to 0-1 (higher = more risk)
        cs_risk   = 1 - (credit_score - 300) / 550
        util_risk = credit_util
        def_risk  = min(num_defaults / 5, 1.0)
        rep_risk  = 1 - repayment / 24
        dti_risk  = min(dti / 3.0, 1.0)
        emi_risk  = min(emi_to_income / 0.6, 1.0)

        radar_vals   = [cs_risk, util_risk, def_risk, rep_risk, dti_risk, emi_risk]
        radar_labels = ["Credit\nScore", "Utilization", "Defaults",
                        "Repayment\nGap", "DTI Ratio", "EMI\nBurden"]

        st.pyplot(draw_radar(radar_vals, radar_labels)); plt.close()
        st.markdown(f"<div style='text-align:center;font-size:10px;color:{MUTED}'>Higher = More Risk &nbsp;·&nbsp; Dashed = 50% Risk Line</div>", unsafe_allow_html=True)

    with r3:
        # Customer position in portfolio scatter
        st.markdown(f"<div style='font-size:11px;color:{MUTED};font-weight:700;letter-spacing:1px;margin-bottom:4px'>YOUR CUSTOMER vs PORTFOLIO</div>", unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(6, 4.8))
        for lbl in ["Low","Medium","High"]:
            s = df[df["risk_label"]==lbl]
            ax.scatter(s["credit_score"], s["credit_utilization"],
                       alpha=.18, s=8, color=RISK_C[lbl], label=lbl, zorder=2)

        # Plot this customer as a star
        ax.scatter(credit_score, credit_util,
                   s=280, color=GOLD, marker="*", zorder=6,
                   edgecolors=NAVY, linewidths=1.2, label="This Customer")
        ax.annotate("  ← This Customer",
                    xy=(credit_score, credit_util),
                    fontsize=9, fontweight="bold", color=NAVY,
                    va="center")

        # Threshold lines
        ax.axvline(580, color=MUTED, lw=1, linestyle="--", alpha=.6)
        ax.axhline(0.60, color=MUTED, lw=1, linestyle="--", alpha=.6)
        ax.text(582, .02, "Min Score 580", fontsize=7, color=MUTED)
        ax.text(.02, .615, "High Util Threshold", fontsize=7, color=MUTED, transform=ax.get_yaxis_transform())

        ax.set_xlabel("Credit Score"); ax.set_ylabel("Credit Utilization")
        ax.set_title("Credit Score vs Utilization — Portfolio View")
        ax.spines[["top","right"]].set_visible(False)
        ax.legend(title="Risk", title_fontsize=9, markerscale=1.5)
        plt.tight_layout(); st.pyplot(fig); plt.close()

    # ── Row C: Risk Flags ──────────────────────────────────────────────────────
    st.markdown("<div class='sec'>Risk Flags & Alerts</div>", unsafe_allow_html=True)
    fc1, fc2 = st.columns(2)

    flags = []
    if credit_util > 0.60:
        flags.append(("CRITICAL", f"Credit utilization {credit_util*100:.0f}% — exceeds 60% threshold", "#8B1A1A", "#FEE2E2"))
    elif credit_util > 0.40:
        flags.append(("WARNING", f"Credit utilization {credit_util*100:.0f}% — elevated, ideal is <30%", "#B5883E", "#FEF3C7"))
    if credit_score < 500:
        flags.append(("CRITICAL", f"Credit score {credit_score} — Very Poor. Minimum threshold is 580", "#8B1A1A", "#FEE2E2"))
    elif credit_score < 580:
        flags.append(("WARNING", f"Credit score {credit_score} — Below minimum lending threshold (580)", "#B5883E", "#FEF3C7"))
    if num_defaults >= 2:
        flags.append(("CRITICAL", f"{num_defaults} historical defaults — high recidivism risk", "#8B1A1A", "#FEE2E2"))
    elif num_defaults == 1:
        flags.append(("WARNING", "1 historical default — proceed with caution", "#B5883E", "#FEF3C7"))
    if dti > 2.0:
        flags.append(("CRITICAL", f"Debt-to-income ratio {dti:.2f} — severely overleveraged", "#8B1A1A", "#FEE2E2"))
    elif dti > 1.0:
        flags.append(("WARNING", f"Debt-to-income ratio {dti:.2f} — moderately high", "#B5883E", "#FEF3C7"))
    if emi_to_income > 0.50:
        flags.append(("CRITICAL", f"EMI is {emi_to_income*100:.0f}% of monthly income — unaffordable", "#8B1A1A", "#FEE2E2"))
    elif emi_to_income > 0.35:
        flags.append(("WARNING", f"EMI is {emi_to_income*100:.0f}% of monthly income — tight budget", "#B5883E", "#FEF3C7"))
    if repayment < 12:
        flags.append(("CRITICAL", f"Only {repayment}/24 on-time payments — poor repayment history", "#8B1A1A", "#FEE2E2"))
    elif repayment < 18:
        flags.append(("WARNING", f"{repayment}/24 on-time payments — below average", "#B5883E", "#FEF3C7"))
    if emp_status == "Unemployed":
        flags.append(("WARNING", "Unemployed — income instability risk", "#B5883E", "#FEF3C7"))

    half = max(1, len(flags) // 2 + len(flags) % 2)
    with fc1:
        if not flags:
            st.markdown("<div class='clear-box'><b>✓ No risk flags detected</b><br>This customer meets all standard lending criteria.</div>", unsafe_allow_html=True)
        for severity, msg, color, bg in flags[:half]:
            icon = "🔴" if severity=="CRITICAL" else "⚠️"
            st.markdown(f"""
            <div style='background:{bg};border-left:4px solid {color};
                 border-radius:0 8px 8px 0;padding:10px 13px;margin:5px 0'>
              <span style='color:{color};font-size:10px;font-weight:800;letter-spacing:1px'>{icon} {severity}</span><br>
              <span style='font-size:12px;color:#333'>{msg}</span>
            </div>""", unsafe_allow_html=True)
    with fc2:
        for severity, msg, color, bg in flags[half:]:
            icon = "🔴" if severity=="CRITICAL" else "⚠️"
            st.markdown(f"""
            <div style='background:{bg};border-left:4px solid {color};
                 border-radius:0 8px 8px 0;padding:10px 13px;margin:5px 0'>
              <span style='color:{color};font-size:10px;font-weight:800;letter-spacing:1px'>{icon} {severity}</span><br>
              <span style='font-size:12px;color:#333'>{msg}</span>
            </div>""", unsafe_allow_html=True)
        if not flags:
            st.markdown(f"""
            <div style='background:#EFF6FF;border-left:4px solid {NAVY_LITE};
                 border-radius:0 8px 8px 0;padding:10px 13px'>
              <span style='color:{NAVY};font-size:10px;font-weight:800'>ℹ RECOMMENDATION</span><br>
              <span style='font-size:12px;color:#333'>
                Consider offering premium credit products or pre-approved limit increase.
              </span>
            </div>""", unsafe_allow_html=True)
