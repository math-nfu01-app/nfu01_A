# generate_linear_memory_st2.py
# 一次関数4択問題

import streamlit as st
import random
import numpy as np
import matplotlib.pyplot as plt
import time
import gspread
from google.oauth2.service_account import Credentials

# =====================================================
# フォント設定
# =====================================================
plt.rcParams["font.family"] = "Meiryo"

# =====================================================
# 一次関数の式表示
# =====================================================
def format_linear(a, b):

    if a == 1:
        a_str = "x"
    elif a == -1:
        a_str = "-x"
    else:
        a_str = f"{a}x"

    if b > 0:
        b_str = f" + {b}"
    elif b < 0:
        b_str = f" - {-b}"
    else:
        b_str = ""

    return f"y = {a_str}{b_str}"


# =====================================================
# 一次関数生成
# =====================================================
def generate_linear():

    a = random.choice([-3, -2, -1, 1, 2, 3])
    b = random.randint(-5, 5)

    return a, b


# =====================================================
# Google Sheets 記録
# =====================================================
def send_to_sheet(
    eq_str,
    selected,
    correct_index,
    is_correct,
    elapsed
):

    try:

        if "gcp_service_account" not in st.secrets:
            return

        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]

        creds = Credentials.from_service_account_info(
            dict(st.secrets["gcp_service_account"]),
            scopes=scope,
        )

        gc = gspread.authorize(creds)

        sheet = gc.open_by_key(
            "1S_koL8VGN2iPs11BR-dl5aDpmfRGCWKzwam6AKB1FmY"
        ).worksheet("一次関数_履歴")

        now = time.strftime("%Y-%m-%d %H:%M:%S")

        sheet.append_row([
            now,
            eq_str,
            selected + 1,
            correct_index + 1,
            "○" if is_correct else "×",
            elapsed,
        ])

    except Exception:
        pass


# =====================================================
# 新しい問題
# =====================================================
def new_problem():

    correct = generate_linear()

    choices = [correct]

    while len(choices) < 4:

        candidate = generate_linear()

        if candidate not in choices:
            choices.append(candidate)

    random.shuffle(choices)

    st.session_state.problem = correct
    st.session_state.choices = choices

    st.session_state.correct_index = choices.index(correct)

    st.session_state.start_problem = time.time()

    st.session_state.answered = False

    # ラジオボタン再生成用
    st.session_state.question_id += 1


# =====================================================
# 初期化
# =====================================================
if "initialized" not in st.session_state:

    st.session_state.initialized = True

    st.session_state.correct_count = 0
    st.session_state.total_count = 0

    st.session_state.study_start = time.time()

    st.session_state.problem = None
    st.session_state.choices = []

    st.session_state.correct_index = -1

    st.session_state.answered = False

    st.session_state.question_id = 0


if st.session_state.problem is None:
    new_problem()


# =====================================================
# 画面設定
# =====================================================
st.set_page_config(
    page_title="一次関数グラフ選択問題",
    layout="centered"
)

# =====================================================
# タイトル
# =====================================================
st.title("📈 一次関数グラフ選択問題")

st.info("""
【使い方】

① 表示された一次関数の式を確認します。

② 4本のグラフの中から、その式に対応するグラフを選びます。

③ 「答え合わせ」を押して正誤を確認します。

④ 「次の問題」を押して次の問題に挑戦します。

⑤ 学習の最後に「学習結果を表示」を押すと、
正答率や学習時間を確認できます。

たくさん挑戦して一次関数の特徴を身につけましょう！
""")

# =====================================================
# 線の太さ
# =====================================================
line_width = st.slider(
    "線の太さ",
    min_value=1,
    max_value=5,
    value=2
)

# =====================================================
# 問題表示
# =====================================================
a, b = st.session_state.problem

st.subheader(
    f"問題： {format_linear(a, b)}"
)

# =====================================================
# グラフ描画
# =====================================================
fig, ax = plt.subplots(figsize=(6, 6))

x = np.linspace(-6, 6, 400)

colors = [
    "red",
    "blue",
    "green",
    "orange"
]

labels = [
    "選択肢1",
    "選択肢2",
    "選択肢3",
    "選択肢4"
]

for i, (aa, bb) in enumerate(st.session_state.choices):

    y = aa * x + bb

    ax.plot(
        x,
        y,
        color=colors[i],
        linewidth=line_width,
        label=labels[i]
    )

ax.axhline(0, color="black")
ax.axvline(0, color="black")

ax.set_xlim(-6, 6)
ax.set_ylim(-6, 6)

ax.grid(True)
ax.legend()

st.pyplot(fig)

# =====================================================
# 回答
# =====================================================
answer = st.radio(
    "選択してください",
    options=[0, 1, 2, 3],
    format_func=lambda x: f"選択肢{x+1}",
    index=None,
    key=f"answer_radio_{st.session_state.question_id}"
)

# =====================================================
# 答え合わせ
# =====================================================
if st.button("答え合わせ"):

    if st.session_state.answered:

        st.warning(
            "この問題は採点済みです。"
        )

    elif answer is None:

        st.warning(
            "選択肢を選んでください。"
        )

    else:

        elapsed = int(
            time.time()
            - st.session_state.start_problem
        )

        is_correct = (
            answer
            == st.session_state.correct_index
        )

        st.session_state.total_count += 1

        if is_correct:

            st.session_state.correct_count += 1

            st.success(
                "正解です！\n\n次の問題へ進みましょう。"
            )

        else:

            st.error(
                f"不正解です。\n\n正解は選択肢 {st.session_state.correct_index + 1} です。"
            )

        st.session_state.answered = True

        send_to_sheet(
            format_linear(a, b),
            answer,
            st.session_state.correct_index,
            is_correct,
            elapsed,
        )

# =====================================================
# 次の問題
# =====================================================
if st.button("次の問題"):

    new_problem()

    st.rerun()

# =====================================================
# 学習結果
# =====================================================
st.divider()

if st.button("学習結果を表示"):

    if st.session_state.total_count == 0:
        rate = 0
    else:
        rate = (
            st.session_state.correct_count
            / st.session_state.total_count
            * 100
        )

    elapsed = int(
        time.time()
        - st.session_state.study_start
    )

    minutes = elapsed // 60
    seconds = elapsed % 60

    st.markdown("## 学習結果")

    st.write(
        f"正解数：{st.session_state.correct_count}"
    )

    st.write(
        f"問題数：{st.session_state.total_count}"
    )

    st.write(
        f"正答率：{rate:.1f}%"
    )

    st.write(
        f"学習時間：{minutes}分 {seconds}秒"
    )

    if rate >= 90:
        st.success(
            "素晴らしい集中力でした！"
        )

    elif rate >= 70:
        st.success(
            "よく頑張りました！"
        )

    elif rate >= 50:
        st.info(
            "あと少しで完璧です！"
        )

    else:
        st.warning(
            "続ければ必ず伸びます！"
        )
