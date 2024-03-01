import streamlit as st
import tools as tls
from io import BytesIO

st.set_page_config("谱漂数据处理", layout="wide", initial_sidebar_state="collapsed")

file_cols = st.columns(2)
f1 = file_cols[0].file_uploader("上传室温下的能道数据文件", type=["txt", "csv", "xls", "xlsx"])
f2 = file_cols[1].file_uploader("上传加热后的能道数据文件", type=["txt", "csv", "xls", "xlsx"])

if "df1" not in st.session_state:
    st.session_state.df1 = None
if "df2" not in st.session_state:
    st.session_state.df2 = None

if f1 is not None:
    st.session_state.df1 = tls.get_df_from_file(f1)
if f2 is not None:
    st.session_state.df2 = tls.get_df_from_file(f2)

chart_cols = st.columns(2)
with chart_cols[0]:
    chart1, container1 = st.columns([3, 1])
    with chart1:
        tls.show_chart(st.session_state.df1)
        channels_standard = [62, 108, 122, 227]
    with container1:
        channel1 = st.number_input("channel:", key="channel1", min_value=1, max_value=256, value=None, step=1,
                                   format="%d")
        value = tls.get_counts(st.session_state.df1, channel1)
        counts1 = st.number_input("counts:", key="counts1", value=value, disabled=True)

with chart_cols[1]:
    chart2, container2 = st.columns([3, 1])
    with chart2:
        tls.show_chart(st.session_state.df2)
        channels_real = [51, 89, 101, 187]
    with container2:
        channel2 = st.number_input("channel:", key="channel2", min_value=1, max_value=256, value=None, step=1,
                                   format="%d")
        value = tls.get_counts(st.session_state.df2, channel2)
        counts2 = st.number_input("counts:", key="counts2", value=value, disabled=True)

st.write("谱漂图如下：")
st.divider()
chart3, container3 = st.columns([4, 1])
with chart3:
    if st.session_state.df1 is not None and st.session_state.df2 is not None:
        new_spectrum = tls.get_new_spectrum(st.session_state.df1, channels_standard, st.session_state.df2,
                                            channels_real, 1e-4)
        result = tls.show_result_chart(st.session_state.df1, new_spectrum, channels_standard)
        excel_data = BytesIO()
        result.to_excel(excel_data, index=False)
        excel_data.seek(0)
        st.download_button("谱漂数据下载", excel_data, file_name='after_data.xlsx')
    else:
        result = None
with container3:
    channel3 = st.number_input("channel:", key="channel3", min_value=1, max_value=256, value=None, step=1, format="%d")
    value1 = tls.get_counts(result, channel3, col1='Channels', col2='Counts_origin')
    value2 = tls.get_counts(result, channel3, col1='Channels', col2='Counts_after')
    counts3_1 = st.number_input("counts_origin:", key="counts3_1", value=value1, disabled=True)
    counts3_2 = st.number_input("counts_after:", key="counts3_2", value=value2, disabled=True)
