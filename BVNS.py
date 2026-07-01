from solution import calculate_objective, open_random_facilities, grasp_constructive, check_feasibility, evaluate_facilities_fast
from local_search_first_improvement import local_search_first_improvement
from load_instances import build_instances, build_pmed_instances
import random
import time
import os
import math


def shake(graph, solution, k):
    """
    Perturbation: randomly replaces k open facilities with k distinct closed ones.
    Always performs a full evaluate_facilities call so the returned solution is
    consistent with the capacity model.
    """
    current_facilities = solution['open_facilities'].copy()
    all_nodes = set(range(len(graph['nodes'])))
    non_selected_nodes = list(all_nodes - set(current_facilities))

    k = min(k, len(current_facilities))
    nodes_to_remove = random.sample(current_facilities, k)
    nodes_to_add = random.sample(non_selected_nodes, k)

    new_facilities = [f for f in current_facilities if f not in nodes_to_remove]
    new_facilities.extend(nodes_to_add)

    return evaluate_facilities_fast(graph, new_facilities)


def bvns(graph, num_facilities, time_limit=1800, num_starts=10000, verbose=True):
    """
    BVNS with multistart: num_starts runs of the full VNS loop (N=1..kmax),
    each starting from S_best. Stops early if time_limit (global) is reached.
    """
    deadline = time.time() + time_limit
    kmax = max(1, math.floor(num_facilities * 0.3))
    #S_best = None
    #for i in range(1):
    #    S = open_random_facilities(graph, num_facilities)
    #    if S_best is None or calculate_objective(graph,S_best) < calculate_objective(graph,S):
    #        S_best = S.copy()

    S_best = grasp_constructive(graph, num_facilities)
    S_best = local_search_first_improvement(graph, S_best, deadline, verbose=verbose)
    best_objective = calculate_objective(graph, S_best)

    for start in range(1, num_starts + 1):
        if time.time() >= deadline:
            break

        N = 1
        S = S_best

        while N <= kmax and time.time() < deadline:
            S_prime = shake(graph, S, N)
            S_double_prime = local_search_first_improvement(graph, S_prime, deadline, verbose=verbose)
            new_objective = calculate_objective(graph, S_double_prime)

            if new_objective > best_objective:
                print(f"    [BVNS start {start}/{num_starts}] Global improvement: {best_objective:.2f} -> {new_objective:.2f}  nodes={S_double_prime['open_facilities']}")
                S_best = S_double_prime
                best_objective = new_objective

            if new_objective > calculate_objective(graph, S):
                S = S_double_prime
                N = 1
            else:
                N += 1

    return S_best


if __name__ == '__main__':
    random.seed(123)

    directory = 'Instances'
    graphs = build_instances(directory)
    pmed_graphs = build_pmed_instances(directory)
    graphs.update(pmed_graphs)

    os.makedirs('Resultados', exist_ok=True)

    k_values = {
        'fcmclp324': [1, 4, 7],
        'fcmclp402': [1, 5, 9],
        'fcmclp500': [2, 7],
        'fcmclp708': [2, 8],
        'fcmclp818': [2, 15],
        'pmed32':    [1, 6, 12],
        'pmed39':    [1, 7],
    }

    path_cobertura = os.path.join('Resultados', 'cobertura_bvns.txt')
    path_completo = os.path.join('Resultados', 'completo_bvns.txt')

    total_start_time = time.time()

    with open(path_cobertura, 'w', encoding='utf-8') as f_cob, \
            open(path_completo, 'w', encoding='utf-8') as f_com:

        for graph in graphs.values():
            name = graph['name']
            if name not in k_values:
                continue

            total_demand = sum(node[1] for node in graph['nodes'])

            print(f"\n{'=' * 60}")
            print(f"{name}:")
            print(f"{'=' * 60}")

            f_cob.write(f"{name}\n")
            f_com.write(f"{name}\n")
            f_com.write("k;Coverage;Time;Final nodes;Objective\n")

            f_cob.flush()
            f_com.flush()

            for k in k_values[name]:
                print(f"\n  k={k}:")

                start_time = time.time()

                final_solution = bvns(graph, k, time_limit=1800, num_starts=10000, verbose=True)
                final_objective = calculate_objective(graph, final_solution)
                final_coverage = (final_objective / total_demand) * 100
                final_nodes = final_solution['open_facilities']

                elapsed_time = time.time() - start_time

                final_cov_str = f"{final_coverage:.2f}".replace('.', ',')
                time_str = f"{elapsed_time:.4f}".replace('.', ',')

                print(f"  Final solution: {final_coverage:.2f}%, nodes: {final_nodes}, time: {elapsed_time:.4f}s")
                check_feasibility(graph, final_solution, k)

                f_cob.write(f"{final_cov_str};{time_str}\n")
                f_com.write(f"{k};{final_cov_str};{time_str};{final_nodes};{final_objective:.2f}\n")

                f_cob.flush()
                f_com.flush()

            f_cob.write("\n")
            f_com.write("\n")
            f_cob.flush()
            f_com.flush()

    total_time = time.time() - total_start_time
    print(f"Tiempo total de ejecución: {total_time:.2f} segundos")
