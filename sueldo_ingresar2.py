import streamlit as st
import pandas as pd
from datetime import datetime
from db import conectar_db
from estilos import aplicar_estilos

# Función para registrar o modificar sueldo
def sueldo_ingresar():
    st.set_page_config(layout="wide")
    aplicar_estilos()

    st.title("💼 Ingresar / Modificar Sueldo del Mes")

    conn = conectar_db()

    meses_dict = {
        "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4,
        "Mayo": 5, "Junio": 6, "Julio": 7, "Agosto": 8,
        "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
    }

    mes_nombre = st.selectbox("Mes del sueldo", list(meses_dict.keys()), index=datetime.today().month - 1)
    mes = meses_dict[mes_nombre]
    anio = st.number_input("Año", min_value=2000, max_value=2100, value=datetime.today().year)

    # Buscar sueldo existente para ese mes y año
    conn.row_factory = lambda cursor, row: row[0]
    cursor = conn.cursor()
    sueldo_existente = cursor.execute("SELECT monto FROM sueldos WHERE mes = ? AND anio = ?", (mes, anio)).fetchone()

    monto_default = sueldo_existente if sueldo_existente else 0
    monto = st.number_input("Monto del sueldo líquido para este mes", min_value=0.0, step=100.0, format="%.2f", value=monto_default)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("💾 Guardar sueldo"):
            if sueldo_existente:
                cursor.execute("UPDATE sueldos SET monto = ? WHERE mes = ? AND anio = ?", (monto, mes, anio))
                conn.commit()
                st.success("Sueldo actualizado correctamente.")
            else:
                cursor.execute("INSERT INTO sueldos (mes, anio, monto) VALUES (?, ?, ?)", (mes, anio, monto))
                conn.commit()
                st.success("Sueldo registrado correctamente.")

    # Mostrar historial
    st.markdown("---")
    st.markdown("### 🗂️ Historial de sueldos ingresados")
    df_sueldos = pd.read_sql_query("SELECT anio, mes, monto FROM sueldos ORDER BY anio DESC, mes DESC", conn)

    if not df_sueldos.empty:
        numero_a_nombre_mes = {v: k for k, v in meses_dict.items()}
        df_sueldos["Mes"] = df_sueldos["mes"].map(numero_a_nombre_mes)
        df_sueldos = df_sueldos[["anio", "Mes", "monto"]]
        df_sueldos.columns = ["Año", "Mes", "Sueldo"]
        st.dataframe(df_sueldos, hide_index=True, use_container_width=True)
    else:
        st.info("No hay sueldos registrados todavía.")

if __name__ == "__main__":
    sueldo_ingresar()