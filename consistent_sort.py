import graphlib

def consistent_sort(presumably_sorted_lists):
    graph = {}
    for sorted_list in presumably_sorted_lists:
        if 1 == len(sorted_list): graph[sorted_list[0]] = []
        for i in range(len(sorted_list) - 1):
            dest = sorted_list[i + 1]
            source = sorted_list[i]
            if source not in graph: graph[source] = []
            if   dest not in graph: graph[dest] = []
            graph[dest].append(source)
    return list(graphlib.TopologicalSorter(graph).static_order())
