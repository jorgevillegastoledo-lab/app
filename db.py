import sqlite3
import os

def conectar_db():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "basededatos.db")
    return sqlite3.connect(db_path, check_same_thread=False)

def crear_tablas():
    conn = conectar_db()
    cursor = conn.cursor()

    # Tabla: prestamos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prestamos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            entidad TEXT,
            valor_cuota REAL NOT NULL,
            cuotas_totales INTEGER NOT NULL,
            cuotas_pagadas INTEGER NOT NULL,
            estado TEXT,
            fecha_pago DATE,
            pagado INTEGER DEFAULT 0,
            monto_total INTEGER,
            deuda_restante REAL DEFAULT 0
        )
    ''')

    # Tabla: gastos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            valor REAL NOT NULL,
            tipo TEXT CHECK(tipo IN ('Básico', 'Otro')),
            tarjeta_id INTEGER,
            fecha_vencimiento DATE,
            mes INTEGER,
            pagado INTEGER DEFAULT 0,
            fecha_pago DATE,
            cuotas INTEGER DEFAULT 0,
            recurrente INTEGER DEFAULT 0,
            pagado_con_tarjeta INTEGER DEFAULT 0,
            anio_contable INTEGER,
            mes_contable INTEGER
        )
    ''')

    # Tabla: tarjetas_credito
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tarjetas_credito (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            tipo TEXT CHECK(tipo IN ('Crédito', 'Débito')),
            cierre_facturacion INTEGER
        )
    ''')

    # Tabla: pagos_prestamo
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pagos_prestamo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prestamo_id INTEGER,
            numero_cuota INTEGER,
            fecha_pago DATE,
            valor_cuota REAL,
            mes_contable INTEGER,
            anio_contable INTEGER,
            mes INTEGER
        )
    ''')

    # Tabla: pagos_tarjeta
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pagos_tarjeta (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarjeta_id INTEGER NOT NULL,
            monto REAL NOT NULL,
            pagado INTEGER DEFAULT 0,
            fecha_pago TEXT,
            mes INTEGER NOT NULL,
            anio_contable INTEGER,
            mes_contable INTEGER
        )
    ''')

    # Eliminar tabla obsoleta si existiera (opcional)
    cursor.execute('DROP TABLE IF EXISTS compras_tarjeta')

    conn.commit()
    conn.close()
