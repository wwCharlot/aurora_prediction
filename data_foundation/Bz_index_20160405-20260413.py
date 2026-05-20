import pandas as pd
import numpy as np

# 1. Leer el archivo .lst descargado de OMNIWeb
# (El orden de los nombres debe coincidir con el orden en el que marcaste las casillas)
columnas = ['Year', 'DOY', 'Hour', 'Magnitud_IMF', 'Bz_GSM', 'Density', 'Speed'] 

# delim_whitespace=True le dice a Pandas que las columnas están separadas por espacios
df_solar = pd.read_csv('omni2_oZYOfvmlma.lst', delim_whitespace=True, names=columnas)

# 2. Gestionar los valores perdidos (Data Prep)
# OMNIWeb usa nueves (999.9, 9999.0) cuando un satélite no pudo medir el dato
df_solar.replace([999.9, 9999.0, 999.99], np.nan, inplace=True)

# 3. Crear la columna 'date' uniendo el Año, el Día del Año (DOY) y la Hora
# format='%Y%j' le indica a Python que estamos usando el formato Año y Día del año (1-365)
df_solar['date'] = pd.to_datetime(df_solar['Year'] * 1000 + df_solar['DOY'], format='%Y%j') + pd.to_timedelta(df_solar['Hour'], unit='h')

# 4. Convertir a UTC para alinear con el Kp y la meteorología terrestre
df_solar['date'] = df_solar['date'].dt.tz_localize('UTC')

# Ver el resultado limpio
print(df_solar[['date', 'Magnitud_IMF', 'Bz_GSM', 'Density', 'Speed']].head())

# Guardar el resultado en CSV
df_solar[['date', 'Magnitud_IMF', 'Bz_GSM', 'Density', 'Speed']].to_csv('solar_wind_data.csv', index=False)
print("\nDatos solares guardados en 'solar_wind_data.csv'")