# Spoof-lab

Signal generation is based on the open-source simulator [GPS-SDR-SIM](https://github.com/osqzss/gps-sdr-sim), which produces realistic GPS baseband signals from satellite ephemerides and receiver motion profiles.

---

## Features

- Generation of custom vehicle trajectories from CSV route files.
- Automatic download of GPS ephemerides from NASA CDDIS.
- Simulation of GPS L1 signals using GPS-SDR-SIM.
- Transmission of simulated signals using GNU Radio and HackRF.
- Support for controlled GPS spoofing scenarios.

---

## Requirements

All dependencies are listed in `requirements.txt`.  
Main required libraries:

- **requests** — HTTP downloads.
- **beautifulsoup4** — HTML parsing for ephemeris download.
- **gnuradio** — SDR signal transmission.
- **numpy** — CSV and numerical processing.

Additionally, the following external tools are required:

- **GPS-SDR-SIM**  
  https://github.com/osqzss/gps-sdr-sim

- **GNU Radio**

- **HackRF One** (or compatible SDR transmitter)

---

## Folder Structure

The project must follow this directory structure:


```
GPS-SPOOFING/
├── efemerides/
│ └── efemérides.25n # Ephemeris file required for simulation
├── gps-sdr-sim/
│ └── gps-sdr-sim # GPS-SDR-SIM executable
│ └── GPSsimulator.grc # GNU Radio flowgraph
├── rutas-save/ # Folder to store generated CSV route files
├── rutas/ # Folder where selected routes are copied for simulation
├── automateCDDIS.py # Script for automatic ephemeris download
├── main.py # Main script that launches the GUI
```
## Automatic Ephemeris Download

To enable automatic ephemeris downloading, you must create an account at `https://cddis.nasa.gov/archive/gnss/data/daily/` 
After registration, request an access token and insert it into the `automateCDDIS.py` script in the indicated field.

This allows the simulator to automatically fetch up-to-date satellite ephemerides.

---

## Running the Simulator

To start the GPS Spoofing Simulator, execute:

```bash
python3 main.py






