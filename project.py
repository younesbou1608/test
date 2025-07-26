import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import random
from matplotlib.widgets import Button

# Soccer Field Dimensions
field_length = 105  # Using a smaller scale for simplicity
field_width = 68

# Ball Movement Parameters
initial_pos = np.array([field_length / 2, field_width / 2], dtype=np.float64)

# Define ball_pos and ball_velocity as global variables
ball_pos = initial_pos.copy()

# Initial Positions for Two Drones
drone1_pos = np.array([10, field_width - 10], dtype=np.float64)  # Top left corner
drone2_pos = np.array([field_length - 10, 10], dtype=np.float64)  # Bottom right corner

# Orbital Parameters
max_drone_speed = 0.5  # Maximum distance a drone can move per frame
orbital_distance = 20
angle_offset = np.pi  # 45 degrees offset for each drone
field_center = np.array([field_length / 2, field_width / 2])
reference_angle = np.arctan2(field_center[1] - ball_pos[1], field_center[0] - ball_pos[0])

# Initialize angles for drones
drone1_angle = np.pi / 4  # Initial angle for Drone 1
drone2_angle = -np.pi / 4  # Initial angle for Drone 2 (opposite direction)



# Function to draw the soccer field
def draw_soccer_field():
    """Draws the soccer field layout."""
    global ax
    fig, ax = plt.subplots(figsize=(10.5, 6.8))  # Scaled figure size
    plt.xlim(0, field_length)
    plt.ylim(0, field_width)
    
    # Field Boundary
    rect = patches.Rectangle((0, 0), field_length, field_width, linewidth=1, edgecolor='white', facecolor='green')
    ax.add_patch(rect)
    
    # Midfield Line and Circle
    plt.plot([field_length / 2, field_length / 2], [0, field_width], color="white")
    midfield_circle = plt.Circle((field_length / 2, field_width / 2), 9.15, color='white', fill=False)  # 9.15m radius
    ax.add_patch(midfield_circle)
    
    # Goal Areas
    goal_area = patches.Rectangle((0, (field_width - 18.32) / 2), 5.5, 18.32, linewidth=1, edgecolor='white', fill=False)
    ax.add_patch(goal_area)
    goal_area = patches.Rectangle((field_length - 5.5, (field_width - 18.32) / 2), 5.5, 18.32, linewidth=1, edgecolor='white', fill=False)
    ax.add_patch(goal_area)
    
    plt.axis('scaled')
    plt.axis('off')
    return fig, ax


# Function to draw drones
def draw_drone(ax, drone_pos, drone_color='blue'):
    # Convert drone_pos NumPy array to a tuple for the position
    drone_marker = patches.RegularPolygon(tuple(drone_pos), numVertices=6, radius=2, orientation=np.pi/6, color=drone_color, fill=True)
    ax.add_patch(drone_marker)
    return drone_marker

# Function to generate random velocity for the ball
def random_velocity():
    """Generates a random, slower velocity vector for the ball."""
    speed = random.uniform(1, 5)  # Further reduced speed range for smoother movement
    angle = random.uniform(0, 2 * np.pi)  # Random direction
    return np.array([speed * np.cos(angle), speed * np.sin(angle)], dtype=np.float64)

ball_velocity = random_velocity()


def update_ball_position(delta_t):
    global ball_pos, ball_velocity  # Access global variables
    # Decrease the chance of direction change for smoother movement
    if random.random() < 0.05:  # Reduced to ~5% chance per time step
        ball_velocity = random_velocity()

    # Update position based on velocity
    ball_pos += ball_velocity * delta_t
    ball_pos = np.clip(ball_pos, [0, 0], [field_length, field_width])
    return ball_pos, ball_velocity


