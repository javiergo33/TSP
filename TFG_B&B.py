import numpy as np
from math import radians, sin, cos, sqrt, atan2
import webbrowser
import folium
import pandas as pd
import time

start_time = time.time()

# Leer datos 
def leer_datos():
    df_estadios = pd.read_excel('Libro1.xlsx', sheet_name='Estadios Eurocopa 2024', decimal=',') 
    df_formula1 = pd.read_excel('Libro1.xlsx', sheet_name='Circuitos Formula 1 2024', decimal=',')
    df_metro    = pd.read_excel('Libro1.xlsx', sheet_name='Paradas Metro Madrid', decimal=',')
    return df_estadios, df_formula1, df_metro

df_estadios, df_formula1, df_metro = leer_datos()

def calcular_distancias_entre_dos_ciudades(coord1:  pd.Series, coord2:  pd.Series) -> float:
    R = 6371.0  # Radio de la tierra en kilometros
    # Calcular diferencias
    dlon = radians(coord2['Longitud']) - radians(coord1['Longitud'])
    dlat = radians(coord2['Latitud']) - radians(coord1['Latitud'])
    a = sin(dlat/2)**2 + cos(radians(coord1['Latitud'])) * cos(radians(coord2['Latitud'])) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def calcular_distancias(df):
    n = len(df)
    distancias = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            distancias[i, j] = calcular_distancias_entre_dos_ciudades(df.iloc[i], df.iloc[j])
    return distancias

# Calcular distancias para diferentes conjuntos de datos
distancias_ciudades = calcular_distancias(df_estadios)
distancias_circuitos = calcular_distancias(df_formula1)
distancias_paradas = calcular_distancias(df_metro)

distancias=distancias_ciudades
def tsp_branch_bound(distancias):
    num=0
    n = distancias.shape[0] 
    mejor_ruta = None  
    mejor_coste = np.inf 

    # inicializa el stack con el nodo raíz
    stack = [(0, [0], set([0]), 0)] 
    while stack: 
        num += 1 
        node = stack.pop() 
        if len(node[1]) == n:  
            coste = node[3] + distancias[node[1][-1], 0] 
            if coste < mejor_coste: 
                mejor_ruta = node[1] 
                mejor_coste = coste 

       # generar nodos hijos considerando todas las ciudades no visitadas             
        else: 
            no_visitadas = set(range(n)) - node[2] 
            for i in no_visitadas:  
                ruta_hijo = node[1] + [i] 
                coste_hijo = node[3] + distancias[node[1][-1], i]  
                if np.min(coste_hijo) < np.min(mejor_coste): 
                    stack.append((i, ruta_hijo, node[2] | set([i]), coste_hijo))  
                 
    return mejor_ruta, mejor_coste, num


mejor_ruta, mejor_coste, total_iteraciones = tsp_branch_bound(distancias)

# Mostrar resultados
print("Mejor ruta:", [f"Estadio {i+1}: {df_estadios.iloc[i]['Lugar']}" for i in mejor_ruta])
print("Mejor coste:", round(mejor_coste, 2), "km")
print("Iteraciones: ",total_iteraciones)

# Crear un mapa centrado en la primera ciudad de la lista
m = folium.Map(location=(df_estadios.iloc[0]['Latitud'], df_estadios.iloc[0]['Longitud']), zoom_start=6)

# Agregar marcadores para cada ciudad
for index, row in df_estadios.iterrows():
    folium.Marker([row['Latitud'], row['Longitud']], popup=row['Lugar']).add_to(m)

# Agregar una polilínea para el camino óptimo
path = [df_estadios.iloc[i] for i in mejor_ruta] + [df_estadios.iloc[mejor_ruta[0]]]  # lista ordenada de ubicaciones de ciudades
folium.PolyLine([(city['Latitud'], city['Longitud']) for city in path], color='red', weight=3).add_to(m)

# Guardar el mapa en un archivo HTML
map_path = 'optimal_path_map.html'
m.save(map_path)
# Abrir el mapa en el navegador web por defecto
webbrowser.open(map_path)

print("--- %s segundos ---" % (time.time() - start_time))
print("------ -------- ----")

