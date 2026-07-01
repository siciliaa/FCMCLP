import random
import time


def calculate_objective(graph, solution):
    # In: graph (dict), solution (dict con 'coverages'). Out: float con la cobertura ponderada total (sum demand_i * coverage_i).
    objective = 0
    for client in range(len(graph['nodes'])):
        demand = graph['nodes'][client][1]
        coverage = solution['coverages'][client]
        objective += demand * coverage
    return objective


def evaluate_facilities(graph, facilities):
    """
    Greedily assigns each client (in index order 0..n-1) to the open facility
    with the highest coverage that still has remaining capacity.

    Earlier-indexed clients take priority when capacity is scarce. A client
    with no feasible assignment gets coverage 0.

    Returns a solution dict with keys:
      'open_facilities': list of facility indices
      'assignments':     list of facility index (or None) per client
      'coverages':       list of coverage value per client
    """
    used_capacity = {facility: 0 for facility in facilities}
    assignments = []
    coverages = []

    for client in range(len(graph['nodes'])):
        best_facility = None
        best_coverage = 0
        client_demand = graph['nodes'][client][1]

        for facility in facilities:
            for neighbor, distance, coverage in graph['adjacency'][facility]:
                if neighbor == client and coverage > best_coverage:
                    demand_covered = client_demand * coverage
                    facility_capacity = graph['nodes'][facility][2]
                    if used_capacity[facility] + demand_covered <= facility_capacity:
                        best_coverage = coverage
                        best_facility = facility

        if best_facility is not None:
            used_capacity[best_facility] += client_demand * best_coverage

        assignments.append(best_facility)
        coverages.append(best_coverage)

    return {
        'open_facilities': list(facilities),
        'assignments': assignments,
        'coverages': coverages,
    }


def evaluate_facilities_fast(graph, facilities, shuffle=True):
    """
    Same greedy as evaluate_facilities but uses graph['coverage_map'] for O(1) per (facility, client).
    Total complexity: O(n·k) vs O(n·k·d) of the original.
    shuffle=True randomises client processing order so early-indexed clients don't always
    get priority over capacity; shuffle=False gives deterministic results.
    """
    coverage_map = graph['coverage_map']
    used_capacity = {facility: 0 for facility in facilities}
    n = len(graph['nodes'])
    assignments = [None] * n
    coverages = [0.0] * n

    client_order = list(range(n))
    if shuffle:
        random.shuffle(client_order)

    for client in client_order:
        best_facility = None
        best_coverage = 0
        client_demand = graph['nodes'][client][1]

        for facility in facilities:
            coverage = coverage_map[facility].get(client, 0)
            if coverage > best_coverage:
                demand_covered = client_demand * coverage
                if used_capacity[facility] + demand_covered <= graph['nodes'][facility][2]:
                    best_coverage = coverage
                    best_facility = facility

        if best_facility is not None:
            used_capacity[best_facility] += client_demand * best_coverage

        assignments[client] = best_facility
        coverages[client] = best_coverage

    return {
        'open_facilities': list(facilities),
        'assignments': assignments,
        'coverages': coverages,
    }


def build_solution_state(graph, solution):
    """
    Augments a solution with a per-facility used_capacity dict, required for
    incremental swap evaluation.

    Returns a state dict with all solution fields plus:
      'used_capacity': {facility: total demand currently served by it}
    """
    used_capacity = {f: 0 for f in solution['open_facilities']}
    for client in range(len(graph['nodes'])):
        facility = solution['assignments'][client]
        if facility is not None:
            demand = graph['nodes'][client][1]
            used_capacity[facility] += demand * solution['coverages'][client]

    return {
        'open_facilities': list(solution['open_facilities']),
        'assignments': solution['assignments'][:],
        'coverages': solution['coverages'][:],
        'used_capacity': used_capacity,
    }


def evaluate_swap(graph, state, node_out, node_in):
    # In: graph, state (dict con used_capacity), node_out e node_in (int). Out: (new_state, new_of) tras el swap exacto vía re-evaluación greedy.
    new_facilities = [f for f in state['open_facilities'] if f != node_out] + [node_in]
    new_solution = evaluate_facilities_fast(graph, new_facilities)
    new_of = calculate_objective(graph, new_solution)
    new_state = build_solution_state(graph, new_solution)
    return new_state, new_of


def check_feasibility(graph, solution, k):
    # In: graph, solution (dict), k (int). Out: bool. Imprime las violaciones de capacidad o cardinalidad encontradas.
    violations = []

    if len(solution['open_facilities']) != k:
        violations.append(f"num_facilities={len(solution['open_facilities'])} != k={k}")

    open_set = set(solution['open_facilities'])
    for client, facility in enumerate(solution['assignments']):
        if facility is not None and facility not in open_set:
            violations.append(f"client {client} assigned to closed facility {facility}")

    used = {f: 0 for f in solution['open_facilities']}
    for client in range(len(graph['nodes'])):
        facility = solution['assignments'][client]
        if facility is not None:
            used[facility] += graph['nodes'][client][1] * solution['coverages'][client]
    for facility, load in used.items():
        capacity = graph['nodes'][facility][2]
        if load > capacity + 1e-6:
            violations.append(f"facility {facility} exceeds capacity: {load:.2f} > {capacity:.2f}")

    if violations:
        print(f"  [INFEASIBLE] {'; '.join(violations)}")
        return False
    print(f"  [OK] Feasible solution")
    return True


