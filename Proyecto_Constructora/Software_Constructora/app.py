import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2

# ==========================================
# CONEXIÓN A LA BASE DE DATOS POSTGRESQL
# ==========================================
def conectar_db():
    try:
        conexion = psycopg2.connect(
            host="localhost",
            database="constructora_db",
            user="postgres",
            password="12345", # <--- CAMBIAR POR LA CONTRASEÑA REAL
            port="5432"
        )
        return conexion
    except Exception as e:
        messagebox.showerror("Error de Conexión", f"No se pudo conectar:\n{e}")
        return None

# Variables globales
id_obra_seleccionada = None
id_empleado_seleccionado = None

# ==========================================
# FUNCIONES DEL SISTEMA (Obras, Empleados, etc.)
# ==========================================
def cargar_obras():
    conexion = conectar_db()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT id_obra, nombre, direccion, estado FROM obra")
        filas = cursor.fetchall()
        for item in tabla_obras.get_children(): tabla_obras.delete(item)
        for fila in filas: tabla_obras.insert("", tk.END, values=fila)
        cursor.close()
        conexion.close()

def seleccionar_obra(event):
    global id_obra_seleccionada
    item = tabla_obras.selection()
    if item:
        valores = tabla_obras.item(item)['values']
        id_obra_seleccionada = valores[0]
        entry_nombre_obra.delete(0, tk.END)
        entry_nombre_obra.insert(0, valores[1])
        entry_direccion_obra.delete(0, tk.END)
        entry_direccion_obra.insert(0, valores[2])

def guardar_obra():
    nombre, direccion, id_tipo = entry_nombre_obra.get(), entry_direccion_obra.get(), combo_tipo_obra.get()
    if not nombre or not direccion or not id_tipo:
        messagebox.showwarning("Atención", "Todos los campos son obligatorios.")
        return
    id_tipo_obra = id_tipo.split(" - ")[0]
    conexion = conectar_db()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("INSERT INTO obra (nombre, direccion, fecha_inicio, id_tipo_obra, estado) VALUES (%s, %s, CURRENT_DATE, %s, 'En ejecución')", (nombre, direccion, id_tipo_obra))
            conexion.commit()
            messagebox.showinfo("Éxito", "Obra guardada.")
            limpiar_formulario_obra()
            cargar_obras()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cursor.close(); conexion.close()

def actualizar_obra():
    global id_obra_seleccionada
    if not id_obra_seleccionada: return
    conexion = conectar_db()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("UPDATE obra SET nombre=%s, direccion=%s WHERE id_obra=%s", (entry_nombre_obra.get(), entry_direccion_obra.get(), id_obra_seleccionada))
            conexion.commit()
            messagebox.showinfo("Éxito", "Obra actualizada.")
            limpiar_formulario_obra()
            cargar_obras()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cursor.close(); conexion.close()

def eliminar_obra():
    global id_obra_seleccionada
    if not id_obra_seleccionada: return
    if messagebox.askyesno("Confirmar", "¿Eliminar obra?"):
        conexion = conectar_db()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute("DELETE FROM obra WHERE id_obra=%s", (id_obra_seleccionada,))
                conexion.commit()
                messagebox.showinfo("Éxito", "Obra eliminada.")
                limpiar_formulario_obra()
                cargar_obras()
            except Exception as e:
                messagebox.showerror("Error", f"No se puede eliminar: {e}")
            finally:
                cursor.close(); conexion.close()

def limpiar_formulario_obra():
    global id_obra_seleccionada
    id_obra_seleccionada = None
    entry_nombre_obra.delete(0, tk.END)
    entry_direccion_obra.delete(0, tk.END)
    combo_tipo_obra.set("")

