import numpy as np
import streamlit as st
import pandas as pd
import altair as alt


@st.cache_data(max_entries=2)
def get_df_from_file(file):
    # 使用 Pandas 读取 CSV 或 Excel 文件
    if file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" or file.type == "application/vnd.ms-excel":
        df = pd.read_excel(file, usecols=['channels', 'counts'])
    else:
        df = pd.read_csv(file, skiprows=1, header=None, names=['counts'])
        df['channels'] = range(1, 257)
        df = df[['channels', 'counts']]
    return df


def show_chart(df):
    line_chart = alt.Chart(df).mark_line().encode(
        x=alt.X("channels", type="ordinal"),
        y=alt.Y("counts", type="quantitative")
    ).configure_axis(
        grid=True,  # 显示网格线
        gridDash=[1, 2]  # 网格线样式
    )
    st.altair_chart(line_chart, use_container_width=True)


@st.cache_data()
def get_counts(df, channel,col1='channels',col2='counts'):
    if df is not None and channel is not None:
        return df.loc[df[col1] == channel, col2].values[0]
    return None


@st.cache_data()
def get_new_spectrum(df1, channels_standard, df2, channels_real, step_len):
    '''
    根据室温和加热情况下的谱图及峰位，拟合出加热后谱漂情况下的谱图，返回谱漂下的计数值
    :param df1:室温下谱图
    :param channels_standard:室温下谱图的峰位
    :param df2:加热下谱图
    :param channels_real:加热下谱图的峰位
    :param step_len:搜索步长
    :return:new_spectrum[]拟合后的计数值
    '''
    # 多项式拟合
    c2e_w = np.polyfit(channels_standard, channels_real, 1)
    c2e_s = np.polyfit(channels_real, channels_standard, 1)
    c2e_w11 = np.poly1d(c2e_w)
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
    '''
    显示室温下和加热后拟合的谱图，观察谱漂现象
    :param old_spectrum: 室温下谱图信息，为dataframe，第一列为channels，第2列为counts
    :param new_spectrum: 加热拟合的谱图，为列表，保存了各个channel的counts信息
    :return: result:包含3列的dataframe,分别为能道、原始计数、拟合计数
    '''
    df_wide = pd.DataFrame(columns=['Channels', 'Counts_origin', 'Counts_after'])
    df_wide['Channels'] = range(1, 257)
    df_wide['Counts_origin'] = old_spectrum['counts']
    df_wide['Counts_after'] = new_spectrum
    df_long = df_wide.melt(id_vars=['Channels'], var_name='condition', value_name='Counts')
    line_chart = alt.Chart(df_long).mark_line().encode(
        x='Channels',
        y='Counts',
        color='condition',
        tooltip=['Channels', 'Counts']
    ).interactive()
    vlines=alt.Chart(pd.DataFrame({'Channels_standard': channels_standard})).mark_rule(color='red', strokeDash=[5,5]).encode(
        x='Channels_standard'
    ).interactive()
    st.altair_chart(line_chart+vlines,use_container_width=True)
    return df_wide


def data_input(uploaded_file):
    """
    :param uploaded_file
    :return: df
    """
    # 如果用户上传了文件，读取文件内容并转换为 DataFrame
    if uploaded_file is not None:
        try:
            # 使用 Pandas 读取 TXT 或 Excel 文件
            if uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                df = pd.read_excel(uploaded_file, usecols=['channels', 'counts'])
            else:
                df = pd.read_csv(uploaded_file, skiprows=1, header=None, names=['counts'])
                df['channels'] = range(1, 257)
                df = df[['channels', 'counts']]

            # 显示 DataFrame
            st.dataframe(df, use_container_width=True, hide_index=True)
            line_chart = alt.Chart(df).mark_line().encode(
                x="channels",
                y="counts"
            ).interactive()
            st.altair_chart(line_chart, use_container_width=True)
            return df
        except Exception as e:
            st.error(f"An error occurred: {e}")
