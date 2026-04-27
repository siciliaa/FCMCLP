from solution import (
    calculate_objective,
    build_solution_state,
    evaluate_swap,
)
from load_instances import build_instances, build_pmed_instances
import random
import time
import os


def local_search_first_improvement(graph, initial_solution, deadline, verbose=True):
    """
    First-improvement local search over the 1-swap neighborhood.

    At each outer iteration the open and closed node lists are shuffled and
    the first swap (node_out, node_in) that strictly improves the objective
    is accepted. Stops when no improving swap exists or deadline (time.time())
    is exceeded.

    Returns the locally optimal solution (or best found before deadline).
    """
    num_facilities = len(initial_solution['open_facilities'])
    state = build_solution_state(graph, initial_solution)
    current_objective = calculate_objective(graph, initial_solution)

    all_nodes = set(range(len(graph['nodes'])))

    improvement_found = True
    iteration = 0

    while improvement_found and time.time() < deadline:
        improvement_found = False
        iteration += 1

        selected_nodes = state['open_facilities'].copy()
        non_selected_nodes = list(all_nodes - set(selected_nodes))

        random.shuffle(selected_nodes)
        random.shuffle(non_selected_nodes)

        for node_out in selected_nodes:
            if time.time() >= deadline:
                break
            for node_in in non_selected_nodes:
                new_state, new_objective = evaluate_swap(graph, state, node_out, node_in)

                if new_objective > current_objective:
                    state = new_state
                    current_objective = new_objective
                    improvement_found = True
                    break

            if improvement_found:
                break

    assert len(state['open_facilities']) == num_facilities

    return {
        'open_facilities': state['open_facilities'],
        'assignments': state['assignments'],
        'coverages': state['coverages'],
    }


if __name__ == '__main__':
    from solution import open_random_facilities, check_feasibility
    random.seed(123)

    directory = 'Instances'
    graphs = build_instances(directory)
    pmed_graphs = build_pmed_instances(directory)
    graphs.update(pmed_graphs)

    os.makedirs('Resultados', exist_ok=True)

    k_ranges = {
        'fcmclp324': 7,
        'fcmclp402': 9,
        'fcmclp500': 13,
        'fcmclp708': 15,
        'fcmclp818': 15,
        'pmed32': 12,
        'pmed39': 13,
    }

    path_cobertura = os.path.join('Resultados', 'cobertura_local_search_first.txt')
    path_completo = os.path.join('Resultados', 'completo_local_search_first.txt')

    total_start_time = time.time()

    with open(path_cobertura, 'w', encoding='utf-8') as f_cob, \
            open(path_completo, 'w', encoding='utf-8') as f_com:

        for graph in graphs.values():
            name = graph['name']
            if name not in k_ranges:
                continue
            max_k = k_ranges.get(name, 7)
            total_demand = sum(node[1] for node in graph['nodes'])

            print(f"\n{'=' * 60}")
            print(f"{name}:")
            print(f"{'=' * 60}")

            f_cob.write(f"{name}\n")
            f_com.write(f"{name}\n")
            f_com.write("k;Cobertura Inicial;Cobertura Final;Tiempo;Nodos iniciales;Nodos finales;Objetivo Inicial;Objetivo Final\n")

            f_cob.flush()
            f_com.flush()

            for k in range(1, max_k + 1):
                print(f"\n  k={k}:")

                start_time = time.time()
                deadline = start_time + 1800

                initial_solution = open_random_facilities(graph, k)
                initial_objective = calculate_objective(graph, initial_solution)
                initial_coverage = (initial_objective / total_demand) * 100
                initial_nodes = initial_solution['open_facilities'].copy()

                print(f"  Solución inicial: {initial_coverage:.2f}%, nodos: {initial_nodes}")

                final_solution = local_search_first_improvement(graph, initial_solution, deadline, verbose=True)
                final_objective = calculate_objective(graph, final_solution)
                final_coverage = (final_objective / total_demand) * 100
                final_nodes = final_solution['open_facilities']

                elapsed_time = time.time() - start_time

                final_cov_str = f"{final_coverage:.2f}".replace('.', ',')
                initial_cov_str = f"{initial_coverage:.2f}".replace('.', ',')
                time_str = f"{elapsed_time:.4f}".replace('.', ',')

                print(f"  Solución final: {final_coverage:.2f}%, nodos: {final_nodes}, tiempo: {elapsed_time:.4f}s")
                check_feasibility(graph, final_solution, k)

                f_cob.write(f"{final_cov_str};{time_str}\n")
                f_com.write(f"{k};{initial_cov_str};{final_cov_str};{time_str};{initial_nodes};{final_nodes};{initial_objective:.2f};{final_objective:.2f}\n")

                f_cob.flush()
                f_com.flush()

            f_cob.write("\n")
            f_com.write("\n")
            f_cob.flush()
            f_com.flush()

    total_time = time.time() - total_start_time
    print(f"Tiempo total de ejecución: {total_time:.2f} segundos")
