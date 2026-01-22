# GPS-Spoofing Simulator

Esta herramienta permite simular señales GPS. El simulador toma rutas de un archivo CSV, usa las efemérides descargadas y genera un archivo de simulación, para ello usa el simulador [GPS-SDR-SIM](https://github.com/osqzss/gps-sdr-sim). 

## Requisitos

El archivo `requirements.txt` contiene todas las dependencias necesarias para ejecutar el proyecto. Las principales son:

- **requests**: Para realizar descargas HTTP.
- **beautifulsoup4**: Para analizar y extraer contenido de HTML.
- **gnuradio**: Para usar GNU Radio en la simulación.

## Estructura de Carpetas

El programa necesita que las carpetas estén organizadas de la siguiente manera dentro de tu proyecto:

```
GPS-SPOOFING/
├── efemerides/
│ └── efemérides.25n # Archivo de efemérides necesario para la simulación
├── gps-sdr-sim/
│ └── gps-sdr-sim # Ejecutable para la simulación
│ └── GPSsimulator.grc # El archivo de flujo de trabajo de GNU Radio
├── rutas-save/ # Carpeta para almacenar archivos CSV de rutas
├── rutas/ # Carpeta donde se copiarán las rutas seleccionadas
├── automateCDDIS.py # Script para descargar efemérides
├── main.py # El script principal que ejecuta la interfaz gráfica
```
### Descargar automatica de Efemérides

Para usar esto deberas hacerte una cuenta en `https://cddis.nasa.gov/archive/gnss/data/daily/` pedir crear tu token y añadirlo en automateCDDIS.py. 




