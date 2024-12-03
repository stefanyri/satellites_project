import requests
import ephem
import numpy as np
import datetime


def fetch_multiple_tle_from_url(tle_url, num_satellites=10):
    """
    Fetch TLE lines for the first N satellites in a TLE file.
    :param tle_url: URL of the TLE file.
    :param num_satellites: Number of satellites to fetch TLE data for.
    :return: List of tuples, each containing (satellite name, TLE line 1, TLE line 2).
    """
    response = requests.get(tle_url)
    if response.status_code != 200:
        raise ValueError(f"Failed to fetch TLE data from {tle_url}")

    lines = response.text.splitlines()
    satellites_data = []
    i = 0
    while i < len(lines) and len(satellites_data) < num_satellites:
        name = lines[i].strip()
        if i + 2 < len(lines):  # Ensure there are two more lines for TLE data
            tle_line1 = lines[i + 1].strip()
            tle_line2 = lines[i + 2].strip()
            satellites_data.append((name, tle_line1, tle_line2))
        i += 3  # Move to the next satellite (name + 2 TLE lines)
    return satellites_data


def generate_satellite_positions(tle_data, time_step, num_steps):
    """
    Generate positions for satellites over time.
    :param tle_data: List of tuples (satellite_name, TLE line 1, TLE line 2).
    :param time_step: Time interval between steps (in seconds).
    :param num_steps: Number of time steps.
    :return: NumPy array of shape [num_satellites, num_steps, 2 (lat, lon)].
    """
    observer = ephem.Observer()
    observer.lat, observer.lon = '0', '0'  # Example location (Equator)

    num_satellites = len(tle_data)
    positions = np.zeros((num_satellites, num_steps, 2))  # [num_satellites, num_steps, 2 (lat, lon)]

    for sat_index, (name, tle_line1, tle_line2) in enumerate(tle_data):
        sat = ephem.readtle(name, tle_line1, tle_line2)
        for step in range(num_steps):
            time_offset = datetime.timedelta(seconds=step * time_step)
            observer.date = datetime.datetime.now(datetime.timezone.utc) + time_offset
            sat.compute(observer)
            positions[sat_index, step, 0] = np.degrees(sat.sublat)  # Latitude
            positions[sat_index, step, 1] = np.degrees(sat.sublong)  # Longitude

    return positions


def calculate_latency(user_lat, user_lon, sat_lat, sat_lon, base_latency=50):
    """
    Calculate latency based on distance and base latency.
    :param user_lat: User latitude.
    :param user_lon: User longitude.
    :param sat_lat: Satellite latitude.
    :param sat_lon: Satellite longitude.
    :param base_latency: Base latency in ms.
    :return: Latency in ms.
    """
    distance = np.sqrt((sat_lat - user_lat) ** 2 + (sat_lon - user_lon) ** 2)
    return base_latency + distance * 10  # Simulate latency based on distance


def calculate_synchronization(user_lat, user_lon, sat_lat, sat_lon):
    """
    Simulate synchronization cost based on relative positions.
    :param user_lat: User latitude.
    :param user_lon: User longitude.
    :param sat_lat: Satellite latitude.
    :param sat_lon: Satellite longitude.
    :return: Synchronization cost (lower is better).
    """
    return np.abs(user_lat - sat_lat) + np.abs(user_lon - sat_lon)


if __name__ == "__main__":
    # Fetch TLE data
    TLE_URL = "https://celestrak.com/NORAD/elements/stations.txt"
    try:
        tle_data = fetch_multiple_tle_from_url(TLE_URL, num_satellites=10)
        print("Fetched TLE Data:")
        for sat_name, line1, line2 in tle_data:
            print(f"Satellite Name: {sat_name}")
            print(f"  TLE Line 1: {line1}")
            print(f"  TLE Line 2: {line2}")
        print()

        # Generate satellite positions
        satellite_positions = generate_satellite_positions(tle_data, time_step=60, num_steps=10)
        print("Generated Satellite Positions:")
        for sat_index, positions in enumerate(satellite_positions):
            print(f"Satellite Index: {sat_index}")
            for step, (latitude, longitude) in enumerate(positions):
                print(f"  Time Step {step}: Latitude {latitude:.4f}, Longitude {longitude:.4f}")
    except ValueError as e:
        print(f"Error: {e}")


def fetch_tle_data(tle_url, num_satellites=10):
    """
    Fetch real TLE data for satellites from Celestrak.
    :param tle_url: URL of the TLE file.
    :param num_satellites: Number of satellites to fetch.
    :return: List of (satellite name, TLE line 1, TLE line 2).
    """
    response = requests.get(tle_url)
    if response.status_code != 200:
        raise ValueError(f"Failed to fetch TLE data from {tle_url}")

    lines = response.text.splitlines()
    tle_data = []

    # Parsing TLE data
    for i in range(0, len(lines), 3):
        if i + 2 < len(lines):
            satellite_name = lines[i].strip()
            tle_line1 = lines[i + 1].strip()
            tle_line2 = lines[i + 2].strip()
            tle_data.append((satellite_name, tle_line1, tle_line2))

        if len(tle_data) >= num_satellites:
            break

    return tle_data
def generate_dynamic_satellite_positions(tle_data, num_steps, time_step=60):
    """
    Generate positions for satellites over time using pyephem and real TLE data.
    :param tle_data: List of (satellite_name, TLE line 1, TLE line 2).
    :param num_steps: Number of time steps to simulate.
    :param time_step: Time interval between each step (in seconds).
    :return: NumPy array of shape [num_satellites, num_steps, 2 (lat, lon)].
    """
    observer = ephem.Observer()
    observer.lat, observer.lon = '0', '0'  # Set observer at equator for simplicity
    observer.elevation = 0  # Sea level

    num_satellites = len(tle_data)
    positions = np.zeros((num_satellites, num_steps, 2))  # [num_satellites, num_steps, 2 (lat, lon)]

    for sat_index, (sat_name, tle_line1, tle_line2) in enumerate(tle_data):
        sat = ephem.readtle(sat_name, tle_line1, tle_line2)
        for step in range(num_steps):
            observer.date = ephem.now() + ephem.second * step * time_step
            sat.compute(observer)
            positions[sat_index, step, 0] = np.degrees(sat.sublat)  # Latitude
            positions[sat_index, step, 1] = np.degrees(sat.sublong)  # Longitude

    return positions