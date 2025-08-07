import streamlit as st
import sqlite3
from datetime import datetime, date
from estilos import aplicar_estilos
import time

def gastos_nuevo(conn):
    st.set_page_config(layout="wide")
    aplicar_estilos()

    st.title("📝 Ingresar Nuevo Gasto")

    nombre = st.text_input("Nombre del gasto")
    valor = st.number_input("Valor", min_value=0.0, step=100.0)
    tipo = st.selectbox("Tipo de gasto", ["Básico", "Otro"])
    con_tarjeta = st.checkbox("¿Pagar con tarjeta de crédito?")
    es_recurrente = st.checkbox("¿Es un gasto recurrente?")
    fecha_vencimiento = st.date_input("Fecha de vencimiento", value=datetime.today().date())

    # Mes contable
    meses_dict = {
        "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4,
        "Mayo": 5, "Junio": 6, "Julio": 7, "Agosto": 8,
        "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
    }

    mes_nombre = st.selectbox("Mes en que se contabiliza el gasto", list(meses_dict.keys()), index=datetime.today().month - 1)
    mes_contable = meses_dict[mes_nombre]
    anio_contable = st.number_input("Año contable", value=datetime.today().year, step=1)

    tarjeta_id = None
    pagado_con_tarjeta = 0

    if con_tarjeta:
        tarjetas = conn.execute("SELECT id, nombre FROM tarjetas_credito").fetchall()
        if not tarjetas:
            st.warning("⚠️ No hay tarjetas registradas.")
            return
        opciones_tarjeta = {f"{t[1]} (ID {t[0]})": t[0] for t in tarjetas}
        seleccion = st.selectbox("Selecciona la tarjeta", list(opciones_tarjeta.keys()))
        tarjeta_id = opciones_tarjeta[seleccion]
        pagado_con_tarjeta = 1

    if st.button("Guardar Gasto"):
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO gastos (
                    nombre, valor, tipo, tarjeta_id, mes,
                    pagado, fecha_pago, fecha_vencimiento,
                    recurrente, pagado_con_tarjeta,
                    mes_contable, anio_contable
                )
                VALUES (?, ?, ?, ?, ?, 0, NULL, ?, ?, ?, ?, ?)
            """, (
                nombre,
                valor,
                tipo,
                tarjeta_id,
                mes_contable,
                fecha_vencimiento,
                int(es_recurrente),
                pagado_con_tarjeta,
                mes_contable,
                anio_contable
            ))

            conn.commit()
            st.success("✅ Gasto guardado correctamente.")
            time.sleep(1.5)
            st.rerun()

        except Exception as e:
            conn.rollback()
            st.error(f"❌ Error al guardar el gasto: {e}")

