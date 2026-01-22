import os
import shutil
import subprocess
import csv
import tkinter as tk
from tkinter import filedialog, messagebox

# Base directory path for the GPS-SPOOFING project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the script's directory path
RUTA_FILE = ""
CSV_FILE_NAME = ""  # Variable to store the CSV file name

# Function to open an HTML file in the browser
def open_html_file(filename):
    filepath = os.path.join(BASE_DIR, filename)
    subprocess.run(["xdg-open", filepath])

# Function to select a route file and copy it to the desired folder
def select_route_file():
    global RUTA_FILE, CSV_FILE_NAME  # Declare that we will use the global variables
    ruta_file = filedialog.askopenfilename(
        title="Select Route CSV File",
        filetypes=[("CSV Files", "*.csv")],
        initialdir=os.path.join(BASE_DIR, "rutas-save")  # Default folder
    )
    if ruta_file:
        rutas_dir = os.path.join(BASE_DIR, "rutas")
        try:
            # Delete existing files in the "rutas" folder
            for f in os.listdir(rutas_dir):
                file_path = os.path.join(rutas_dir, f)
                if os.path.isfile(file_path):
                    os.remove(file_path)  # Delete the file
            # Copy the selected file to the "rutas" folder
            shutil.copy(ruta_file, rutas_dir)
            RUTA_FILE = os.path.join(rutas_dir, os.path.basename(ruta_file))  # Update the global variable
            CSV_FILE_NAME = os.path.basename(ruta_file).split('.')[0]  # Get the file name without extension
            ruta_label.config(text=f"Selected Route: {os.path.basename(ruta_file)}")
        except Exception as e:
            messagebox.showerror("Error", f"There was an error handling the route files: {e}")

# Function to download ephemerides
def download_efemides():
    try:
        # Run the 'automateCDDIS.py' script from the base directory
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
            messagebox.showinfo("Success", "Ephemerides downloaded successfully.")
        else:
            log_output.config(state=tk.NORMAL)
            log_output.delete(1.0, tk.END)
            log_output.insert(tk.END, stderr.decode())
            log_output.config(state=tk.DISABLED)
            messagebox.showerror("Error", "There was an error downloading the ephemerides.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Function to get coordinates from the CSV file
def get_coordinates_from_csv(csv_file):
    coordinates = []
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row:  # Ensure the row is not empty
                coordinates.append(row)  # Assume each row is a coordinate
    return coordinates

# Function to get the ephemerides file from the folder
def get_efemides_file():
    efem_dir = os.path.join(BASE_DIR, "efemerides")
    files = [f for f in os.listdir(efem_dir) if os.path.isfile(os.path.join(efem_dir, f))]
    
    if len(files) == 1:
        return os.path.join(efem_dir, files[0])  # Return the path of the only file
    elif len(files) == 0:
        messagebox.showerror("Error", "No ephemerides files found in the folder.")
        return None
    else:
        messagebox.showerror("Error", "Multiple ephemerides files found. Only one should exist.")
        return None

# Function to start the simulation with the GPS simulator
def start_simulation():
    global RUTA_FILE, CSV_FILE_NAME  # Referencing the global variables

    if not RUTA_FILE or not os.path.exists(RUTA_FILE):
        messagebox.showerror("Error", "No valid route file selected.")
        return

    efem_file = get_efemides_file()
    if not efem_file:
        return

    # Get coordinates from the CSV file
    coordinates = get_coordinates_from_csv(RUTA_FILE)

    custom_output_name = f"{CSV_FILE_NAME}_simulation"
    output_format = format_var.get()
    output_dir = output_folder_entry.get() or os.path.join(BASE_DIR, "gps-sdr-sim")

    output_file = os.path.join(output_dir, f"{custom_output_name}.{output_format}")

    # Base command to run the simulator
    base_dir = os.path.join(BASE_DIR, "gps-sdr-sim")
    command = [
        os.path.join(base_dir, "gps-sdr-sim"),
        "-e", efem_file,
        "-s", "2600000",  # Frequency
        "-b", "8",        # Band
        "-p",
        "-d", "300",      # Duration
        "-o", output_file
    ]

    # If there is only one coordinate, use the -l option
    if len(coordinates) == 1:
        coord = coordinates[0]  # Get the only coordinate
        command.extend(["-l", f"{coord[0]},{coord[1]}"])  # Assume the coordinate is in the first two columns (lat, lon)
    else:
        # If there are multiple coordinates, use the -x option with the CSV file
        command.extend(["-x", RUTA_FILE])

    try:
        subprocess.run(command, check=True)
        messagebox.showinfo("Success", f"Simulation completed: {output_file}")

        if output_dir != os.path.join(BASE_DIR, "gps-sdr-sim"):
            shutil.copy(output_file, output_dir)
            os.remove(output_file)  # Remove the original file from the default folder
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"There was an error running the simulator: {e}")

    # Open GNU Radio if the option is selected
    if open_grc_check.get():
        open_grc_file()

