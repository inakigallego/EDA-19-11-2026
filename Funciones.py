import os
import urllib.request
from pathlib import Path
import requests
import pandas as pd


def descargar_datos_noaa():
  """Función para descargar el registro mensual de CO2 de la NOAA. En archivo anual ya no está disponible"""
  
  url = "https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_mlo.csv"
  nombre_archivo = "noaa_co2_mensual_mlo.csv"

  carpeta_destino = "emisiones_data"
  ruta_carpeta = Path(carpeta_destino)
  ruta_carpeta.mkdir(exist_ok = True)

  ruta_archivo = ruta_carpeta / nombre_archivo
  if ruta_archivo.exists():
    print(f"El archivo de NOAA ya existe (Versión local)")
    return True
  print("Iniciando la descarga del archivo de la NOAA...")

  try:
    # Descarga el archivo desde internet por bloques y le he metido un límite de tiempo para que no se atasque en un bucle
    respuesta = requests.get(url, stream = True, timeout = 30)
    respuesta.raise_for_status()

    # Guardar el contenido descargado en el disco duro, me lo propuso la IA porque me daba problemas al descargarlo de golpe: mejor a paquetitos
    with open(ruta_archivo, "wb") as archivo:
      for bloque in respuesta.iter_content(chunk_size = 8192):
        archivo.write(bloque)

    print(f"   [ÉXITO] Archivo guardado correctamente en: {ruta_archivo}")
    return True

  except requests.exceptions.RequestException as error:
    
    print(f"   [ERROR] No se pudo descargar la NOAA. Motivo: {error}")
    return False


def descargar_owid_co2():
  """
  Descargo el dataset histórico de emisiones de CO2 de Our World in Data
    """
  
  url = "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv"
  nombre_archivo = "owid_co2_data.csv"
  
  carpeta_destino = "emisiones_data"
  ruta_carpeta = Path(carpeta_destino)
  ruta_carpeta.mkdir(exist_ok = True)
    
  ruta_archivo = ruta_carpeta / nombre_archivo
  if ruta_archivo.exists():
      print(f"El archivo de OWID ya existe (Versión local)")
      return True
  print("Iniciando la descarga del archivo de OWID...")
    
  try:
    respuesta = requests.get(url, stream = True, timeout = 30)
    respuesta.raise_for_status()
        
    with open(ruta_archivo, "wb") as archivo:
      for bloque in respuesta.iter_content(chunk_size = 8192):
        archivo.write(bloque)
                
    print(f"   [ÉXITO] Archivo OWID guardado correctamente en: {ruta_archivo}")
    return True

  except requests.exceptions.RequestException as error:
    print(f"   [ERROR] No se pudo descargar OWID. Motivo: {error}")
    return False

def descargar_temp_noaa():
    """Función para descargar la temperatura global de la NOAA (NCEI)"""
    
     url = "https://www.ncei.noaa.gov/access/monitoring/climate-at-a-glance/global/time-series/globe/land_ocean/1/0/1850-2025.csv"
    nombre_archivo = "noaa_temp_global_anual.csv"
    
    carpeta_destino = "emisiones_data"
    ruta_carpeta = Path(carpeta_destino)
    ruta_carpeta.mkdir(exist_ok=True)
    
    ruta_archivo = ruta_carpeta / nombre_archivo
    if ruta_archivo.exists():
        print(f"El archivo de NOAA temperatura ya existe (Versión local)")
        return True
    
    # Cabecera necesaria para que el servidor no rechace la conexión por script
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    print("Iniciando la descarga del archivo de temperatura de la NOAA...")

    try:
        respuesta = requests.get(url, headers=headers, stream=True, timeout=30)
        respuesta.raise_for_status()

        with open(ruta_archivo, "wb") as archivo:
            for bloque in respuesta.iter_content(chunk_size=8192):
                archivo.write(bloque)

        print(f"   [ÉXITO] Archivo guardado correctamente en: {ruta_archivo}")
        return True

    except requests.exceptions.RequestException as error:
        print(f"   [ERROR] No se pudo descargar la temperatura de la NOAA. Motivo: {error}")
        return False



def depurar_dataset():
    try:
      path = Path("emisiones_data/noaa_co2_mensual_mlo.csv")
      df = pd.read_csv(path, comment="#")
      df = df.rename(columns={
          "year": "año",
          "month": "mes",
          "decimal date": "fecha_decimal",
          "average": "promedio ppm",
          "deseasonalized": "desestacionalizado",
          "ndays": "dias",
          "sdev": "desv_estandar ppm",
          "unc": "incertidumbre ppm",})
      df_anual = df.groupby("año", as_index=False).mean(numeric_only=True)
      df_noaa_anual = df_anual[["año", "promedio ppm"]]
      df_noaa = df_noaa_anual.iloc[:-1].reset_index(drop=True)

      path = Path("emisiones_data/owid_co2_data.csv")
      df2 = pd.read_csv(path, comment="#")
      df3 = df2.iloc[:, [0, 1, 3, 7, 10, 25, 41]]
      df3_mundial = df3[df3['country'] == 'World']
      df4_mundial = df3_mundial[df3_mundial["year"] >= 1850].reset_index(drop=True)
      df5_mundial = df4_mundial
      columnas = [col for col in df5_mundial.columns if col not in ("country", "year", "population")]
      df5_mundial[columnas] = df5_mundial[columnas].div(7820)
      df_owid_anual = df5_mundial
      df_owid = df_owid_anual[df_owid_anual["year"] >= 1958].reset_index(drop=True)
      df_owid = df_owid.drop(columns=['country'])

      path = Path("emisiones_data/noaa_temp_global_anual.csv")
      df_1 = pd.read_csv(path, skiprows=4)
      df_1.columns = ["periodo", "anomalia"]
      df_1["año"] = df_1["periodo"].astype(str).str[:4].astype(int)
      df_1_anual = df_1.groupby("año")["anomalia"].mean().reset_index()
      df_1_anual = df_1_anual[(df_1_anual["año"] >= 1958) & (df_1_anual["año"] <= 2025)]
      df_2_anual = df_1_anual[(df_1_anual["año"] >= 1958) & (df_1_anual["año"] <= 2025)]
      df_2_anual["temp_media(Cº)"] = df_2_anual["anomalia"] + 13.9
      df_3_anual = df_2_anual 
      df_temp = df_3_anual.drop(columns=["anomalia"])

      df_final = pd.merge(df_owid, df_noaa, left_on = "year", right_on = "año", how="inner")
      df_final = df_final.drop(columns=["year"])
      df_final = df_final[["año", "population", "cumulative_co2", "land_use_change_co2", "co2_including_luc", "co2", "promedio ppm"]]
      df_final = df_final.rename(columns = {"año": "año", "population": "población", "cumulative_co2": "co2_acumulado (ppm)", "land_use_change_co2": "co2_cambio_uso_suelo (ppm)", "co2_including_luc": "co2_incluyendo_luc (ppm)", "co2": "co2 (ppm)", "promedio ppm": "co2_promedio (ppm)"})  
      df_final = pd.merge(df_final, df_temp, left_on = "año", right_on = "año", how="inner")

      return df_final

    except FileNotFoundError as e:
      print(f"Error crítico: No se ha encontrado alguno de los ficheros CSV. Detalle: {e}")
      return None
    except Exception as e:
      print(f"Error inesperado durante la depuración del dataset: {e}")
      return None
    



