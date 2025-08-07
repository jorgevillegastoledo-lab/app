# auth.py
import streamlit as st

def require_login():
    # Si ya hay sesión, ok
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

        if not valid_user or not valid_pass:
            st.error("Faltan credenciales en *Secrets* (APP_USER / APP_PASS).")
            return False

        if user == valid_user and pwd == valid_pass:
            st.session_state["logged_in"] = True
            st.success("¡Bienvenido!")
            st.experimental_rerun()
        else:
            st.error("Usuario o contraseña incorrectos.")
            return False

    # Bloquea el resto de la app hasta que inicie sesión
    st.stop()

def _logout_button():
    with st.sidebar:
        if st.button("🚪 Cerrar sesión"):
            for k in ("logged_in",):
                st.session_state.pop(k, None)
            st.experimental_rerun()
