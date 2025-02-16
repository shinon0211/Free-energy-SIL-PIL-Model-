from pkgutil import read_code
#要先 pip install matplotlib
#要先 pip install numpy
import math
import numpy as np
import matplotlib
from openpyxl.worksheet.print_settings import PRINT_AREA_RE

matplotlib.use('Agg')
# 使用非交互式後端
import matplotlib.pyplot as plt


msd_sigma=np.array([0.00638,0.00440,0.00496,0.00507,0.00506])
IQ=np.array([0.74149,0.74396,0.76962,0.77392,0.76719])
V=np.array([0.89621,0.94070,0.99620,1.03101,1.07354])
Rm=pow(3/4*V/math.pi,1/3)

#TEST 之後會改用input
Kc=1
Kcn=1
rm=0.005
rc_cn=0.04

#之後會x = np.arange(1, 6, 1) 顯示1,2,3,4,5
fc=0.005
#fc^1/3
fcz=pow(fc,1/3)
fcy=pow(fc,-1/3)


#5種環境
SIL=(0.5*Kcn*msd_sigma/pow(1-pow(fc,1/3),2))+(rm/2*3*(pow(IQ,-1/3)-1)/Rm)
PIL=((Kc+Kcn)/2*msd_sigma)+((rm/2+rc_cn*pow(fc,-1/3))*(3*(pow(IQ,-1/3)-1)/Rm))
print('F SIL=',SIL)
print('F PIL=',PIL)

#畫圖比較
x = np.arange(1,6,1)
plt.scatter(x, SIL, label='F SIL')
plt.scatter(x, PIL, label='F PIL')
plt.legend()
plt.savefig('fc=0.05.png')
