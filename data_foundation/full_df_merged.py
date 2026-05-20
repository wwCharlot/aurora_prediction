import pandas as pd
from functools import reduce

# CARGA ARCHIVOS CSV
print("Cargando archivos CSV...")
df_meteo = pd.read_csv('hourly_data.csv')
df_kp = pd.read_csv('Kp_index_horario_2016-04-05_al_2026-04-22.csv')
df_solar = pd.read_csv('solar_wind_data.csv') 

# UNIFICAMOS FORMATO DE LA FECHA
df_meteo['date'] = pd.to_datetime(df_meteo['date'])
df_kp['date'] = pd.to_datetime(df_kp['date'])
df_solar['date'] = pd.to_datetime(df_solar['date'])

print("Tamaño original Meteo:", df_meteo.shape)
print("Tamaño original Kp:", df_kp.shape)
print("Tamaño original Solar:", df_solar.shape)

# INTEGRACIÓN DE DATOS

# Terrestre + Kp
df_temp = pd.merge(df_meteo, df_kp, on='date', how='inner')
# (Terrestre + Kp) + Solar
df_master = pd.merge(df_temp, df_solar, on='date', how='inner')

### LIMPIEZA ###

# Ordenamos por fecha
df_master = df_master.sort_values('date').reset_index(drop=True)

# Revisamos desajustes del cruce
print("\nTamaño del Dataset Maestro:", df_master.shape)

# Eliminamos filas vacías (NaN) 
df_master = df_master.dropna(subset=['Bz_GSM', 'Kp_index', 'cloud_cover_low'])
print("Tamaño tras eliminar NaNs:", df_master.shape)

# CREACIÓN DE LA VARIABLE OBJETIVO (TARGET)

def calcular_visibilidad(row):
    # Si es de día o hay nubes muy bajas visibilidad = 0
    if row['is_day'] == 1.0:
        return 0
    if row['cloud_cover_low'] > 50.0: # umbral ajustable
        return 0
        
    # Reglas de Aurora (Si la física es favorable, visibilidad = 1)
    # p.e: Kp alto, Bz apuntando al sur (negativo) y viento rápido
    if row['Kp_index'] >= 2.0 and row['Bz_GSM'] < 0.0 and row['Speed'] > 350.0:
        return 1
        
    # Si no cumple ni veto absoluto ni aurora clara, no hay aurora visible
    return 0

# Aplicamos la función fila por fila para crear la nueva columna
df_master['Target_Aurora_Visible'] = df_master.apply(calcular_visibilidad, axis=1)

print("\nDistribución variable objetivo:")
print(df_master['Target_Aurora_Visible'].value_counts())

# Guardamos archivo final
df_master.to_csv('dataset_tromso_maestro.csv', index=False)
print("\nDataset guardado")