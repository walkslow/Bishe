import numpy as np
import streamlit as st
import pandas as pd
import altair as alt


@st.cache_data(max_entries=2)
def get_df_from_file(file):
    """
    接受st.file_uploader的返回值，将file文件转化为dataframe格式
    :param file:
    :return: df:dataframe格式，第一列为channels，第二列为counts
    """
    # 读取xlsx和xls文件，格式为包含channels和counts这2列数据，每列有256个数据
    if (file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            or file.type == "application/vnd.ms-excel"):
        df = pd.read_excel(file, usecols=['channels', 'counts'])
    # 读取txt文件，格式为1列数据，第1行为列名，从第2行到第257行为counts计数值
    else:
        df = pd.read_csv(file, skiprows=1, header=None, names=['counts'])
        df['channels'] = range(1, 257)
        df = df[['channels', 'counts']]
    return df


def show_chart(df):
    """
    根据df显示折线图
    :param df:2列，第1列为channels，第2列为counts
    :return:
    """
    line_chart = alt.Chart(df).mark_line().encode(
        x=alt.X("channels", type="ordinal"),
        y=alt.Y("counts", type="quantitative")
    ).configure_axis(
        grid=True,  # 显示网格线
        gridDash=[1, 2]  # 网格线样式
    )
    st.altair_chart(line_chart, use_container_width=True)


@st.cache_data()
def get_counts(df, value, col1='channels', col2='counts'):
    """
    df包含col1和col2这2列，当col1的某一行的值为value时，返回col2的同一行的值
    :param df:
    :param value:
    :param col1:
    :param col2:
    :return:
    """
    if df is not None and value is not None:
        return df.loc[df[col1] == value, col2].values[0]
    return None


@st.cache_data()
def get_new_spectrum(df1, channels_standard, df2, channels_real, step_len):
    """
    根据室温和加热情况下的谱图及峰位，拟合出加热后谱漂情况下的谱图，返回谱漂下的计数值
    :param df1:室温下谱图
    :param channels_standard:室温下谱图的峰位
    :param df2:加热下谱图
    :param channels_real:加热下谱图的峰位
    :param step_len:搜索步长
    :return:new_spectrum[]拟合后的计数值
    """
    # 多项式拟合
    c2e_w = np.polyfit(channels_standard, channels_real, 1)  # 拟合系数
    c2e_s = np.polyfit(channels_real, channels_standard, 1)
    c2e_w11 = np.poly1d(c2e_w)  # 拟合函数
    c2e_s11 = np.poly1d(c2e_s)

    new_spectrum_len = len(df2)
    new_spectrum = np.zeros(new_spectrum_len)
    for i in range(new_spectrum_len):
        channel_left = c2e_w11(i)
        channel_right = c2e_w11(i + 1)

        if channel_left < 0:
            left_bond = 0
        else:
            left_bond = channel_left

        if channel_right > 255:
            right_bond = 255
        else:
            right_bond = channel_right

        position = left_bond
        while position < right_bond:
            new_spectrum[i] += step_len * df2.iloc[int(position), 1]
            position += step_len

    return new_spectrum


def show_result_chart(old_spectrum, new_spectrum, channels_standard):
    """
    显示室温下和加热后拟合的谱图，观察谱漂现象
    :param old_spectrum: 室温下谱图信息，为dataframe，第一列为channels，第2列为counts
    :param new_spectrum: 加热拟合的谱图，为列表，保存了各个channel的counts信息
    :param channels_standard:室温下谱图的峰位值
    :return: result:包含3列的dataframe,分别为能道Channels、原始计数Counts_origin、拟合计数Counts_after
    """
    # 将室温下谱图数据和加热拟合谱图数据合并为df_wide
    df_wide = pd.DataFrame(columns=['Channels', 'Counts_origin', 'Counts_after'])
    df_wide['Channels'] = range(1, 257)
    df_wide['Counts_origin'] = old_spectrum['counts']
    df_wide['Counts_after'] = new_spectrum
    # 将宽格式的df_wide转化为长格式的df_long，便于altair作图
    df_long = df_wide.melt(id_vars=['Channels'], var_name='condition', value_name='Counts')
    line_chart = alt.Chart(df_long).mark_line().encode(
        x='Channels',
        y='Counts',
        color='condition',
        tooltip=['Channels', 'Counts']
    ).interactive()
    # 显示峰位值的几条垂直虚线
    v_lines = alt.Chart(
        pd.DataFrame({'Channels_standard': channels_standard})
    ).mark_rule(
        color='red', strokeDash=[5, 5]
    ).encode(
        x='Channels_standard'
    ).interactive()
    # 将折线图与峰位值虚线叠加显示
    st.altair_chart(line_chart + v_lines, use_container_width=True)
    return df_wide
