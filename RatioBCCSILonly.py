import math
import numpy as np
import pandas as pd
import os
from tkinter import Tk, filedialog
# 環境設定
os.environ["TCL_LIBRARY"] = r"C:\Users\USER\AppData\Local\Programs\Python\Python310\tcl\tcl8.6"
os.environ["TK_LIBRARY"] = r"C:\Users\USER\AppData\Local\Programs\Python\Python310\tcl\tk8.6"

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

# BCC phase
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
weights_Z = [3, 2,  2]
Np_Z = 7

# fc 值範圍
fc_values = np.arange(0.005, 0.505, 0.005)

# 初始化數據結構
def initialize_phase_lists():
    return {
        "fc_list": [],
        "index_list": [],
        "F_SIL_list": [],
        "F_PIL_list": [],
        "Smaller Value": [],
        "Weighted Value": [],
        "Ratio": [],
        "Weighted Ratio Sum": [],
        "F/Np": []
    }

data_Sigma = initialize_phase_lists()
data_C14 = initialize_phase_lists()
data_C15 = initialize_phase_lists()
data_BCC = initialize_phase_lists()
data_A15 = initialize_phase_lists()
data_Z = initialize_phase_lists()

# 處理每個相的數據
def process_phase(msd, IQ, Rm, weights, data, Np, is_BCC=False):
    for fc in fc_values:
        F_new_temp = 0
        weighted_ratio_sum = 0
        fcz = np.power(fc, 1 / 3)
        fcy = np.power(fc, -1 / 3)

        for index in range(len(msd)):
            # 計算 SIL
            SIL = (0.5 * Kcn * msd[index] / np.power(1 - fcz, 2)) + (
                (rm / 2) * 3 * (np.power(IQ[index], -1 / 3) - 1) / Rm[index]
            )

            if is_BCC:
                PIL = None
                smaller_value = SIL
                ratio = 0
            else:
                # 計算 PIL
                PIL = ((Kc + Kcn) / 2 * msd[index]) + (
                    (rm / 2 + rc_cn * fcy) * (3 * (np.power(IQ[index], -1 / 3) - 1) / Rm[index])
                )
                smaller_value = np.minimum(SIL, PIL)
                ratio = 0 if smaller_value == SIL else 1

            weighted_value = smaller_value * weights[index]
            weighted_ratio = ratio * weights[index]
            F_new_temp += weighted_value
            weighted_ratio_sum += weighted_ratio

            # 更新數據
            data["fc_list"].append(fc)
            data["index_list"].append(index + 1)
            data["F_SIL_list"].append(SIL)
            data["F_PIL_list"].append(PIL)
            data["Smaller Value"].append(smaller_value)
            data["Weighted Value"].append(weighted_value)
            data["Ratio"].append(ratio)

        F_new_temp_normalized = F_new_temp / Np
        data["F/Np"].append(F_new_temp_normalized)
        data["Weighted Ratio Sum"].append(weighted_ratio_sum)

# 處理每個相的數據
process_phase(msd_sigma, IQ_Sigma, Rm_Sigma, weights_sigma, data_Sigma, Np_Sigma)
process_phase(msd_C14, IQ_C14, Rm_C14, weights_C14, data_C14, Np_C14)
process_phase(msd_C15, IQ_C15, Rm_C15, weights_C15, data_C15, Np_C15)
process_phase(msd_BCC, IQ_BCC, Rm_BCC, weights_BCC, data_BCC, Np_BCC, is_BCC=True)
process_phase(msd_A15, IQ_A15, Rm_A15, weights_A15, data_A15, Np_A15)
process_phase(msd_Z, IQ_Z, Rm_Z, weights_Z, data_Z, Np_Z)

# 建立 DataFrame
def create_dataframe(data, msd_length):
    return pd.DataFrame({
        "fc": data["fc_list"],
        "Index": data["index_list"],
        "F_SIL": data["F_SIL_list"],
        "F_PIL": data["F_PIL_list"],
        "Smaller Value": data["Smaller Value"],
        "Weighted Value": data["Weighted Value"],
        "Ratio": data["Ratio"],
        "Weighted Ratio Sum": np.repeat(data["Weighted Ratio Sum"], msd_length),
        "F/Np": np.repeat(data["F/Np"], msd_length)
    })

df_Sigma = create_dataframe(data_Sigma, len(msd_sigma))
df_C14 = create_dataframe(data_C14, len(msd_C14))
df_C15 = create_dataframe(data_C15, len(msd_C15))
df_BCC = create_dataframe(data_BCC, len(msd_BCC))
df_A15 = create_dataframe(data_A15, len(msd_A15))
df_Z = create_dataframe(data_Z, len(msd_Z))

# 儲存到 Excel
with pd.ExcelWriter(output_path) as writer:
    df_Sigma.to_excel(writer, sheet_name="Sigma Phase", index=False)
    df_C14.to_excel(writer, sheet_name="C14 Phase", index=False)
    df_C15.to_excel(writer, sheet_name="C15 Phase", index=False)
    df_BCC.to_excel(writer, sheet_name="BCC Phase", index=False)
    df_A15.to_excel(writer, sheet_name="A15 Phase", index=False)
    df_Z.to_excel(writer, sheet_name="Z Phase", index=False)

print(f"結果已儲存至：{output_path}")
