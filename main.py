import pandas as pd
from pathlib import Path
from Funciones import descargar_datos_noaa
from Funciones import descargar_owid_co2
from Funciones import descargar_temp_noaa
import matplotlib.pyplot as plt
from pathlib import Path
from variables import df_final


descargar_datos_noaa()
descargar_owid_co2()
descargar_temp_noaa()

