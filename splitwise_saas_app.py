"""
Splitwise Pro — Enterprise Expense Splitter
Premium dark UI · Multi-currency · JSON Save/Load · Analytics
Run with: streamlit run splitwise_pro.py
"""

import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from io import BytesIO
from datetime import datetime
import json
import uuid

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="Splitwise Pro",
    layout="wide",
    page_icon="💸",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# PREMIUM DARK CSS
# ─────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #080C12; color: #D4DCE8; }

[data-testid="stSidebar"] {
    background: #0D1219;
    border-right: 1px solid #1C2535;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #0D1219;
    border: 1px solid #1C2535;
    border-radius: 12px;
    padding: 5px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #5A7090;
    border-radius: 9px;
    font-weight: 500;
    font-size: 0.88rem;
    padding: 8px 18px;
    transition: all 0.2s ease;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #1A4FAA 0%, #0E3A80 100%) !important;
    color: #EBF0FF !important;
    box-shadow: 0 2px 12px rgba(26,79,170,0.4);
}

/* KPI Cards */
[data-testid="stMetric"] {
    background: linear-gradient(145deg, #0F1A28 0%, #0A1020 100%);
    border: 1px solid #1C2F48;
    border-radius: 14px;
    padding: 18px 20px;
    position: relative;
    overflow: hidden;
}
[data-testid="stMetric"]::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #1A4FAA, #00D4AA);
}
[data-testid="stMetricLabel"] { color: #5A7090 !important; font-size: 0.75rem !important; text-transform: uppercase; letter-spacing: 0.08em; }
[data-testid="stMetricValue"] { color: #E8F0FF !important; font-size: 1.5rem !important; font-weight: 700; font-family: 'JetBrains Mono', monospace; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #1A4FAA 0%, #0E3A80 100%);
    color: #EBF0FF;
    border: none;
    border-radius: 9px;
    font-weight: 600;
    font-size: 0.875rem;
    padding: 10px 22px;
    transition: all 0.2s ease;
    box-shadow: 0 2px 8px rgba(26,79,170,0.3);
}
.stButton > button:hover {
    background: linear-gradient(135deg, #1E5CC4 0%, #1244A0 100%);
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(26,79,170,0.45);
}

/* Inputs */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
    background: #0D1826 !important;
    border: 1px solid #1C2F48 !important;
    border-radius: 9px !important;
    color: #D4DCE8 !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* Selectbox */
[data-baseweb="select"] > div {
    background: #0D1826 !important;
    border: 1px solid #1C2F48 !important;
    border-radius: 9px !important;
    color: #D4DCE8 !important;
}

/* Dataframe */
[data-testid="stDataFrame"] { border: 1px solid #1C2F48; border-radius: 12px; overflow: hidden; }

/* Expander */
[data-testid="stExpander"] { background: #0D1219; border: 1px solid #1C2535; border-radius: 12px; }

/* Divider */
hr { border-color: #1C2535; margin: 20px 0; }

/* Multiselect tags */
[data-baseweb="tag"] { background: #0D2244 !important; border-color: #1A4FAA !important; color: #5B9CF6 !important; border-radius: 6px !important; }

/* File uploader */
[data-testid="stFileUploader"] { background: #0D1826; border: 1px dashed #1C2F48; border-radius: 10px; padding: 8px; }

/* Custom components */
.app-header {
    display: flex; align-items: center; gap: 16px;
    padding: 24px 0 8px;
    border-bottom: 1px solid #1C2535;
    margin-bottom: 24px;
}
.app-header h1 {
    margin: 0; font-size: 1.9rem; font-weight: 700;
    background: linear-gradient(135deg, #5B9CF6 0%, #00D4AA 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.pill {
    background: #0D2244; color: #5B9CF6;
    border: 1px solid #1A4FAA;
    padding: 3px 12px; border-radius: 20px;
    font-size: 0.78rem; font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
    display: inline-block;
}
.pill-green { background: #072218; color: #00D4AA; border-color: #0A5540; }
.pill-amber { background: #1E1400; color: #F0A500; border-color: #5A3A00; }

.section-label {
    font-size: 0.72rem; font-weight: 600; color: #4A6080;
    text-transform: uppercase; letter-spacing: 0.12em;
    margin-bottom: 12px; margin-top: 24px;
}
.sidebar-section {
    font-size: 0.68rem; font-weight: 700; color: #2E4060;
    text-transform: uppercase; letter-spacing: 0.14em;
    padding: 12px 0 6px;
}

.settlement-row {
    display: flex; align-items: center; justify-content: space-between;
    background: linear-gradient(135deg, #0A1E38 0%, #060F1C 100%);
    border: 1px solid #1C3560;
    border-radius: 10px;
    padding: 14px 20px; margin: 6px 0;
}
.settle-arrow { color: #5B9CF6; font-size: 1.2rem; }
.settle-amount { font-family: 'JetBrains Mono', monospace; color: #00D4AA; font-weight: 700; font-size: 1rem; }
.settle-name { color: #C0CCD8; font-weight: 600; }

.member-row {
    display: flex; align-items: center; justify-content: space-between;
    background: #0A1420; border: 1px solid #1C2F48;
    border-radius: 9px; padding: 10px 16px; margin: 5px 0;
}
.conv-info {
    background: linear-gradient(135deg, #071428 0%, #040C1A 100%);
    border: 1px solid #1A3060; border-radius: 10px;
    padding: 12px 18px; margin: 10px 0;
    display: flex; align-items: center; gap: 10px;
    font-size: 0.875rem;
}
.conv-info span { color: #5A7090; }
.conv-info strong { color: #5B9CF6; font-family: 'JetBrains Mono', monospace; }
.empty-state { text-align: center; padding: 48px 24px; color: #3A5070; }
.empty-state .emoji { font-size: 2.5rem; margin-bottom: 12px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DATABASE INIT
# ─────────────────────────────────────────────

@st.cache_resource
def init_db():
    c = sqlite3.connect("splitwise_pro.db", check_same_thread=False)
    c.executescript("""
        CREATE TABLE IF NOT EXISTS groups (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT UNIQUE NOT NULL,
            base_currency TEXT NOT NULL DEFAULT 'EUR',
            created_at    TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS currencies (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            code     TEXT NOT NULL,
            rate     REAL NOT NULL DEFAULT 1.0,
            UNIQUE(group_id, code)
        );
        CREATE TABLE IF NOT EXISTS members (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            name     TEXT NOT NULL,
            UNIQUE(group_id, name)
        );
        CREATE TABLE IF NOT EXISTS expenses (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id        INTEGER NOT NULL,
            date            TEXT NOT NULL,
            description     TEXT NOT NULL,
            category        TEXT,
            paid_by         TEXT NOT NULL,
            person          TEXT NOT NULL,
            amount_original REAL NOT NULL,
            currency        TEXT NOT NULL,
            amount_base     REAL NOT NULL,
            created_at      TEXT NOT NULL,
            expense_ref     TEXT
        );
    """)
    c.commit()
    return c

conn   = init_db()
cursor = conn.cursor()

# ── Migration: add expense_ref if not present ──
try:
    cursor.execute("ALTER TABLE expenses ADD COLUMN expense_ref TEXT")
    conn.commit()
except Exception:
    pass  # column already exists

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────

CATEGORIES = [
    "🍽️ Food & Dining", "🏨 Accommodation", "✈️ Transport",
    "🎭 Entertainment", "🛒 Shopping", "⚕️ Health",
    "📱 Utilities", "🎒 Activities", "💡 Miscellaneous",
]

COMMON_CURRENCIES = [
    "EUR", "USD", "GBP", "INR", "JPY", "AED", "SGD",
    "CHF", "AUD", "CAD", "THB", "MYR", "IDR", "KRW", "HKD",
]

PALETTE = ["#5B9CF6", "#00D4AA", "#F0A500", "#F06090", "#9B72FF", "#FF7A50", "#50C8FF"]
PLOTLY_THEME = dict(template="plotly_dark", paper_bgcolor="#0D1219", plot_bgcolor="#0D1219", font_color="#8AA0BC")

# ─────────────────────────────────────────────
# DATA HELPERS
# ─────────────────────────────────────────────

def get_groups():
    return cursor.execute("SELECT id,name,base_currency FROM groups ORDER BY created_at DESC").fetchall()

def get_currencies(group_id: int) -> dict:
    rows = cursor.execute("SELECT code,rate FROM currencies WHERE group_id=?", (group_id,)).fetchall()
    return {r[0]: r[1] for r in rows}

def get_members(group_id: int) -> list:
    rows = cursor.execute("SELECT name FROM members WHERE group_id=? ORDER BY name", (group_id,)).fetchall()
    return [r[0] for r in rows]

def get_expenses(group_id: int) -> pd.DataFrame:
    return pd.read_sql_query(
        "SELECT * FROM expenses WHERE group_id=? ORDER BY date DESC, id DESC",
        conn, params=(group_id,)
    )

def to_base(amount: float, currency: str, currencies: dict, base: str) -> float:
    """Convert foreign amount → base.  Rate definition: 1 base = X foreign."""
    if currency == base:
        return amount
    rate = currencies.get(currency, 1.0)
    return amount / rate if rate else amount

def compute_balances(df: pd.DataFrame, members: list) -> dict:
    bal = {m: 0.0 for m in members}
    for _, r in df.iterrows():
        if r["paid_by"] in bal:
            bal[r["paid_by"]] += r["amount_base"]
        if r["person"] in bal:
            bal[r["person"]] -= r["amount_base"]
    return {k: round(v, 2) for k, v in bal.items()}

def compute_settlements(balance: dict) -> list:
    creditors = sorted([[p, b]  for p, b in balance.items() if b > 0.005],  key=lambda x: -x[1])
    debtors   = sorted([[p, -b] for p, b in balance.items() if b < -0.005], key=lambda x: -x[1])
    result = []
    for d in debtors:
        for c in creditors:
            if d[1] < 0.005: break
            pay = min(d[1], c[1])
            if pay > 0.005:
                result.append((d[0], c[0], round(pay, 2)))
                d[1] -= pay
                c[1] -= pay
    return result

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown('<div style="padding:16px 0 4px;"><h2 style="margin:0;font-size:1.3rem;background:linear-gradient(135deg,#5B9CF6,#00D4AA);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">💸 Splitwise Pro</h2></div>', unsafe_allow_html=True)

    # ── Create Trip ──
    st.markdown('<div class="sidebar-section">New Trip / Project</div>', unsafe_allow_html=True)
    with st.expander("➕ Create Trip", expanded=False):
        trip_name     = st.text_input("Trip / Project Name", placeholder="e.g. Tokyo 2025", key="new_trip_name")
        base_curr_sel = st.selectbox("Base Currency", COMMON_CURRENCIES, key="new_base_curr")
        if st.button("Create Trip", use_container_width=True, key="btn_create"):
            if trip_name.strip():
                try:
                    cursor.execute(
                        "INSERT INTO groups(name,base_currency,created_at) VALUES(?,?,?)",
                        (trip_name.strip(), base_curr_sel, datetime.now().isoformat())
                    )
                    gid = cursor.lastrowid
                    cursor.execute(
                        "INSERT OR IGNORE INTO currencies(group_id,code,rate) VALUES(?,?,?)",
                        (gid, base_curr_sel, 1.0)
                    )
                    conn.commit()
                    st.success(f"'{trip_name}' created!")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("A trip with this name already exists.")
            else:
                st.error("Enter a trip name.")

    # ── Select Trip ──
    st.markdown('<div class="sidebar-section">Active Trip</div>', unsafe_allow_html=True)
    groups = get_groups()
    if not groups:
        st.info("Create a trip above to get started.")
        st.stop()

    group_map     = {g[1]: (g[0], g[2]) for g in groups}
    selected_name = st.selectbox("", list(group_map.keys()), label_visibility="collapsed", key="sel_group")
    group_id, base_currency = group_map[selected_name]
    st.markdown(f'Base currency: <span class="pill">{base_currency}</span>', unsafe_allow_html=True)

    # ── Delete Trip ──
    with st.expander("🗑️ Delete This Trip", expanded=False):
        st.warning("Permanently deletes all data for this trip.")
        if st.button("Confirm Delete", use_container_width=True, key="btn_del_trip"):
            for tbl in ("expenses", "members", "currencies"):
                cursor.execute(f"DELETE FROM {tbl} WHERE group_id=?", (group_id,))
            cursor.execute("DELETE FROM groups WHERE id=?", (group_id,))
            conn.commit()
            st.rerun()

    # ── Save / Load ──
    st.markdown('<div class="sidebar-section">Save & Restore</div>', unsafe_allow_html=True)

    def build_json_export() -> str:
        return json.dumps({
            "meta":      {"exported_at": datetime.now().isoformat(), "app": "Splitwise Pro"},
            "group":     {"name": selected_name, "base_currency": base_currency},
            "currencies": [{"code": c, "rate": r} for c, r in get_currencies(group_id).items()],
            "members":   get_members(group_id),
            "expenses":  [] if get_expenses(group_id).empty else get_expenses(group_id).to_dict(orient="records"),
        }, indent=2, default=str)

    st.download_button(
        "📥 Save Session (JSON)",
        data=build_json_export(),
        file_name=f"{selected_name.replace(' ','_')}_splitwise.json",
        mime="application/json",
        use_container_width=True,
        key="btn_save_json",
    )

    uploaded = st.file_uploader("📤 Load Session", type=["json"], key="json_upload")
    if uploaded:
        try:
            data = json.load(uploaded)
            grp  = data["group"]
            cursor.execute(
                "INSERT OR IGNORE INTO groups(name,base_currency,created_at) VALUES(?,?,?)",
                (grp["name"], grp["base_currency"], datetime.now().isoformat())
            )
            conn.commit()
            ngid = cursor.execute("SELECT id FROM groups WHERE name=?", (grp["name"],)).fetchone()[0]
            for c in data.get("currencies", []):
                cursor.execute("INSERT OR REPLACE INTO currencies(group_id,code,rate) VALUES(?,?,?)", (ngid, c["code"], c["rate"]))
            for m in data.get("members", []):
                cursor.execute("INSERT OR IGNORE INTO members(group_id,name) VALUES(?,?)", (ngid, m))
            cursor.execute("DELETE FROM expenses WHERE group_id=?", (ngid,))
            for e in data.get("expenses", []):
                cursor.execute("""
                    INSERT INTO expenses(group_id,date,description,category,paid_by,person,
                        amount_original,currency,amount_base,created_at)
                    VALUES(?,?,?,?,?,?,?,?,?,?)
                """, (ngid, e.get("date"), e.get("description"), e.get("category"),
                      e.get("paid_by"), e.get("person"), e.get("amount_original"),
                      e.get("currency"), e.get("amount_base"),
                      e.get("created_at", datetime.now().isoformat())))
            conn.commit()
            st.success(f"Loaded '{grp['name']}'!")
            st.rerun()
        except Exception as ex:
            st.error(f"Load failed: {ex}")

# ─────────────────────────────────────────────
# MAIN — LOAD DATA + HEADER
# ─────────────────────────────────────────────

members        = get_members(group_id)
currencies_map = get_currencies(group_id)
df             = get_expenses(group_id)
n_members      = len(members)
n_expenses     = df["description"].nunique() if not df.empty else 0
total_spent    = df["amount_base"].sum() if not df.empty else 0.0

st.markdown(f"""
<div class="app-header">
    <div style="flex:1">
        <h1>💸 {selected_name}</h1>
        <div style="display:flex;gap:8px;margin-top:6px;flex-wrap:wrap;">
            <span class="pill">Base: {base_currency}</span>
            <span class="pill-green">{n_members} Members</span>
            <span class="pill-amber">{n_expenses} Expenses</span>
        </div>
    </div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:1.7rem;font-weight:700;
         background:linear-gradient(135deg,#5B9CF6,#00D4AA);
         -webkit-background-clip:text;-webkit-text-fill-color:transparent;white-space:nowrap;">
        {base_currency} {total_spent:,.2f}
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────

tab_overview, tab_add, tab_manage, tab_analytics, tab_export = st.tabs([
    "📊  Overview", "➕  Add Expense", "⚙️  Manage", "📈  Analytics", "📤  Export",
])

# ══════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ══════════════════════════════════════════════

with tab_overview:

    if not df.empty:
        avg_exp     = df.groupby("description")["amount_base"].sum().mean()
        top_spender = df.groupby("paid_by")["amount_base"].sum().idxmax()
        top_cat     = df.groupby("category")["amount_base"].sum().idxmax() if "category" in df.columns else "—"
        per_head    = total_spent / n_members if n_members else 0.0
    else:
        avg_exp = per_head = 0.0
        top_spender = top_cat = "—"

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric(f"Total ({base_currency})",    f"{total_spent:,.2f}")
    k2.metric("Unique Expenses",             n_expenses)
    k3.metric(f"Per Head ({base_currency})", f"{per_head:,.2f}")
    k4.metric("Top Spender",                 top_spender)
    k5.metric("Top Category",                top_cat.split()[-1] if top_cat != "—" else "—")

    st.markdown("---")

    if members and not df.empty:
        balance = compute_balances(df, members)

        # ── Row 1: Net Balances + Pairwise Individual Amounts ─────────────
        col_bal, col_pair = st.columns(2, gap="large")

        with col_bal:
            st.markdown('<div class="section-label">💰 Net Balances</div>', unsafe_allow_html=True)
            for person, bal in sorted(balance.items(), key=lambda x: -x[1]):
                color  = "#00D4AA" if bal >= 0 else "#F06090"
                symbol = "▲" if bal >= 0 else "▼"
                label  = "gets back" if bal >= 0 else "owes"
                st.markdown(f"""
                <div class="member-row">
                    <span style="color:#C0CCD8;font-weight:600;">👤 {person}</span>
                    <span style="color:{color};font-family:'JetBrains Mono',monospace;font-weight:700;">
                        {symbol} {base_currency} {abs(bal):,.2f}
                        <span style="font-size:0.7rem;font-weight:400;color:#5A7090;"> {label}</span>
                    </span>
                </div>
                """, unsafe_allow_html=True)

        with col_pair:
            st.markdown('<div class="section-label">🔗 Individual Amounts Owed</div>', unsafe_allow_html=True)
            # Pairwise: for every (A, B) pair, calculate net amount A owes B
            # = sum(rows where paid_by=B, person=A) - sum(rows where paid_by=A, person=B)
            # If positive → A owes B; if negative → B owes A
            any_pair = False
            for i, person_a in enumerate(members):
                for person_b in members[i+1:]:
                    b_paid_for_a = df[(df["paid_by"] == person_b) & (df["person"] == person_a)]["amount_base"].sum()
                    a_paid_for_b = df[(df["paid_by"] == person_a) & (df["person"] == person_b)]["amount_base"].sum()
                    net = round(b_paid_for_a - a_paid_for_b, 2)
                    if abs(net) < 0.01:
                        continue
                    any_pair = True
                    if net > 0:
                        debtor, creditor, amt = person_a, person_b, net
                    else:
                        debtor, creditor, amt = person_b, person_a, -net
                    st.markdown(f"""
                    <div class="member-row" style="justify-content:space-between;">
                        <div style="display:flex;align-items:center;gap:8px;">
                            <span style="color:#C0CCD8;font-weight:600;">👤 {debtor}</span>
                            <span style="color:#5B9CF6;font-size:0.9rem;">owes</span>
                            <span style="color:#C0CCD8;font-weight:600;">👤 {creditor}</span>
                        </div>
                        <span style="color:#F0A500;font-family:'JetBrains Mono',monospace;font-weight:700;">
                            {base_currency} {amt:,.2f}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
            if not any_pair:
                st.success("✅ No individual amounts outstanding!")

        # ── Row 2: Settlement Suggestions (full width) ────────────────────
        st.markdown("---")
        st.markdown('<div class="section-label">🔄 Settlement Suggestions — Minimum Transactions</div>', unsafe_allow_html=True)
        settlements = compute_settlements(balance)
        if settlements:
            s_cols = st.columns(min(len(settlements), 3), gap="medium")
            for idx, (debtor, creditor, amt) in enumerate(settlements):
                with s_cols[idx % len(s_cols)]:
                    st.markdown(f"""
                    <div class="settlement-row" style="flex-direction:column;align-items:flex-start;gap:8px;">
                        <div style="display:flex;align-items:center;justify-content:space-between;width:100%;">
                            <span style="color:#5A7090;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.08em;">Payment {idx+1}</span>
                            <span class="settle-amount">{base_currency} {amt:,.2f}</span>
                        </div>
                        <div style="display:flex;align-items:center;gap:10px;width:100%;">
                            <span class="settle-name">👤 {debtor}</span>
                            <span class="settle-arrow" style="flex:1;text-align:center;">→ pays →</span>
                            <span class="settle-name">👤 {creditor}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.success("✅ Everyone is settled up — no payments needed!")

    else:
        col_bal, col_settle = st.columns(2, gap="large")
        with col_bal:
            st.markdown('<div class="section-label">💰 Net Balances</div>', unsafe_allow_html=True)
            st.markdown('<div class="empty-state"><div class="emoji">💳</div><p>Add members &amp; expenses<br>to see balances.</p></div>', unsafe_allow_html=True)
        with col_settle:
            st.markdown('<div class="section-label">🔄 Settlement Suggestions</div>', unsafe_allow_html=True)
            st.markdown('<div class="empty-state"><div class="emoji">🤝</div><p>Settlements appear<br>once expenses are logged.</p></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-label">📋 Expense Log</div>', unsafe_allow_html=True)
    if not df.empty:
        display = df[["date","description","category","paid_by","person","currency","amount_original","amount_base"]].copy()
        display.columns = ["Date","Description","Category","Paid By","Person","Curr","Amount (Orig)",f"Amount ({base_currency})"]
        display["Amount (Orig)"]                 = display["Amount (Orig)"].round(2)
        display[f"Amount ({base_currency})"]     = display[f"Amount ({base_currency})"].round(2)
        st.dataframe(display, use_container_width=True, hide_index=True, height=320)
    else:
        st.markdown('<div class="empty-state"><div class="emoji">📭</div><p>No expenses yet.<br>Head to <strong>Add Expense</strong> to get started.</p></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 2 — ADD EXPENSE
# ══════════════════════════════════════════════

with tab_add:

    if not members:
        st.warning("⚠️ No members yet — add them in the **Manage** tab first.")
        st.markdown('<div class="empty-state"><div class="emoji">👥</div><p>Head to <strong>Manage → Members</strong><br>to add people to this trip.</p></div>', unsafe_allow_html=True)
    elif not currencies_map:
        st.warning("⚠️ No currencies configured. Go to the **Manage** tab.")
    else:
        all_curr = list(currencies_map.keys())

        st.markdown('<div class="section-label">Expense Details</div>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
        with c1:
            desc     = st.text_input("Description", placeholder="Hotel Bali...", key="add_desc")
        with c2:
            exp_curr = st.selectbox("Currency", all_curr, key="add_curr")
        with c3:
            amount   = st.number_input("Amount", min_value=0.0, step=0.01, format="%.2f", key="add_amount")
        with c4:
            exp_date = st.date_input("Date", datetime.today(), key="add_date")

        c5, c6 = st.columns(2)
        with c5:
            payer    = st.selectbox("Paid By", members, key="add_payer")
        with c6:
            category = st.selectbox("Category", CATEGORIES, key="add_cat")

        # Live conversion preview
        if exp_curr != base_currency and amount > 0:
            rate       = currencies_map.get(exp_curr, 1.0)
            base_equiv = to_base(amount, exp_curr, currencies_map, base_currency)
            st.markdown(f"""
            <div class="conv-info">
                💱 <span>{exp_curr} {amount:,.2f}</span>
                &nbsp;→&nbsp;
                <strong>{base_currency} {base_equiv:,.2f}</strong>
                <span style="margin-left:auto;font-size:0.78rem;color:#3A5070;">
                    1 {base_currency} = {rate} {exp_curr}
                </span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="section-label">Split Configuration</div>', unsafe_allow_html=True)
        split_mode    = st.radio("Split Type", ["Equal Split", "Unequal Split"], horizontal=True, key="add_split_mode")
        split_between = st.multiselect("Split Between", members, default=members, key="add_split_between")

        amount_inputs = {}
        if split_mode == "Unequal Split" and split_between:
            st.markdown("**Enter each person's share** (must total the expense amount):")
            cols = st.columns(min(len(split_between), 4))
            for i, person in enumerate(split_between):
                amount_inputs[person] = cols[i % 4].number_input(
                    person, min_value=0.0, step=0.01, format="%.2f", key=f"unequal_{person}"
                )
            entered_total = sum(amount_inputs.values())
            ok    = abs(entered_total - amount) < 0.01
            color = "#00D4AA" if ok else "#F06090"
            st.markdown(
                f"<span style='color:{color};font-size:0.85rem;font-family:JetBrains Mono,monospace;'>"
                f"Entered: {exp_curr} {entered_total:,.2f} / {exp_curr} {amount:,.2f}</span>",
                unsafe_allow_html=True
            )

        if st.button("💾 Save Expense", use_container_width=True, key="btn_save_expense"):
            err = None
            if not desc.strip():      err = "Enter a description."
            elif amount <= 0:         err = "Amount must be greater than zero."
            elif not split_between:   err = "Select at least one person to split with."
            elif split_mode == "Unequal Split" and abs(sum(amount_inputs.values()) - amount) > 0.01:
                err = f"Shares sum to {sum(amount_inputs.values()):.2f} but total is {amount:.2f}. Please fix."

            if err:
                st.error(err)
            else:
                now = datetime.now().isoformat()
                ref = str(uuid.uuid4())
                if split_mode == "Equal Split":
                    share_orig = amount / len(split_between)
                    share_base = to_base(share_orig, exp_curr, currencies_map, base_currency)
                    for person in split_between:
                        cursor.execute("""
                            INSERT INTO expenses(group_id,date,description,category,paid_by,person,
                                amount_original,currency,amount_base,created_at,expense_ref)
                            VALUES(?,?,?,?,?,?,?,?,?,?,?)
                        """, (group_id, str(exp_date), desc.strip(), category,
                              payer, person, share_orig, exp_curr, share_base, now, ref))
                else:
                    for person, val in amount_inputs.items():
                        base_val = to_base(val, exp_curr, currencies_map, base_currency)
                        cursor.execute("""
                            INSERT INTO expenses(group_id,date,description,category,paid_by,person,
                                amount_original,currency,amount_base,created_at,expense_ref)
                            VALUES(?,?,?,?,?,?,?,?,?,?,?)
                        """, (group_id, str(exp_date), desc.strip(), category,
                              payer, person, val, exp_curr, base_val, now, ref))
                conn.commit()
                st.success(f"✅ '{desc}' added successfully!")
                st.rerun()

# ══════════════════════════════════════════════
# TAB 3 — MANAGE
# ══════════════════════════════════════════════

with tab_manage:

    col_m, col_c = st.columns(2, gap="large")

    # Members
    with col_m:
        st.markdown('<div class="section-label">👥 Members</div>', unsafe_allow_html=True)
        nm = st.text_input("New Member Name", placeholder="e.g. Balaji", key="mgmt_new_member")
        if st.button("Add Member", use_container_width=True, key="btn_add_member"):
            if nm.strip():
                try:
                    cursor.execute("INSERT OR IGNORE INTO members(group_id,name) VALUES(?,?)", (group_id, nm.strip()))
                    conn.commit()
                    st.success(f"Added {nm.strip()}")
                    st.rerun()
                except Exception as ex:
                    st.error(str(ex))
            else:
                st.error("Enter a name.")

        current_members = get_members(group_id)
        if current_members:
            for m in current_members:
                mc1, mc2 = st.columns([4, 1])
                mc1.markdown(f'<div style="padding:10px 0;color:#C0CCD8;">👤 {m}</div>', unsafe_allow_html=True)
                if mc2.button("✕", key=f"rm_m_{m}"):
                    cursor.execute("DELETE FROM members WHERE group_id=? AND name=?", (group_id, m))
                    conn.commit()
                    st.rerun()
        else:
            st.markdown('<div class="empty-state" style="padding:24px;"><p>No members yet.</p></div>', unsafe_allow_html=True)

    # Currencies
    with col_c:
        st.markdown('<div class="section-label">💱 Currencies</div>', unsafe_allow_html=True)
        st.markdown(f'Base: <span class="pill">{base_currency}</span> &nbsp; rate = 1.0 (fixed)', unsafe_allow_html=True)
        st.markdown("")

        available_curr = [c for c in COMMON_CURRENCIES if c != base_currency]
        nc_code = st.selectbox("Add Currency", available_curr, key="mgmt_curr_code")
        nc_rate = st.number_input(
            f"Rate (1 {base_currency} = ? {nc_code})",
            min_value=0.0001, value=1.0, step=0.01, format="%.4f",
            key="mgmt_curr_rate"
        )
        if st.button("Add Currency", use_container_width=True, key="btn_add_curr"):
            cursor.execute(
                "INSERT OR REPLACE INTO currencies(group_id,code,rate) VALUES(?,?,?)",
                (group_id, nc_code, nc_rate)
            )
            conn.commit()
            st.success(f"{nc_code} added — 1 {base_currency} = {nc_rate} {nc_code}")
            st.rerun()

        current_curr = get_currencies(group_id)
        for code, rate in current_curr.items():
            if code == base_currency:
                continue
            cc1, cc2, cc3 = st.columns([1, 3, 1])
            cc1.markdown(f'<span style="font-family:JetBrains Mono,monospace;color:#5B9CF6;font-weight:700;">{code}</span>', unsafe_allow_html=True)
            cc2.markdown(f'<span style="color:#5A7090;font-size:0.82rem;">1 {base_currency} = {rate:,.4f} {code}</span>', unsafe_allow_html=True)
            if cc3.button("✕", key=f"rm_c_{code}"):
                cursor.execute("DELETE FROM currencies WHERE group_id=? AND code=?", (group_id, code))
                conn.commit()
                st.rerun()

    st.markdown("---")

    # Edit / Delete Expenses — full re-split form
    st.markdown('<div class="section-label">✏️ Edit / Delete Expenses</div>', unsafe_allow_html=True)
    df_edit = get_expenses(group_id)

    if df_edit.empty:
        st.info("No expenses to edit yet.")
    else:
        mgmt_members = get_members(group_id)
        mgmt_currs   = get_currencies(group_id)
        mgmt_cl      = list(mgmt_currs.keys())

        # ── Build grouped expense list ──
        # Group by expense_ref if present, else fallback to (description,date,paid_by,currency)
        def get_ref(row):
            if pd.notna(row.get("expense_ref")) and str(row["expense_ref"]).strip():
                return row["expense_ref"]
            return f'{row["description"]}||{row["date"]}||{row["paid_by"]}||{row["currency"]}'

        df_edit["_ref"] = df_edit.apply(get_ref, axis=1)

        # One representative row per expense group
        grouped = (
            df_edit.groupby("_ref", sort=False)
            .agg(
                id=("id", "first"),
                date=("date", "first"),
                description=("description", "first"),
                category=("category", "first"),
                paid_by=("paid_by", "first"),
                currency=("currency", "first"),
                total_orig=("amount_original", "sum"),
                persons=("person", list),
                amounts=("amount_original", list),
                expense_ref=("_ref", "first"),
            )
            .reset_index(drop=True)
        )

        options_g = grouped.apply(
            lambda r: (
                f"{r['date']}  |  {r['description']}  |  "
                f"Paid by {r['paid_by']}  |  "
                f"{r['currency']} {float(r['total_orig']):,.2f}  |  "
                f"Split: {', '.join(r['persons'])}"
            ), axis=1
        ).tolist()

        eg_idx  = st.selectbox("Select Expense to Edit", range(len(options_g)),
                               format_func=lambda i: options_g[i], key="edit_grp_sel")
        eg_row  = grouped.iloc[eg_idx]
        e_ref   = eg_row["expense_ref"]

        # Detect current split type
        persons_now  = list(eg_row["persons"])
        amounts_now  = list(eg_row["amounts"])
        total_now    = float(eg_row["total_orig"])
        is_equal_now = all(abs(a - amounts_now[0]) < 0.01 for a in amounts_now) if amounts_now else True

        # ── KEY SUFFIX: include eg_idx so every widget re-renders fresh
        #    when a different expense is selected from the dropdown ──────
        ks = f"_{eg_idx}"

        # ── Preview card of currently selected expense ──────────────────
        split_label = "Equal" if is_equal_now else "Unequal"
        persons_str = ", ".join(persons_now)
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#0A1E38,#060F1C);border:1px solid #1C3560;
             border-radius:12px;padding:16px 20px;margin:12px 0 20px;">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
                <div>
                    <div style="color:#5A7090;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;">Selected Expense</div>
                    <div style="color:#E8F0FF;font-size:1.05rem;font-weight:700;margin-top:4px;">{eg_row['description']}</div>
                    <div style="color:#5A7090;font-size:0.82rem;margin-top:4px;">
                        📅 {eg_row['date']} &nbsp;·&nbsp; 👤 Paid by <strong style="color:#A0B8D0;">{eg_row['paid_by']}</strong>
                        &nbsp;·&nbsp; 🔀 {split_label} split among <strong style="color:#A0B8D0;">{persons_str}</strong>
                    </div>
                </div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:1.4rem;font-weight:700;
                     background:linear-gradient(135deg,#5B9CF6,#00D4AA);
                     -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                    {eg_row['currency']} {total_now:,.2f}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-label">Edit Expense Details</div>', unsafe_allow_html=True)

        ec1, ec2, ec3, ec4 = st.columns([2, 1, 1, 1])
        with ec1:
            e_desc = st.text_input("Description", value=eg_row["description"], key=f"e_desc{ks}")
        with ec2:
            e_ci   = mgmt_cl.index(eg_row["currency"]) if eg_row["currency"] in mgmt_cl else 0
            e_curr = st.selectbox("Currency", mgmt_cl, index=e_ci, key=f"e_curr{ks}")
        with ec3:
            e_amt  = st.number_input("Total Amount", value=total_now, min_value=0.0,
                                     step=0.01, format="%.2f", key=f"e_amt{ks}")
        with ec4:
            e_date = st.date_input("Date", pd.to_datetime(eg_row["date"]), key=f"e_date{ks}")

        ec5, ec6 = st.columns(2)
        with ec5:
            e_pi    = mgmt_members.index(eg_row["paid_by"]) if eg_row["paid_by"] in mgmt_members else 0
            e_payer = st.selectbox("Paid By", mgmt_members, index=e_pi, key=f"e_payer{ks}")
        with ec6:
            cat_list = CATEGORIES
            e_cat_i  = cat_list.index(eg_row["category"]) if eg_row["category"] in cat_list else 0
            e_cat    = st.selectbox("Category", cat_list, index=e_cat_i, key=f"e_cat{ks}")

        # Live conversion preview
        if e_curr != base_currency and e_amt > 0:
            rate_e       = mgmt_currs.get(e_curr, 1.0)
            base_equiv_e = to_base(e_amt, e_curr, mgmt_currs, base_currency)
            st.markdown(f"""
            <div class="conv-info">
                💱 <span>{e_curr} {e_amt:,.2f}</span>
                &nbsp;→&nbsp;
                <strong>{base_currency} {base_equiv_e:,.2f}</strong>
                <span style="margin-left:auto;font-size:0.78rem;color:#3A5070;">
                    1 {base_currency} = {rate_e} {e_curr}
                </span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="section-label">Edit Split Configuration</div>', unsafe_allow_html=True)

        e_split_mode = st.radio("Split Type", ["Equal Split", "Unequal Split"],
                                index=0 if is_equal_now else 1,
                                horizontal=True, key=f"e_split_mode{ks}")

        valid_default   = [p for p in persons_now if p in mgmt_members]
        e_split_between = st.multiselect("Split Between", mgmt_members,
                                         default=valid_default or mgmt_members,
                                         key=f"e_split_between{ks}")

        e_amount_inputs = {}
        if e_split_mode == "Unequal Split" and e_split_between:
            st.markdown("**Each person's share** (pre-filled from saved data):")
            ecols         = st.columns(min(len(e_split_between), 4))
            person_amt_map = dict(zip(persons_now, amounts_now))
            for i, person in enumerate(e_split_between):
                saved_share = float(person_amt_map.get(person, 0.0))
                e_amount_inputs[person] = ecols[i % 4].number_input(
                    person, min_value=0.0, value=saved_share,
                    step=0.01, format="%.2f", key=f"e_unequal_{person}{ks}"
                )
            e_entered = sum(e_amount_inputs.values())
            e_ok    = abs(e_entered - e_amt) < 0.01
            e_color = "#00D4AA" if e_ok else "#F06090"
            st.markdown(
                f"<span style='color:{e_color};font-size:0.85rem;font-family:JetBrains Mono,monospace;'>"
                f"Entered: {e_curr} {e_entered:,.2f} / {e_curr} {e_amt:,.2f}</span>",
                unsafe_allow_html=True
            )

        eu1, eu2 = st.columns(2)
        with eu1:
            if st.button("✅ Update Expense", use_container_width=True, key="btn_update"):
                err_e = None
                if not e_desc.strip():        err_e = "Enter a description."
                elif e_amt <= 0:              err_e = "Amount must be greater than zero."
                elif not e_split_between:     err_e = "Select at least one person."
                elif e_split_mode == "Unequal Split" and abs(sum(e_amount_inputs.values()) - e_amt) > 0.01:
                    err_e = f"Shares sum to {sum(e_amount_inputs.values()):.2f} but total is {e_amt:.2f}."

                if err_e:
                    st.error(err_e)
                else:
                    # Delete all rows sharing this ref
                    if pd.notna(e_ref) and "||" not in str(e_ref):
                        cursor.execute("DELETE FROM expenses WHERE expense_ref=?", (e_ref,))
                    else:
                        parts = str(e_ref).split("||")
                        if len(parts) == 4:
                            cursor.execute(
                                "DELETE FROM expenses WHERE group_id=? AND description=? AND date=? AND paid_by=? AND currency=?",
                                (group_id, parts[0], parts[1], parts[2], parts[3])
                            )
                        else:
                            cursor.execute("DELETE FROM expenses WHERE expense_ref=?", (e_ref,))

                    new_ref  = str(uuid.uuid4())
                    now_e    = datetime.now().isoformat()
                    if e_split_mode == "Equal Split":
                        share_orig = e_amt / len(e_split_between)
                        share_base = to_base(share_orig, e_curr, mgmt_currs, base_currency)
                        for person in e_split_between:
                            cursor.execute("""
                                INSERT INTO expenses(group_id,date,description,category,paid_by,person,
                                    amount_original,currency,amount_base,created_at,expense_ref)
                                VALUES(?,?,?,?,?,?,?,?,?,?,?)
                            """, (group_id, str(e_date), e_desc.strip(), e_cat,
                                  e_payer, person, share_orig, e_curr, share_base, now_e, new_ref))
                    else:
                        for person, val in e_amount_inputs.items():
                            base_val = to_base(val, e_curr, mgmt_currs, base_currency)
                            cursor.execute("""
                                INSERT INTO expenses(group_id,date,description,category,paid_by,person,
                                    amount_original,currency,amount_base,created_at,expense_ref)
                                VALUES(?,?,?,?,?,?,?,?,?,?,?)
                            """, (group_id, str(e_date), e_desc.strip(), e_cat,
                                  e_payer, person, val, e_curr, base_val, now_e, new_ref))
                    conn.commit()
                    st.success("✅ Expense updated!")
                    st.rerun()

        with eu2:
            if st.button("🗑️ Delete Expense", use_container_width=True, key="btn_delete"):
                if pd.notna(e_ref) and "||" not in str(e_ref):
                    cursor.execute("DELETE FROM expenses WHERE expense_ref=?", (e_ref,))
                else:
                    parts = str(e_ref).split("||")
                    if len(parts) == 4:
                        cursor.execute(
                            "DELETE FROM expenses WHERE group_id=? AND description=? AND date=? AND paid_by=? AND currency=?",
                            (group_id, parts[0], parts[1], parts[2], parts[3])
                        )
                    else:
                        cursor.execute("DELETE FROM expenses WHERE expense_ref=?", (e_ref,))
                conn.commit()
                st.success("🗑️ Expense deleted!")
                st.rerun()

# ══════════════════════════════════════════════
# TAB 4 — ANALYTICS
# ══════════════════════════════════════════════

with tab_analytics:

    if df.empty:
        st.markdown('<div class="empty-state"><div class="emoji">📊</div><p>No data yet.<br>Add expenses to unlock analytics.</p></div>', unsafe_allow_html=True)
    else:
        def apply_theme(fig, extra=None):
            layout = dict(
                template="plotly_dark",
                paper_bgcolor="#0D1219",
                plot_bgcolor="#0D1219",
                font_color="#8AA0BC",
                margin=dict(t=44, b=20, l=10, r=10),
            )
            if extra:
                layout.update(extra)
            fig.update_layout(**layout)
            return fig

        # ── True Personal Spend Calculation ──────────────────────────────
        # For each person:
        #   spent_on_self    = paid_by == me  AND  person == me
        #   others_paid_me   = paid_by != me  AND  person == me
        #   i_paid_others    = paid_by == me  AND  person != me
        #   TRUE SPEND = spent_on_self + others_paid_me - i_paid_others
        #              = sum(person == me)  -  i_paid_others
        # ─────────────────────────────────────────────────────────────────
        all_persons = members if members else sorted(df["person"].unique().tolist())

        spend_rows = []
        for p in all_persons:
            spent_on_self  = df[(df["paid_by"] == p) & (df["person"] == p)]["amount_base"].sum()
            others_paid_me = df[(df["person"]  == p) & (df["paid_by"] != p)]["amount_base"].sum()
            i_paid_others  = df[(df["paid_by"] == p) & (df["person"]  != p)]["amount_base"].sum()
            true_spend     = round(spent_on_self + others_paid_me - i_paid_others, 2)
            spend_rows.append({
                "Person":          p,
                "Spent on Self":   round(spent_on_self,  2),
                "Others Paid Me":  round(others_paid_me, 2),
                "I Paid for Others": round(i_paid_others, 2),
                "True Spend":      true_spend,
            })

        spend_df = pd.DataFrame(spend_rows)

        # ── Row 1: stacked bar + donut ────────────────────────────────────
        a1, a2 = st.columns(2)

        with a1:
            # Stacked bar showing the three components
            import plotly.graph_objects as go
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name="Spent on Self",
                x=spend_df["Person"],
                y=spend_df["Spent on Self"],
                marker_color="#5B9CF6",
                marker_line_width=0,
            ))
            fig.add_trace(go.Bar(
                name="Others Paid Me",
                x=spend_df["Person"],
                y=spend_df["Others Paid Me"],
                marker_color="#00D4AA",
                marker_line_width=0,
            ))
            fig.add_trace(go.Bar(
                name="I Paid for Others",
                x=spend_df["Person"],
                y=-spend_df["I Paid for Others"],   # negative → goes below zero
                marker_color="#F06090",
                marker_line_width=0,
            ))
            # Net true-spend marker line
            fig.add_trace(go.Scatter(
                name="True Spend (Net)",
                x=spend_df["Person"],
                y=spend_df["True Spend"],
                mode="markers+text",
                marker=dict(color="#F0A500", size=10, symbol="diamond"),
                text=[f"{base_currency} {v:,.0f}" for v in spend_df["True Spend"]],
                textposition="top center",
                textfont=dict(size=11, color="#F0A500"),
            ))
            apply_theme(fig, {
                "barmode": "relative",
                "title":   f"True Spend Breakdown ({base_currency})",
                "legend":  dict(orientation="h", y=-0.2, font=dict(size=11)),
                "yaxis":   dict(title=base_currency, gridcolor="#1C2535"),
                "xaxis":   dict(gridcolor="#1C2535"),
            })
            st.plotly_chart(fig, use_container_width=True)

        with a2:
            fig2 = px.pie(
                spend_df[spend_df["True Spend"] > 0],
                values="True Spend", names="Person",
                title=f"True Spend Share ({base_currency})",
                color_discrete_sequence=PALETTE, hole=0.45,
            )
            apply_theme(fig2)
            st.plotly_chart(fig2, use_container_width=True)

        # ── Breakdown table ───────────────────────────────────────────────
        st.markdown('<div class="section-label">📋 True Spend Breakdown per Person</div>', unsafe_allow_html=True)
        table_df = spend_df.copy()
        for col in ["Spent on Self","Others Paid Me","I Paid for Others","True Spend"]:
            table_df[col] = table_df[col].apply(lambda v: f"{base_currency} {v:,.2f}")
        st.dataframe(table_df, use_container_width=True, hide_index=True)

        st.markdown(
            '<div style="font-size:0.78rem;color:#3A5070;margin-top:-8px;margin-bottom:16px;">'
            '🟦 Spent on Self &nbsp;|&nbsp; 🟩 Others Paid Me &nbsp;|&nbsp; 🟥 I Paid for Others (deducted) &nbsp;|&nbsp; 🔶 Net True Spend</div>',
            unsafe_allow_html=True
        )

        a3, a4 = st.columns(2)

        if "category" in df.columns and df["category"].notna().any():
            spend_cat = df.groupby("category")["amount_base"].sum().reset_index()
            spend_cat.columns = ["Category", "Total"]
            spend_cat = spend_cat.sort_values("Total", ascending=True)
            with a3:
                fig3 = px.bar(spend_cat, x="Total", y="Category", orientation="h",
                              color="Category", title=f"Spending by Category ({base_currency})",
                              color_discrete_sequence=PALETTE)
                apply_theme(fig3, {"showlegend": False})
                fig3.update_traces(marker_line_width=0)
                st.plotly_chart(fig3, use_container_width=True)

        df_time = df.copy()
        df_time["date"] = pd.to_datetime(df_time["date"])
        time_agg = df_time.groupby("date")["amount_base"].sum().cumsum().reset_index()
        time_agg.columns = ["Date", "Cumulative"]

        with a4:
            fig4 = px.area(time_agg, x="Date", y="Cumulative",
                           title=f"Cumulative Spend ({base_currency})",
                           color_discrete_sequence=["#5B9CF6"])
            apply_theme(fig4)
            fig4.update_traces(fill="tozeroy", line_width=2)
            st.plotly_chart(fig4, use_container_width=True)

        # Per-person breakdown by category
        st.markdown('<div class="section-label">Per-Person Category Breakdown</div>', unsafe_allow_html=True)
        person_cat = df.groupby(["person","category"])["amount_base"].sum().reset_index()
        person_cat.columns = ["Person","Category","Amount"]
        fig5 = px.bar(person_cat, x="Person", y="Amount", color="Category",
                      title=f"Expense Breakdown per Person ({base_currency})",
                      color_discrete_sequence=PALETTE, barmode="stack")
        apply_theme(fig5)
        st.plotly_chart(fig5, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 5 — EXPORT
# ══════════════════════════════════════════════

with tab_export:

    if df.empty:
        st.info("No data to export. Add some expenses first.")
    else:
        st.markdown('<div class="section-label">Download Options</div>', unsafe_allow_html=True)

        exp_members      = get_members(group_id)
        balance_exp      = compute_balances(df, exp_members) if exp_members else {}
        bal_df_exp       = pd.DataFrame([(k, round(v,2)) for k,v in balance_exp.items()],
                                         columns=["Member", f"Balance ({base_currency})"])
        settlements_exp  = compute_settlements(balance_exp)
        settle_df_exp    = pd.DataFrame(settlements_exp,
                                         columns=["Debtor","Creditor",f"Amount ({base_currency})"]
                                        ) if settlements_exp else pd.DataFrame()

        col_x1, col_x2 = st.columns(2)

        with col_x1:
            st.markdown("**📊 Excel Export**")
            st.caption("Expenses · Balances · Settlements — three separate sheets.")

            def make_excel():
                buf = BytesIO()
                with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                    df.to_excel(writer, sheet_name="Expenses", index=False)
                    bal_df_exp.to_excel(writer, sheet_name="Balances", index=False)
                    if not settle_df_exp.empty:
                        settle_df_exp.to_excel(writer, sheet_name="Settlements", index=False)
                return buf.getvalue()

            st.download_button(
                "⬇️ Download Excel (.xlsx)",
                data=make_excel(),
                file_name=f"{selected_name.replace(' ','_')}_expenses.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

        with col_x2:
            st.markdown("**📄 CSV Export**")
            st.caption("Plain CSV of all expense rows for external tools.")
            st.download_button(
                "⬇️ Download CSV",
                data=df.to_csv(index=False),
                file_name=f"{selected_name.replace(' ','_')}_expenses.csv",
                mime="text/csv",
                use_container_width=True,
            )

        st.markdown("---")
        st.markdown('<div class="section-label">Preview: Balances</div>', unsafe_allow_html=True)
        st.dataframe(bal_df_exp, use_container_width=True, hide_index=True)

        if not settle_df_exp.empty:
            st.markdown('<div class="section-label">Preview: Settlements</div>', unsafe_allow_html=True)
            st.dataframe(settle_df_exp, use_container_width=True, hide_index=True)
