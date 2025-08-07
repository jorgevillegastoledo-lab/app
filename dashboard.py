import streamlit as st
import pandas as pd
from datetime import datetime
from db import conectar_db
#from estilos import aplicar_estilos

def dashboard():
    st.set_page_config(layout="wide")
    aplicar_estilos()

    st.title("📊 Panel General de Finanzas")

    conn = conectar_db()
    
    anio_actual = datetime.today().year
    
    
    meses_dict = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }

    mes_nombre = st.selectbox("Selecciona el mes a visualizar:", list(meses_dict.values()), index=datetime.today().month - 1)
    mes_actual = list(meses_dict.keys())[list(meses_dict.values()).index(mes_nombre)]

# ----------- GASTOS ----------- #
    df_gastos = pd.read_sql_query("""
        SELECT *, 
               CASE WHEN pagado_con_tarjeta = 1 THEN '💳' ELSE '' END AS marca_tarjeta
        FROM gastos 
        WHERE mes = ?
    """, conn, params=(mes_actual,))

    total_gastos = df_gastos[(df_gastos["pagado"] == 1) & (df_gastos["pagado_con_tarjeta"] == 0)]["valor"].sum()
    gastos_pendientes = df_gastos[df_gastos["pagado"] == 0]
    total_gastos_pendientes = gastos_pendientes[gastos_pendientes["pagado_con_tarjeta"] == 0]["valor"].sum()
    gastos_tarjeta_pendientes = gastos_pendientes[gastos_pendientes["pagado_con_tarjeta"] == 1]
    total_gastos_tarjeta_pendientes = gastos_tarjeta_pendientes["valor"].sum()
    total_gastos_tarjeta_pagados = df_gastos[(df_gastos["pagado"] == 1) & (df_gastos["pagado_con_tarjeta"] == 1)]["valor"].sum()

    vencimientos_esporadicos = df_gastos[(df_gastos["tipo"] == "Otro") & (df_gastos["pagado"] == 0)][["nombre", "fecha_vencimiento", "marca_tarjeta"]]
   
# ----------- PRÉSTAMOS ----------- #
    df_prestamos = pd.read_sql_query("SELECT * FROM prestamos", conn)
    df_pagos_prestamo = pd.read_sql_query("SELECT * FROM pagos_prestamo", conn)

# Convertir fecha de inicio a datetime
    df_prestamos["fecha_inicio_pago"] = pd.to_datetime(df_prestamos["fecha_inicio_pago"], errors="coerce")
    fecha_referencia = datetime(datetime.today().year, mes_actual, 1)

# Filtrar préstamos activos que ya comenzaron a pagarse y que aún tienen cuotas por pagar
    prestamos_activos = df_prestamos[
    (df_prestamos["cuotas_pagadas"] < df_prestamos["cuotas_totales"]) &
    (df_prestamos["fecha_inicio_pago"] <= fecha_referencia)
     ].copy()

# Filtrar pagos registrados en el mes contable actual
    pagos_mes = df_pagos_prestamo[df_pagos_prestamo["mes_contable"] == mes_actual]

# Calcular total pagado en el mes (real)
    resultado_total_pagado_mes = pd.read_sql_query("""
       SELECT SUM(valor_cuota) AS total_pagado_mes
       FROM pagos_prestamo
       WHERE mes_contable = ?
    """, conn, params=(mes_actual,))
    total_prestamos = resultado_total_pagado_mes.iloc[0]["total_pagado_mes"] or 0

# Calcular cuotas pendientes del mes
    pagos_conteo = pagos_mes.groupby("prestamo_id").size().reset_index(name="cuotas_pagadas_este_mes")
    prestamos_con_pagos = prestamos_activos.merge(pagos_conteo, left_on="id", right_on="prestamo_id", how="left").fillna(0)
    prestamos_con_pagos["cuotas_pendientes_mes"] = 1 - prestamos_con_pagos["cuotas_pagadas_este_mes"]
    prestamos_con_pagos["cuotas_pendientes_mes"] = prestamos_con_pagos["cuotas_pendientes_mes"].clip(lower=0)
    prestamos_con_pagos["pendiente_mes"] = prestamos_con_pagos["cuotas_pendientes_mes"] * prestamos_con_pagos["valor_cuota"]
    total_prestamos_pendientes_mes = prestamos_con_pagos["pendiente_mes"].sum()

# Deuda total restante (informativo)
    total_deuda_prestamos = df_prestamos["deuda_restante"].sum()
   
