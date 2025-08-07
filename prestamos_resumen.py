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

def prestamos_resumen(conn):
    st.set_page_config(layout="wide")
    aplicar_estilos()

    st.title("📄 Resumen de Préstamos")

    # Obtener datos de préstamos
    df_prestamos = pd.read_sql_query("SELECT * FROM prestamos", conn)

    if df_prestamos.empty:
        st.info("No hay préstamos registrados.")
        return

    # ⚠️ Conversión segura a tipo numérico
    df_prestamos["valor_cuota"] = pd.to_numeric(df_prestamos["valor_cuota"], errors='coerce').fillna(0)
    df_prestamos["cuotas_pagadas"] = pd.to_numeric(df_prestamos["cuotas_pagadas"], errors='coerce').fillna(0)
    df_prestamos["monto_total"] = pd.to_numeric(df_prestamos["monto_total"], errors='coerce').fillna(0)

    # Calcular columnas derivadas
    df_prestamos["pagado"] = df_prestamos["valor_cuota"] * df_prestamos["cuotas_pagadas"]
    df_prestamos["deuda_restante"] = df_prestamos["monto_total"] - df_prestamos["pagado"]

    # Obtener mes contable desde pagos
    df_pagos = pd.read_sql_query("SELECT * FROM pagos_prestamo", conn)
    df_pagos["fecha_pago"] = pd.to_datetime(df_pagos["fecha_pago"], errors='coerce')

    df_pagos["orden_contable"] = df_pagos["anio_contable"] * 100 + df_pagos["mes_contable"]
    idx_ultimos = df_pagos.groupby("prestamo_id")["orden_contable"].idxmax()
    df_ultimos_pagos = df_pagos.loc[idx_ultimos, ["prestamo_id", "mes_contable", "anio_contable"]]

    df_ultimos_pagos = df_ultimos_pagos.rename(columns={"mes_contable": "mes_pago", "anio_contable": "anio_pago"})
    df_prestamos = df_prestamos.merge(df_ultimos_pagos, left_on="id", right_on="prestamo_id", how="left")

    meses_dict = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
        7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }
    df_prestamos["Mes de Pago"] = df_prestamos["mes_pago"].map(meses_dict)

    # Mostrar tabla de resumen
    st.markdown("### 💰 Detalle de préstamos")
    st.dataframe(
        df_prestamos[[
            "id", "nombre", "entidad", "valor_cuota", "cuotas_totales",
            "cuotas_pagadas", "pagado", "deuda_restante", "estado", "Mes de Pago"
        ]].rename(columns={
            "id": "Identificador",
            "nombre": "Nombre",
            "entidad": "Entidad Financiera",
            "valor_cuota": "Valor Cuota",
            "cuotas_totales": "Cantidad de Cuotas",
            "cuotas_pagadas": "Cuotas Pagadas",
            "pagado": "Total Pagado",
            "deuda_restante": "Total Restante",
            "estado": "Estado"
        }),
        use_container_width=True,
        hide_index=True
    )

    # -----------------------------------------
    st.markdown("---")
    st.markdown("### 🧾 Registrar Pago de Cuota")

    prestamos_disponibles = df_prestamos["id"].astype(str) + " - " + df_prestamos["nombre"]
    seleccion = st.selectbox("Selecciona un préstamo:", prestamos_disponibles.tolist())

    id_seleccionado = int(seleccion.split(" - ")[0])
    mes_opciones = list(meses_dict.values())
    mes_nombre = st.selectbox("Selecciona el mes contable a aplicar:", mes_opciones)
    mes_num = list(meses_dict.keys())[mes_opciones.index(mes_nombre)]
    anio_actual = datetime.today().year
    anio_filtro = st.number_input("Año contable:", min_value=2020, max_value=2100, value=anio_actual, key="anio_filtro")

    if st.button("🔴 Registrar cuota como pagada"):
        df_pagos_existente = pd.read_sql_query(
            "SELECT * FROM pagos_prestamo WHERE prestamo_id = ? AND mes_contable = ? AND anio_contable = ?",
            conn,
            params=(id_seleccionado, mes_num, anio_filtro)
        )

        if not df_pagos_existente.empty:
            st.warning("⚠️ Ya existe un pago registrado para ese mes y préstamo.")
        else:
            prestamo = df_prestamos[df_prestamos["id"] == id_seleccionado].iloc[0]
            cuota_actual = prestamo["cuotas_pagadas"] + 1
            fecha_pago = datetime.today().date()
            valor_cuota = prestamo["valor_cuota"]

            conn.execute("""
                INSERT INTO pagos_prestamo (prestamo_id, numero_cuota, fecha_pago, valor_cuota, mes_contable, anio_contable, mes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (id_seleccionado, cuota_actual, fecha_pago, valor_cuota, mes_num, anio_filtro, mes_num))
            conn.commit()

            nuevo_total_pagado = cuota_actual * valor_cuota
            nueva_deuda = prestamo["monto_total"] - nuevo_total_pagado

            conn.execute("""
                UPDATE prestamos
                SET cuotas_pagadas = ?, pagado = ?, deuda_restante = ?
                WHERE id = ?
            """, (cuota_actual, nuevo_total_pagado, nueva_deuda, id_seleccionado))
            conn.commit()

            st.success("✅ Cuota registrada correctamente.")

    # -----------------------------------------
    st.markdown("---")
    st.markdown("### 📋 Historial de Pagos por Mes")

    mes_historial = st.selectbox("Mes contable:", list(meses_dict.values()), key="mes_historial")
    mes_historial_num = list(meses_dict.keys())[list(meses_dict.values()).index(mes_historial)]
    anio_historial = st.number_input("Año contable:", min_value=2020, max_value=2100, value=anio_actual, key="anio_historial")

    df_pagos = pd.read_sql_query("SELECT * FROM pagos_prestamo", conn)
    df_filtrado = df_pagos[
        (df_pagos["mes_contable"] == mes_historial_num) & 
        (df_pagos["anio_contable"] == anio_historial)
    ]

    if df_filtrado.empty:
        st.info("No hay pagos registrados en ese mes.")
    else:
        df_nombres = df_prestamos[["id", "nombre"]].rename(columns={"id": "prestamo_id", "nombre": "Nombre del Préstamo"})
        df_resultado = df_filtrado.merge(df_nombres, on="prestamo_id", how="left")
        df_resultado["Mes"] = df_resultado["mes_contable"].map(meses_dict)

        st.dataframe(df_resultado[[ 
            "id", "Nombre del Préstamo", "numero_cuota", "valor_cuota",
            "fecha_pago", "Mes", "anio_contable"
        ]].rename(columns={
            "id": "ID",
            "numero_cuota": "Cuota N°",
            "valor_cuota": "Valor",
            "fecha_pago": "Fecha de Pago",
            "anio_contable": "Año"
        }), use_container_width=True, hide_index=True)
