import streamlit as st
import plotly.graph_objects as go

def show_header():

    st.markdown("""
    <h1 style='text-align:center;color:#00ADB5;'>
    AI Resume Analyzer
    </h1>

    <p style='text-align:center;font-size:20px;'>
    ATS Resume Scanner & Career Recommendation System
    </p>
    """, unsafe_allow_html=True)

def show_metrics(skills, pages, score):

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Skills", len(skills))

    with col2:
        st.metric("Pages", pages)

    with col3:
        st.metric("Resume Score", score)

def ats_chart(score):

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': "ATS Score"},
        gauge={
            'axis': {'range': [0,100]}
        }
    ))

    st.plotly_chart(fig, use_container_width=True)