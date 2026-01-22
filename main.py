import os
import shutil
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

# Ruta base relativa para el proyecto GPS-SPOOFING
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Obtiene la ruta del script
RUTA_FILE = ""
CSV_FILE_NAME = ""  # Variable para almacenar el nombre del archivo CSV

# Función para abrir un archivo HTML en el navegador
def open_html_file(filename):
    filepath = os.path.join(BASE_DIR, filename)
    subprocess.run(["xdg-open", filepath])

# Función para elegir un archivo de ruta y copiarlo a la carpeta deseada
def select_route_file():
    global RUTA_FILE, CSV_FILE_NAME  # Declarar que vamos a usar las variables globales
    ruta_file = filedialog.askopenfilename(
        title="Selecciona el archivo CSV de ruta",
        filetypes=[("Archivos CSV", "*.csv")],
        initialdir=os.path.join(BASE_DIR, "rutas-save")  # Carpeta por defecto
    )
    if ruta_file:
        rutas_dir = os.path.join(BASE_DIR, "rutas")
        try:
            # Borrar los archivos existentes en la carpeta rutas
            for f in os.listdir(rutas_dir):
                file_path = os.path.join(rutas_dir, f)
                if os.path.isfile(file_path):
                    os.remove(file_path)  # Borrar el archivo
            # Copiar el archivo seleccionado a la carpeta de rutas
            shutil.copy(ruta_file, rutas_dir)
            RUTA_FILE = os.path.join(rutas_dir, os.path.basename(ruta_file))  # Actualizar la variable global
            CSV_FILE_NAME = os.path.basename(ruta_file).split('.')[0]  # Obtener solo el nombre sin la extensión
            ruta_label.config(text=f"Ruta seleccionada: {os.path.basename(ruta_file)}")
        except Exception as e:
            messagebox.showerror("Error", f"Hubo un error al manejar las rutas: {e}")

# Función para ejecutar el script de automatización de efemérides
def download_efemides():
    try:
        # Ejecutar el script 'automateCDDIS.py' desde el directorio base
        process = subprocess.Popen(
            ["python3", os.path.join(BASE_DIR, "automateCDDIS.py")], 
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()

        if process.returncode == 0:
            log_output.config(state=tk.NORMAL)
            log_output.delete(1.0, tk.END)
            log_output.insert(tk.END, stdout.decode())
            log_output.config(state=tk.DISABLED)
            messagebox.showinfo("Éxito", "Efemérides descargadas correctamente.")
        else:
            log_output.config(state=tk.NORMAL)
            log_output.delete(1.0, tk.END)
            log_output.insert(tk.END, stderr.decode())
            log_output.config(state=tk.DISABLED)
            messagebox.showerror("Error", "Hubo un error al descargar las efemérides.")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {e}")

# Función para obtener el archivo de efemérides de la carpeta
def get_efemides_file():
    efem_dir = os.path.join(BASE_DIR, "efemerides")
    files = [f for f in os.listdir(efem_dir) if os.path.isfile(os.path.join(efem_dir, f))]
    
    if len(files) == 1:
        return os.path.join(efem_dir, files[0])  # Retorna la ruta del único archivo
    elif len(files) == 0:
        messagebox.showerror("Error", "No se encontraron archivos de efemérides en la carpeta.")
        return None
    else:
        messagebox.showerror("Error", "Se encontraron múltiples archivos de efemérides. Solo debe haber uno.")
        return None

# Función para iniciar la generación del archivo con el simulador GPS
def start_simulation():
    global RUTA_FILE, CSV_FILE_NAME  # Referenciar las variables globales

    if not RUTA_FILE or not os.path.exists(RUTA_FILE):
        messagebox.showerror("Error", "No se ha seleccionado un archivo de ruta válido.")
        return

    efem_file = get_efemides_file()
    if not efem_file:
        return

    custom_output_name = f"{CSV_FILE_NAME}_simulacion"
    output_format = format_var.get()
    output_dir = output_folder_entry.get() or os.path.join(BASE_DIR, "gps-sdr-sim")

    output_file = os.path.join(output_dir, f"{custom_output_name}.{output_format}")

    # Comando para ejecutar el simulador
    base_dir = os.path.join(BASE_DIR, "gps-sdr-sim")
    command = [
        os.path.join(base_dir, "gps-sdr-sim"),
        "-e", efem_file,
        "-x", RUTA_FILE,
        "-s", "2600000",  # Frecuencia
        "-b", "8",        # Banda
        "-d", "300",      # Duración
        "-o", output_file
    ]

    try:
        subprocess.run(command, check=True)
        messagebox.showinfo("Éxito", f"Simulación completada: {output_file}")

        if output_dir != os.path.join(BASE_DIR, "gps-sdr-sim"):
            shutil.copy(output_file, output_dir)
            os.remove(output_file)  # Borrar archivo original de la carpeta por defecto
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Hubo un error al ejecutar el simulador: {e}")

    # Abrir GNU Radio si se seleccionó la opción
    if open_grc_check.get():
        open_grc_file()

def open_grc_file():
    grc_file = "/home/ado/Escritorio/GPS-SPOOFING/gps-sdr-sim/GPSsimulator.grc"
    try:
        subprocess.run(["gnuradio-companion", grc_file], check=True)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"No se pudo abrir el archivo de GNU Radio: {e}")

