import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from estilos import aplicar_estilos

def gastos_resumen(conn):
    st.set_page_config(layout="wide")
    aplicar_estilos()

    st.markdown("""
        <style>
        .pill-paid{
            display:inline-block; padding:6px 14px; border-radius:999px;
            background:#e6f4ea; color:#137333; font-weight:600; font-size:0.9rem;
            border:1px solid #cce8d5;
        }
        .header-cell{
            font-weight:700; font-size:1.0rem; color:#0b3b69; margin-bottom:4px;
        }
        .row-wrap{ padding:6px 0; }
        </style>
    """, unsafe_allow_html=True)

    st.title("📋 Resumen de Gastos")

    meses = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]
    mes_actual = datetime.today().month
    mes_nombre = st.selectbox("Selecciona el mes a visualizar:", meses, index=mes_actual - 1)
    mes_seleccionado = meses.index(mes_nombre) + 1

    gastos = pd.read_sql_query("SELECT * FROM gastos", conn)
    tarjetas = pd.read_sql_query("SELECT * FROM tarjetas_credito", conn)

    if gastos.empty:
        st.info("No hay gastos registrados.")
        return

    gastos_mes = gastos[gastos["mes"] == mes_seleccionado].copy()
    if gastos_mes.empty:
        st.info("No hay gastos para este mes.")
        return

    if "fecha_vencimiento" in gastos_mes.columns:
        gastos_mes["fecha_vencimiento"] = pd.to_datetime(gastos_mes["fecha_vencimiento"], errors="coerce")

    def fmt_money(x):
        try:
            return f"${float(x):,.0f}".replace(",", ".")
        except Exception:
            return f"${x}"

    st.markdown("### 💰 Gastos del mes")

    h0, h1, h2, h3, h4, h5 = st.columns([1.2, 4, 1.4, 1.1, 1.6, 1.4])
    with h0: st.markdown('<div class="header-cell">Código</div>', unsafe_allow_html=True)
    with h1: st.markdown('<div class="header-cell">Concepto</div>', unsafe_allow_html=True)
    with h2: st.markdown('<div class="header-cell">Valor</div>', unsafe_allow_html=True)
    with h3: st.markdown('<div class="header-cell">Tipo</div>', unsafe_allow_html=True)
    with h4: st.markdown('<div class="header-cell">Forma de Pago Ingresada</div>', unsafe_allow_html=True)
    with h5: st.markdown('<div class="header-cell">Estado</div>', unsafe_allow_html=True)

    gastos_mes = gastos_mes.sort_values(["pagado", "nombre"]).reset_index(drop=True)

    for _, gasto in gastos_mes.iterrows():
        c0, c1, c2, c3, c4, c5 = st.columns([1.2, 4, 1.4, 1.1, 1.6, 1.4])

        with c0:
            st.markdown(f"<div class='row-wrap'>{gasto['id']}</div>", unsafe_allow_html=True)

        with c1:
            st.markdown(f"<div class='row-wrap'>{gasto['nombre']}</div>", unsafe_allow_html=True)

        with c2:
            st.markdown(f"<div class='row-wrap'>{fmt_money(gasto['valor'])}</div>", unsafe_allow_html=True)

        with c3:
            st.markdown(f"<div class='row-wrap'>{gasto['tipo']}</div>", unsafe_allow_html=True)

        with c4:
            forma_pago = "T. Crédito" if int(gasto.get("pagado_con_tarjeta", 0)) == 1 else "Efectivo"
            st.markdown(f"<div class='row-wrap'>{forma_pago}</div>", unsafe_allow_html=True)

        with c5:
            if int(gasto.get("pagado", 0)) == 1:
                st.markdown("<div class='pill-paid'>Pagado</div>", unsafe_allow_html=True)
            else:
                if st.button("Marcar como pagado", key=f"pagar_{gasto['id']}"):
                    try:
                        cursor = conn.cursor()
                        fecha_pago = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

                        cursor.execute("""
                            UPDATE gastos
                            SET pagado = 1, fecha_pago = ?
                            WHERE id = ?
                        """, (fecha_pago, int(gasto["id"])))

                        if int(gasto.get("recurrente", 0)) == 1:
                            nuevo_mes = int(gasto["mes"]) + 1 if int(gasto["mes"]) < 12 else 1
                            nuevo_anio = datetime.today().year + 1 if nuevo_mes == 1 else datetime.today().year

                            nueva_fecha_venc = None
                            if pd.notna(gasto.get("fecha_vencimiento")):
                                nueva_fecha_venc = (gasto["fecha_vencimiento"] + timedelta(days=30)).strftime("%Y-%m-%d")

                            cursor.execute("""
                                INSERT INTO gastos
                                    (nombre, valor, tipo, tarjeta_id, fecha_vencimiento,
                                     mes, anio_contable, mes_contable,
                                     pagado, fecha_pago, cuotas, recurrente, pagado_con_tarjeta)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, NULL, 0, ?, ?)
                            """, (
                                gasto["nombre"],
                                gasto["valor"],
                                gasto["tipo"],
                                gasto["tarjeta_id"],
                                nueva_fecha_venc,
                                nuevo_mes,
                                nuevo_anio,
                                nuevo_mes,
                                int(gasto.get("recurrente", 0)),
                                int(gasto.get("pagado_con_tarjeta", 0))
                            ))

                        conn.commit()
                        st.rerun()
                    except Exception as e:
                        conn.rollback()
                        st.error(f"❌ Error al marcar como pagado: {e}")

