import random
import numpy as np
from users_information import user
from session_information import session
from satellites import fetch_multiple_tle_from_url, generate_satellite_positions, calculate_latency, calculate_synchronization

def generate_sessions(num_sessions, max_users_per_session):
    """
    Generate a list of session objects with randomized users.
    """
    sessions = []
    user_id = 0

    for session_id in range(num_sessions):
        new_session = session(session_id)
        num_users = random.randint(1, max_users_per_session)

        for _ in range(num_users):
            city = random.choice(["New York", "Los Angeles", "London", "Tokyo", "Paris"])
            latitude = random.uniform(-90, 90)
            longitude = random.uniform(-180, 180)
            create_time = random.randint(1609459200, 1672444800)

            new_user = user(user_id, city, latitude, longitude, create_time, session_id)
            new_session.add_user(new_user)
            user_id += 1

        sessions.append(new_session)

    return sessions


def find_best_satellite(user_lat, user_lon, sat_lats, sat_longs, k=3):
    """
    Find the best satellite for a user based on latency and synchronization.
    """
    distances = np.sqrt((sat_lats - user_lat) ** 2 + (sat_longs - user_lon) ** 2)
    closest_indices = np.argsort(distances)[:k]

    best_satellite = None
    min_cost = float('inf')

    for idx in closest_indices:
        latency = calculate_latency(user_lat, user_lon, sat_lats[idx], sat_longs[idx])
        sync_cost = calculate_synchronization(user_lat, user_lon, sat_lats[idx], sat_longs[idx])
        cost = 0.7 * latency + 0.3 * sync_cost
        if cost < min_cost:
            min_cost = cost
            best_satellite = idx

    return best_satellite


if __name__ == "__main__":
    num_sessions = 10
    max_users_per_session = 10
    num_satellites = 10
    num_steps = 1  # Static visualization, so one step is enough
    k = 3  # Number of nearest satellites to consider
    time_step = 60

    TLE_URL = "https://celestrak.com/NORAD/elements/stations.txt"
    tle_data = fetch_multiple_tle_from_url(TLE_URL, num_satellites)
    satellite_positions = generate_satellite_positions(tle_data, time_step, num_steps)
    generated_sessions = generate_sessions(num_sessions, max_users_per_session)

    # Allocation results
    print("User-Satellite Allocation Results:")
    for time in range(num_steps):
        print(f"Time slot: {time + 1}")
        sat_lats = satellite_positions[:, time, 0]
        sat_longs = satellite_positions[:, time, 1]

        for session in generated_sessions:
            for user_obj in session.get_user():
                user_lat, user_lon = user_obj.get_location()
                best_satellite = find_best_satellite(user_lat, user_lon, sat_lats, sat_longs, k)

                print(f"  Satellite {best_satellite} assigned to User {user_obj.get_id()} (Session {session.id})")
