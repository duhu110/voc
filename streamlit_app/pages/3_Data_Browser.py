from __future__ import annotations

import streamlit as st

from streamlit_app.app_services import fetch_table_rows


st.set_page_config(page_title='Data Browser', page_icon='🗂️', layout='wide')

st.title('Data Browser')
st.caption('浏览待处理工单、结果表和统计表的当前数据。')

table_options = {
    '待处理工单': 'pending_tickets',
    '分类结果': 'category_results',
    '标签结果': 'tag_results',
    '关键词结果': 'keyword_results',
    '命中明细': 'match_details',
    '分类统计': 'category_stats',
    '标签统计': 'tag_stats',
    '分类-标签关系统计': 'category_tag_relations',
    '分类关键词统计': 'category_keyword_stats',
    '标签关键词统计': 'tag_keyword_stats',
}

selected_label = st.selectbox('选择数据表', list(table_options.keys()), index=0)
limit = st.slider('显示行数', min_value=10, max_value=200, value=50, step=10)

rows = fetch_table_rows(table_options[selected_label], limit=limit)
st.caption(f'当前表: `{table_options[selected_label]}`')

if rows:
    st.dataframe(rows, use_container_width=True, hide_index=True)
else:
    st.info('当前查询没有返回数据。')
