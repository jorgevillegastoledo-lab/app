import streamlit as st

def aplicar_estilos():
    st.markdown("""
        <style>
        /* Fondo principal */
        div[data-testid="stAppViewContainer"] {
            background-color: #f9f9f9;
        }
        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #e9f7c8;
        }
        /* Títulos */
        h1, h2, h3, h4, h5 {
            color: #004488 !important;
        }
        /* Botones */
        div.stButton > button {
            background-color: #f7c6d9;
            color: #004488;
            border: none;
            border-radius: 10px;
        }
        /* Tablas más limpias */
        .stDataFrame, .stDataFrame table {
            border-collapse: collapse;
        }
        </style>
    """, unsafe_allow_html=True)
