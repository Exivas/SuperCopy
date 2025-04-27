import tkinter as tk
from tkinter import filedialog, messagebox
import shutil
import os
import json
import threading
from PIL import Image, ImageDraw
import pystray
import keyboard 

# ---------------------- CONFIGURACIÓN INICIAL ----------------------
BASE_DIR = os.path.dirname(__file__)
DB_DIR = os.path.join(BASE_DIR, "db")
RUTAS_GUARDADAS = os.path.join(DB_DIR, "database.json")
os.makedirs(DB_DIR, exist_ok=True)


if not os.path.exists(RUTAS_GUARDADAS) or os.stat(RUTAS_GUARDADAS).st_size == 0:
    with open(RUTAS_GUARDADAS, "w") as f:
        json.dump([], f)

# ---------------------- FUNCIONES PRINCIPALES ----------------------
def seleccionar_archivo():
    ruta = filedialog.askopenfilename()
    if ruta:
        entrada_archivo.delete(0, tk.END)
        entrada_archivo.insert(0, ruta)

def seleccionar_destino():
    destino = filedialog.askdirectory()
    if destino:
        entrada_destino.delete(0, tk.END)
        entrada_destino.insert(0, destino)

def copiar_archivo():
    archivo = entrada_archivo.get()
    destino = entrada_destino.get()
    if not archivo or not destino:
        messagebox.showwarning("Faltan datos", "Selecciona un archivo y una carpeta de destino.")
        return
    try:
        nombre_archivo = os.path.basename(archivo)
        ruta_destino = os.path.join(destino, nombre_archivo)
        shutil.copy2(archivo, ruta_destino)
        messagebox.showinfo("Éxito", f"Archivo copiado a:\n{ruta_destino}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo copiar el archivo:\n{e}")

def limpiar_campos():
    entrada_archivo.delete(0, tk.END)
    entrada_destino.delete(0, tk.END)

def guardar_rutas():
    archivo = entrada_archivo.get()
    destino = entrada_destino.get()
    if not archivo or not destino:
        messagebox.showwarning("Faltan datos", "No puedes guardar rutas vacías.")
        return
    rutas = cargar_rutas()
    rutas.append({"archivo": archivo, "destino": destino})
    with open(RUTAS_GUARDADAS, "w") as f:
        json.dump(rutas, f, indent=2)
    messagebox.showinfo("Guardado", "Rutas guardadas correctamente.")
    actualizar_lista_guardadas()

def cargar_rutas():
    if os.path.exists(RUTAS_GUARDADAS):
        try:
            with open(RUTAS_GUARDADAS, "r") as f:
                contenido = f.read().strip()
                if contenido:
                    return json.loads(contenido)
        except json.JSONDecodeError:
            messagebox.showwarning("Advertencia", "El archivo de rutas está dañado. Se cargará vacío.")
    return []

def usar_ruta_guardada(event):
    seleccion = lista_guardadas.curselection()
    if seleccion:
        index = seleccion[0]
        ruta = rutas_guardadas[index]
        entrada_archivo.delete(0, tk.END)
        entrada_archivo.insert(0, ruta["archivo"])
        entrada_destino.delete(0, tk.END)
        entrada_destino.insert(0, ruta["destino"])

def actualizar_lista_guardadas():
    global rutas_guardadas
    rutas_guardadas = cargar_rutas()
    lista_guardadas.delete(0, tk.END)
    for i, ruta in enumerate(rutas_guardadas):
        nombre = os.path.basename(ruta["archivo"])
        lista_guardadas.insert(tk.END, f"{i+1}. {nombre} → {ruta['destino']}")

def limpiar_rutas_guardadas():
    if messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres borrar todas las rutas guardadas?"):
        with open(RUTAS_GUARDADAS, "w") as f:
            json.dump([], f)
        actualizar_lista_guardadas()
        messagebox.showinfo("Limpieza", "Rutas guardadas eliminadas.")

# ---------------------- BANDEJA DEL SISTEMA ----------------------
def crear_icono_bandeja():
    def crear_icono():
        imagen = Image.new('RGB', (64, 64), (0, 0, 0))
        draw = ImageDraw.Draw(imagen)
        draw.rectangle((16, 16, 48, 48), fill="green")
        return imagen

    def mostrar_ventana(icono, item):
        ventana.after(0, ventana.deiconify)

    def salir(icono, item):
        icono.stop()
        ventana.destroy()

    icono = pystray.Icon("supercopy")
    icono.icon = crear_icono()
    icono.menu = pystray.Menu(
        pystray.MenuItem("Mostrar", mostrar_ventana),
        pystray.MenuItem("Salir", salir)
    )
    icono.run()

def minimizar_a_bandeja():
    ventana.withdraw()
    threading.Thread(target=crear_icono_bandeja, daemon=True).start()
    
# ---------------------- CONFIGURACIÓN DE TECLAS GLOBALES ----------------------
def configurar_atajo_teclado():
    keyboard.add_hotkey('ctrl+shift+c', copiar_archivo)


# ---------------------- INTERFAZ ----------------------
ventana = tk.Tk()
ventana.title("Copiar archivo")
ventana.geometry("600x450")
ventana.resizable(False, False)

# Configurar el atajo de teclado global
configurar_atajo_teclado()

ventana.protocol("WM_DELETE_WINDOW", minimizar_a_bandeja)

tk.Label(ventana, text="Archivo origen:").pack()
entrada_archivo = tk.Entry(ventana, width=70)
entrada_archivo.pack()
tk.Button(ventana, text="Buscar archivo", command=seleccionar_archivo).pack(pady=2)

tk.Label(ventana, text="Carpeta de destino:").pack()
entrada_destino = tk.Entry(ventana, width=70)
entrada_destino.pack()
tk.Button(ventana, text="Seleccionar carpeta", command=seleccionar_destino).pack(pady=2)


frame_botones = tk.Frame(ventana)
frame_botones.pack(pady=10)
tk.Button(frame_botones, text="Copiar archivo", command=copiar_archivo, bg="green", fg="white").grid(row=0, column=0, padx=5)
tk.Button(frame_botones, text="Limpiar", command=limpiar_campos).grid(row=0, column=1, padx=5)
tk.Button(frame_botones, text="Guardar ruta", command=guardar_rutas).grid(row=0, column=2, padx=5)

tk.Label(ventana, text="Rutas guardadas:").pack()
lista_guardadas = tk.Listbox(ventana, width=80, height=6)
lista_guardadas.pack()
lista_guardadas.bind('<<ListboxSelect>>', usar_ruta_guardada)

tk.Button(ventana, text="Limpiar rutas guardadas", command=limpiar_rutas_guardadas, bg="red", fg="white").pack(pady=5)

actualizar_lista_guardadas()
ventana.mainloop()
