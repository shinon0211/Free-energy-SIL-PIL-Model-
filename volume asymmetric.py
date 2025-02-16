import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import os
os.environ["TCL_LIBRARY"] = r"C:\Users\USER\AppData\Local\Programs\Python\Python310\tcl\tcl8.6"
os.environ["TK_LIBRARY"] = r"C:\Users\USER\AppData\Local\Programs\Python\Python310\tcl\tk8.6"
from tkinter import Tk, filedialog

# 初始化 tkinter 並隱藏主視窗
root = Tk()
root.withdraw()

# 提示用戶輸入參數值，或使用預設值
Kc = input("請輸入 Kc (預設 1): ") or 1
Kcn = input("請輸入 Kcn (預設 1): ") or 1
rm = input("請輸入 rm (預設 0.005): ") or 0.005
rc_cn = input("請輸入 rc_cn (預設 0.04): ") or 0.04

# 確保輸入值是數值
Kc, Kcn, rm, rc_cn = float(Kc), float(Kcn), float(rm), float(rc_cn)

# 選擇輸出路徑
output_path = filedialog.asksaveasfilename(
    title="選擇輸出 Excel 檔案位置",
    defaultextension=".xlsx",
    filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")]
)

if not output_path:
    print("未選擇輸出路徑，程式結束。")
    exit()

print(f"將輸出檔案保存至: {output_path}")
# 繼續後續程式執行...

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

# fc 值範圍
fc_values = np.arange(0.005, 0.505, 0.005)

# 初始化數據結構（加入體積不對稱項的列表）
def initialize_phase_lists():
    return {
        "fc_list": [],
        "index_list": [],
        "F_SIL_list": [],
        "F_PIL_list": [],
        "smaller_value_list": [],
        "weighted_value_list": [],
        "F_weighted_value": [],
        "F/Np_value": [],
        "F_vol_correction": [],  # 體積修正項
        "F_total_corrected": []  # 總修正後的 F 值
    }

data_Sigma = initialize_phase_lists()
data_C14 = initialize_phase_lists()
data_C15 = initialize_phase_lists()
data_BCC = initialize_phase_lists()

# 處理每個相的數據，加入體積修正項
def process_phase(msd, IQ, Rm, weights, data, Np, is_BCC=False):
    # 計算體積相關的數據
    V_mean = np.mean((4 / 3) * np.pi * Rm**3)  # 平均體積
    sigma_V2 = np.var((4 / 3) * np.pi * Rm**3)  # 體積方差

    for fc in fc_values:
        F_new_temp = 0
        fcz = np.power(fc, 1 / 3)
        fcy = np.power(fc, -1 / 3)

        for index in range(len(msd)):
            # 計算 SIL
            SIL = (0.5 * Kcn * msd[index] / np.power(1 - fcz, 2)) + (
                (rm / 2) * 3 * (np.power(IQ[index], -1 / 3) - 1) / Rm[index]
            )

            if is_BCC:
                data["F_PIL_list"].append(None)
                weighted_value = SIL * weights[index]
                smaller_value = SIL
            else:
                # 計算 PIL
                PIL = ((Kc + Kcn) / 2 * msd[index]) + (
                    (rm / 2 + rc_cn * fcy) * (3 * (np.power(IQ[index], -1 / 3) - 1) / Rm[index])
                )
                smaller_value = np.minimum(SIL, PIL)
                weighted_value = smaller_value * weights[index]
                data["F_PIL_list"].append(PIL)

            # 更新數據
            F_new_temp += weighted_value
            data["fc_list"].append(fc)
            data["index_list"].append(index + 1)
            data["F_SIL_list"].append(SIL)
            data["smaller_value_list"].append(smaller_value)
            data["weighted_value_list"].append(weighted_value)

        # 體積不對稱修正項
        F_vol = -fc * (sigma_V2 / V_mean**2)
        data["F_vol_correction"].append(F_vol)

        # 總修正後自由能
        F_new_temp_normalized = F_new_temp / Np  # 原始自由能
        F_total = F_new_temp_normalized + F_vol  # 加入修正項後的自由能
        data["F_weighted_value"].append(F_new_temp)
        data["F/Np_value"].append(F_new_temp_normalized)
        data["F_total_corrected"].append(F_total)

# 分別處理每個相
process_phase(msd_sigma, IQ_Sigma, Rm_Sigma, weights_sigma, data_Sigma, Np_Sigma)
process_phase(msd_C14, IQ_C14, Rm_C14, weights_C14, data_C14, Np_C14)
process_phase(msd_C15, IQ_C15, Rm_C15, weights_C15, data_C15, Np_C15)
process_phase(msd_BCC, IQ_BCC, Rm_BCC, weights_BCC, data_BCC, Np_BCC, is_BCC=True)

# 修改 DataFrame 函數以包含體積修正項
def create_dataframe(data, msd_length):
    return pd.DataFrame({
        "fc": data["fc_list"],
        "Index": data["index_list"],
        "F_SIL": data["F_SIL_list"],
        "F_PIL": data["F_PIL_list"],
        "Smaller Value": data["smaller_value_list"],
        "Weighted Value (F)": data["weighted_value_list"],
        "F/Np": np.repeat(data["F/Np_value"], msd_length),
        "F_vol_correction": np.repeat(data["F_vol_correction"], msd_length),
        "F_total_corrected": np.repeat(data["F_total_corrected"], msd_length)
    })

df_Sigma = create_dataframe(data_Sigma, len(msd_sigma))
df_C14 = create_dataframe(data_C14, len(msd_C14))
df_C15 = create_dataframe(data_C15, len(msd_C15))
df_BCC = create_dataframe(data_BCC, len(msd_BCC))

# 儲存到 Excel，新增修正後數據
with pd.ExcelWriter(output_path) as writer:
    df_Sigma.to_excel(writer, sheet_name="Sigma Phase", index=False)
    df_C14.to_excel(writer, sheet_name="C14 Phase", index=False)
    df_C15.to_excel(writer, sheet_name="C15 Phase", index=False)
    df_BCC.to_excel(writer, sheet_name="BCC Phase", index=False)

print(f"結果已儲存至：{output_path}")

# 選擇保存圖表的路徑
plot_path = filedialog.asksaveasfilename(
    title="選擇輸出圖表位置",
    defaultextension=".png",
    filetypes=[("PNG Files", "*.png"), ("All Files", "*.*")]
)

if not plot_path:
    print("未選擇圖表保存路徑，程式結束。")
    exit()

# Plot
plt.figure(figsize=(8, 6))
plt.plot(fc_values, data_Sigma["F_total_corrected"], label='Sigma Phase', color='blue')
plt.plot(fc_values, data_C14["F_total_corrected"], label='C14 Phase', color='mediumslateblue')
plt.plot(fc_values, data_C15["F_total_corrected"], label='C15 Phase', color='green')
plt.plot(fc_values, data_BCC["F_total_corrected"], label='BCC Phase', color='red')
plt.xlabel('fc')
plt.ylabel('F_new (Weighted Sum of Min(SIL, PIL)) / Np')
plt.title('Normalized F vs fc')
plt.legend()
plt.grid(True)
plt.tight_layout()

# Save the plot
plt.savefig(plot_path)

# Output paths for reference
print(f"Results saved to: {output_path}")
print(f"Plot saved to: {plot_path}")
