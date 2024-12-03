import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from satellites import fetch_tle_data, generate_dynamic_satellite_positions, calculate_latency, calculate_synchronization


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


# Parameters
num_satellites = 30
num_users = 20
num_steps = 100
k_nearest = 3

TLE_URL = "https://www.celestrak.com/NORAD/elements/stations.txt"
tle_data = fetch_tle_data(TLE_URL, num_satellites)
satellite_positions = generate_dynamic_satellite_positions(tle_data, num_steps)

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
ax.set_title('Dynamic Satellite and User Assignments Over Time')
ax.legend(loc='upper left')
ax.grid(True)

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

        best_satellite_idx = find_best_satellite(user_lat, user_lon, sat_lats, sat_longs, k=k_nearest)

        # Draw a line connecting the user to the best satellite
        line = ax.plot([user_lon, sat_longs[best_satellite_idx]],
                       [user_lat, sat_lats[best_satellite_idx]],
                       color='green', lw=0.5, alpha=0.7)[0]
        line_segments.append(line)

    return satellite_scatter, user_scatter, *line_segments


ani = FuncAnimation(fig, update, frames=num_steps, interval=500, blit=False)
plt.show()
