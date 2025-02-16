import math
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import messagebox
import os
# 環境設定
os.environ["TCL_LIBRARY"] = r"C:\Users\USER\AppData\Local\Programs\Python\Python310\tcl\tcl8.6"
os.environ["TK_LIBRARY"] = r"C:\Users\USER\AppData\Local\Programs\Python\Python310\tcl\tk8.6"

# 初始化主視窗
root = tk.Tk()
root.title('SIL PIL Model')
root.geometry('600x250')

# 全局變量初始化
selected_phases = []

# 輸入參數
parameters = {
    "Kc": tk.DoubleVar(value=1),
    "Kcn": tk.DoubleVar(value=1),
    "rm": tk.DoubleVar(value=0.005),
    "rc_cn": tk.DoubleVar(value=0.04),
}

# 數據初始化函數
def initialize_phase_lists():
    return {
        "fc_list": [],
        "F/Np_value": [],
        "el_list": [],
        "s_list": []
    }

def initialize_all_phase_lists():
    return {
        "Sigma": initialize_phase_lists(),
        "C14": initialize_phase_lists(),
        "C15": initialize_phase_lists(),
        "BCC": initialize_phase_lists(),
        "A15": initialize_phase_lists(),
        "Z": initialize_phase_lists(),
    }

# 計算邏輯
def process_phase(msd, IQ, Rm, weights, data, Np):
    fc_values = np.arange(0.005, 0.505, 0.005)
    for fc in fc_values:
        F_new_temp = 0
        fcz = np.power(fc, 1 / 3)
        fcy = np.power(fc, -1 / 3)

        el_list = []
        s_list = []

        for index in range(len(msd)):
            # SIL 計算
            SIL_el = 0.5 * parameters["Kcn"].get() * msd[index] / np.power(1 - fcz, 2)
            SIL_s = (parameters["rm"].get() / 2) * 3 * (np.power(IQ[index], -1 / 3) - 1) / Rm[index]
            SIL = SIL_el + SIL_s

            # PIL 計算
            PIL_el = (parameters["Kc"].get() + parameters["Kcn"].get()) / 2 * msd[index]
            PIL_s = (parameters["rm"].get() / 2 + parameters["rc_cn"].get() * fcy) * (
                3 * (np.power(IQ[index], -1 / 3) - 1) / Rm[index]
            )
            PIL = PIL_el + PIL_s

            # 計算較小值及加權
            smaller_value = np.minimum(SIL, PIL)
            weighted_value = smaller_value * weights[index]

            if SIL < PIL:  # 如果SIL較小，將加權後的SIL的el和s值加入
                el_list.append(SIL_el * weights[index])
                s_list.append(SIL_s * weights[index])
            else:  # 如果PIL較小，將加權後的PIL的el和s值加入
                el_list.append(PIL_el * weights[index])
                s_list.append(PIL_s * weights[index])

            F_new_temp += weighted_value

        data["fc_list"].append(fc)
        data["F/Np_value"].append(F_new_temp / Np)
        data["el_list"].append(np.mean(el_list))
        data["s_list"].append(np.mean(s_list))

