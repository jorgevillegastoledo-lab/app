import streamlit as st
from datetime import datetime
from db import conectar_db
from estilos import aplicar_estilos

def prestamos_nuevo(conn):
    st.set_page_config(layout="wide")
    aplicar_estilos()

    st.title("➕ Registrar Nuevo Préstamo")

    cursor = conn.cursor()

    with st.form("form_prestamo"):
        nombre = st.text_input("Nombre del préstamo", placeholder="Ej: Préstamo Automotriz")
        entidad = st.text_input("Entidad financiera", placeholder="Ej: BancoEstado")
        valor_cuota = st.number_input("Valor de la cuota", min_value=0.0, step=1000.0)
        cuotas_totales = st.number_input("Cantidad total de cuotas", min_value=1, step=1)
        cuotas_pagadas = st.number_input("Cuotas ya pagadas", min_value=0, max_value=cuotas_totales, step=1)

        submitted = st.form_submit_button("Guardar préstamo")

        if submitted:
            estado = "Pagado" if cuotas_pagadas == cuotas_totales else "Activo"
            monto_total = valor_cuota * cuotas_totales  # ✅ Se calcula automáticamente

            cursor.execute('''
                INSERT INTO prestamos (nombre, entidad, valor_cuota, cuotas_totales, cuotas_pagadas, estado, monto_total)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (nombre, entidad, valor_cuota, cuotas_totales, cuotas_pagadas, estado, monto_total))
            conn.commit()

            st.success("✅ Préstamo registrado correctamente.")

if __name__ == "__main__":
    prestamos_nuevo()