def cargar_empleados(filtro=""):
    conexion = conectar_db()
    if conexion:
        cursor = conexion.cursor()
        query = """
            SELECT e.id_empleado, e.nombre, e.apellido, e.dpi, t.id_tipo_empleado, t.nombre 
            FROM empleado e JOIN tipo_empleado t ON e.id_tipo_empleado = t.id_tipo_empleado
            WHERE e.nombre ILIKE %s OR e.apellido ILIKE %s
        """
        cursor.execute(query, (f'%{filtro}%', f'%{filtro}%'))
        filas = cursor.fetchall()
        for item in tabla_empleados.get_children(): tabla_empleados.delete(item)
        for fila in filas: 
            tabla_empleados.insert("", tk.END, values=(fila[0], fila[1], fila[2], fila[3], fila[5]))
        cursor.close()
        conexion.close()

def seleccionar_empleado(event):
    global id_empleado_seleccionado
    item = tabla_empleados.selection()
    if item:
        valores = tabla_empleados.item(item)['values']
        id_empleado_seleccionado = valores[0]
        entry_nombre_emp.delete(0, tk.END); entry_nombre_emp.insert(0, valores[1])
        entry_apellido_emp.delete(0, tk.END); entry_apellido_emp.insert(0, valores[2])
        entry_dpi_emp.delete(0, tk.END); entry_dpi_emp.insert(0, valores[3])
        combo_tipo_emp.set(valores[4]) 

def guardar_empleado():
    nombre, apellido, dpi, tipo = entry_nombre_emp.get(), entry_apellido_emp.get(), entry_dpi_emp.get(), combo_tipo_emp.get()
    if not nombre or not apellido or not dpi or not tipo:
        messagebox.showwarning("Atención", "Llene todos los campos.")
        return
    conexion = conectar_db()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT id_tipo_empleado FROM tipo_empleado WHERE nombre = %s", (tipo,))
            id_tipo = cursor.fetchone()[0]
            cursor.execute("INSERT INTO empleado (nombre, apellido, dpi, id_tipo_empleado) VALUES (%s, %s, %s, %s)", (nombre, apellido, dpi, id_tipo))
            conexion.commit()
            messagebox.showinfo("Éxito", "Empleado contratado.")
            limpiar_formulario_emp()
            cargar_empleados()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cursor.close(); conexion.close()

def actualizar_empleado():
    global id_empleado_seleccionado
    if not id_empleado_seleccionado: return
    conexion = conectar_db()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT id_tipo_empleado FROM tipo_empleado WHERE nombre = %s", (combo_tipo_emp.get(),))
            id_tipo = cursor.fetchone()[0]
            cursor.execute("UPDATE empleado SET nombre=%s, apellido=%s, dpi=%s, id_tipo_empleado=%s WHERE id_empleado=%s", 
                           (entry_nombre_emp.get(), entry_apellido_emp.get(), entry_dpi_emp.get(), id_tipo, id_empleado_seleccionado))
            conexion.commit()
            messagebox.showinfo("Éxito", "Empleado actualizado.")
            limpiar_formulario_emp()
            cargar_empleados()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cursor.close(); conexion.close()

def eliminar_empleado():
    global id_empleado_seleccionado
    if not id_empleado_seleccionado: return
    if messagebox.askyesno("Confirmar", "¿Despedir a este empleado?"):
        conexion = conectar_db()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute("DELETE FROM empleado WHERE id_empleado=%s", (id_empleado_seleccionado,))
                conexion.commit()
                messagebox.showinfo("Éxito", "Empleado eliminado.")
                limpiar_formulario_emp()
                cargar_empleados()
            except Exception as e:
                messagebox.showerror("Error", f"No se puede eliminar (tiene contratos o asignaciones): {e}")
            finally:
                cursor.close(); conexion.close()

def limpiar_formulario_emp():
    global id_empleado_seleccionado
    id_empleado_seleccionado = None
    entry_nombre_emp.delete(0, tk.END)
    entry_apellido_emp.delete(0, tk.END)
    entry_dpi_emp.delete(0, tk.END)
    combo_tipo_emp.set("")

