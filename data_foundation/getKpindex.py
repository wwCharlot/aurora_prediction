#!/usr/bin/env python3

"""
getKpindex.py 
===================================
GFZ German Research Centre for Geosciences (CC BY 4.0)
"""

from datetime import datetime
import json, urllib.request
import pandas as pd # Añadido para la manipulación de datos

def __checkdate__(starttime,endtime):
    if starttime > endtime:
        raise NameError("Error! Start time must be before or equal to end time")
    return True

def __checkIndex__(index):
    if index not in ['Kp', 'ap', 'Ap', 'Cp', 'C9', 'Hp30', 'Hp60', 'ap30', 'ap60', 'SN', 'Fobs', 'Fadj']:
        raise IndexError("Error! Wrong index parameter! \nAllowed are only the string parameter: 'Kp', 'ap', 'Ap', 'Cp', 'C9', 'Hp30', 'Hp60', 'ap30', 'ap60', 'SN', 'Fobs', 'Fadj'")
    return True

def __checkstatus__(status):
    if status not in ['all', 'def']:
        raise IndexError("Error! Wrong option parameter! \nAllowed are only the string parameter: 'def'")
    return True
       
def __addstatus__(url,status):
    if status == 'def':
        url = url + '&status=def'
    return url 

def getKpindex(starttime, endtime, index, status='all'):
    result_t=0; result_index=0; result_s=0

    if len(starttime) == 10 and len(endtime) == 10:
        starttime = starttime + 'T00:00:00Z'
        endtime = endtime + 'T23:59:00Z'

    try:
        d1 = datetime.strptime(starttime, '%Y-%m-%dT%H:%M:%SZ')
        d2 = datetime.strptime(endtime, '%Y-%m-%dT%H:%M:%SZ')

        __checkdate__(d1,d2)
        __checkIndex__(index)  
        __checkstatus__(status)

        time_string = "start=" + d1.strftime('%Y-%m-%dT%H:%M:%SZ') + "&end=" + d2.strftime('%Y-%m-%dT%H:%M:%SZ')
        url = 'https://kp.gfz-potsdam.de/app/json/?' + time_string  + "&index=" + index
        if index not in ['Hp30', 'Hp60', 'ap30', 'ap60', 'Fobs', 'Fadj']:
            url = __addstatus__(url, status)

        print(f"Descargando datos desde: {url}")
        webURL = urllib.request.urlopen(url)
        binary = webURL.read()
        text=binary.decode('utf-8')
    
        try:
            data = json.loads(text)
            result_t = tuple(data["datetime"])
            result_index = tuple(data[index])
            if index not in ['Hp30', 'Hp60', 'ap30', 'ap60', 'Fobs', 'Fadj']:
                result_s = tuple(data["status"])
        except:
            print(text)

    except NameError as er:
        print(er)
    except IndexError as er:
        print(er)
    except ValueError:
        print("Error! Wrong datetime string")
    except urllib.error.URLError:
        print("Connection Error\nCan not reach " + url)
    # finally:
    return result_t, result_index, result_s

# =====================================================================
# EJECUCIÓN Y TRANSFORMACIÓN
# =====================================================================
if __name__ == "__main__":
    # Rango de fechas
    FECHA_INICIO = '2016-04-05'
    FECHA_FIN = '2026-04-22'
    
    print(f"Iniciando extracción del Índice Kp desde {FECHA_INICIO} hasta {FECHA_FIN}...")
    
    # Función para extraer Kp
    tiempos, kp_valores, estatus = getKpindex(FECHA_INICIO, FECHA_FIN, 'Kp')
    
    if tiempos != 0 and kp_valores != 0:
        # DataFrame de Pandas
        df_kp = pd.DataFrame({
            'date': tiempos,
            'Kp_index': kp_valores
        })
        
        # Columna 'date' a tipo datetime + asegurar que es UTC
        df_kp['date'] = pd.to_datetime(df_kp['date'])
        
        print("\nFormato original (cada 3 horas):")
        print(df_kp.head(3))
        
        # Relleno para que el espaciado temporal sea de 1hora igual que en la meteo terrestre con ffill() para rellenar los valores faltantes con el último valor conocido
        df_kp.set_index('date', inplace=True)
        
        df_kp_horario = df_kp.resample('1h').ffill()
        
        # Restauramos la fecha como columna normal
        df_kp_horario.reset_index(inplace=True)
        
        print("\nFormato transformado (cada 1 hora):")
        print(df_kp_horario.head(5))
        
        # Guardar resultado en CSV
        nombre_archivo = f"Kp_index_horario_{FECHA_INICIO}_al_{FECHA_FIN}.csv"
        df_kp_horario.to_csv(nombre_archivo, index=False)
        print(f"\nDatos guardados en el archivo: {nombre_archivo}")
    else:
        print("\nHubo un error al extraer los datos.")