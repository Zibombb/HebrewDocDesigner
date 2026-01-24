#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard לניתוח נתוני מטופלות - Patient Data Analysis Dashboard
מערכת אינטראקטיבית לעיבוד וניתוח נתוני מטופלות ממרפאת כאבי גב
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
from pathlib import Path
from data_processor import PatientDataProcessor

# הגדרות עמוד
st.set_page_config(
    page_title="ניתוח נתוני מטופלות - מרפאת כאבי גב",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS מותאם אישית לתמיכה בעברית
st.markdown("""
<style>
    .main {
        direction: rtl;
        text-align: right;
    }
    .stButton button {
        width: 100%;
    }
    h1, h2, h3 {
        direction: rtl;
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """אתחול משתני מצב"""
    if 'processor' not in st.session_state:
        st.session_state.processor = PatientDataProcessor()
    if 'merged_data' not in st.session_state:
        st.session_state.merged_data = None
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None


def upload_files_section():
    """סקציית העלאת קבצים"""
    st.header("📁 העלאת קבצי JSON")

    uploaded_files = st.file_uploader(
        "בחר קבצי JSON (ניתן לבחור מספר קבצים)",
        type=['json'],
        accept_multiple_files=True,
        help="העלה 2-3 קבצי JSON בכל פעם לאיחוד וניתוח"
    )

    if uploaded_files:
        st.success(f"✅ נבחרו {len(uploaded_files)} קבצים")

        # הצגת שמות הקבצים
        for file in uploaded_files:
            st.text(f"• {file.name}")

        if st.button("🔄 עבד ואחד קבצים", type="primary"):
            with st.spinner("מעבד נתונים..."):
                # שמירת קבצים זמנית
                temp_paths = []
                for uploaded_file in uploaded_files:
                    temp_path = Path("data") / uploaded_file.name
                    with open(temp_path, 'wb') as f:
                        f.write(uploaded_file.getbuffer())
                    temp_paths.append(str(temp_path))

                # עיבוד
                results = st.session_state.processor.process_files(temp_paths)

                if 'error' in results:
                    st.error(f"❌ שגיאה: {results['error']}")
                else:
                    st.session_state.analysis_results = results
                    st.session_state.df = results['dataframe']
                    st.success("✅ הנתונים עובדו בהצלחה!")
                    st.rerun()


def statistics_section():
    """סקציית סטטיסטיקות"""
    if st.session_state.analysis_results is None:
        return

    st.header("📊 סטטיסטיקות כלליות")

    results = st.session_state.analysis_results
    stats = results['statistics']

    # כרטיסי מידע
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="סך הכל מטופלות",
            value=stats['total_patients']
        )

    with col2:
        st.metric(
            label="כפולים שנמצאו",
            value=results['duplicates_found']
        )

    with col3:
        st.metric(
            label="קבוצות שמות דומים",
            value=results['similar_names_groups']
        )

    with col4:
        st.metric(
            label="שדות במערכת",
            value=len(stats['columns'])
        )

    # טווח תאריכים
    if 'date_range' in stats and stats['date_range']['earliest']:
        st.subheader("📅 טווח תאריכים")
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"תאריך מוקדם ביותר: {stats['date_range']['earliest'][:10]}")
        with col2:
            st.info(f"תאריך מאוחר ביותר: {stats['date_range']['latest'][:10]}")


def duplicates_section():
    """סקציית כפולים"""
    if st.session_state.analysis_results is None:
        return

    results = st.session_state.analysis_results

    if results['duplicates_found'] > 0:
        st.header("⚠️ רשומות כפולות")
        st.warning(f"נמצאו {results['duplicates_found']} רשומות כפולות")

        with st.expander("הצג רשומות כפולות", expanded=False):
            for i, dup in enumerate(results['duplicates']):
                st.subheader(f"כפילות #{i+1}")
                col1, col2 = st.columns(2)
                with col1:
                    st.json(dup['original'])
                with col2:
                    st.json(dup['duplicate'])
                st.divider()


def similar_names_section():
    """סקציית שמות דומים"""
    if st.session_state.analysis_results is None:
        return

    results = st.session_state.analysis_results

    if results['similar_names_groups'] > 0:
        st.header("👥 שמות דומים")
        st.info(f"נמצאו {results['similar_names_groups']} קבוצות של שמות דומים")

        with st.expander("הצג קבוצות שמות דומים", expanded=False):
            for i, group in enumerate(results['similar_names']):
                st.subheader(f"קבוצה #{i+1}")
                for item in group['group']:
                    st.text(f"• {item['name']}")
                st.divider()


def timeline_visualization():
    """ויזואליזציה של ציר זמן"""
    if st.session_state.df is None:
        return

    st.header("📈 מפת פעילות על ציר הזמן")

    df = st.session_state.df

    # זיהוי עמודת תאריך
    date_cols = df.select_dtypes(include=['datetime64']).columns
    if len(date_cols) == 0:
        st.warning("לא נמצאה עמודת תאריך לויזואליזציה")
        return

    date_col = date_cols[0]

    # סינון נתונים עם תאריכים תקינים
    df_with_dates = df[df[date_col].notna()].copy()

    if len(df_with_dates) == 0:
        st.warning("אין נתונים עם תאריכים תקינים")
        return

    # יצירת עמודת שנה-חודש לקיבוץ
    df_with_dates['year_month'] = df_with_dates[date_col].dt.to_period('M').astype(str)

    # ספירת מטופלות לפי חודש
    monthly_counts = df_with_dates.groupby('year_month').size().reset_index(name='count')

    # גרף קו
    fig_line = px.line(
        monthly_counts,
        x='year_month',
        y='count',
        title='מספר מטופלות לאורך זמן',
        labels={'year_month': 'חודש', 'count': 'מספר מטופלות'}
    )
    fig_line.update_layout(
        xaxis_title="חודש-שנה",
        yaxis_title="מספר מטופלות",
        hovermode='x unified'
    )
    st.plotly_chart(fig_line, use_container_width=True)

    # גרף עמודות
    fig_bar = px.bar(
        monthly_counts,
        x='year_month',
        y='count',
        title='התפלגות מטופלות לפי חודש',
        labels={'year_month': 'חודש', 'count': 'מספר מטופלות'},
        color='count',
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # heat map לפי שנה וחודש
    df_with_dates['year'] = df_with_dates[date_col].dt.year
    df_with_dates['month'] = df_with_dates[date_col].dt.month

    heatmap_data = df_with_dates.groupby(['year', 'month']).size().reset_index(name='count')
    heatmap_pivot = heatmap_data.pivot(index='month', columns='year', values='count').fillna(0)

    fig_heatmap = go.Figure(data=go.Heatmap(
        z=heatmap_pivot.values,
        x=heatmap_pivot.columns,
        y=['ינואר', 'פברואר', 'מרץ', 'אפריל', 'מאי', 'יוני',
           'יולי', 'אוגוסט', 'ספטמבר', 'אוקטובר', 'נובמבר', 'דצמבר'],
        colorscale='Blues',
        text=heatmap_pivot.values,
        texttemplate='%{text}',
        textfont={"size": 10}
    ))

    fig_heatmap.update_layout(
        title='מפת חום - פעילות לפי חודש ושנה',
        xaxis_title='שנה',
        yaxis_title='חודש'
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)


def data_table_section():
    """סקציית טבלת נתונים"""
    if st.session_state.df is None:
        return

    st.header("📋 טבלת נתונים")

    df = st.session_state.df

    # אפשרויות סינון
    st.subheader("סינון נתונים")

    # בחירת עמודות להצגה
    all_columns = list(df.columns)
    selected_columns = st.multiselect(
        "בחר עמודות להצגה",
        options=all_columns,
        default=all_columns[:5] if len(all_columns) > 5 else all_columns
    )

    if selected_columns:
        filtered_df = df[selected_columns]

        # הצגת הטבלה
        st.dataframe(filtered_df, use_container_width=True, height=400)

        # הורדה
        csv = filtered_df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="💾 הורד כ-CSV",
            data=csv,
            file_name=f"patient_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )


def main():
    """פונקציה ראשית"""
    init_session_state()

    # כותרת ראשית
    st.title("🏥 מערכת ניתוח נתוני מטופלות")
    st.subheader("מרפאת כאבי גב - ניהול וניתוח מידע רפואי")

    # sidebar
    with st.sidebar:
        st.header("ℹ️ מידע")
        st.info("""
        **מערכת לניתוח נתוני מטופלות**

        המערכת מאפשרת:
        - 📤 העלאת קבצי JSON
        - 🔄 איחוד נתונים
        - 🔍 זיהוי כפולים
        - 👥 זיהוי שמות דומים
        - 📊 ויזואליזציה על ציר זמן
        - 📋 ניתוח וסינון נתונים
        """)

        if st.session_state.analysis_results:
            st.success("✅ נתונים נטענו")
            if st.button("🔄 התחל מחדש"):
                st.session_state.merged_data = None
                st.session_state.df = None
                st.session_state.analysis_results = None
                st.rerun()

    # סקציות ראשיות
    upload_files_section()

    if st.session_state.analysis_results:
        st.divider()
        statistics_section()

        st.divider()
        duplicates_section()

        st.divider()
        similar_names_section()

        st.divider()
        timeline_visualization()

        st.divider()
        data_table_section()


if __name__ == "__main__":
    main()