# Function to calculate the new position for the drones orbiting the ball
def calculate_orbital_position(ball_pos, drone_id):
    global orbital_distance, reference_angle, angle_offset

    # Update the reference angle to simulate continuous orbital movement
    reference_angle += angle_offset if drone_id == 1 else -angle_offset

    # Calculate new position based on the updated reference angle and orbital distance
    new_drone_pos = np.array([
        ball_pos[0] + orbital_distance * np.cos(reference_angle),
        ball_pos[1] + orbital_distance * np.sin(reference_angle)
    ])

    return np.clip(new_drone_pos, [0, 0], [field_length, field_width])


def move_towards(current_pos, target_pos, max_distance):
    """
    Move from current_pos towards target_pos but do not exceed max_distance.
    """
    direction_vector = target_pos - current_pos
    distance = np.linalg.norm(direction_vector)
    if distance <= max_distance:
        return target_pos
    else:
        # Normalize the direction vector and scale by max_distance
        direction_vector /= distance
        new_pos = current_pos + direction_vector * max_distance
        return new_pos


# Function to update the positions of both drones
def update_drones_positions():
    global drone1_pos, drone2_pos, drone1_angle, drone2_angle

    # Angular speed determines how fast drones orbit around the ball
    angular_speed = 0.02  # Radians per frame

    # Update angles for each drone
    drone1_angle += angular_speed
    drone2_angle -= angular_speed  # Negative for opposite direction

    # Calculate new positions based on updated angles
    drone1_pos = ball_pos + orbital_distance * np.array([np.cos(drone1_angle), np.sin(drone1_angle)])
    drone2_pos = ball_pos + orbital_distance * np.array([np.cos(drone2_angle), np.sin(drone2_angle)])

    # Ensure new positions are within field boundaries
    drone1_pos = np.clip(drone1_pos, [0, 0], [field_length, field_width])
    drone2_pos = np.clip(drone2_pos, [0, 0], [field_length, field_width])

# Control functions (start, pause, reset) and update_frame function
running = False

def start(event):
    global running
    running = True

def pause(event):
    global running
    running = False

def reset(event):
    global ball_pos, ball_velocity, drone1_pos, drone2_pos
    ball_pos = initial_pos.copy()
    ball_velocity = random_velocity()
    drone1_pos = np.array([10, field_width - 10], dtype=np.float64)
    drone2_pos = np.array([field_length - 10, 10], dtype=np.float64)
    running = False
    update_frame()  # Ensure the frame is updated immediately when reset

def update_frame():
    global ball, drone1, drone2
    if running:
        update_ball_position(0.1)
        update_drones_positions()
        ball.set_center(ball_pos)
        drone1.remove()  # Remove the previous drone shape
        drone2.remove()  # Remove the previous drone shape
        drone1 = draw_drone(ax, drone1_pos, 'blue')  # Draw the new drone shape
        drone2 = draw_drone(ax, drone2_pos, 'red')  # Draw the new drone shape
        plt.draw()

def simulate_ball_movement():
    fig, ax = draw_soccer_field()
    global ball, drone1,drone2  # Declare ball and drone as global to access them in update_frame
    ball = plt.Circle(ball_pos, 0.7, color='white')  # Initialize ball
    drone1 = draw_drone(ax, drone1_pos, 'blue')
    drone2 = draw_drone(ax, drone2_pos, 'red')
    ax.add_patch(ball)

    # Initialize Buttons
    ax_start = plt.axes([0.7, 0.01, 0.1, 0.075])
    ax_pause = plt.axes([0.81, 0.01, 0.1, 0.075])
    ax_reset = plt.axes([0.59, 0.01, 0.1, 0.075])
    btn_start = Button(ax_start, 'Start')
    btn_pause = Button(ax_pause, 'Pause')
    btn_reset = Button(ax_reset, 'Reset')
    btn_start.on_clicked(start)
    btn_pause.on_clicked(pause)
    btn_reset.on_clicked(reset)

    # Timer for updating the frame
    timer = fig.canvas.new_timer(interval=20)
    timer.add_callback(update_frame)
    timer.start()

    plt.show()

simulate_ball_movement()
