from pathlib import Path
import pandas as pd
from Funciones import (descargar_datos_noaa, descargar_owid_co2, descargar_temp_noaa, depurar_dataset)

# Ojo a las carpetas y las rutas relativas
#path = Path("emisiones_data/noaa_co2_mensual_mlo.csv")
#path = Path("emisiones_data/owid_co2_data.csv")
#path = Path("emisiones_data/noaa_temp_global_anual.csv")
CARPETA_DATA = Path("emisiones_data")
RUTA_NOAA = CARPETA_DATA / "noaa_co2_mensual_mlo.csv"
RUTA_OWID = CARPETA_DATA / "owid_co2_data.csv"  # Me ha dado muchos problemas
RUTA_TEMP = CARPETA_DATA / "noaa_temp_global_anual.csv" # La descarga ha sido una odisea

df_final = depurar_dataset()
