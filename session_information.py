import users_information
import allocation
import random

class session:
    def __init__(self, session_id):
        self.id = session_id
        self.user = []
        self.best_user_relay_path = []
        self.current_user_relay_path = []
        self.cu_set = None
        self.current_relay = None
        self.best_relay = None
        self.bandwidth = random.randint(2, 4)

    def get_bandwidth(self):
        return self.bandwidth
    def get_user(self):
        return self.user

    def get_cu_set(self):
        return self.cu_set

    def get_best_relay(self):
        return self.best_relay

    def get_current_relay(self):
        return self.current_relay

    def get_current_path(self):
        return self.current_user_relay_path
    def add_user(self, to_add):
        self.user.append(to_add)

    def find_k_central(self, satellite_positions, time, k):
        """
        Find the k-central satellites based on user locations.
        :param satellite_positions: Array of satellite positions [num_satellites, num_steps, 2 (lat, lon)].
        :param time: Time index to consider for satellite positions.
        :param k: Number of central satellites to find.
        """
        self.cu_set = users_information.k_center(self.user, satellite_positions, time, k)

    def find_best_relay(self, all_path_set, satellite_num, bandwidth, isl_capacity, isl_max, antenna):
        # TODO:
        self.best_user_relay_path = []
        set_num = len(self.cu_set)
        delay_set = [99999 for i in range(set_num)]
        for i in range(set_num):
            flag = True
            hop = 0
            for user_index in range(len(self.user)):
                if all_path_set[user_index][i] == []:
                    flag = False
                    break
                current_path = allocation.allocate(all_path_set[user_index][i], satellite_num, bandwidth, isl_capacity,
                                                   isl_max, antenna)
                if current_path == 0:
                    flag = False
                    break
                hop += (len(current_path) - 1)
            if flag:
                delay_set[i] = hop
            else:
                delay_set[i] = 99999
        if min(delay_set) == 99999:
            self.best_relay = None
            return 0
        variation = [99999 for i in range(set_num)]
        for i in range(set_num):
            if delay_set[i] == 99999:
                variation[i] = 99999
                continue
            ave = delay_set[i] / (len(self.user))
            for user_index in range(len(self.user)):
                variation[i] += abs(delay_set[i] - ave)
        total_set = [99999 for i in range(set_num)]
        for i in range(set_num):
            total_set[i] = delay_set[i] / len(self.user) + 50 * variation[i]
        self.best_relay = self.cu_set[total_set.index(min(total_set))]
        for user_index in range(len(self.user)):
            self.best_user_relay_path.append(
                allocation.allocate(all_path_set[user_index][i], satellite_num, bandwidth, isl_capacity, isl_max,
                                    antenna))
            self.user[user_index].path = allocation.allocate(all_path_set[user_index][i], satellite_num, bandwidth,
                                                             isl_capacity, isl_max, antenna)

    def switch_relay(self):
        self.current_relay = self.best_relay
        self.current_user_relay_path = self.best_user_relay_path