# ----------- TARJETAS ----------- #
    df_pagos_tarjeta = pd.read_sql_query("SELECT * FROM pagos_tarjeta", conn)
    df_pagos_tarjeta["monto"] = pd.to_numeric(df_pagos_tarjeta["monto"], errors="coerce")

    tarjetas_mes = df_pagos_tarjeta[df_pagos_tarjeta["mes"] == mes_actual]
    tarjetas_pendientes = tarjetas_mes[tarjetas_mes["pagado"] == 0]
    tarjetas_pagadas = tarjetas_mes[tarjetas_mes["pagado"] == 1]

    total_tarjetas_pendientes_mes = tarjetas_pendientes["monto"].sum()
    total_tarjetas = tarjetas_pagadas["monto"].sum()
    deuda_tarjetas = df_pagos_tarjeta[df_pagos_tarjeta["pagado"] == 0]["monto"].sum()

# ----------- TOTALES ----------- #
    total_pagado_debito = total_gastos + total_prestamos + total_tarjetas
    total_gasto_mes = total_pagado_debito + total_gastos_tarjeta_pagados
    total_pendiente_mes = total_gastos_pendientes + total_prestamos_pendientes_mes + total_tarjetas_pendientes_mes + total_gastos_tarjeta_pendientes
    total_pendiente_mes_sin_tarjeta = total_gastos_pendientes + total_prestamos_pendientes_mes + total_tarjetas_pendientes_mes

# ----------- VISUALIZACIÓN ----------- #
    st.subheader("🟢 Totales Pendientes del Mes")

    if total_gastos_pendientes > 0:
        st.error(f"🧾 Gastos pendientes (efectivo/transferencia): ${total_gastos_pendientes:,.0f}")
    else:
        st.success("🧾 Gastos pendientes (efectivo/transferencia): $0")

    if total_gastos_tarjeta_pendientes > 0:
        st.error(f"💳 Gastos pagados con tarjeta (pendientes): ${total_gastos_tarjeta_pendientes:,.0f}")
    else:
        st.success("💳 Gastos pagados con tarjeta (pendientes): $0")

    if total_prestamos_pendientes_mes > 0:
        st.error(f"🏦 Cuotas de préstamos por pagar: ${total_prestamos_pendientes_mes:,.0f}")
    else:
        st.success("🏦 Cuotas de préstamos por pagar: $0")

    if total_tarjetas_pendientes_mes > 0:
        st.error(f"💳 Facturado de tarjetas por pagar: ${total_tarjetas_pendientes_mes:,.0f}")
    else:
        st.success("💳 Facturado de tarjetas por pagar: $0")

    st.warning(f"💰 **Total pendiente del mes (Pago solo Efectivo/Débito):** ${total_pendiente_mes_sin_tarjeta:,.0f}")
    st.warning(f"💰 **Total pendiente del mes (incluye pago con tarjetas de crédito):** ${total_pendiente_mes:,.0f}")
    
 # ----------- SUELDO Y SALDO DISPONIBLE ------------------------------------------------------------------------------------#
    st.markdown("### 💼 Estado del Sueldo del Mes")

    df_sueldo = pd.read_sql_query(
        "SELECT monto FROM sueldos WHERE mes = ? AND anio = ?",
        conn,
        params=(mes_actual, anio_actual)
    )

    if not df_sueldo.empty:
        sueldo_mes = df_sueldo.iloc[0]["monto"]
        saldo_disponible = sueldo_mes - total_pendiente_mes_sin_tarjeta

        st.info(f"💰 **Sueldo registrado:** ${sueldo_mes:,.0f}")

        if saldo_disponible >= 0:
            st.success(f"📊 **Saldo disponible después de pagar (efectivo/débito):** ${saldo_disponible:,.0f}")
        else:
            st.error(f"❗Tu sueldo es insuficiente. Te faltarían ${abs(saldo_disponible):,.0f}")

        st.markdown("#### 📈 Porcentaje del sueldo comprometido")
        if sueldo_mes > 0:
            porcentaje_gastado = (total_pendiente_mes_sin_tarjeta / sueldo_mes)
            st.progress(min(porcentaje_gastado, 1.0), text=f"{porcentaje_gastado*100:.1f}% del sueldo comprometido")
        else:
            st.info("No se puede calcular la barra de progreso sin sueldo registrado.")
    else:
        st.warning("⚠️ No se ha registrado sueldo para este mes. Puedes hacerlo desde el menú '💼 Ingresar - Sueldo'")    
        
#-------------------------------------------------------------------------------------------------------------------------------------#      
    
    st.markdown("---")

    st.subheader(f"📅 Resumen Financiero del Mes de {mes_nombre}")
    col1, col2, col3 = st.columns(3)
    col1.metric("💸 Total Gastos Pagados", f"${total_gastos:,.0f}")
    col2.metric("🏦 Cuotas de Préstamos Pagadas", f"${total_prestamos:,.0f}")
    col3.metric("💳 Pagos de Tarjetas Realizados", f"${total_tarjetas:,.0f}")
    
    st.success(f"✅ Total Pagado Débito del mes: ${total_pagado_debito:,.0f}")
    st.info(f"💳 Total Gastos Pagados con Tarjeta: ${total_gastos_tarjeta_pagados:,.0f}")
    st.warning(f"📊 Total Gasto del Mes: ${total_gasto_mes:,.0f}")

    st.markdown("### 📌 Información Complementaria")
    st.markdown(f"**Deuda restante en préstamos:** ${total_deuda_prestamos:,.0f}")

    if not vencimientos_esporadicos.empty:
        st.markdown("#### 📅 Vencimientos próximos de gastos esporádicos")
        st.dataframe(vencimientos_esporadicos)


    
