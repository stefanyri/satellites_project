import requests


def fetch_multiple_tle_from_url(tle_url, num_satellites=10):
    """
    Fetch TLE lines for the first N satellites in a TLE file.
    :param tle_url: URL of the TLE file.
    :param num_satellites: Number of satellites to fetch TLE data for.
    :return: List of tuples, each containing (satellite name, TLE line 1, TLE line 2).
    """
    # Download the TLE file
    response = requests.get(tle_url)
    if response.status_code != 200:
        raise ValueError(f"Failed to fetch TLE data from {tle_url}")

    # Split the file into lines
    lines = response.text.splitlines()

    # Collect TLE data
    satellites_data = []
    i = 0
    while i < len(lines) and len(satellites_data) < num_satellites:
        name = lines[i].strip()
        if i + 2 < len(lines):  # Ensure there are two more lines for TLE data
            tle_line1 = lines[i + 1].strip()
            tle_line2 = lines[i + 2].strip()
            satellites_data.append((name, tle_line1, tle_line2))
        i += 3  # Move to the next satellite (names and 2 TLE lines)

    return satellites_data


# Fetch TLE data for up to 10 satellites from CelesTrak
TLE_URL = "https://celestrak.com/NORAD/elements/stations.txt"
satellites = fetch_multiple_tle_from_url(TLE_URL, num_satellites=10)

# Print the fetched TLE data
for sat in satellites:
    print(f"Satellite Name: {sat[0]}")
    print(f"TLE Line 1: {sat[1]}")
    print(f"TLE Line 2: {sat[2]}")
    print()
