import streamlit as st
import sqlite3
from estilos import aplicar_estilos
from db import conectar_db, crear_tablas  # Importamos ambas funciones
#from db import crear_tablas  # ⬅️ NUEVO

# Crear conexión global a la base de datos
# conn = sqlite3.connect("basededatos.db", check_same_thread=False)
#crear_tablas()  # ⬅️ NUEVO: crear las tablas si no existen


conn = conectar_db()
crear_tablas()

st.set_page_config(page_title="Finanzas", layout="wide")
aplicar_estilos()

# Bloquea toda la app hasta que haya login
if not require_login():
    st.stop()

# Menú principal
st.sidebar.title("📁 Menú Principal")

menu_principal = [
    "🏠 Dashboard",
    "📂 Gastos - Resumen",
    "🏦 Préstamos - Resumen",
    "💳 Tarjetas - Resumen",
    "💼 Ingresar - Sueldo"
]

# Selector principal
opcion_seleccionada = st.sidebar.radio("Ir a:", menu_principal)

# Submenú dinámico (sin mostrar Dashboard nuevamente)
if opcion_seleccionada == "📂 Gastos - Resumen":
    opciones = [
        "📂 Gastos - Resumen",
        "📂 Gastos - Nuevo",
        "📂 Gastos - Modificar"
    ]
elif opcion_seleccionada == "🏦 Préstamos - Resumen":
    opciones = [
        "🏦 Préstamos - Resumen",
        "🏦 Préstamos - Nuevo",
        "🏦 Préstamos - Modificar"
    ]
elif opcion_seleccionada == "💳 Tarjetas - Resumen":
    opciones = [
        "💳 Tarjetas - Resumen",
        "💳 Tarjetas - Nuevo",
        "💳 Tarjetas - Modificar",
        "💳 Tarjetas - Gestion"
    ]
else:
    opciones = []  # Si es Dashboard, no mostrar submenú

# Mostrar submenú solo si hay opciones adicionales
if opciones:
    opcion = st.sidebar.radio("Opciones disponibles:", opciones, index=0)
else:
    opcion = opcion_seleccionada  # ✅ Corregido: mantener la opción elegida

# Navegación a pantallas
if opcion == "🏠 Dashboard":
    from dashboard import dashboard
    dashboard()
elif opcion == "📂 Gastos - Nuevo":
    from gastos_nuevo import gastos_nuevo
    gastos_nuevo(conn)
elif opcion == "📂 Gastos - Resumen":
    from gastos_resumen import gastos_resumen
    gastos_resumen(conn)
elif opcion == "📂 Gastos - Modificar":
    from gastos_modificar import gastos_modificar
    gastos_modificar(conn)
elif opcion == "🏦 Préstamos - Nuevo":
    from prestamos_nuevo import prestamos_nuevo
    prestamos_nuevo(conn)
elif opcion == "🏦 Préstamos - Resumen":
    from prestamos_resumen import prestamos_resumen
    prestamos_resumen(conn)
elif opcion == "🏦 Préstamos - Modificar":
    from prestamos_modificar import prestamos_modificar
    prestamos_modificar(conn)
elif opcion == "💳 Tarjetas - Nuevo":
    from tarjetas_nuevo import tarjetas_nuevo
    tarjetas_nuevo(conn)
elif opcion == "💳 Tarjetas - Resumen":
    from tarjetas_resumen import tarjetas_resumen
    tarjetas_resumen(conn)
elif opcion == "💳 Tarjetas - Modificar":
    from tarjetas_modificar import tarjetas_modificar
    tarjetas_modificar(conn)
elif opcion == "💳 Tarjetas - Gestion":
    from tarjetas_gestion import tarjetas_gestion
    tarjetas_gestion(conn)
elif opcion == "💼 Ingresar - Sueldo":
    from sueldo_ingresar import sueldo_ingresar
    sueldo_ingresar(conn)