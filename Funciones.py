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





