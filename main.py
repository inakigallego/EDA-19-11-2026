from Funciones import descargar_datos_noaa
from Funciones import descargar_owid_co2
from Funciones import descargar_temp_noaa
from Funciones import (grafico1, grafico2, grafico3, grafico4, grafico5, grafico6)
from Variables import df_final


descargar_datos_noaa()
descargar_owid_co2()
descargar_temp_noaa()

grafico1(df_final)
grafico2(df_final)
grafico3(df_final)
grafico4(df_final) 
grafico5(df_final) 
grafico6(df_final)


