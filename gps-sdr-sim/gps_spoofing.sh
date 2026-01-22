#!/bin/bash
set -e

echo "🚀 Ejecutando simulador GPS..."


# === 2️⃣ Definir rutas base ===
BASE_DIR="/home/ado/Escritorio/GPS-SPOOFING/gps-sdr-sim"
EFEMERIDES_DIR="/home/ado/Escritorio/GPS-SPOOFING/efemerides"
RUTAS_DIR="/home/ado/Escritorio/GPS-SPOOFING/rutas"

cd "$BASE_DIR"

# === 3️⃣ Buscar archivos ===
EFEM_FILE=$(find "$EFEMERIDES_DIR" -type f -name "*.25n" -print -quit)
RUTA_FILE=$(find "$RUTAS_DIR" -type f -name "*.csv" -print -quit)

# === 4️⃣ Validaciones ===
if [[ ! -f "$EFEM_FILE" ]]; then
    echo "❌ No se encontró archivo de efemérides (.25n)"
    exit 1
fi

if [[ ! -f "$RUTA_FILE" ]]; then
    echo "❌ No se encontró archivo CSV de ruta"
    exit 1
fi

# === 5️⃣ Nombre de salida basado en el CSV ===
CSV_NAME=$(basename "$RUTA_FILE" .csv)
OUTPUT_FILE="${CSV_NAME}simulacion.bin"

echo "✅ Efemérides : $EFEM_FILE"
echo "✅ Ruta       : $RUTA_FILE"
echo "📦 Salida     : $OUTPUT_FILE"

# === 6️⃣ Ejecutar gps-sdr-sim ===
./gps-sdr-sim \
    -e "$EFEM_FILE" \
    -x "$RUTA_FILE" \
    -s 2600000 \
    -b 8 \
    -d 300\
    -o "$OUTPUT_FILE"

echo "✅ Archivo generado: $BASE_DIR/$OUTPUT_FILE"

# === 7️⃣ Abrir GNU Radio ===
GRC_FILE="$BASE_DIR/GPSsimulator.grc"

if [[ -f "$GRC_FILE" ]]; then
    echo "📡 Abriendo GPSsimulator.grc..."
    gnuradio-companion "$GRC_FILE" &
else
    echo "⚠️ GPSsimulator.grc no encontrado"
fi

echo "🎯 Proceso completado correctamente."

