from pathlib import Path
import requests
import pandas as pd
import matplotlib.pyplot as plt




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
    

def grafico1(df):   
    # 1. Calculo el incremento anual real del Balance (ppm/año)
    df["variacion_balance_anual"] = df["co2_promedio (ppm)"].diff()

    # 2. Me salen demasiados picos, así que suavizo ambas tasas con media móvil de 5 años para comparar ciclos reales
    df["variacion_balance_5a"] = df["variacion_balance_anual"].rolling(window=5).mean()
    df["emisiones_luc_5a"] = df["co2_incluyendo_luc (ppm)"].rolling(window=5).mean()

    # 3. Gráfico de eje único y escala real (ppm/año)
    plt.figure(figsize=(12, 6))

    plt.plot(df["año"], df["co2_incluyendo_luc (ppm)"], color="tab:blue", alpha=0.35, linestyle="--", label="Emisiones anuales incl. LUC (bruta, ppm/año)")

    plt.plot(df["año"], df["emisiones_luc_5a"], color="tab:blue", linewidth=2.5, label="Emisiones anuales incl. LUC (media móvil 5 años)")

    plt.plot(df["año"], df["variacion_balance_anual"], color="tab:red", alpha=0.35, marker="o", markersize=3, label="Variación anual del Balance (bruta, ppm/año)")

    plt.plot(df["año"], df["variacion_balance_5a"], color="tab:red", linewidth=2.5, label="Variación anual del Balance (media móvil 5 años)")

    plt.title("Comparativa Homogénea en Escala Real: Flujo Emitido vs. Variación del Balance (1958-2025)", fontsize=12)
    plt.xlabel("Año", fontsize=11)
    plt.ylabel("Tasa Anual (ppm / año)", fontsize=11)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc="upper left", fontsize=10)

    plt.tight_layout()

    carpeta = Path("graficos")
    carpeta.mkdir(exist_ok=True)  # Crea la carpeta si no existe

    ruta_imagen = carpeta / "comparativa_emisiones_balance.png"
    plt.savefig(ruta_imagen, dpi=300)  # dpi=300 alta calidad
    print(f"Gráfico guardado")
    plt.show()

    plt.close()



def grafico2(df):
    # 1. Calcul0 los incrementos anuales en bruto de las tres variables
    df["variacion_emisiones_anual"] = df["co2_incluyendo_luc (ppm)"].diff()
    df["variacion_balance_anual"] = df["co2_promedio (ppm)"].diff()
    df["variacion_temperatura_anual"] = df["temp_media(Cº)"].diff()

    fig, ax1 = plt.subplots(figsize=(12, 6))

    # --- EJE y IZQUIERDO: Variación de Emisiones y Balance de CO₂ (ppm/año) ---
    ax1.plot(df["año"], df["variacion_emisiones_anual"], color="tab:blue", alpha=0.6, linestyle="-", linewidth=1.5, label="Var. Emisiones incl. LUC (ppm/año)")
    ax1.plot(df["año"], df["variacion_balance_anual"], color="tab:red", alpha=0.7, linestyle="-", linewidth=1.5, label="Var. anual del Balance Atmosférico (ppm/año)")
    ax1.set_xlabel("Año", fontsize = 11)
    ax1.set_ylabel("Tasa de CO₂ (ppm / año)", fontsize = 11, color = "tab:red")
    ax1.grid(True, linestyle = ":", alpha = 0.6)

    # --- EJE y DERECHO: Variación Anual de Temperatura (°C/año) ---
    ax2 = ax1.twinx()
    ax2.plot(df["año"], df["variacion_temperatura_anual"], color="tab:green", alpha=0.7, linestyle="-", linewidth=1.5, label="Var. anual Temperatura (°C/año)")
    ax2.set_ylim(-1.1, 1.1)
    ax2.set_ylabel("Variación de Temperatura (°C / año)", fontsize = 10, color = "tab:green")
    ax2.grid(False)  # Quedaba feo y así se evita que se solapen las líneas de la cuadrícula


    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc = "upper left", fontsize = 9)

    plt.title("Variaciones Interanuales en Bruto: Emisiones, Balance de CO₂ y Temperatura (1958-2025)", fontsize = 12)
    plt.tight_layout()

    carpeta = Path("graficos")
    carpeta.mkdir(exist_ok=True)
    
    ruta_imagen = carpeta / "Variaciones_anuales_emisiones_balance_temperatura.png"
    plt.savefig(ruta_imagen, dpi=300)
    print(f"Gráfico guardado")
    plt.show()
    
    plt.close()


