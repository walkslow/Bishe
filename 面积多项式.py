import pandas as pd 
import numpy as np 
import sys
import matplotlib.pyplot as plt
from tqdm import trange
from sklearn.metrics import mean_squared_error as MSE
import streamlit as st

st.set_page_config(page_title='伽马能谱类测井数据处理算法和程序开发',page_icon=':shark:',layout='centered')
fname1 = st.text_input("请输入温度扣本底后数据文件路径")#温度扣本底后5.xlsx
fname2 = st.text_input("请输入正常情况扣本底后数据文件路径")#正常情况扣本底后2.xlsx
if fname1=='' or fname2=='':exit(0)
df = pd.read_excel(fname1,usecols=['channels','counts'])
df1 = pd.read_excel(fname2,usecols=['channels','counts'])
#Energy_3peak=[1.46,1.76,2.62]#单位Mev,对应钾,钍,铀，对应标准峰对应能量
Channels_real = [51, 89,101,187]
Channels_standard = [62, 108,122,227]
step_len=1e-4

de_values=df.values.tolist()
Channels=[]
Counts=[]
for i in range(len(de_values)):
    Channels.append(de_values[i][0])
    Counts.append(de_values[i][1])
    
de1_values=df1.values.tolist()
Channels1=[]
Counts1=[]
for i in range(len(de1_values)):
    Channels1.append(de1_values[i][0])
    Counts1.append(de1_values[i][1])
    
Channels_new=[]#再次刻度后的实测道数
#n=int(len(Channels_standard)-1)#多项式次数
n=1
c2e_w,residuals, rank, singular_values, rcond= np.polyfit(Channels_standard, Channels_real, n,full=True)#多项式拟合
#print(residuals, rank, singular_values, rcond,'residuals, rank, singular_values, rcond')
c2e_s,residuals, rank, singular_values, rcond= np.polyfit(Channels_real, Channels_standard, n,full=True)
#print(residuals, rank, singular_values, rcond,'residuals, rank, singular_values, rcond')

c2e_s11 = np.poly1d(c2e_s)
c2e_w11 = np.poly1d(c2e_w)
# x1 = np.arange(0, 256, 0.1)
# y2=c2e_s11(x1)
# plt.plot(Channels_real, Channels_standard, 'o', label='peak_standard')
# plt.plot(x1, y2, label='line_fit')
# plt.legend(loc='best')
# plt.show()

x1=[c2e_s11(i) for i in Channels]
#print(c2e_s11,'c2e_s11',c2e_w11,'c2e_w11')
Channels_3_new= c2e_s11(Channels_real) 
#print(Channels_3_new,'Channels_3_new')

new_spectrum = np.zeros(len(Channels))
for i in range(len(new_spectrum)):  
    Channels_left=c2e_w11(i)
    Channels_right=c2e_w11(i+1)
    #print(i,Channels_left,Channels_right)
    
    if Channels_left<0:
        left_bond=0
    else:
        left_bond=Channels_left
        
    if Channels_right>255:
        right_bond=255
    else:
        right_bond=Channels_right
    
    positon=left_bond
    while positon<right_bond:
        new_spectrum[i]+=step_len*Counts[int(positon)]
        positon+=step_len

total_origin=sum(Counts)
total_final=sum(new_spectrum)
#print(total_origin,total_final,total_origin-total_final,'total_origin,total_final')

#fig,ax=plt.subplots()
fig=plt.figure(figsize=(8,4.5))
ax=fig.add_subplot(111)
#plt.figure(figsize=(10, 6))
#plt.plot(Channels,Counts,label='Origin',color='r')#label 随意更改即可

ax.plot(Channels1,Counts1,label='The normal spectrum',color='b')
ax.plot(Channels,new_spectrum,label='After_final',color='red')
#plt.vlines(Channels_real, 0, 50000, colors='b', linestyles='dashed')
ax.vlines(Channels_standard, 0, 50000, colors='r', linestyles='dashed')
#plt.vlines(61, 0, 3000, colors='b', linestyles='dashed')
#plt.vlines(106, 0, 3000, colors='b', linestyles='dashed')
#plt.vlines(120, 0, 3000, colors='b', linestyles='dashed')
plt.legend()
ax.set_xlabel("Channels")
ax.set_ylabel("Counts")
ax.set_yscale('log')#使用对数Y轴
ax.set_title("Spectrum")
plt.rcParams['font.sans-serif'] = ['SimHei']#显示中文
#plt.show()

output_excel = {'Channels':[], 'Counts_origin':[],'Counts_after':[]}
output_excel['Channels'] = Channels
output_excel['Counts_origin'] = Counts
output_excel['Counts_after'] = new_spectrum
output = pd.DataFrame(output_excel)
output.to_excel('after_data.xlsx', index=False)
#df.to_excel

st.pyplot(fig)