def cargar_inventario():
    conexion = conectar_db()
    if conexion:
        cursor = conexion.cursor()
        query = """
            SELECT i.id_inventario, b.nombre, m.nombre, i.cantidad, m.unidad_medida, i.stock_minimo
            FROM inventario_bodega i JOIN bodega b ON i.id_bodega = b.id_bodega JOIN material m ON i.id_material = m.id_material
        """
        cursor.execute(query)
        filas = cursor.fetchall()
        for item in tabla_materiales.get_children(): tabla_materiales.delete(item)
        for fila in filas: tabla_materiales.insert("", tk.END, values=fila)
        cursor.close(); conexion.close()

def generar_reporte_gastos():
    conexion = conectar_db()
    if conexion:
        cursor = conexion.cursor()
        query = """
            SELECT o.nombre AS Obra, COALESCE(SUM(mb.cantidad * pm.precio), 0) AS Gasto
            FROM obra o LEFT JOIN area_trabajo a ON o.id_obra = a.id_obra
            LEFT JOIN movimiento_bodega mb ON a.id_area = mb.id_area AND mb.tipo = 'Egreso'
            LEFT JOIN precio_material pm ON mb.id_material = pm.id_material
            GROUP BY o.nombre ORDER BY Gasto DESC
        """
        cursor.execute(query)
        filas = cursor.fetchall()
        for item in tabla_reportes.get_children(): tabla_reportes.delete(item)
        for fila in filas: tabla_reportes.insert("", tk.END, values=(fila[0], f"Q. {float(fila[1]):,.2f}"))
        cursor.close(); conexion.close()

