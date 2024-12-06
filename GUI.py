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
        "index_list": [],
        "F_SIL_list": [],
        "F_PIL_list": [],
        "smaller_value_list": [],
        "weighted_value_list": [],
        "F_weighted_value": [],
        "F/Np_value": []
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
def process_phase(msd, IQ, Rm, weights, data, Np, is_BCC=False):
    fc_values = np.arange(0.005, 0.505, 0.005)
    for fc in fc_values:
        F_new_temp = 0
        fcz = np.power(fc, 1 / 3)
        fcy = np.power(fc, -1 / 3)

        for index in range(len(msd)):
            SIL = (0.5 * parameters["Kcn"].get() * msd[index] / np.power(1 - fcz, 2)) + (
                    (parameters["rm"].get() / 2) * 3 * (np.power(IQ[index], -1 / 3) - 1) / Rm[index]
            )

            if is_BCC:
                PIL = None
                weighted_value = SIL * weights[index]
                smaller_value = SIL
            else:
                PIL = ((parameters["Kc"].get() + parameters["Kcn"].get()) / 2 * msd[index]) + (
                        (parameters["rm"].get() / 2 + parameters["rc_cn"].get() * fcy) *
                        (3 * (np.power(IQ[index], -1 / 3) - 1) / Rm[index])
                )
                smaller_value = np.minimum(SIL, PIL)
                weighted_value = smaller_value * weights[index]
                data["F_PIL_list"].append(PIL)

            F_new_temp += weighted_value
            data["fc_list"].append(fc)
            data["index_list"].append(index + 1)
            data["F_SIL_list"].append(SIL)
            data["smaller_value_list"].append(smaller_value)
            data["weighted_value_list"].append(weighted_value)
            data["F_weighted_value"].append(F_new_temp)

        data["F/Np_value"].append(F_new_temp / Np)


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
    weights_Z = [6, 4,  4]
    Np_Z = 14

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
        process_phase(msd_BCC, IQ_BCC, Rm_BCC, weights_BCC, data["BCC"], Np_BCC, is_BCC=True)
    if "A15" in selected_phases:
        process_phase(msd_A15, IQ_A15, Rm_A15, weights_A15, data["A15"], Np_A15)
    if "Z" in selected_phases:
        process_phase(msd_Z, IQ_Z, Rm_Z, weights_Z, data["Z"], Np_Z)

    # 畫圖
    plot_data(fc_values, data)


# 畫圖函數
# 畫圖函數
def plot_data(fc_values, data):
    fig, ax = plt.subplots(figsize=(8, 6))

    # 在圖中畫出每個選擇的相的曲線
    for phase, phase_data in data.items():
        if phase in selected_phases:
            ax.plot(fc_values, phase_data["F/Np_value"], label=f'{phase} Phase')

    # 動態插入參數到標題
    parameter_text = (
        f"Kc = {parameters['Kc'].get():.2f}, "
        f"Kcn = {parameters['Kcn'].get():.2f}, "
        f"rm = {parameters['rm'].get():.3f}, "
        f"rc_cn = {parameters['rc_cn'].get():.3f}"
    )

    ax.set_xlabel("fc")
    ax.set_ylabel("Free energy(Weighted Sum of Min(SIL, PIL)) / Np")
    ax.set_title(f"F-fc plot\n{parameter_text}")  # 在標題下方加參數
    ax.legend()
    ax.grid(True)

    # 顯示圖形
    plt.show()

# 建立 GUI
row = 0
for key, var in parameters.items():
    tk.Label(root, text=f"{key}:").grid(row=row, column=0, padx=10, pady=5)
    tk.Entry(root, textvariable=var).grid(row=row, column=1, padx=10, pady=5)
    row += 1

tk.Label(root, text="選擇要計算的相：").grid(row=row, column=0, padx=5, pady=10)
phase_vars = {phase: tk.BooleanVar(value=False) for phase in ["Sigma", "C14", "C15", "BCC", "A15",  "Z"]}
col = 1
for phase, var in phase_vars.items():
    tk.Checkbutton(root, text=phase, variable=var).grid(row=row, column=col, padx=5, pady=5)
    col += 1

row += 1
tk.Button(root, text="開始計算", command=run_calculation).grid(row=row, column=0, columnspan=10, pady=20)

root.mainloop()
