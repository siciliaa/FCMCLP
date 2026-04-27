import os


def build_coverage_map(graph):
    """
    Builds a nested dict {facility: {client: coverage}} from the adjacency list,
    allowing O(1) coverage lookups instead of iterating over all neighbors.
    Called once after loading a graph and stored in graph['coverage_map'].
    """
    coverage_map = {}
    for facility in range(len(graph['nodes'])):
        coverage_map[facility] = {
            neighbor: coverage
            for neighbor, _, coverage in graph['adjacency'][facility]
        }
    return coverage_map


def detect_pmed_instances(directory):
    """
    Scans a directory for pmed instance files (pattern: 'pmed*_demand.txt')
    and returns a sorted list of their base names (e.g. 'pmed32', 'pmed39').
    """
    instances = []
    for filename in os.listdir(directory):
        if filename.endswith('_demand.txt') and filename.startswith('pmed'):
            name = filename.replace('_demand.txt', '')
            instances.append(name)
    return sorted(instances)


def load_pmed_graph(directory, name):
    """
    Loads a pmed instance from four files (demand, capacity, distance, coverage)
    and builds the graph dict with keys:
      'name':         instance name
      'nodes':        list of (id, demand, capacity) tuples
      'adjacency':    dict {node: [(neighbour, distance, coverage), ...]} — only non-zero coverage pairs
      'distances':    full distance matrix
      'coverage_map': precomputed {facility: {client: coverage}} for fast lookups
    """
    demand_file = os.path.join(directory, f'{name}_demand.txt')
    capacity_file = os.path.join(directory, f'{name}-capacity.txt')
    distance_file = os.path.join(directory, f'{name}_distance.txt')
    coverage_file = os.path.join(directory, f'{name}_degcov_20_10_5.txt')

    demand = read_list(demand_file)
    capacity = read_list(capacity_file)
    distance = read_matrix(distance_file)
    coverage = read_matrix(coverage_file)

    nodes = []
    adjacency = {}
    for i in range(len(demand)):
        node = (i, demand[i], capacity[i])
        nodes.append(node)
        neighbour = []
        for j in range(len(demand)):
            if i != j and coverage[i][j] > 0:
                n = (j, distance[i][j], coverage[i][j])
                neighbour.append(n)
        adjacency[i] = neighbour

    graph = {
        'name': name,
        'nodes': nodes,
        'adjacency': adjacency,
        'distances': distance,
    }
    graph['coverage_map'] = build_coverage_map(graph)

    return graph


def build_pmed_instances(directory):
    """
    Detects and loads all pmed instances found in directory.
    Returns a dict {name: graph} ready to be used by the solver.
    """
    names = detect_pmed_instances(directory)
    graphs = {}
    for name in names:
        graph = load_pmed_graph(directory, name)
        graphs[name] = graph
    return graphs

def detect_instances(directory):
    """
    Scans a directory for generic instance files (pattern: 'demand-*.txt')
    and returns a sorted list of their base names (e.g. 'fcmclp324', 'fcmclp500').
    """
    instances = []
    for filename in os.listdir(directory):
        if filename.startswith('demand-') and filename.endswith('.txt'):
            name = filename.replace('demand-', '').replace('.txt', '')
            instances.append(name)

    return sorted(instances)


def read_list(file):
    """
    Reads a plain-text file with one numeric value per line.
    Returns a list of floats.
    """
    values = []

    with open(file, 'r') as f:
        for line in f:
            values.append(float(line.strip()))

    return values


def read_matrix(file):
    """
    Reads a CSV file where each line is a row of comma-separated numeric values.
    Returns a list of lists of floats representing the full matrix.
    """
    matrix = []

    with open(file, 'r') as f:
        for line in f:
            parts = line.strip().split(',')
            row = []
            for p in parts:
                row.append(float(p))
            matrix.append(row)
    return matrix

def load_graph(directory, name):
    """
    Loads a generic FCMCLP instance from four files (demand, capacity, distance, coverage)
    and builds the graph dict with keys:
      'name':         instance name
      'nodes':        list of (id, demand, capacity) tuples
      'adjacency':    dict {node: [(neighbour, distance, coverage), ...]} — only non-zero coverage pairs
      'distances':    full distance matrix
      'coverage_map': precomputed {facility: {client: coverage}} for fast lookups
    """
    demand_file = os.path.join(directory, f'demand-{name}.txt')  # Esto es una lista
    capacity_file = os.path.join(directory, f'capacity-{name}.txt')  # Esto es una lista
    distance_file = os.path.join(directory, f'distance_{name}.txt')  # Esto es una matriz
    coverage_file = os.path.join(directory, f'degcov_600_300_100_{name}.txt')  # Esto es una matriz

    demand = read_list(demand_file)
    capacity = read_list(capacity_file)
    distance = read_matrix(distance_file)
    coverage = read_matrix(coverage_file)

    nodes = []
    adjacency = {}
    for i in range(len(demand)):
        node = (i, demand[i], capacity[i])
        nodes.append(node)
        neighbour = []
        for j in range(len(demand)):
            if i!=j and coverage[i][j] > 0:
                n = (j, distance[i][j], coverage[i][j])
                neighbour.append(n)
        adjacency[i] = neighbour

    graph = {
        'name': name,
        'nodes': nodes,
        'adjacency': adjacency,
        'distances': distance,
    }
    graph['coverage_map'] = build_coverage_map(graph)

    return graph

def build_instances(directory):
    """
    Detects and loads all generic FCMCLP instances found in directory.
    Returns a dict {name: graph} ready to be used by the solver.
    """
    names = detect_instances(directory)

    graphs = {}
    i = 0
    for name in names:
        graph = load_graph(directory, name)
        graphs[name] = graph

    return graphs


if __name__ == '__main__':
    directory = 'Instances'
    graphs = build_instances(directory)
    i = 0
    for g in graphs.values():
        print(f"Name: {g['name']} - Nodes: {len(g['nodes'])}")
        if i == 0:
            print(f"Neighbors of node 0: {g['adjacency'][i][:3]}")
            print(f"Distancia entre nodo 26 y 25: {g['distances'][26][54]}")
        i += 1
