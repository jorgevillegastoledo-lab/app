import streamlit as st
import pandas as pd
from estilos import aplicar_estilos
from datetime import datetime

try:
    from estilos import aplicar_estilos
except Exception:
    # Fallback por si el import falla en la nube
    def aplicar_estilos():
        pass

def tarjetas_modificar(conn):
    st.set_page_config(layout="wide")
    aplicar_estilos()

    st.title("✏️ Modificar facturación registrada")

    # Cargar pagos con nombre de tarjeta
    pagos = pd.read_sql_query("""
        SELECT pt.id, tc.nombre AS tarjeta, pt.tarjeta_id, pt.monto, pt.pagado, pt.fecha_pago, pt.mes
        FROM pagos_tarjeta pt
        JOIN tarjetas_credito tc ON pt.tarjeta_id = tc.id
        ORDER BY pt.mes DESC
    """, conn)

    if pagos.empty:
        st.info("No hay facturación registrada.")
        return

    # Filtro por mes contable
    meses = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]
    mes_nombre = st.selectbox("Filtrar por mes contable:", meses, index=datetime.today().month - 1)
    mes_num = meses.index(mes_nombre) + 1
    pagos_mes = pagos[pagos["mes"] == mes_num]

    if pagos_mes.empty:
        st.warning("No hay registros para el mes seleccionado.")
        return

    pagos_mes["selector"] = pagos_mes.apply(
        lambda row: f"{row['tarjeta']} - {meses[row['mes'] - 1]} - ${int(row['monto']):,}".replace(",", "."),
        axis=1
    )

    seleccion = st.selectbox("Selecciona un registro a modificar:", pagos_mes["selector"])
    pago_id = int(pagos_mes[pagos_mes["selector"] == seleccion]["id"].values[0])
    datos = pagos_mes[pagos_mes["id"] == pago_id].iloc[0]

    tarjetas = pd.read_sql_query("SELECT id, nombre FROM tarjetas_credito", conn)
    nueva_tarjeta = st.selectbox(
        "Tarjeta asociada:",
        tarjetas["nombre"],
        index=int(tarjetas[tarjetas["nombre"] == datos["tarjeta"]].index[0])
    )
    nueva_tarjeta_id = int(tarjetas[tarjetas["nombre"] == nueva_tarjeta]["id"].values[0])

    nuevo_monto = st.number_input("Monto a pagar:", min_value=0.0, step=100.0, value=float(datos["monto"]))
    nuevo_mes = st.selectbox("Mes contable:", list(range(1, 13)), index=int(datos["mes"]) - 1)
    nuevo_pagado = st.checkbox("¿Está pagado?", value=bool(datos["pagado"]))

    if st.button("Guardar cambios"):
        try:
            fecha_pago = datetime.today().strftime("%Y-%m-%d") if nuevo_pagado else None

            cursor = conn.cursor()
            cursor.execute("""
                UPDATE pagos_tarjeta
                SET tarjeta_id = ?, monto = ?, mes = ?, pagado = ?, fecha_pago = ?
                WHERE id = ?
            """, (
                nueva_tarjeta_id,
                nuevo_monto,
                nuevo_mes,
                1 if nuevo_pagado else 0,
                fecha_pago,
                pago_id
            ))
            conn.commit()

            if cursor.rowcount == 0:
                st.error("⚠️ No se encontró el registro o no se realizaron cambios.")
            else:
                st.success("✅ Factura modificada correctamente.")
                import time
                time.sleep(1.5)
                st.rerun()

        except Exception as e:
            conn.rollback()
            st.error(f"❌ Error al guardar los cambios: {e}")

    st.markdown("---")

    with st.expander("🗑 ¿Eliminar este registro por error?"):
        st.warning("Esta acción no se puede deshacer.")
        confirmar = st.checkbox("Confirmo que deseo eliminar esta factura.")
        if st.button("Eliminar factura seleccionada"):
            if confirmar:
                try:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM pagos_tarjeta WHERE id = ?", (pago_id,))
                    conn.commit()
                    st.success("✅ Registro eliminado correctamente.")
                    import time
                    time.sleep(1.5)
                    st.rerun()
                except Exception as e:
                    conn.rollback()
                    st.error(f"❌ Error al eliminar el registro: {e}")
            else:
                st.warning("Debes confirmar antes de eliminar.")