# mostar detalle de gastos
    with st.expander("🔍 Ver detalles de gastos"):
        if not df_gastos.empty:
            df_detalle = df_gastos.copy()

            # Cargar nombres de tarjeta
            tarjetas_df = pd.read_sql_query("SELECT id, nombre FROM tarjetas_credito", conn)
            tarjeta_dict = dict(zip(tarjetas_df["id"], tarjetas_df["nombre"]))
            df_detalle["tarjeta_id"] = df_detalle["tarjeta_id"].map(tarjeta_dict)
            df_detalle.rename(columns={"tarjeta_id": "Nombre Tarjeta"}, inplace=True)

# Agregar nombre del mes contable -------------------------------------------------------#
            meses_dict = {
                1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
                5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
                9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
            }
            df_detalle["Mes Cargo"] = df_detalle["mes_contable"].map(meses_dict)

# Renombrar columnas visibles --------------------------------------------------------------------#
            df_detalle.rename(columns={
                "nombre": "Nombre",
                "valor": "Monto a Pagar",
                "tipo": "Tipo de Gasto",
                "fecha_vencimiento": "Fecha",
                "recurrente": "Pago Periódico",
                "pagado_con_tarjeta": "Pagada con Crédito",
                "fecha_pago": "Fecha de Pago"
            }, inplace=True)

# Formatear valores booleanos
            df_detalle["Pagada con Crédito"] = df_detalle["Pagada con Crédito"].replace({1: "💳 Sí", 0: "No"})
            df_detalle["Pago Periódico"] = df_detalle["Pago Periódico"].replace({1: "Sí", 0: "No"})

# Eliminar columnas no deseadas
            columnas_ocultar = ["id", "mes", "pagado", "cuotas", "marca_tarjeta", "anio_contable", "mes_contable"]
            df_detalle.drop(columns=[c for c in columnas_ocultar if c in df_detalle.columns], inplace=True)

# Reordenar columnas
            columnas_orden = ["Nombre", "Monto a Pagar", "Tipo de Gasto", "Nombre Tarjeta", "Fecha", "Fecha de Pago", "Pago Periódico", "Pagada con Crédito", "Mes Cargo"]
            df_detalle = df_detalle[columnas_orden]

            df_detalle.reset_index(drop=True, inplace=True)
            st.dataframe(df_detalle, use_container_width=True, hide_index=True)
        else:
            st.info("No hay gastos registrados para este mes.")
            
# mostar detalle de prestamos ------------------------------------------------------#

    with st.expander("🔍 Ver detalles de préstamos"):
        df_prestamos_detalle = df_prestamos[["nombre", "entidad", "valor_cuota", "cuotas_pagadas", "deuda_restante"]].copy()
        df_prestamos_detalle.rename(columns={
            "nombre": "Nombre Asignado",
            "entidad": "Banco Préstamo",
            "valor_cuota": "Valor Mensual",
            "cuotas_pagadas": "Cantidad Cuotas Pagadas",
            "deuda_restante": "Deuda Pendiente"
        }, inplace=True)
        df_prestamos_detalle.reset_index(drop=True, inplace=True)
        st.dataframe(df_prestamos_detalle, use_container_width=True, hide_index=True)
        
# mostar detalle de facturacion a credito ---------------------------------------------------#

    with st.expander("🔍 Ver detalles de Facturación de tarjetas de crédito"):
        df_tarjetas = pd.read_sql_query("SELECT id, nombre FROM tarjetas_credito", conn)
        tarjetas_detalle = tarjetas_mes.merge(df_tarjetas, left_on="tarjeta_id", right_on="id", how="left")
        tarjetas_detalle["Pagado"] = tarjetas_detalle["pagado"].apply(lambda x: "Sí" if x == 1 else "No")
        tarjetas_vista = tarjetas_detalle.rename(columns={
            "nombre": "Nombre tarjeta",
            "monto": "Monto facturado",
            "fecha_pago": "Fecha de Pago"
        })
        columnas_mostrar = ["Nombre tarjeta", "Monto facturado", "Pagado", "Fecha de Pago"]
        tarjetas_vista = tarjetas_vista[columnas_mostrar].reset_index(drop=True)
        st.dataframe(tarjetas_vista, use_container_width=True, hide_index=True)



if __name__ == "__main__":
    dashboard()