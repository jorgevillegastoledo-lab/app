import streamlit as st
import sqlite3
from datetime import datetime
from estilos import aplicar_estilos

def sueldo_ingresar(conn):
    st.set_page_config(layout="wide")
    aplicar_estilos()

    st.title("💼 Ingresar / Modificar Sueldo del Mes")

    # Diccionario de meses
    meses_dict = {
        "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4,
        "Mayo": 5, "Junio": 6, "Julio": 7, "Agosto": 8,
        "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
    }

    # Selección de mes y año
    mes_nombre = st.selectbox("Mes del sueldo", list(meses_dict.keys()), index=datetime.today().month - 1)
    mes = meses_dict[mes_nombre]
    anio = st.number_input("Año", value=datetime.today().year, step=1)

    # Obtener si ya existe sueldo ingresado
    cursor = conn.cursor()
    cursor.execute("SELECT monto FROM sueldos WHERE mes = ? AND anio = ?", (mes, anio))
    resultado = cursor.fetchone()

    sueldo_actual = resultado[0] if resultado else 0.0
    nuevo_sueldo = st.number_input("Monto del sueldo líquido para este mes", min_value=0.0, step=100.0, value=sueldo_actual)

    if st.button("💾 Guardar sueldo"):
        try:
            if resultado:
                cursor.execute("""
                    UPDATE sueldos SET monto = ?
                    WHERE mes = ? AND anio = ?
                """, (nuevo_sueldo, mes, anio))
            else:
                cursor.execute("""
                    INSERT INTO sueldos (anio, mes, monto)
                    VALUES (?, ?, ?)
                """, (anio, mes, nuevo_sueldo))
            conn.commit()
            st.success("✅ Sueldo guardado correctamente.")
        except Exception as e:
            conn.rollback()
            st.error(f"❌ Error al guardar el sueldo: {e}")

    # Mostrar tabla de sueldos guardados
    st.markdown("---")
    st.subheader("📋 Historial de sueldos ingresados")
    df_sueldos = cursor.execute("SELECT anio, mes, monto FROM sueldos ORDER BY anio DESC, mes DESC").fetchall()
    if df_sueldos:
        import pandas as pd
        df = pd.DataFrame(df_sueldos, columns=["Año", "Mes", "Sueldo"])
        df["Mes"] = df["Mes"].map({v: k for k, v in meses_dict.items()})
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No hay sueldos registrados aún.")

if __name__ == "__main__":
    conn = sqlite3.connect("basedatos.db")
    sueldo_ingresar(conn)