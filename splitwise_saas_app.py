import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="Splitwise SaaS", layout="wide")

# -----------------------
# DARK THEME
# -----------------------

st.markdown("""
<style>

body {background-color:#0E1117;color:white;}

[data-testid="stMetric"] {
background:#1F2937;
padding:15px;
border-radius:10px;
}

</style>
""", unsafe_allow_html=True)

# -----------------------
# DATABASE
# -----------------------

conn = sqlite3.connect("splitwise_saas.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY,
username TEXT,
password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS groups(
id INTEGER PRIMARY KEY,
name TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses(
id INTEGER PRIMARY KEY,
group_id INTEGER,
date TEXT,
description TEXT,
paid_by TEXT,
person TEXT,
amount REAL
)
""")

conn.commit()

# -----------------------
# LOGIN
# -----------------------

if "user" not in st.session_state:
    st.session_state.user = None

st.title("💳 ಸ್ನೇಹಹಂಚಿಕೆ(Splitwise)")

if st.session_state.user is None:

    tab1,tab2 = st.tabs(["Login","Register"])

    with tab1:

        u = st.text_input("Username")
        p = st.text_input("Password",type="password")

        if st.button("Login"):

            user = cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (u,p)).fetchone()

            if user:
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Invalid login")

    with tab2:

        new_u = st.text_input("New Username")
        new_p = st.text_input("New Password",type="password")

        if st.button("Create Account"):

            cursor.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (new_u,new_p)
            )

            conn.commit()

            st.success("Account created")

    st.stop()

# -----------------------
# GROUPS
# -----------------------

st.sidebar.header("Groups")

groups = cursor.execute("SELECT * FROM groups").fetchall()

group_names = [g[1] for g in groups]

new_group = st.sidebar.text_input("Create Group")

if st.sidebar.button("Add Group"):

    cursor.execute(
    "INSERT INTO groups(name) VALUES(?)",
    (new_group,)
    )

    conn.commit()
    st.rerun()

if len(group_names) == 0:
    st.warning("Create a group first")
    st.stop()

group_selected = st.sidebar.selectbox("Select Group",group_names)

group_id = cursor.execute(
"SELECT id FROM groups WHERE name=?",
(group_selected,)
).fetchone()[0]

# -----------------------
# FRIENDS
# -----------------------

friends_input = st.sidebar.text_input(
"Friends",
"Balaji,Shashikant,Arun"
)

friends = [f.strip() for f in friends_input.split(",")]

# -----------------------
# ADD EXPENSE
# -----------------------

st.header("Add Expense")

c1,c2,c3,c4 = st.columns(4)

with c1:
    desc = st.text_input("Description")

with c2:
    amount = st.number_input("Amount",min_value=0.0)

with c3:
    payer = st.selectbox("Paid By",friends)

with c4:
    date = st.date_input("Date")

split_mode = st.radio(
"Split Type",
["Equal Split","Unequal Split"]
)

split = st.multiselect("Split Between",friends,default=friends)

amount_inputs = {}

if split_mode == "Unequal Split" and len(split) > 0:

    st.subheader("Enter amount per person")

    for person in split:
        amount_inputs[person] = st.number_input(
            f"{person}",
            min_value=0.0,
            key=f"amt_{person}"
        )

if st.button("Add Expense"):

    if len(split) > 0:

        # ----------------
        # Equal split
        # ----------------

        if split_mode == "Equal Split":

            share = amount / len(split)

            for person in split:

                cursor.execute("""
                INSERT INTO expenses
                (group_id,date,description,paid_by,person,amount)
                VALUES(?,?,?,?,?,?)
                """,(group_id,str(date),desc,payer,person,share))

        # ----------------
        # Unequal split
        # ----------------

        else:

            total_entered = sum(amount_inputs.values())

            if abs(total_entered - amount) > 0.01:
                st.error("Entered amounts must equal total expense")
                st.stop()

            for person,val in amount_inputs.items():

                cursor.execute("""
                INSERT INTO expenses
                (group_id,date,description,paid_by,person,amount)
                VALUES(?,?,?,?,?,?)
                """,(group_id,str(date),desc,payer,person,val))

        conn.commit()

        st.success("Expense saved")
        st.rerun()

# -----------------------
# LOAD DATA
# -----------------------

df = pd.read_sql_query(
f"SELECT * FROM expenses WHERE group_id={group_id}",
conn)

# -----------------------
# KPI DASHBOARD
# -----------------------

st.header("Dashboard")

k1,k2,k3,k4 = st.columns(4)

if not df.empty:

    total = df["amount"].sum()
    transactions = len(df)
    avg = df["amount"].mean()
    top = df.groupby("paid_by")["amount"].sum().idxmax()

else:

    total=0
    transactions=0
    avg=0
    top="-"

k1.metric("Total Spent",f"€{round(total,2)}")
k2.metric("Transactions",transactions)
k3.metric("Average Expense",f"€{round(avg,2)}")
k4.metric("Top Spender",top)

# -----------------------
# EXPENSE LOG
# -----------------------

st.header("Expense Log")

if not df.empty:
    st.dataframe(df)

# -----------------------
# EDIT / DELETE
# -----------------------

st.subheader("Edit or Delete Expense")

if not df.empty:

    expense_id = st.selectbox("Expense ID",df["id"])

    selected = df[df["id"]==expense_id].iloc[0]

    c1,c2,c3,c4 = st.columns(4)

    with c1:
        new_desc = st.text_input(
    "Description",
    selected["description"],
    key="edit_desc"
)

    with c2:
        new_amount = st.number_input(
    "Amount",
    value=float(selected["amount"]),
    key="edit_amount"
)

    with c3:
        new_payer = st.selectbox(
    "Paid By",
    friends,
    index=friends.index(selected["paid_by"]),
    key="edit_payer"
)

    with c4:
        new_date = st.date_input(
    "Date",
    pd.to_datetime(selected["date"]),
    key="edit_date"
)

    col1,col2 = st.columns(2)

    with col1:

        if st.button("Update Expense"):

            cursor.execute("""
            UPDATE expenses
            SET description=?,paid_by=?,amount=?,date=?
            WHERE id=?
            """,(new_desc,new_payer,new_amount,str(new_date),expense_id))

            conn.commit()
            st.success("Updated")
            st.rerun()

    with col2:

        if st.button("Delete Expense"):

            cursor.execute(
            "DELETE FROM expenses WHERE id=?",
            (expense_id,)
            )

            conn.commit()
            st.success("Deleted")
            st.rerun()

# -----------------------
# BALANCES
# -----------------------

balance = {f:0 for f in friends}

for _,r in df.iterrows():

    balance[r["paid_by"]] += r["amount"]
    balance[r["person"]] -= r["amount"]

balance_df = pd.DataFrame(
list(balance.items()),
columns=["Friend","Balance"]
)

st.header("Balances")

st.dataframe(balance_df)

# -----------------------
# ANALYTICS
# -----------------------

if not df.empty:

    st.header("Analytics")

    col1,col2 = st.columns(2)

    spend = df.groupby("paid_by")["amount"].sum().reset_index()

    with col1:

        fig = px.bar(
        spend,
        x="paid_by",
        y="amount",
        color="paid_by",
        title="Spending by Person"
        )

        st.plotly_chart(fig)

    with col2:

        fig2 = px.pie(
        spend,
        values="amount",
        names="paid_by",
        title="Expense Distribution"
        )

        st.plotly_chart(fig2)

# -----------------------
# SETTLEMENT ENGINE
# -----------------------

st.header("Settlement Suggestions")

creditors=[]
debtors=[]

for p,b in balance.items():

    if b>0:
        creditors.append([p,b])
    elif b<0:
        debtors.append([p,-b])

for d in debtors:

    for c in creditors:

        if d[1]==0:
            break

        pay=min(d[1],c[1])

        if pay>0:

            st.write(f"{d[0]} pays {c[0]} €{round(pay,2)}")

            d[1]-=pay
            c[1]-=pay

# -----------------------
# EXPORT EXCEL
# -----------------------

st.header("Export")

def export_excel(data):

    output=BytesIO()

    with pd.ExcelWriter(output,engine="openpyxl") as writer:
        data.to_excel(writer,index=False)

    return output.getvalue()

if not df.empty:

    excel=export_excel(df)

    st.download_button(
    "Download Excel",
    excel,
    "expenses.xlsx"

    )


