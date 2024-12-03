import random
import numpy as np
import matplotlib.pyplot as plt
from users_information import user
from session_information import session
from satellites import fetch_multiple_tle_from_url, generate_satellite_positions

def generate_sessions(num_sessions, max_users_per_session):
    """
    Generate a list of session objects with randomized users.
    :param num_sessions: Number of sessions to generate.
    :param max_users_per_session: Maximum number of users in a single session.
    :return: A list of session instances.
    """
    sessions = []
    user_id = 0  # Counter for unique user IDs

    for session_id in range(num_sessions):
        # Create a new session
        new_session = session(session_id)

        # Determine how many users are in this session
        num_users = random.randint(1, max_users_per_session)

        # Generate and add users to the session
        for _ in range(num_users):
            # Randomized user attributes
            city = random.choice(["New York", "Los Angeles", "London", "Tokyo", "Paris"])
            latitude = random.uniform(-90, 90)  # Latitude range
            longitude = random.uniform(-180, 180)  # Longitude range
            create_time = random.randint(1609459200, 1672444800)  # Random timestamp (2021-2023)
            user_session_id = session_id  # Users inherit session ID

            # Create a user and add them to the session
            new_user = user(user_id, city, latitude, longitude, create_time, user_session_id)
            new_session.add_user(new_user)

            # Increment user ID counter
            user_id += 1

        sessions.append(new_session)

    return sessions

if __name__ == "__main__":
    num_sessions = 10
    max_users_per_session = 10
    num_satellites = 10
    time_step = 60
    num_steps = 100

    # Fetch TLE data for multiple satellites
    TLE_URL = "https://celestrak.com/NORAD/elements/stations.txt"
    tle_data = fetch_multiple_tle_from_url(TLE_URL, num_satellites)

    satellite_positions = generate_satellite_positions(tle_data, time_step, num_steps)
    generated_sessions = generate_sessions(num_sessions, max_users_per_session)

    for session in generated_sessions:
        session.find_k_central(satellite_positions, time=10, k=3)

    for session in generated_sessions:
        print(f"Session ID: {session.id}")
        for user in session.get_user():
            print(f"  User ID: {user.get_id()}, City: {user.get_city()}, Location: {user.get_location()}")



# Parameters
num_satellites = 50  # Number of satellites
num_users = 100  # Number of users

# Generate random satellite positions (latitude, longitude)
satellite_latitudes = np.random.uniform(-90, 90, num_satellites)  # Latitude range from -90 to 90
satellite_longitudes = np.random.uniform(-180, 180, num_satellites)  # Longitude range from -180 to 180

# Generate random user positions (latitude, longitude)
user_latitudes = np.random.uniform(-90, 90, num_users)
user_longitudes = np.random.uniform(-180, 180, num_users)


# Create a scatter plot for visualization
def plot_positions(satellite_latitudes, satellite_longitudes, user_latitudes, user_longitudes):
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot satellites in red
    ax.scatter(satellite_longitudes, satellite_latitudes, color='red', label='Satellites', alpha=0.6)

    # Plot users in blue
    ax.scatter(user_longitudes, user_latitudes, color='blue', label='Users', alpha=0.6)

    # Labels and title
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_title(f'Satellite and User Positions ({num_satellites} Satellites, {num_users} Users)')
    ax.legend(loc='upper left')

    plt.grid(True)
    plt.show()


# Call the plot function to visualize
plot_positions(satellite_latitudes, satellite_longitudes, user_latitudes, user_longitudes)