def grafico3(df):
    # 1. Calculo la variación porcentual interanual (%) de ambas series
    df["var_pct_balance"] = df["co2_promedio (ppm)"].pct_change() * 100
    df["var_pct_luc"] = df["co2_incluyendo_luc (ppm)"].pct_change() * 100

    # 2. Suavizo con media móvil de 5 años
    df["var_pct_balance_5a"] = df["var_pct_balance"].rolling(window=5).mean()
    df["var_pct_luc_5a"] = df["var_pct_luc"].rolling(window=5).mean()

    plt.figure(figsize=(12, 6))

    plt.plot(df["año"], df["var_pct_luc_5a"], color="tab:blue", linewidth=2.5, label="Emisiones incl. LUC (% anual, media móvil 5 años)")

    plt.plot(df["año"], df["var_pct_balance_5a"], color="tab:red", linewidth=2.5, label="Balance (% anual, media móvil 5 años)")

    plt.axhline(y=0, color="black", linewidth=0.8, alpha=0.5)
    plt.title("Variación Porcentual Interanual: Emisiones incl. LUC vs. Balance (1958-2025)", fontsize=12)
    plt.xlabel("Año", fontsize=11)
    plt.ylabel("Variación Interanual (%)", fontsize=11)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc="upper right", fontsize=10)

    plt.tight_layout()

    carpeta = Path("graficos")
    carpeta.mkdir(exist_ok=True)
        
    ruta_imagen = carpeta / "Variaciones_anuales_emisiones_balance.png"
    plt.savefig(ruta_imagen, dpi=300)
    print(f"Gráfico guardado")
    plt.show()
        
    plt.close()
    

def grafico4(df):
    # 1. Calculo el incremento anual de CO2 en la atmósfera
    df["incremento_atmosferico_ppm"] = df["co2_promedio (ppm)"].diff()

    # 2. Calculo la fracción aerotransportada relacionando el incremento con las emisiones totales
    df["fraccion_aerotransportada_pct"] = (df["incremento_atmosferico_ppm"] / df["co2 (ppm)"]) * 10

    plt.figure(figsize=(12, 6))

    plt.plot(df["año"][1:], df["fraccion_aerotransportada_pct"][1:], color="tab:purple", marker="o", markersize=3, linestyle="-", linewidth=1.5, label="Fracción Aerotransportada Anual (%)")

    # Línea de media histórica
    media_historica = df["fraccion_aerotransportada_pct"].mean()
    plt.axhline(y=media_historica, color="tab:gray", linestyle="--", label=f"Media histórica (~{media_historica:.1f}%)")

    plt.title("Evolución de la Fracción Aerotransportada de CO2 (1958-2025)", fontsize = 13, pad = 15)
    plt.xlabel("Año", fontsize = 12)
    plt.ylabel("Porcentaje que permanece en la atmósfera (%)", fontsize = 12)
    plt.grid(True, linestyle = ":", alpha = 0.6)
    plt.legend(loc = "upper left", fontsize = 11)

    plt.tight_layout()

    carpeta = Path("graficos")
    carpeta.mkdir(exist_ok=True)
            
    ruta_imagen = carpeta / "Fraccion aerotransportada.png"
    plt.savefig(ruta_imagen, dpi=300)
    print(f"Gráfico guardado")
    plt.show()
            
    plt.close()


