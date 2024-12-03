import networkx as nx
import sys


def search_alternate_path(G, i, j):
    return nx.all_shortest_paths(G, source=i, target=j)


def allocate(path_set, satellite_num, bandwidth, isl_capacity, isl_max, antenna):
    # path_set=search_alternate_path(G, i, j)
    path_set_num = len(path_set)
    activate_counter = [0 for i in range(path_set_num)]
    exist = False
    for index in range(path_set_num):
        isavailable = True
        # check antenna remain
        for node_index in range(len(path_set[index])):
            if node_index == 0 or node_index == len(path_set[index])-1:
                if path_set[index][node_index] < satellite_num and antenna[path_set[index][node_index]] < 1:
                    isavailable = False
                    activate_counter[index] = -1
                    break
            else:
                if path_set[index][node_index] < satellite_num and antenna[path_set[index][node_index]] < 2:
                    isavailable = False
                    activate_counter[index] = -1
                    break
        # check bandwidth remain
        for node_index in range(len(path_set[index])-1):
           # check whether it is an ISL
            if path_set[index][node_index] < satellite_num and path_set[index][node_index+1] < satellite_num:
                if isl_capacity[path_set[index][node_index]][path_set[index][node_index+1]] <= bandwidth:
                    isavailable = False
                    activate_counter[index] = -1
                    break
                # check whether the link is already activated
                elif isl_capacity[path_set[index][node_index]][path_set[index][node_index+1]] < isl_max:
                    activate_counter[index] += 1
            # TODO: also consider ICL, CSL...
            elif path_set[index][node_index] > satellite_num and path_set[index][node_index+1] > satellite_num:
                if isavailable == False:
                    continue
        exist = True
    if exist == False:
        print("No available path!\n")
        return 0
        sys.exit(1)
    best_path_index = activate_counter.index(max(activate_counter))
    best_path = path_set[best_path_index]
    return best_path


def reset_antenna(current_path, antenna, satellite_num):
    for node_index in range(len(current_path)):
        if node_index == 0 or node_index == len(current_path)-1:
            if current_path[node_index] < satellite_num:
                antenna[current_path[node_index]] += 1
        else:
            if current_path[node_index] < satellite_num:
                antenna[current_path[node_index]] += 2
    return antenna


def reset_isl_capacity(current_path, bandwidth, isl_capacity, satellite_num):
    for node_index in range(len(current_path)-1):
        if current_path[node_index] < satellite_num and current_path[node_index+1] < satellite_num:
            isl_capacity[current_path[node_index]][current_path[node_index+1]] += bandwidth
            isl_capacity[current_path[node_index+1]][current_path[node_index]] += bandwidth
    return isl_capacity


def update_antenna(best_path, antenna, satellite_num):
    for node_index in range(len(best_path)):
        if node_index == 0 or node_index == len(best_path)-1:
            if best_path[node_index] < satellite_num:
                antenna[best_path[node_index]] -= 1
        else:
            if best_path[node_index] < satellite_num:
                antenna[best_path[node_index]] -= 2
    return antenna


def update_isl_capacity(best_path, bandwidth, isl_capacity, satellite_num):
    for node_index in range(len(best_path)-1):
        if best_path[node_index] < satellite_num and best_path[node_index+1] < satellite_num:
            isl_capacity[best_path[node_index]][best_path[node_index+1]] -= bandwidth
            isl_capacity[best_path[node_index+1]][best_path[node_index]] -= bandwidth
    return isl_capacity

