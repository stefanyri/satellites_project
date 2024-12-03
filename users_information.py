import scipy.io as scio
import heapq


class user:
    def __init__(self, id, city, latitude, longitude, create_time, session):
        self.id = id
        self.latitude = latitude
        self.city = city
        self.longitude = longitude
        self.create_time = create_time
        self.session = session
        self.path = None

    def get_city(self):
        return self.city

    def get_location(self):
        return [self.latitude, self.longitude]

    def get_id(self):
        return self.id

def find_user_center(user_list):
    user_num = len(user_list)
    mean_latitude = mean_longitude = 0
    for i in range(user_num):
        mean_latitude += user_list[i].latitude
        mean_longitude += user_list[i].longitude
    mean_latitude /= user_num
    mean_longitude /= user_num
    return [mean_latitude, mean_longitude]
def k_center(user_list, satellite_positions, time, k):
    """
    Find k satellites that are closest to the user center.
    :param user_list: List of user objects.
    :param satellite_positions: Array of satellite positions [num_satellites, num_steps, 2 (lat, lon)].
    :param time: Time index to consider for satellite positions.
    :param k: Number of closest satellites to find.
    :return: Indices of the k-central satellites.
    """
    user_center = find_user_center(user_list)
    distance_list = []

    for sat_position in satellite_positions[:, time]:
        latitude, longitude = sat_position
        distance = (latitude - user_center[0]) ** 2 + (longitude - user_center[1]) ** 2
        distance_list.append(distance)

    # Indices of the k closest satellites
    min_indices = heapq.nsmallest(k, range(len(distance_list)), key=distance_list.__getitem__)
    return min_indices