def open_random_facilities(graph, n):
    # In: graph, n (int). Out: solution dict con n instalaciones abiertas aleatoriamente evaluadas con evaluate_facilities_fast.
    open_facilities = random.sample(range(len(graph['nodes'])), n)
    return evaluate_facilities_fast(graph, open_facilities)


def grasp_constructive(graph, k, alpha=-1):
    """
    GRASP constructive: builds k facilities one by one.
    At each step computes the marginal demand-weighted coverage gain of every
    candidate respecting its capacity: clients that the facility can cover better
    than their current best are greedily packed in descending order of marginal
    gain until the facility's capacity is exhausted. Builds an RCL with all
    candidates whose gain >= g_max - alpha*(g_max - g_min), and picks one at
    random.  alpha=0 -> pure greedy, alpha=1 -> pure random.
    The final set is evaluated with evaluate_facilities_fast to get a feasible
    solution that respects capacity.
    """
    coverage_map = graph['coverage_map']
    n = len(graph['nodes'])
    candidates = list(range(n))
    selected = []
    best_coverage = [0.0] * n
    realAlpha = alpha
    for _ in range(k):
        if alpha == -1.0:
            realAlpha = random.random()
        if not candidates:
            break

        gains = []
        for f in candidates:
            # Capacidad restante de la instalación candidata
            remaining = graph['nodes'][f][2]
            gain = 0.0

            # Construimos una lista de clientes que mejorarían si usamos esta instalación
            improving = []
            for client, cov in coverage_map[f].items():
                # Solo nos interesa este cliente si la instalación f le da más cobertura
                # de la que ya tiene asignada
                if cov > best_coverage[client]:
                    peso = graph['nodes'][client][1]

                    # Ganancia marginal: cuánto mejora este cliente respecto a su mejor cobertura actual
                    marginal = peso * (cov - best_coverage[client])

                    # Carga total que este cliente necesita de la instalación
                    load = peso * cov

                    improving.append((marginal, load, client))

            # Ordenamos de mayor a menor ganancia marginal
            # para atender primero a los clientes más rentables (greedy)
            improving.sort(reverse=True)

            # Recorremos los clientes en orden de rentabilidad
            # y los asignamos mientras la instalación tenga capacidad
            for tupla in improving:
                marginal = tupla[0]
                load = tupla[1]
                # tupla[2] sería el cliente, pero aquí no lo necesitamos

                if remaining >= load:
                    gain += marginal
                    remaining -= load

            gains.append((gain, f))

        g_max = max(g for g, _ in gains)
        g_min = min(g for g, _ in gains)
        threshold = g_max - realAlpha * (g_max - g_min)
        rcl = [f for g, f in gains if g >= threshold]

        chosen = random.choice(rcl)
        selected.append(chosen)
        candidates.remove(chosen)

        for client, cov in coverage_map[chosen].items():
            if cov > best_coverage[client]:
                best_coverage[client] = cov

    return evaluate_facilities_fast(graph, selected)


def test_evaluate_facilities_equivalence(graph, facilities):
    # In: graph, facilities (list). Out: bool. Comprueba que evaluate_facilities y evaluate_facilities_fast producen el mismo resultado e imprime tiempos.
    t0 = time.perf_counter()
    sol_ref = evaluate_facilities(graph, facilities)
    t_ref = time.perf_counter() - t0

    t0 = time.perf_counter()
    sol_fast = evaluate_facilities_fast(graph, facilities)
    t_fast = time.perf_counter() - t0

    assert sol_ref['open_facilities'] == sol_fast['open_facilities'], \
        f"open_facilities differ: {sol_ref['open_facilities']} vs {sol_fast['open_facilities']}"
    assert sol_ref['assignments'] == sol_fast['assignments'], \
        f"assignments differ at indices: {[i for i, (a, b) in enumerate(zip(sol_ref['assignments'], sol_fast['assignments'])) if a != b]}"
    assert sol_ref['coverages'] == sol_fast['coverages'], \
        f"coverages differ at indices: {[i for i, (a, b) in enumerate(zip(sol_ref['coverages'], sol_fast['coverages'])) if a != b]}"

    print(f"  [{graph['name']} k={len(facilities)}] ref={t_ref*1000:.3f}ms  fast={t_fast*1000:.3f}ms  speedup={t_ref/t_fast:.1f}x")
    return True
