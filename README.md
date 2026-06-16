import streamlit as st
import pandas as pd
from datetime import date
import os

st.set_page_config(page_title="JobNavi", page_icon="💼", layout="wide")

FILE_NAME = "job_data.csv"

# =====================
# データ読み込み
# =====================
if os.path.exists(FILE_NAME):
    df = pd.read_csv(FILE_NAME)
else:
    df = pd.DataFrame(columns=[
        "企業名", "業界", "志望度", "ES締切",
        "面接日", "面接形式", "ステータス", "メモ"
    ])

df["志望度"] = pd.to_numeric(df["志望度"], errors="coerce").fillna(3)
df["ES締切"] = pd.to_datetime(df["ES締切"], errors="coerce")
df["面接日"] = pd.to_datetime(df["面接日"], errors="coerce")

st.title("💼 JobNavi")

# =====================
# サイドバー（登録）
# =====================
with st.sidebar:

    st.header("企業登録")

    company = st.text_input("企業名")

    industry = st.selectbox(
        "業界",
        ["食品", "IT", "メーカー", "金融", "商社", "広告", "人材", "その他"]
    )

    priority = st.slider("志望度", 1, 5, 3)

    es_deadline = st.date_input("ES締切", date.today())

    interview_known = st.checkbox("面接日が決まっている")

    interview_date = pd.NaT
    interview_type = "未定"

    if interview_known:
        interview_date = st.date_input("面接日", date.today())
        interview_type = st.selectbox("面接形式", ["Web", "対面"])

    status = st.selectbox(
        "ステータス",
        ["興味あり", "エントリー済", "ES提出済", "Webテスト",
         "一次面接", "二次面接", "最終面接", "内定", "不合格"]
    )

    memo = st.text_area("メモ")

    if st.button("登録") and company:

        new_row = pd.DataFrame([{
            "企業名": company,
            "業界": industry,
            "志望度": priority,
            "ES締切": es_deadline,
            "面接日": interview_date,
            "面接形式": interview_type,
            "ステータス": status,
            "メモ": memo
        }])

        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(FILE_NAME, index=False)

        st.success("登録完了")
        st.rerun()

# =====================
# ダッシュボード
# =====================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("応募企業", len(df))

with col2:
    st.metric(
        "選考中",
        len(df[df["ステータス"].isin([
            "ES提出済", "Webテスト", "一次面接", "二次面接", "最終面接"
        ])])
    )

with col3:
    st.metric("内定", len(df[df["ステータス"] == "内定"]))

with col4:
    st.metric("不合格", len(df[df["ステータス"] == "不合格"]))

st.divider()

# =====================
# ES締切アラート
# =====================
st.subheader("🚨 今やること")

if len(df):

    today = pd.Timestamp.today().normalize()

    alerts = df[df["ES締切"].notna()]
    alerts = alerts[(alerts["ES締切"] - today).dt.days <= 7]
    alerts = alerts.sort_values("ES締切")

    for _, row in alerts.iterrows():

        days = (row["ES締切"] - today).days

        if days <= 1:
            st.error(f"🚨 {row['企業名']} ES締切まであと{days}日")
        elif days <= 3:
            st.warning(f"⚠️ {row['企業名']} ES締切まであと{days}日")

st.divider()

# =====================
# 今日の面接
# =====================
st.subheader("📅 今日の面接")

today_interview = df[
    df["面接日"].notna() &
    (df["面接日"].dt.date == date.today())
]

if len(today_interview) > 0:
    for _, row in today_interview.iterrows():
        st.info(f"{row['企業名']} ({row['面接形式']})")
else:
    st.write("本日の面接予定はありません")

st.divider()

# =====================
# 企業一覧（クリック削除）
# =====================
st.subheader("📋 企業一覧")

for _, row in df.iterrows():

    with st.container(border=True):

        # ★ここがポイント（クリック＝削除）
        if st.button(f"🗑 {row['企業名']}", key=f"del_{row.name}"):

            df = df.drop(index=row.name)
            df.to_csv(FILE_NAME, index=False)

            st.success(f"{row['企業名']} を削除しました")
            st.rerun()

        st.markdown(f"""
🏢 業界：{row['業界']}

⭐ 志望度：{'★' * int(row['志望度'])}

📄 ステータス：{row['ステータス']}

📅 ES締切：{row['ES締切']}

🎤 面接日：{row['面接日'] if pd.notna(row['面接日']) else '未定'}

💻 面接形式：{row['面接形式']}
""")
