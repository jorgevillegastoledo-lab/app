import streamlit as st
from datetime import datetime
from estilos import aplicar_estilos

try:
    from estilos import aplicar_estilos
except Exception:
    # Fallback por si el import falla en la nube
    def aplicar_estilos():
        pass

def tarjetas_nuevo(conn):
    st.set_page_config(layout="wide")
    aplicar_estilos()

    st.title("💳 Registrar Pago de Tarjeta")

    tarjetas = conn.execute("SELECT id, nombre FROM tarjetas_credito").fetchall()
    if not tarjetas:
        st.warning("Primero debes registrar una tarjeta en el sistema.")
        return

    tarjeta_opciones = {f"{t[1]} (ID {t[0]})": t[0] for t in tarjetas}
    seleccion = st.selectbox("Selecciona la tarjeta", list(tarjeta_opciones.keys()))
    tarjeta_id = tarjeta_opciones[seleccion]

    monto = st.number_input("Monto a pagar", min_value=0.0, step=100.0)

    # Agregar selección manual del mes
    # Lista de meses en español
    meses_dict = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

    mes_nombre = st.selectbox("Mes en que se contabiliza el pago", list(meses_dict.values()), index=datetime.today().month - 1)
    mes = list(meses_dict.keys())[list(meses_dict.values()).index(mes_nombre)]
    
    
    
    
    #mes_seleccionado = st.selectbox("Mes en que se contabiliza el pago", list(range(1, 13)), index=datetime.today().month - 1)

    if st.button("Guardar pago"):
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO pagos_tarjeta (tarjeta_id, monto, pagado, fecha_pago, mes)
                VALUES (?, ?, 0, NULL, ?)
            """, (tarjeta_id, monto, mes))

            conn.commit()
            st.success("✅ Pago registrado correctamente.")
        except Exception as e:
            conn.rollback()
            st.error(f"❌ Error al guardar el pago: {e}")

