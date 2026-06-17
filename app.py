import streamlit as st
import pandas as pd
from datetime import date
import os

st.set_page_config(
    page_title="就活ログ",
    page_icon="💼",
    layout="wide"
)

FILE_NAME = "job_data.csv"

# =====================
# CSV読込
# =====================
columns = [
    "企業名",
    "業界",
    "志望度",
    "ES締切",
    "面接日",
    "面接形式",
    "ステータス",
    "メモ"
]

try:
    if os.path.exists(FILE_NAME) and os.path.getsize(FILE_NAME) > 0:
        df = pd.read_csv(FILE_NAME)
    else:
        df = pd.DataFrame(columns=columns)
except:
    df = pd.DataFrame(columns=columns)

# 必要な列がない場合追加
for col in columns:
    if col not in df.columns:
        df[col] = None

# 型変換
df["志望度"] = pd.to_numeric(
    df["志望度"],
    errors="coerce"
).fillna(3)

df["ES締切"] = pd.to_datetime(
    df["ES締切"],
    errors="coerce"
)

df["面接日"] = pd.to_datetime(
    df["面接日"],
    errors="coerce"
)

# =====================
# タイトル
# =====================
st.title("💼 就活ログ")

# =====================
# サイドバー
# =====================
with st.sidebar:

    st.header("企業登録")

    company = st.text_input("企業名")

    industry = st.selectbox(
        "業界",
        [
            "食品",
            "IT",
            "メーカー",
            "金融",
            "商社",
            "広告",
            "人材",
            "その他"
        ]
    )

    priority = st.slider(
        "志望度",
        1,
        5,
        3
    )

    es_deadline = st.date_input(
        "ES締切",
        date.today()
    )

    interview_known = st.checkbox(
        "面接日が決まっている"
    )

    interview_date = None
    interview_type = "未定"

    if interview_known:

        interview_date = st.date_input(
            "面接日",
            date.today()
        )

        interview_type = st.selectbox(
            "面接形式",
            ["Web", "対面"]
        )

    status = st.selectbox(
        "ステータス",
        [
            "興味あり",
            "エントリー済",
            "ES提出済",
            "Webテスト",
            "一次面接",
            "二次面接",
            "最終面接",
            "内定",
        ]
    )

    memo = st.text_area("メモ")

    if st.button("登録"):

        if company.strip() == "":
            st.warning("企業名を入力してください")

        else:

            company_clean = (
                company
                .strip()
                .lower()
            )

            existing_companies = (
                df["企業名"]
                .astype(str)
                .str.strip()
                .str.lower()
                .tolist()
            )

            if company_clean in existing_companies:

                st.warning(
                    "⚠️ この企業は登録済みです"
                )

            else:

                new_row = pd.DataFrame([{
                    "企業名": company.strip(),
                    "業界": industry,
                    "志望度": priority,
                    "ES締切": pd.Timestamp(es_deadline),
                    "面接日": (
                        pd.Timestamp(interview_date)
                        if interview_date
                        else pd.NaT
                    ),
                    "面接形式": interview_type,
                    "ステータス": status,
                    "メモ": memo
                }])

                df = pd.concat(
                    [df, new_row],
                    ignore_index=True
                )

                df.to_csv(
                    FILE_NAME,
                    index=False
                )

                st.success("登録完了")
                st.rerun()

# =====================
# ダッシュボード
# =====================
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "応募企業",
        len(df)
    )

with col2:
    st.metric(
        "選考中",
        len(
            df[
                df["ステータス"].isin([
                    "ES提出済",
                    "Webテスト",
                    "一次面接",
                    "二次面接",
                    "最終面接"
                ])
            ]
        )
    )

with col3:
    st.metric(
        "内定",
        len(
            df[
                df["ステータス"] == "内定"
            ]
        )
    )

st.divider()

# =====================
# 1週間以内にやること
# =====================
st.subheader("📌 1週間以内にやること")

today = pd.Timestamp.today().normalize()

alerts = df[
    df["ES締切"].notna()
].copy()

alerts["残り日数"] = (
    alerts["ES締切"] - today
).dt.days

alerts = alerts[
    (alerts["残り日数"] >= 0)
    &
    (alerts["残り日数"] <= 7)
]

alerts = alerts.sort_values(
    "ES締切"
)

if len(alerts) == 0:

    st.success(
        "1週間以内の締切はありません"
    )

else:

    for _, row in alerts.iterrows():

        days = row["残り日数"]

        if days == 0:

            st.error(
                f"🚨 {row['企業名']} ES締切は今日です"
            )

        elif days <= 3:

            st.warning(
                f"⚠️ {row['企業名']} ES締切まであと{days}日"
            )

        else:

            st.info(
                f"📄 {row['企業名']} ES締切まであと{days}日"
            )

st.divider()

# =====================
# 今日の面接
# =====================
st.subheader("📅 今日の面接")

today_interview = df[
    df["面接日"].notna()
    &
    (
        df["面接日"].dt.date
        == date.today()
    )
]

if len(today_interview):

    for _, row in today_interview.iterrows():

        st.info(
            f"{row['企業名']} ({row['面接形式']})"
        )

else:

    st.write(
        "本日の面接予定はありません"
    )

st.divider()

# =====================
# 企業一覧
# =====================
st.subheader("📋 企業一覧")

for _, row in df.iterrows():

    with st.container(border=True):

        if st.button(
            f"🗑 {row['企業名']}",
            key=f"delete_{row.name}"
        ):

            df = (
                df
                .drop(index=row.name)
                .reset_index(drop=True)
            )

            df.to_csv(
                FILE_NAME,
                index=False
            )

            st.success(
                f"{row['企業名']} を削除しました"
            )

            st.rerun()

        # 日付表示
        es_text = "未設定"

        if pd.notna(row["ES締切"]):
            es_text = row["ES締切"].strftime("%Y/%m/%d")

        interview_text = "未定"

        if pd.notna(row["面接日"]):
            interview_text = row["面接日"].strftime("%Y/%m/%d")

        # メモ
        memo_text = ""

        if pd.notna(row["メモ"]):

            memo_text = str(row["メモ"])

            if memo_text.lower() == "nan":
                memo_text = ""

        st.markdown(f"""
🏢 業界：{row['業界']}

⭐ 志望度：{'★' * int(row['志望度'])}

📄 ステータス：{row['ステータス']}

📅 ES締切：{es_text}

🎤 面接日：{interview_text}

💻 面接形式：{row['面接形式']}

📝 メモ：{memo_text}
""")
