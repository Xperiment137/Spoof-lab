import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import shutil
import gzip
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from requests.exceptions import ChunkedEncodingError, RequestException

# Base URL del servidor
BASE_URL = "https://cddis.nasa.gov/archive/gnss/data/daily/"

# Token de acceso (reemplázalo con tu token OAuth)
ACCESS_TOKEN = ""

# Crear sesión con reintentos
SESSION = requests.Session()
retries = Retry(
    total=5,  # número de reintentos
    backoff_factor=0.5,  # espera incremental entre reintentos
    status_forcelist=[500, 502, 503, 504]  # códigos HTTP que disparan reintento
)
adapter = HTTPAdapter(max_retries=retries)
SESSION.mount("http://", adapter)
SESSION.mount("https://", adapter)

# Añadir el token OAuth en las cabeceras
SESSION.headers.update({"Authorization": f"Bearer {ACCESS_TOKEN}"})


def get_latest_directory(url):
    """Devuelve el último subdirectorio (ordenado alfabéticamente)"""
    try:
        # Desactivar streaming y poner timeout para evitar ChunkedEncodingError
        resp = SESSION.get(url, stream=False, timeout=10)
        resp.raise_for_status()
    except (ChunkedEncodingError, RequestException) as e:
        print(f"Error al acceder a {url}: {e}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")
    dirs = [
        a['href'].strip('/')
        for a in soup.find_all('a', href=True)
        if a['href'].strip('/').isdigit()
    ]
    return sorted(dirs)[-1] if dirs else None

def clean_folder(folder_path):
    """Elimina todo el contenido de la carpeta (si existe)"""
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"No se pudo eliminar {file_path}: {e}")
    else:
        os.makedirs(folder_path)

def download_and_extract_brdc_file(year, doy, subfolder='25n'):
    yy = str(year)[-2:]
    doy_str = f"{int(doy):03d}"
    filename = f"brdc{doy_str}0.{yy}n.gz"
    file_url = urljoin(BASE_URL, f"{year}/{doy_str}/{subfolder}/{filename}")

    print(f"Intentando descargar: {file_url}")

    folder = "efemerides"
    clean_folder(folder)

    gz_path = os.path.join(folder, filename)
    extracted_path = gz_path[:-3]  # Quita .gz para dejar el archivo .n

    try:
        resp = SESSION.get(file_url, stream=True, timeout=30)
        resp.raise_for_status()
    except RequestException as e:
        print(f"No se pudo descargar el archivo: {e}")
        return

    # Descargar archivo en chunks
    with open(gz_path, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    print(f"Archivo descargado en: {gz_path}")

    # Descomprimir
    with gzip.open(gz_path, 'rb') as f_in, open(extracted_path, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
    print(f"Archivo descomprimido en: {extracted_path}")

    # Eliminar archivo .gz
    os.remove(gz_path)
    print("Archivo .gz eliminado después de descomprimir.")

def main():
    print("Obteniendo año más reciente...")
    latest_year = get_latest_directory(BASE_URL)
    if not latest_year:
        print("No se encontró ningún año.")
        return

    print(f"Año más reciente: {latest_year}")

    year_url = urljoin(BASE_URL, f"{latest_year}/")
    print("Obteniendo día más reciente...")
    latest_doy = get_latest_directory(year_url)
    if not latest_doy:
        print("No se encontró ningún DOY.")
        return

    print(f"Último DOY disponible: {latest_doy}")
    print("Buscando y descargando efemérides más recientes...")

    download_and_extract_brdc_file(latest_year, latest_doy)

if __name__ == "__main__":
    main()

