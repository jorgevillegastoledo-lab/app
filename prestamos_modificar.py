import streamlit as st
import pandas as pd
#from db import conectar_db
from estilos import aplicar_estilos

try:
    from estilos import aplicar_estilos
except Exception:
    # Fallback por si el import falla en la nube
    def aplicar_estilos():
        pass

def prestamos_modificar(conn):
    st.set_page_config(layout="wide")
    aplicar_estilos()

    st.title("✏️ Modificar Préstamo")

    #conn = conectar_db()
    df = pd.read_sql_query("SELECT * FROM prestamos", conn)

    if df.empty:
        st.info("No hay préstamos registrados para modificar.")
        return

    df["opcion"] = df["nombre"] + " - " + df["entidad"] + " (ID: " + df["id"].astype(str) + ")"
    seleccion = st.selectbox("Selecciona un préstamo para modificar:", df["opcion"])

    if seleccion:
        prestamo_id = int(seleccion.split("ID: ")[-1].replace(")", ""))
        prestamo = df[df["id"] == prestamo_id].iloc[0]

        with st.form("form_modificar"):
            nuevo_nombre = st.text_input("Nombre del préstamo", value=prestamo["nombre"])
            nueva_entidad = st.text_input("Entidad financiera", value=prestamo["entidad"])
            nuevo_valor_cuota = st.number_input("Valor de la cuota", min_value=0.0, value=prestamo["valor_cuota"])
            nuevas_cuotas_totales = st.number_input("Cantidad total de cuotas", min_value=1, value=prestamo["cuotas_totales"])
            nuevas_cuotas_pagadas = st.number_input("Cuotas pagadas", min_value=0, max_value=nuevas_cuotas_totales, value=prestamo["cuotas_pagadas"])

            submitted = st.form_submit_button("Guardar cambios")

            if submitted:
                nuevo_estado = "Pagado" if nuevas_cuotas_pagadas == nuevas_cuotas_totales else "Activo"
                nuevo_pagado = 1 if nuevo_estado == "Pagado" else 0

                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE prestamos
                    SET nombre = ?, entidad = ?, valor_cuota = ?, cuotas_totales = ?, cuotas_pagadas = ?, estado = ?, pagado = ?
                    WHERE id = ?
                """, (nuevo_nombre, nueva_entidad, nuevo_valor_cuota, nuevas_cuotas_totales, nuevas_cuotas_pagadas, nuevo_estado, nuevo_pagado, prestamo_id))

                conn.commit()
                st.success("✅ Préstamo actualizado correctamente.")

if __name__ == "__main__":
    prestamos_modificar()