def open_grc_file():
    grc_file = "/home/ado/Escritorio/GPS-SPOOFING/gps-sdr-sim/GPSsimulator.grc"
    try:
        subprocess.run(["gnuradio-companion", grc_file], check=True)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Could not open the GNU Radio file: {e}")

# Create the GUI with Tkinter
root = tk.Tk()
root.title("GPS Simulator")

# Create frames with padding
frame1 = tk.Frame(root)
frame1.pack(padx=20, pady=10, fill="x")

frame2 = tk.Frame(root)
frame2.pack(padx=20, pady=10, fill="x")

frame3 = tk.Frame(root)
frame3.pack(padx=20, pady=10, fill="x")

# Route generation section
create_route_label = tk.Label(frame1, text="Generate Route", font=("Arial", 14))
create_route_label.pack(pady=10)

create_route_button1 = tk.Button(frame1, text="Create Free Route", command=lambda: open_html_file("CalculateSpeedPoints.html"))
create_route_button1.pack(pady=5)

create_route_button2 = tk.Button(frame1, text="Create Route by Road", command=lambda: open_html_file("CalculateSpeedPointsV2.html"))
create_route_button2.pack(pady=5)



# Route file selection and format section
select_route_button = tk.Button(frame2, text="Select Route File", command=select_route_file)
select_route_button.pack(pady=10)

ruta_label = tk.Label(frame2, text="Selected Route: None", font=("Arial", 10))
ruta_label.pack(pady=5)

format_label = tk.Label(frame2, text="Select Output Format:", font=("Arial", 10))
format_label.pack(pady=10)

# Place format buttons in a horizontal row
format_var = tk.StringVar(value="bin")
format_frame = tk.Frame(frame2)
format_frame.pack(pady=5)

format_radio_bin = tk.Radiobutton(format_frame, text=".bin", variable=format_var, value="bin")
format_radio_bin.pack(side="left", padx=5)

format_radio_c8 = tk.Radiobutton(format_frame, text=".C8", variable=format_var, value="c8")
format_radio_c8.pack(side="left", padx=5)

# Ephemerides download section
download_button = tk.Button(frame3, text="Download Ephemerides", command=download_efemides)
download_button.pack(pady=10)

log_output = tk.Text(frame3, height=10, width=60, state=tk.DISABLED)
log_output.pack(pady=5)

# Additional options section
output_folder_label = tk.Label(frame3, text="Output Folder:", font=("Arial", 10))
output_folder_label.pack(pady=5)

output_folder_entry = tk.Entry(frame3)
output_folder_entry.insert(0, os.path.join(BASE_DIR, "gps-sdr-sim"))
output_folder_entry.pack(pady=5)

open_grc_check = tk.BooleanVar()
open_grc_check_button = tk.Checkbutton(frame3, text="Open GNU Radio", variable=open_grc_check)
open_grc_check_button.pack(pady=10)

start_button = tk.Button(frame3, text="Start Simulation", command=start_simulation)
start_button.pack(pady=10)

# Run the GUI
root.mainloop()

