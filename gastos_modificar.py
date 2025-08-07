import streamlit as st
import pandas as pd
from datetime import datetime
from estilos import aplicar_estilos

try:
    from estilos import aplicar_estilos
except Exception:
    # Fallback por si el import falla en la nube
    def aplicar_estilos():
        pass

def gastos_modificar(conn):
    aplicar_estilos()
    st.title("📝 Modificar Gasto")

    gastos = pd.read_sql_query("SELECT * FROM gastos", conn)
    tarjetas = pd.read_sql_query("SELECT * FROM tarjetas_credito", conn)

    # Meses en español
    meses = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]

    mes_nombre = st.selectbox("Mes contable", meses, index=datetime.today().month - 1)
    mes = meses.index(mes_nombre) + 1

    gastos_mes = gastos[gastos["mes"] == mes]
    if gastos_mes.empty:
        st.warning("No hay gastos en este mes para modificar.")
        return

    gastos_mes["descripcion"] = gastos_mes.apply(
        lambda row: f"{row['id']} - {row['nombre']} (${row['valor']})", axis=1
    )
    seleccionado = st.selectbox("Selecciona el gasto a modificar:", gastos_mes["descripcion"].tolist())
    gasto_id = int(seleccionado.split("-")[0].strip())
    gasto = gastos[gastos["id"] == gasto_id].iloc[0]

    nuevo_nombre = st.text_input("Nombre del gasto", value=gasto["nombre"])
    nuevo_valor = st.number_input("Valor del gasto", value=float(gasto["valor"]))
    nuevo_tipo = st.selectbox("Tipo", ["Básico", "Extra"], index=0 if gasto["tipo"] == "Básico" else 1)

    pagar_con_tarjeta = st.checkbox("¿Pagar con tarjeta de crédito?", value=bool(gasto["pagado_con_tarjeta"]))
    tarjeta_id = None
    if pagar_con_tarjeta:
        nombre_tarjetas = {row["nombre"]: row["id"] for _, row in tarjetas.iterrows()}
        tarjeta_nombre = st.selectbox("Selecciona la tarjeta", list(nombre_tarjetas.keys()))
        tarjeta_id = nombre_tarjetas[tarjeta_nombre]

    recurrente = st.checkbox("¿Es un gasto recurrente?", value=bool(gasto["recurrente"]))
    marcar_pagado = st.checkbox("¿Marcar como pagado?", value=bool(gasto["pagado"]))

    if st.button("Guardar cambios"):
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE gastos
                   SET nombre = ?, valor = ?, tipo = ?, tarjeta_id = ?,
                       recurrente = ?, pagado = ?, pagado_con_tarjeta = ?
                 WHERE id = ?
            """, (
                nuevo_nombre,
                nuevo_valor,
                nuevo_tipo,
                tarjeta_id,
                int(recurrente),
                int(marcar_pagado),
                int(pagar_con_tarjeta),
                gasto_id
            ))
            conn.commit()
            st.success("✅ Gasto actualizado correctamente.")
            import time
            time.sleep(1.5)
            st.rerun()
        except Exception as e:
            conn.rollback()
            st.error(f"❌ Error al guardar los cambios: {e}")
            
            
             # Bloque de eliminación con mismo diseño que tarjetas
    st.markdown("---")
    with st.expander("🗑 ¿Eliminar este gasto por error?"):
        st.warning("Esta acción no se puede deshacer.")
        confirmar = st.checkbox("Confirmo que deseo eliminar este gasto.")
        if st.button("Eliminar gasto"):
            if confirmar:
                try:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM gastos WHERE id = ?", (gasto_id,))
                    conn.commit()
                    st.success("✅ Gasto eliminado correctamente.")
                    st.rerun()
                except Exception as e:
                    conn.rollback()
                    st.error(f"❌ Error al eliminar el gasto: {e}")
            else:
                st.warning("Debes confirmar antes de eliminar.")
            
                  
