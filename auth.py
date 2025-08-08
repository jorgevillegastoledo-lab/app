# auth.py
import streamlit as st

def require_login():
    if st.session_state.get("logged_in"):
        _logout_button()
        return True

    st.title("🔒 Iniciar sesión")
    with st.form("login_form", clear_on_submit=False):
        user = st.text_input("Usuario")
        pwd = st.text_input("Contraseña", type="password")
        ok = st.form_submit_button("Entrar")

    if ok:
        valid_user = st.secrets.get("APP_USER")
        valid_pass = st.secrets.get("APP_PASS")

        # Debug mínimo: mostrar qué keys de secrets existen (no sus valores)
        if not (valid_user and valid_pass):
            st.error("Faltan credenciales en Secrets (APP_USER / APP_PASS).")
            st.caption(f"Secrets cargados: {list(st.secrets.keys())}")
            st.stop()

        if user == valid_user and pwd == valid_pass:
            st.session_state["logged_in"] = True
            st.success("¡Bienvenido!")
            try:
                st.rerun()                  # Streamlit >= 1.30
            except Exception:
                st.experimental_rerun()     # Compatibilidad retro
        else:
            st.error("Usuario o contraseña incorrectos.")
            st.stop()

    st.stop()

def _logout_button():
    with st.sidebar:
        if st.button("🚪 Cerrar sesión"):
            st.session_state.pop("logged_in", None)
            try:
                st.rerun()
            except Exception:
                st.experimental_rerun()
