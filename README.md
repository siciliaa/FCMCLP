# Búsqueda de vecindad variable para la resolución del problema de localización de cobertura máxima capacitada y difusa

## Resumen



---



---

## Conjunto de datos

Los experimentos utilizan dos conjuntos de instancias: las instancias de referencia FCMCLP de [Atta et al. (2022)](https://soumenatta.github.io/fcmclp/) (*Computers & Industrial Engineering*, Elsevier) e instancias estándar de p-mediana (pmed), cada una con niveles de cobertura difusa derivados de umbrales de distancia, obtenidas también de este mismo reposotorio.

| Instancia    | Nodos | Umbrales de cobertura |
|--------------|------:|-----------------------|
| fcmclp324    |   323 | 100 / 300 / 600       |
| fcmclp402    |   401 | 100 / 300 / 600       |
| fcmclp500    |   499 | 100 / 300 / 600       |
| fcmclp708    |   707 | 100 / 300 / 600       |
| fcmclp818    |   817 | 100 / 300 / 600       |
| pmed32       |   700 | 5 / 10 / 20           |
| pmed39       |   900 | 5 / 10 / 20           |

### Formato de las instancias

Cada instancia se define mediante cuatro ficheros:

- **`demand-{nombre}.txt`** / **`{nombre}_demand.txt`**: un valor de demanda por línea, representando la demanda de cada nodo.
- **`capacity-{nombre}.txt`** / **`{nombre}-capacity.txt`**: un valor de capacidad por línea, representando la capacidad de servicio de cada instalación.
- **`distance_{nombre}.txt`** / **`{nombre}_distance.txt`**: matriz de distancias completa en formato CSV (una fila por línea, separada por comas).
- **`degcov_T1_T2_T3_{nombre}.txt`** / **`{nombre}_degcov_T1_T2_T3.txt`**: matriz de cobertura difusa en formato CSV. Cada entrada `cobertura[i][j]` es un valor en `[0, 1]` que representa el grado de cobertura que la instalación `i` proporciona al cliente `j`, calculado a partir de la distancia y los tres umbrales (T1 < T2 < T3):
  - `1.0` si distancia ≤ T1
  - Valor parcial en (0, 1) si T1 < distancia ≤ T3
  - `0.0` si distancia > T3

Todos los ficheros de instancias se encuentran en la carpeta `Instances/`.

---

## Estructura del repositorio

```
FCMCLP/
├── BVNS.py                          # Metaheurística BVNS — punto de entrada principal
├── local_search_first_improvement.py # Búsqueda local de primera mejora (1-swap)
├── solution.py                       # Función objetivo, evaluación y comprobación de factibilidad
├── load_instances.py                 # Utilidades de carga de instancias
├── Instances/                        # Ficheros de instancias (demanda, capacidad, distancia, cobertura)
└── Resultados/                       # Ficheros de resultados generados tras la ejecución
```

---

## Ejecución del algoritmo

Requiere Python 3.x sin dependencias externas.

```bash
python BVNS.py
```

El script ejecuta el BVNS sobre todas las instancias para cada valor de k (número de instalaciones abiertas) y escribe los resultados en `Resultados/`:

- **`cobertura_bvns.txt`**: porcentaje de cobertura y tiempo de cómputo por instancia y k.
- **`completo_bvns.txt`**: resultados completos con k, cobertura, tiempo, índices de instalaciones abiertas y valor objetivo.

### Parámetros

Los parámetros principales pueden ajustarse directamente en `BVNS.py`:

| Parámetro     |   Valor por defecto | Descripción                                                  |
|---------------|--------------------:|--------------------------------------------------------------|
| `time_limit`  |                1800 | Tiempo máximo en segundos por ejecución (instancia, k)       |
| `num_starts`  |               10000 | Número de reinicios del VNS desde la mejor solución conocida |
| `kmax`        |         `⌊0.3·k⌋`  | Tamaño máximo del vecindario de perturbación                 |
