from __future__ import annotations

from datetime import date

import streamlit as st

from streamlit_app.app_services import fetch_table_rows, run_statistics_refresh


st.set_page_config(page_title='Stats Center', page_icon='📈', layout='wide')

st.title('Stats Center')
st.caption('手动刷新统计表，并查看当前统计结果。')

with st.form('stats-refresh-form'):
    stat_date = st.date_input('统计日期', value=date.today())
    refresh_submitted = st.form_submit_button('刷新统计')

if refresh_submitted:
    with st.spinner('正在刷新统计表，请等待...'):
        refresh_summary = run_statistics_refresh(stat_date.isoformat())
    st.success('统计刷新完成。')
    metric_columns = st.columns(5)
    metric_columns[0].metric('分类统计', refresh_summary.get('category_stats', 0))
    metric_columns[1].metric('标签统计', refresh_summary.get('tag_stats', 0))
    metric_columns[2].metric('分类标签关系', refresh_summary.get('category_tag_relations', 0))
    metric_columns[3].metric('分类关键词统计', refresh_summary.get('category_keyword_stats', 0))
    metric_columns[4].metric('标签关键词统计', refresh_summary.get('tag_keyword_stats', 0))
    st.json(refresh_summary, expanded=True)

tabs = st.tabs(['分类统计', '标签统计', '分类标签关系', '分类关键词', '标签关键词'])

with tabs[0]:
    rows = fetch_table_rows('category_stats', limit=100)
    st.dataframe(rows, use_container_width=True, hide_index=True)

with tabs[1]:
    rows = fetch_table_rows('tag_stats', limit=100)
    st.dataframe(rows, use_container_width=True, hide_index=True)

with tabs[2]:
    rows = fetch_table_rows('category_tag_relations', limit=100)
    st.dataframe(rows, use_container_width=True, hide_index=True)

with tabs[3]:
    rows = fetch_table_rows('category_keyword_stats', limit=100)
    st.dataframe(rows, use_container_width=True, hide_index=True)

with tabs[4]:
    rows = fetch_table_rows('tag_keyword_stats', limit=100)
    st.dataframe(rows, use_container_width=True, hide_index=True)