# Crear la interfaz gráfica con Tkinter
root = tk.Tk()
root.title("Simulador GPS")

# Crear frames con padding
frame1 = tk.Frame(root)
frame1.pack(padx=20, pady=10, fill="x")

frame2 = tk.Frame(root)
frame2.pack(padx=20, pady=10, fill="x")

frame3 = tk.Frame(root)
frame3.pack(padx=20, pady=10, fill="x")

# Parte de generar rutas
create_route_label = tk.Label(frame1, text="Generar Ruta", font=("Arial", 14))
create_route_label.pack(pady=10)

create_route_button1 = tk.Button(frame1, text="Crear Ruta Libre", command=lambda: open_html_file("CalculaPuntosVelocidad.html"))
create_route_button1.pack(pady=5)

create_route_button2 = tk.Button(frame1, text="Crear Ruta por Carretera", command=lambda: open_html_file("CalculaPuntosVelocidadV2.html"))
create_route_button2.pack(pady=5)

# Parte de selección de formato y ruta
select_route_button = tk.Button(frame2, text="Seleccionar Archivo de Ruta", command=select_route_file)
select_route_button.pack(pady=10)

ruta_label = tk.Label(frame2, text="Ruta seleccionada: Ninguna", font=("Arial", 10))
ruta_label.pack(pady=5)

format_label = tk.Label(frame2, text="Selecciona formato de salida:", font=("Arial", 10))
format_label.pack(pady=10)

# Colocar botones de formato en una fila horizontal
format_var = tk.StringVar(value="bin")
format_frame = tk.Frame(frame2)
format_frame.pack(pady=5)

format_radio_bin = tk.Radiobutton(format_frame, text=".bin", variable=format_var, value="bin")
format_radio_bin.pack(side="left", padx=5)

format_radio_c8 = tk.Radiobutton(format_frame, text=".c8", variable=format_var, value="c8")
format_radio_c8.pack(side="left", padx=5)

# Parte de descarga de efemérides
download_button = tk.Button(frame3, text="Descargar Efemérides", command=download_efemides)
download_button.pack(pady=10)

log_output = tk.Text(frame3, height=10, width=60, state=tk.DISABLED)
log_output.pack(pady=5)

# Parte de opciones adicionales
output_folder_label = tk.Label(frame3, text="Carpeta de salida:", font=("Arial", 10))
output_folder_label.pack(pady=5)

output_folder_entry = tk.Entry(frame3)
output_folder_entry.insert(0, os.path.join(BASE_DIR, "gps-sdr-sim"))
output_folder_entry.pack(pady=5)

open_grc_check = tk.BooleanVar()
open_grc_check_button = tk.Checkbutton(frame3, text="Abrir GNU Radio", variable=open_grc_check)
open_grc_check_button.pack(pady=10)

start_button = tk.Button(frame3, text="Iniciar Simulación", command=start_simulation)
start_button.pack(pady=10)

# Ejecutar la interfaz gráfica
root.mainloop()