# ==========================================
# INTERFAZ PRINCIPAL (Se abre después del login)
# ==========================================
def abrir_sistema_principal():
    global ventana_principal, entry_nombre_obra, entry_direccion_obra, combo_tipo_obra, tabla_obras
    global entry_nombre_emp, entry_apellido_emp, entry_dpi_emp, combo_tipo_emp, tabla_empleados
    global tabla_materiales, tabla_reportes

    ventana_principal = tk.Tk()
    ventana_principal.title("Sistema de Gestión - Constructora")
    ventana_principal.geometry("1150x750")
    ventana_principal.configure(bg="#f0f0f0")

    tk.Label(ventana_principal, text="Constructora - Sistema de Base de Datos", font=("Arial", 20, "bold"), bg="#f0f0f0", fg="#2c3e50").pack(pady=15)

    notebook = ttk.Notebook(ventana_principal)
    notebook.pack(fill='both', expand=True, padx=20, pady=10)

    # --- PESTAÑA 1: OBRAS ---
    tab_obras = tk.Frame(notebook)
    notebook.add(tab_obras, text=" Obras ")
    frame_form_obra = tk.LabelFrame(tab_obras, text="Gestión de Obras", font=("Arial", 10, "bold"), bg="#f0f0f0")
    frame_form_obra.pack(fill="x", padx=20, pady=10)
    tk.Label(frame_form_obra, text="Nombre:", bg="#f0f0f0").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    entry_nombre_obra = tk.Entry(frame_form_obra, width=30); entry_nombre_obra.grid(row=0, column=1, padx=5, pady=5)
    tk.Label(frame_form_obra, text="Dirección:", bg="#f0f0f0").grid(row=0, column=2, padx=5, pady=5, sticky="e")
    entry_direccion_obra = tk.Entry(frame_form_obra, width=30); entry_direccion_obra.grid(row=0, column=3, padx=5, pady=5)
    tk.Label(frame_form_obra, text="Tipo:", bg="#f0f0f0").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    combo_tipo_obra = ttk.Combobox(frame_form_obra, width=28, state="readonly")
    combo_tipo_obra['values'] = ("1 - Casa habitacional", "2 - Edificio de oficinas", "3 - Edificio habitacional", "4 - Bodega"); combo_tipo_obra.grid(row=1, column=1, padx=5, pady=5)
    frame_botones_accion = tk.Frame(frame_form_obra, bg="#f0f0f0"); frame_botones_accion.grid(row=1, column=2, columnspan=2, pady=5)
    tk.Button(frame_botones_accion, text="Guardar", command=guardar_obra, bg="#008CBA", fg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=2)
    tk.Button(frame_botones_accion, text="Actualizar", command=actualizar_obra, bg="#FFC107", fg="black", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=2)
    tk.Button(frame_botones_accion, text="Eliminar", command=eliminar_obra, bg="#f44336", fg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=2)
    columnas_obras = ("ID", "Nombre", "Dirección", "Estado")
    tabla_obras = ttk.Treeview(tab_obras, columns=columnas_obras, show="headings")
    for col in columnas_obras: tabla_obras.heading(col, text=col); tabla_obras.column(col, width=200)
    tabla_obras.pack(fill='both', expand=True, padx=20, pady=10)
    tabla_obras.bind("<<TreeviewSelect>>", seleccionar_obra)

    # --- PESTAÑA 2: EMPLEADOS ---
    tab_empleados = tk.Frame(notebook)
    notebook.add(tab_empleados, text=" Empleados ")
    frame_form_emp = tk.LabelFrame(tab_empleados, text="Gestión de Empleados", font=("Arial", 10, "bold"), bg="#f0f0f0")
    frame_form_emp.pack(fill="x", padx=20, pady=10)
    tk.Label(frame_form_emp, text="Nombre:", bg="#f0f0f0").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    entry_nombre_emp = tk.Entry(frame_form_emp, width=20); entry_nombre_emp.grid(row=0, column=1, padx=5, pady=5)
    tk.Label(frame_form_emp, text="Apellido:", bg="#f0f0f0").grid(row=0, column=2, padx=5, pady=5, sticky="e")
    entry_apellido_emp = tk.Entry(frame_form_emp, width=20); entry_apellido_emp.grid(row=0, column=3, padx=5, pady=5)
    tk.Label(frame_form_emp, text="DPI:", bg="#f0f0f0").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    entry_dpi_emp = tk.Entry(frame_form_emp, width=20); entry_dpi_emp.grid(row=1, column=1, padx=5, pady=5)
    tk.Label(frame_form_emp, text="Tipo:", bg="#f0f0f0").grid(row=1, column=2, padx=5, pady=5, sticky="e")
    combo_tipo_emp = ttk.Combobox(frame_form_emp, width=18, state="readonly")
    combo_tipo_emp['values'] = ("Ingeniero Civil", "Arquitecto", "Albañil", "Personal Administrativo", "Maestro de Obra")
    combo_tipo_emp.grid(row=1, column=3, padx=5, pady=5)
    frame_botones_emp = tk.Frame(frame_form_emp, bg="#f0f0f0"); frame_botones_emp.grid(row=2, column=0, columnspan=4, pady=5)
    tk.Button(frame_botones_emp, text="Contratar", command=guardar_empleado, bg="#008CBA", fg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=5)
    tk.Button(frame_botones_emp, text="Actualizar", command=actualizar_empleado, bg="#FFC107", fg="black", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=5)
    tk.Button(frame_botones_emp, text="Despedir", command=eliminar_empleado, bg="#f44336", fg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=5)
    tk.Button(frame_botones_emp, text="Limpiar", command=limpiar_formulario_emp, bg="#9E9E9E", fg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=5)
    frame_buscador = tk.Frame(tab_empleados); frame_buscador.pack(pady=5)
    tk.Label(frame_buscador, text="Buscar:", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
    entrada_busqueda = tk.Entry(frame_buscador, width=30); entrada_busqueda.pack(side=tk.LEFT, padx=5)
    tk.Button(frame_buscador, text="Buscar", command=lambda: cargar_empleados(entrada_busqueda.get()), bg="#2196F3", fg="white").pack(side=tk.LEFT, padx=5)
    tk.Button(frame_buscador, text="Todos", command=lambda: [entrada_busqueda.delete(0, tk.END), cargar_empleados()], bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)
    columnas_emp = ("ID", "Nombre", "Apellido", "DPI", "Tipo")
    tabla_empleados = ttk.Treeview(tab_empleados, columns=columnas_emp, show="headings")
    for col in columnas_emp: tabla_empleados.heading(col, text=col); tabla_empleados.column(col, width=180)
    tabla_empleados.pack(fill='both', expand=True, padx=20, pady=10)
    tabla_empleados.bind("<<TreeviewSelect>>", seleccionar_empleado)

    # --- PESTAÑA 3: MATERIALES ---
    tab_materiales = tk.Frame(notebook)
    notebook.add(tab_materiales, text=" Materiales ")
    frame_botones_mat = tk.Frame(tab_materiales); frame_botones_mat.pack(pady=10)
    tk.Button(frame_botones_mat, text="Cargar Inventario", command=cargar_inventario, bg="#FF9800", fg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=5)
    columnas_mat = ("ID", "Bodega", "Material", "Cantidad", "Unidad", "Stock Mínimo")
    tabla_materiales = ttk.Treeview(tab_materiales, columns=columnas_mat, show="headings")
    for col in columnas_mat: tabla_materiales.heading(col, text=col); tabla_materiales.column(col, width=150)
    tabla_materiales.pack(fill='both', expand=True, padx=20, pady=10)

    # --- PESTAÑA 4: REPORTES ---
    tab_reportes = tk.Frame(notebook)
    notebook.add(tab_reportes, text=" Reporte de Gastos ")
    frame_rep = tk.Frame(tab_reportes); frame_rep.pack(pady=10)
    tk.Button(frame_rep, text="Generar Reporte de Gastos por Obra", command=generar_reporte_gastos, bg="#9C27B0", fg="white", font=("Arial", 10, "bold")).pack()
    columnas_rep = ("Obra", "Total Gasto en Materiales")
    tabla_reportes = ttk.Treeview(tab_reportes, columns=columnas_rep, show="headings", height=15)
    for col in columnas_rep: tabla_reportes.heading(col, text=col); tabla_reportes.column(col, width=300, anchor="center")
    tabla_reportes.pack(fill='both', expand=True, padx=20, pady=10)

    ventana_principal.after(100, cargar_obras)
    ventana_principal.after(100, cargar_empleados)
    ventana_principal.mainloop()


# ==========================================
# PANTALLA DE LOGIN (El filtro inicial)
# ==========================================
def verificar_login():
    usuario = entry_usuario.get()
    contrasena = entry_contrasena.get()

    # Aquí definimos el usuario y contraseña maestros
    if usuario == "admin" and contrasena == "admin123":
        ventana_login.destroy() # Cierra la ventana de login
        abrir_sistema_principal() # Abre el sistema completo
    else:
        messagebox.showerror("Error de Acceso", "Usuario o contraseña incorrectos.")

ventana_login = tk.Tk()
ventana_login.title("Login - Constructora")
ventana_login.geometry("350x250")
ventana_login.configure(bg="#2c3e50")
ventana_login.eval('tk::PlaceWindow . center') # Centra la ventana

tk.Label(ventana_login, text="Iniciar Sesión", font=("Arial", 16, "bold"), bg="#2c3e50", fg="white").pack(pady=20)

frame_login = tk.Frame(ventana_login, bg="#2c3e50")
frame_login.pack()

tk.Label(frame_login, text="Usuario:", font=("Arial", 10), bg="#2c3e50", fg="white").grid(row=0, column=0, pady=5, sticky="e")
entry_usuario = tk.Entry(frame_login, width=20)
entry_usuario.grid(row=0, column=1, pady=5)

tk.Label(frame_login, text="Contraseña:", font=("Arial", 10), bg="#2c3e50", fg="white").grid(row=1, column=0, pady=5, sticky="e")
entry_contrasena = tk.Entry(frame_login, width=20, show="*") # El show="*" oculta la contraseña
entry_contrasena.grid(row=1, column=1, pady=5)

tk.Button(ventana_login, text="Ingresar al Sistema", command=verificar_login, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), width=20).pack(pady=20)

ventana_login.mainloop()