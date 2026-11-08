import tkinter as tk
from tkinter import messagebox
import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
import time

# Google Sheets 用
import gspread
from google.oauth2.service_account import Credentials

matplotlib.rcParams['font.family'] = 'Yu Gothic'

# -----------------------------
# 一次関数の式を教科書形式に整形
# -----------------------------
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

# -----------------------------
# 一次関数を生成
# -----------------------------
def generate_linear():
    a = random.choice([-3, -2, -1, 1, 2, 3])
    b = random.randint(-5, 5)
    return a, b

# -----------------------------
# Google Sheets に記録する関数
# -----------------------------
def send_to_sheet(eq_str, selected, correct_index, is_correct, elapsed):
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_file(
        "service_account.json",   # ←あなたの JSON キー
        scopes=scope
    )

    gc = gspread.authorize(creds)

    # ★あなたの指定したスプレッドシート
    sheet = gc.open_by_key("1S_koL8VGN2iPs11BR-dl5aDpmfRGCWKzwam6AKB1FmY").worksheet("一次関数_履歴")

    now = time.strftime("%Y-%m-%d %H:%M:%S")

    row = [
        now,
        eq_str,
        selected + 1,
        correct_index + 1,
        "○" if is_correct else "×",
        elapsed
    ]

    sheet.append_row(row)

# -----------------------------
# 新しい問題（式 → グラフ）
# -----------------------------
def new_problem():
    global correct_index, choices

    st["total"] += 1
    st["start_problem"] = time.time()  # ←追加：問題開始時刻

    # 正解の式
    correct = generate_linear()

    # 誤答生成
    choices = [correct]
    while len(choices) < 4:
        cand = generate_linear()
        if cand not in choices:
            choices.append(cand)

    random.shuffle(choices)
    correct_index = choices.index(correct)

    # 問題文（式）
    a, b = correct
    eq_label.config(text="問題： " + format_linear(a, b))

    # グラフ描画（4本）
    ax.clear()

    ax.annotate("", xy=(6, 0), xytext=(-6, 0),
                arrowprops=dict(arrowstyle="->", color="black"))
    ax.annotate("", xy=(0, 6), xytext=(0, -6),
                arrowprops=dict(arrowstyle="->", color="black"))

    x = np.linspace(-6, 6, 400)

    colors = ["red", "blue", "green", "orange"]
    labels = ["選択肢 1（赤）", "選択肢 2（青）", "選択肢 3（緑）", "選択肢 4（オレンジ）"]

    lw = line_width.get()

    for i in range(4):
        a2, b2 = choices[i]
        y = a2 * x + b2
        ax.plot(x, y, color=colors[i], linewidth=lw, label=labels[i])

    ax.set_xlim(-6, 6)
    ax.set_ylim(-6, 6)
    ax.grid(True)
    ax.legend()

    canvas.draw()
    selected.set(-1)

# -----------------------------
# 正誤判定
# -----------------------------
def check_answer():
    if selected.get() == -1:
        messagebox.showinfo("確認", "選択肢を選んでください。")
        return

    choice = selected.get()
    is_correct = (choice == correct_index)

    elapsed = int(time.time() - st["start_problem"])

    if is_correct:
        st["correct"] += 1
        messagebox.showinfo("結果", "正解です！")
    else:
        messagebox.showinfo("結果", f"不正解… 正しいのは 選択肢 {correct_index+1} です。")

    # ★Google Sheets に記録
    eq_str = eq_label.cget("text").replace("問題： ", "")
    send_to_sheet(eq_str, choice, correct_index, is_correct, elapsed)

# -----------------------------
# 終了処理
# -----------------------------
def finish():
    total = st["total"]
    correct = st["correct"]

    elapsed = int(time.time() - st["start"])
    minutes = elapsed // 60
    seconds = elapsed % 60

    if total == 0:
        rate = 0
    else:
        rate = correct / total * 100

    if rate >= 90:
        msg = "素晴らしい集中力でした！"
    elif rate >= 70:
        msg = "よく頑張りました！"
    elif rate >= 50:
        msg = "あと少しで完璧です！"
    else:
        msg = "続ければ必ず伸びます！"

    messagebox.showinfo(
        "学習結果",
        f"お疲れさまでした！\n\n"
        f"正解数：{correct} / {total}\n"
        f"正答率：{rate:.1f}%\n"
        f"所要時間：{minutes}分 {seconds}秒\n\n"
        f"{msg}"
    )

    root.destroy()

# -----------------------------
# Tkinter GUI
# -----------------------------
root = tk.Tk()
root.title("直線のグラフ選択問題（式 → グラフ）")

st = {"correct": 0, "total": 0, "start": time.time()}

eq_label = tk.Label(root, text="", font=("Arial", 16))
eq_label.pack(pady=10)

fig, ax = plt.subplots(figsize=(6, 6))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

selected = tk.IntVar(value=-1)

# 線の太さ設定
setting_frame = tk.Frame(root)
setting_frame.pack(pady=10)

tk.Label(setting_frame, text="線の太さ：", font=("Arial", 14)).grid(row=0, column=0)
line_width = tk.Scale(setting_frame, from_=1, to=5, orient=tk.HORIZONTAL)
line_width.set(2)
line_width.grid(row=0, column=1)

# 選択肢ボタン
radio_frame = tk.Frame(root)
radio_frame.pack(pady=10)

for i in range(4):
    tk.Radiobutton(
        radio_frame,
        text=f"選択肢 {i+1}",
        variable=selected,
        value=i,
        font=("Arial", 16)
    ).pack(side=tk.LEFT, padx=10)

# ボタン
btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="答え合わせ", command=check_answer, font=("Arial", 16)).pack(side=tk.LEFT, padx=20)
tk.Button(btn_frame, text="次の問題", command=new_problem, font=("Arial", 16)).pack(side=tk.LEFT, padx=20)
tk.Button(btn_frame, text="終了する", command=finish, font=("Arial", 16)).pack(side=tk.LEFT, padx=20)

new_problem()
root.mainloop()
