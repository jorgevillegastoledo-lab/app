import streamlit as st
import pandas as pd
from estilos import aplicar_estilos

try:
    from estilos import aplicar_estilos
except Exception:
    # Fallback por si el import falla en la nube
    def aplicar_estilos():
        pass

def tarjetas_gestion(conn):
    st.set_page_config(layout="wide")
    aplicar_estilos()

    st.title("💳 Gestión de Tarjetas de Crédito y Débito")

    st.markdown("Agrega tus tarjetas y define su tipo y fecha de facturación si corresponde.")

    with st.form("form_tarjeta"):
        nombre = st.text_input("Nombre de la tarjeta", placeholder="Ej: Banco de Chile, Falabella")
        tipo = st.selectbox("Tipo de tarjeta", ["Crédito", "Débito"])
        cierre = st.number_input("Día de cierre de facturación (solo crédito)", min_value=1, max_value=31, step=1) if tipo == "Crédito" else None

        submitted = st.form_submit_button("Guardar tarjeta")

        if submitted:
            if not nombre:
                st.warning("⚠️ Debes ingresar el nombre de la tarjeta.")
            else:
                conn.execute("INSERT INTO tarjetas_credito (nombre, tipo, cierre_facturacion) VALUES (?, ?, ?)", (nombre, tipo, cierre))
                conn.commit()
                st.success("✅ Tarjeta guardada correctamente.")

    st.markdown("### 🗂 Tarjetas registradas")
    df = pd.read_sql_query("SELECT * FROM tarjetas_credito", conn)
    if df.empty:
        st.info("Aún no hay tarjetas registradas.")
    else:
        st.dataframe(df, use_container_width=True)
