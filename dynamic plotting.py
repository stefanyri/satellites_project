import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import requests
import ephem
from satellites import calculate_synchronization,calculate_latency

def fetch_tle_data(tle_url, num_satellites=10):
    response = requests.get(tle_url)
    if response.status_code != 200:
        raise ValueError(f"Failed to fetch TLE data from {tle_url}")

    lines = response.text.splitlines()
    tle_data = []

    for i in range(0, len(lines), 3):
        if i + 2 < len(lines):
            satellite_name = lines[i].strip()
            tle_line1 = lines[i + 1].strip()
            tle_line2 = lines[i + 2].strip()
            tle_data.append((satellite_name, tle_line1, tle_line2))

        if len(tle_data) >= num_satellites:
            break

    return tle_data


def generate_satellite_positions(tle_data, num_steps, time_step=60):
    observer = ephem.Observer()
    observer.lat, observer.lon = '0', '0'
    observer.elevation = 0

    num_satellites = len(tle_data)
    positions = np.zeros((num_satellites, num_steps, 2))

    for sat_index, (sat_name, tle_line1, tle_line2) in enumerate(tle_data):
        sat = ephem.readtle(sat_name, tle_line1, tle_line2)
        for step in range(num_steps):
            observer.date = ephem.now() + ephem.second * step * time_step
            sat.compute(observer)
            positions[sat_index, step, 0] = np.degrees(sat.sublat)
            positions[sat_index, step, 1] = np.degrees(sat.sublong)

    return positions

# Parameters
num_satellites = 10
num_users = 20
num_steps = 100
k_nearest = 3
latency_weight = 0.7  # Weight for latency in the cost function
synchronization_weight = 0.3  # Weight for synchronization in the cost function

TLE_URL = "https://www.celestrak.com/NORAD/elements/stations.txt"
tle_data = fetch_tle_data(TLE_URL, num_satellites)
satellite_positions = generate_satellite_positions(tle_data, num_steps)

user_latitudes = np.random.uniform(-90, 90, num_users)
user_longitudes = np.random.uniform(-180, 180, num_users)

fig, ax = plt.subplots(figsize=(10, 6))
satellite_scatter = ax.scatter([], [], color='red', label='Satellites', alpha=0.6)
user_scatter = ax.scatter(user_longitudes, user_latitudes, color='blue', label='Users', alpha=0.6)
line_segments = []

ax.set_xlim(-180, 180)
ax.set_ylim(-90, 90)
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.set_title('Satellite and User Positions Over Time')
ax.legend(loc='upper left')
ax.grid(True)


def find_best_satellite(user_lat, user_lon, sat_lats, sat_longs, k=3):
    """
    Find the best satellite for a user based on latency and synchronization.
    :param user_lat: Latitude of the user.
    :param user_lon: Longitude of the user.
    :param sat_lats: Array of satellite latitudes.
    :param sat_longs: Array of satellite longitudes.
    :param k: Number of closest satellites to consider.
    :return: Index of the best satellite.
    """
    distances = np.sqrt((sat_lats - user_lat) ** 2 + (sat_longs - user_lon) ** 2)
    closest_indices = np.argsort(distances)[:k]

    best_satellite = None
    min_cost = float('inf')

    for idx in closest_indices:
        latency = calculate_latency(user_lat, user_lon, sat_lats[idx], sat_longs[idx])
        sync_cost = calculate_synchronization(user_lat, user_lon, sat_lats[idx], sat_longs[idx])
        cost = latency_weight * latency + synchronization_weight * sync_cost

        if cost < min_cost:
            min_cost = cost
            best_satellite = idx

    return best_satellite


def update(frame):
    global line_segments
    for line in line_segments:
        line.remove()
    line_segments = []

    sat_lats = satellite_positions[:, frame, 0]
    sat_longs = satellite_positions[:, frame, 1]

    satellite_scatter.set_offsets(np.c_[sat_longs, sat_lats])

    for i in range(num_users):
        user_lat = user_latitudes[i]
        user_lon = user_longitudes[i]

        # Select the best satellite considering latency and synchronization
        best_satellite_idx = find_best_satellite(user_lat, user_lon, sat_lats, sat_longs, k=k_nearest)

        # Draw a line between the user and the best satellite
        line = ax.plot([user_lon, sat_longs[best_satellite_idx]],
                       [user_lat, sat_lats[best_satellite_idx]],
                       color='green', lw=0.5, alpha=0.7)[0]
        line_segments.append(line)

    return satellite_scatter, user_scatter, *line_segments


ani = FuncAnimation(fig, update, frames=num_steps, interval=500, blit=False)
plt.show()