def grafico5(df):
    # 1. Gráficas independientes en sus unidades reales (sin doble eje Y)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    # Subgráfico 1: Emisiones por cambio de uso de suelo (ppm/año)
    df["co2_luc_5a"] = df["co2_cambio_uso_suelo (ppm)"].rolling(window=5).mean()

    ax1.plot(df["año"], df["co2_cambio_uso_suelo (ppm)"], color="tab:green", alpha=0.35, linewidth=1.5, label="CO2 cambio de uso de suelo (anual, ppm/año)")
    ax1.plot(df["año"], df["co2_luc_5a"], color="tab:green", linewidth=2.5, label="CO2 cambio de uso de suelo (media móvil 5 años)")
    ax1.set_title("Emisiones de CO2 por Cambio de Uso de Suelo (1958-2025)", fontsize=12)
    ax1.set_ylabel("Flujo Anual (ppm / año)", fontsize=11)
    ax1.grid(True, alpha=0.4)
    ax1.legend(loc="upper right", fontsize=10)

    # Subgráfico 2: Población mundial
    ax2.plot(df["año"], df["población"] / 1e9, color="tab:purple", linewidth=2.5, label="Población mundial (miles de millones)")
    ax2.set_title("Evolución de la Población Mundial (1958-2025)", fontsize=12)
    ax2.set_xlabel("Año", fontsize=11)
    ax2.set_ylabel("Miles de millones de habitantes", fontsize=11)
    ax2.grid(True, alpha=0.4)
    ax2.legend(loc="upper left", fontsize=10)

    plt.tight_layout()

    carpeta = Path("graficos")
    carpeta.mkdir(exist_ok=True)
            
    ruta_imagen = carpeta / "Emisiones_cambio_suelo_poblacion.png"
    plt.savefig(ruta_imagen, dpi=300)
    print(f"Gráfico guardado")
    plt.show()
            
    plt.close()


def grafico6(df):
    # 1. Comparativa directa en eje único adimensional (% anual, media móvil 5 años)
    df["var_pct_luc_5a"] = (df["co2_cambio_uso_suelo (ppm)"].pct_change() * 100).rolling(window=5).mean()
    df["var_pct_pob_5a"] = (df["población"].pct_change() * 100).rolling(window=5).mean()

    plt.figure(figsize=(12, 6))

    plt.plot(df["año"], df["var_pct_luc_5a"], color="tab:green", linewidth=2.5, label="CO2 cambio de uso de suelo (% anual, media móvil 5 años)")

    plt.plot(df["año"], df["var_pct_pob_5a"], color="tab:purple", linewidth=2.5, label="Población (% anual, media móvil 5 años)")

    plt.axhline(y=0, color="black", linewidth=0.8, alpha=0.5)
    plt.title("Variación Porcentual Interanual: Cambio de Uso de Suelo vs. Población (1958-2025)", fontsize=12)
    plt.xlabel("Año", fontsize=11)
    plt.ylabel("Variación Interanual (%)", fontsize=11)
    plt.grid(True, alpha=0.4)
    plt.legend(loc="upper right", fontsize=10)

    plt.tight_layout()

    carpeta = Path("graficos")
    carpeta.mkdir(exist_ok=True)
            
    ruta_imagen = carpeta / "Emisiones%_cambio_suelo_poblacion.png"
    plt.savefig(ruta_imagen, dpi=300)
    print(f"Gráfico guardado")
    plt.show()

    plt.close()

  
def grafico7(df):
    fig, ax1 = plt.subplots(figsize=(12, 6)) # Es el estándar para que me ocupe la pantalla

    ax1.plot(df["año"], df["co2_promedio (ppm)"], color="tab:red", linewidth=2.5, label="Balance atmosférico (ppm)")
    ax1.plot(df["año"], df["co2_acumulado (ppm)"], color="tab:green", linestyle="-.", linewidth=2, label="CO2 acumulado emitido (ppm)")
    ax1.plot(df["año"], df["co2 (ppm)"], color="tab:orange", linestyle="--", linewidth=1.5, label="Emisiones anuales (ppm)")

    ax1.set_xlabel("Año", fontsize=12)
    ax1.set_ylabel("Concentración y Acumulados de CO2 (ppm)", color="tab:red", fontsize=12)
    ax1.tick_params(axis="y", labelcolor="tab:red")
    ax1.grid(True, linestyle=":", alpha=0.6)


    ax2 = ax1.twinx()
    ax2.plot(df["año"], df["población"], color="tab:blue", linewidth=2, label="Población mundial")

    ax2.set_ylabel("Población", color="tab:blue", fontsize=12)
    ax2.tick_params(axis="y", labelcolor="tab:blue")


    plt.title("Evolución Histórica: Población, Emisiones Anuales, Acumuladas y Balance Atmosférico (1958-2025)", fontsize=13, pad=15)


    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc="upper left", fontsize=10)

    plt.tight_layout()

    carpeta = Path("graficos")
    carpeta.mkdir(exist_ok=True)
            
    ruta_imagen = carpeta / "Evolucion_histórica.png"
    plt.savefig(ruta_imagen, dpi=300)
    print(f"Gráfico guardado")
    plt.show()

    plt.close()
    
    