# 按鈕處理函數
def run_calculation():
    global selected_phases
    selected_phases = [
        phase for phase, var in phase_vars.items() if var.get()
    ]
    if not selected_phases:
        messagebox.showerror("錯誤", "請至少選擇一個相進行計算！")
        return

    # 固定數據
    # Sigma phase
    msd_sigma = np.array([0.00638, 0.00440, 0.00496, 0.00507, 0.00506])
    IQ_Sigma = np.array([0.74149, 0.74396, 0.76962, 0.77392, 0.76719])
    V_Sigma = np.array([0.89621, 0.94070, 0.99620, 1.03101, 1.07354])
    Rm_Sigma = np.power((3 / 4 * V_Sigma / math.pi), 1 / 3)
    weights_sigma = [2, 8, 8, 4, 8]
    Np_Sigma = 30

    # C14 phase
    msd_C14 = np.array([0.00725, 0.00208])
    IQ_C14 = np.array([0.73690, 0.81011])
    V_C14 = np.array([0.92884, 1.14232])
    Rm_C14 = np.power((3 / 4 * V_C14 / math.pi), 1 / 3)
    weights_C14 = [8, 4]
    Np_C14 = 12

    # C15 phase
    msd_C15 = np.array([0.00724, 0.00208])
    IQ_C15 = np.array([0.73690, 0.81011])
    V_C15 = np.array([0.92884, 1.14232])
    Rm_C15 = np.power((3 / 4 * V_C15 / math.pi), 1 / 3)
    weights_C15 = [16, 8]
    Np_C15 = 24

    # BCC phase (單一數值情況)
    msd_BCC = [0.00422]
    IQ_BCC = [0.75337]
    V_BCC = [1]
    Rm_BCC = np.power((3 / 4 * np.array(V_BCC) / math.pi), 1 / 3)
    weights_BCC = [1]
    Np_BCC = 1

    # A15 phase
    msd_A15 = np.array([0.00329, 0.00541])
    IQ_A15 = np.array([0.74931, 0.76589])
    V_A15 = np.array([0.97656, 1.00781])
    Rm_A15 = np.power((3 / 4 * V_A15 / math.pi), 1 / 3)
    weights_A15 = [2, 6]
    Np_A15 = 8

    # Z phase
    msd_Z = np.array([0.00589, 0.00589, 0.00308])
    IQ_Z = np.array([0.74292, 0.76522, 0.79095])
    V_Z = np.array([0.90447, 1.02042, 1.12288])
    Rm_Z = np.power((3 / 4 * V_Z / math.pi), 1 / 3)
    weights_Z = [3, 2, 2]
    Np_Z = 7

    fc_values = np.arange(0.005, 0.505, 0.005)
    data = initialize_all_phase_lists()

    # 執行計算
    if "Sigma" in selected_phases:
        process_phase(msd_sigma, IQ_Sigma, Rm_Sigma, weights_sigma, data["Sigma"], Np_Sigma)
    if "C14" in selected_phases:
        process_phase(msd_C14, IQ_C14, Rm_C14, weights_C14, data["C14"], Np_C14)
    if "C15" in selected_phases:
        process_phase(msd_C15, IQ_C15, Rm_C15, weights_C15, data["C15"], Np_C15)
    if "BCC" in selected_phases:
        process_phase(msd_BCC, IQ_BCC, Rm_BCC, weights_BCC, data["BCC"], Np_BCC)
    if "A15" in selected_phases:
        process_phase(msd_A15, IQ_A15, Rm_A15, weights_A15, data["A15"], Np_A15)
    if "Z" in selected_phases:
        process_phase(msd_Z, IQ_Z, Rm_Z, weights_Z, data["Z"], Np_Z)

    # 畫圖
    plot_data(fc_values, data)

# 畫圖函數
def plot_data(fc_values, data):
    num_phases = len(selected_phases)

    if num_phases == 0:
        messagebox.showinfo("提示", "未選擇任何相，無法繪圖！")
        return

    # 設置子圖數量和高度比例（上方自由能摺線圖 + 下方每個 phase 的堆疊直條圖）
    fig, axs = plt.subplots(1 + num_phases, 1, figsize=(8, 5 + 3 * num_phases), gridspec_kw={'height_ratios': [2] + [1] * num_phases})

    # 自由能摺線圖（第一個子圖）
    for phase, phase_data in data.items():
        if phase in selected_phases:
            axs[0].plot(phase_data["fc_list"], phase_data["F/Np_value"], label=f'{phase} Phase')
    axs[0].set_xlabel("fc")
    axs[0].set_ylabel("Free Energy / Np")
    axs[0].legend()
    axs[0].grid(True)
    axs[0].set_title("Free Energy vs fc")

    # 堆疊直條子圖（根據選擇的 phase 數量動態生成）
    for i, phase in enumerate(selected_phases):
        if phase in data:
            phase_data = data[phase]
            x = np.arange(len(phase_data["fc_list"]))
            axs[i + 1].bar(x, phase_data["el_list"], width=0.4, label='el', alpha=0.7, color='blue')
            axs[i + 1].bar(x, phase_data["s_list"], width=0.4, label='s', alpha=0.7, color='orange', bottom=phase_data["el_list"])
            axs[i + 1].set_xlabel("fc Index")
            axs[i + 1].set_ylabel("Energy Contribution")
            axs[i + 1].set_xticks(x)
            axs[i + 1].set_xticklabels([f"{fc:.3f}" for fc in phase_data["fc_list"]], rotation=45)
            axs[i + 1].legend()
            axs[i + 1].grid(True)
            axs[i + 1].set_title(f"{phase} Phase Energy Contribution")

    # 調整圖形布局
    plt.tight_layout()
    plt.show()

# 建立 GUI
row = 0
for key, var in parameters.items():
    tk.Label(root, text=f"{key}:").grid(row=row, column=0, padx=10, pady=5)
    tk.Entry(root, textvariable=var).grid(row=row, column=1, padx=10, pady=5)
    row += 1

tk.Label(root, text="選擇要計算的相：").grid(row=row, column=0, padx=5, pady=10)
phase_vars = {phase: tk.BooleanVar(value=False) for phase in ["Sigma", "C14", "C15", "BCC", "A15", "Z"]}
col = 1
for phase, var in phase_vars.items():
    tk.Checkbutton(root, text=phase, variable=var).grid(row=row, column=col, padx=5, pady=5)
    col += 1

row += 1
tk.Button(root, text="開始計算", command=run_calculation).grid(row=row, column=0, columnspan=10, pady=20)

root.mainloop()
