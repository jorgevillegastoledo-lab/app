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

def tarjetas_resumen(conn):
    st.set_page_config(layout="wide")
    aplicar_estilos()

    st.markdown("""
        <style>
        .pill-paid{
            display:inline-block; padding:6px 14px; border-radius:999px;
            background:#e6f4ea; color:#137333; font-weight:600; font-size:0.9rem;
            border:1px solid #cce8d5;
        }
        .card-name {
            color: #003366;
            font-weight: 700;
        }
        .row-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            font-size: 1.0rem;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("💳 Resumen de Pagos de Tarjetas")
    
    # Lista de nombres de meses en español
    meses_dict = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}
    
    mes_nombre = st.selectbox("Selecciona el mes a visualizar:", list(meses_dict.values()), index=datetime.today().month - 1)
    mes = list(meses_dict.keys())[list(meses_dict.values()).index(mes_nombre)]

    #mes_actual = datetime.today().month
    #mes = st.selectbox("Selecciona el mes a visualizar:", list(range(1, 13)), index=mes_actual - 1)

    pagos = pd.read_sql_query("SELECT * FROM pagos_tarjeta WHERE mes = ?", conn, params=(mes,))
    tarjetas = pd.read_sql_query("SELECT * FROM tarjetas_credito", conn)

    if pagos.empty:
        st.info("No hay pagos registrados para este mes.")
        return

    st.markdown("### 📌 Pagos del mes")

    pagos = pagos.merge(tarjetas, left_on="tarjeta_id", right_on="id", suffixes=("_pago", "_tarjeta"))

    for _, row in pagos.iterrows():
        nombre = row["nombre"]
        monto = f"${int(row['monto']):,}".replace(",", ".")
        pagado = int(row["pagado"])

        col1, col2, col3 = st.columns([4, 2, 2])
        with col1:
            st.markdown(f"<div class='card-name'>{nombre}</div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='row-container'>{monto}</div>", unsafe_allow_html=True)
        with col3:
            if pagado:
                st.markdown("<div class='pill-paid'>Pagado</div>", unsafe_allow_html=True)
            else:
                if st.button("Marcar como pagado", key=f"pagar_{row['id_pago']}"):
                    try:
                        cursor = conn.cursor()
                        fecha = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
                        cursor.execute("""
                            UPDATE pagos_tarjeta
                               SET pagado = 1,
                                   fecha_pago = ?
                             WHERE id = ?
                        """, (fecha, row["id_pago"]))
                        conn.commit()
                        st.rerun()
                    except Exception as e:
                        conn.rollback()
                        st.error(f"❌ Error al actualizar el estado: {e}")
