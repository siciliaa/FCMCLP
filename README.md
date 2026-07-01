# Búsqueda de vecindad variable para la resolución del problema de localización de cobertura máxima capacitada y difusa

## Resumen



---

El problema de localización de cobertura máxima capacitada y difusa es un problema de optimización de tipo $\mathcal{NP}$-duro. Aparece en contextos donde es necesario decidir la ubicación de un conjunto de instalaciones capacitadas y que necesita asignar los clientes garantizando la satisfacción de su demanda. El objetivo es maximizar la demanda atendida, considerando que la cobertura proporcionada depende de la distancia entre clientes e instalaciones. Este tipo de formulaciones tiene aplicabilidad en áreas como la gestión de emergencias, la logística o las redes de telecomunicaciones. Para abordar el problema, en la literatura se propuso inicialmente un modelo de programación lineal entera resuelto mediante CPLEX, capaz de obtener soluciones óptimas únicamente para instancias de tamaño pequeño. Posteriormente, investigadores han desarrollado distintas aproximaciones, entre las que destacan un enfoque basado en cuatro metaheurísticas poblacionales y un algoritmo híbrido que combina el optimizador Grey Wolf con operadores de intensificación y diversificación. Dado que la complejidad del problema impide obtener soluciones exactas en tiempos razonables para instancias de gran tamaño, en este trabajo se desarrolla una metaheurística de Búsqueda de Vecindad Variable. El algoritmo propuesto combina una fase constructiva aleatoria, una fase de mejora y una perturbación con el objetivo de explorar distintas estructuras de vecindad. Para evaluar la robustez del método, se realizaron 10 ejecuciones independientes. Los resultados demuestran que la propuesta es competitiva al analizar el mejor valor y el promedio de estas 10 ejecuciones. La desviación media de dicho promedio es del 0,20\% frente al estado del arte, y superan los resultados promedios en 52 de las 84 instancias analizadas.

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
