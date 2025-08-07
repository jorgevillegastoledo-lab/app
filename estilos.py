import streamlit as st

def aplicar_estilos():
    st.markdown("""
        <style>
        /* Fondo principal claro rosa */
        .main {
            background-color: #ffeef5;
        }

        /* Fondo completo */
        html, body, .stApp {
            background-color: #ffeef5 !important;
        }

        .block-container {
            background-color: #ffeef5 !important;
            padding: 2rem 1rem;
        }

        /* Colores de títulos */
        h1, h2, h3, h4, h5, h6 {
            color: #003366;
        }

        /* Sidebar: fondo verde amarillento */
        section[data-testid="stSidebar"] {
            background-color: #f1ffcd;
        }

        /* Texto del sidebar */
        section[data-testid="stSidebar"] * {
            color: #003366;
            font-weight: bold;
        }

        /* Botones */
        div.stButton > button {
            background-color: #f7c6d9;
            color: #003366;
            border: none;
            border-radius: 8px;
            font-weight: bold;
            padding: 0.5em 1em;
        }
        div.stButton > button:hover {
            background-color: #f4acc6;
            color: #001133;
        }

        /* Inputs en general */
        input, select, textarea {
            background-color: #ffffff !important;
            color: #003366 !important;
            border: 1px solid #d4ed73 !important;
            border-radius: 5px;
        }

        /* Inputs number personalizados */
        .stNumberInput input {
            background-color: #ffffff !important;
            color: #003366 !important;
        }
        .stNumberInput button {
            background-color: #f7c6d9 !important;
            color: #003366 !important;
        }

        /* Date inputs */
        .stDateInput input {
            background-color: #ffffff !important;
            color: #003366 !important;
        }

        /* Selectbox con baseweb */
        div[data-baseweb="select"] {
            background-color: #ffffff !important;
            color: #003366 !important;
            border: 1px solid #d4ed73 !important;
            border-radius: 5px;
        }
        div[data-baseweb="popover"] {
            background-color: #ffffff !important;
            color: #003366 !important;
        }
        div[data-baseweb="option"] {
            color: #003366 !important;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab"] {
            background-color: #fdf0f5;
            border-radius: 10px 10px 0 0;
            color: #003366;
            font-weight: bold;
            padding: 0.5em 1em;
        }
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #fbd1df;
        }

        </style>
    """, unsafe_allow_html=True)
