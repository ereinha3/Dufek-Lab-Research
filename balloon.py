import numpy as np
from scipy.optimize import curve_fit, fsolve
import matplotlib.pyplot as plt
from ncep_scraper import retrieve_table
import math

MOLAR_MASS_HELIUM = 4.002602 / 1000  # kg / mol
GAS_CONSTANT = 8.314  # (m^3 Pa) / (K mol)
MOLAR_MASS_DRY_AIR = 28.96 / 1000 # kg / mol
MOLAR_MASS_WATER_VAPOR = 18.02 / 1000  # kg / mol
DENSITY_AIR = 1.225  # Density of air at sea level in kg/m^3 (approximate)
GRAVITY = 9.81  # Acceleration due to gravity in m/s^2
DRAG_COEFFICIENT_SPHERE = 0.47  # Drag coefficient for a sphere
radius = 0.42  # m
popping_pressure_difference = 4600  # Pa
mass_helium = 15 / 1000  # kg
mass_balloon = 47 / 1000 # kg
mass_payload = 0 / 1000 # kg

class Balloon:
    def __init__(self, radius, mass_helium, mass_balloon, mass_payload):
        self.radius = radius
        self.mass_helium = mass_helium
        self.mass_balloon = mass_balloon
        self.moles_helium = mass_helium / MOLAR_MASS_HELIUM
        self.gas_constant = GAS_CONSTANT
        self.molar_mass_dry_air = MOLAR_MASS_DRY_AIR
        self.molar_mass_water_vapor = MOLAR_MASS_WATER_VAPOR
        self.cross_sectional_area = np.pi * radius**2
        self.mass_payload = mass_payload
        self.drag_coefficient = DRAG_COEFFICIENT_SPHERE
        self.x = 0
        self.y = 0
        self.z = 1
        self.vx = 0
        self.vy = 0
        self.vz = 0

        

tracer = Balloon(radius, mass_helium, mass_balloon, mass_payload)


# # Read in data in this format

# # Data provided
# data = retrieve_table()

data = [[1005.0, 42.0, 288.0, 0.0085517, 82.0, 10.14, 9.6],
[1000.0, 149.0, 289.2, 0.00932, 82.0, 7.37, 7.8],
[925.0, 813.0, 291.0, 0.0047, 34.0, 6.48, 38.1],
[850.0, 1538.0, 291.7, 0.00299, 19.0, 4.88, 61.9],
[700.0, 3177.0, 283.0, 0.00335, 31.0, 3.41, 185.0],
[600.0, 4436.0, 273.7, 0.0023, 35.0, 6.08, 189.5],
[500.0, 5868.0, 262.6, 0.001847, 54.0, 5.71, 176.0],
[400.0, 7546.0, 250.9, 0.000539, 33.0, 6.55, 187.0],
[300.0, 9598.0, 235.6, 0.000177, 33.0, 11.11, 200.6],
[250.0, 10829.0, 226.6, -999.0, -999.0, 14.58, 198.8],
[200.0, 12293.0, 223.9, -999.0, -999.0, 20.62, 199.0],
[150.0, 14203.0, 223.6, -999.0, -999.0, 14.91, 209.3],
[100.0, 16762.0, 211.3, -999.0, -999.0, 4.53, 210.5],
[70.0, 18973.0, 212.8, -999.0, -999.0, 4.88, 151.9],
[50.0, 21086.0, 216.2, -999.0, -999.0, 3.98, 107.5],
[30.0, 24353.0, 220.2, -999.0, -999.0, 9.76, 83.5],
[20.0, 27000.0, 225.9, -999.0, -999.0, 11.42, 86.5],
[10.0, 31618.0, 228.0, -999.0, -999.0, 17.42, 87.4]]

# Create numpy arrays from the data above
height = np.array([data[i][1] for i in range(len(data))])
pressure = np.array([(data[i][0] * 100) for i in range(len(data))]) # convert to Pa from mB
temperature = np.array([data[i][2] for i in range(len(data))])
specific_humidity = np.array([data[i][3] if data[i][3] != -999.0 else 0 for i in range(len(data))])
wind_speed = np.array([data[i][5] for i in range(len(data))])
wind_direction = np.array([data[i][6] for i in range(len(data))])


# Define the exponential model
# This produces Pa
def exponential_model(h, P0, H):
    return P0 * np.exp(-h / H)

# Initial guess for P0 (initial pressure in Pa) and H (lapse rate)
initial_guess = [100000, 7500]

# Bounds for P0 and H to ensure they are within realistic ranges
# [pMin, tMin] , [pMax, tMax]
bounds = ([0, 200], [120000, 32000])

# Fit pressure to an exponential
popt, pcov = curve_fit(exponential_model, height, pressure, p0=initial_guess, bounds=bounds)
P0, H = popt
print(f"Fitted Parameters:\nP0 = {P0}\nH = {H}")

# Equal spaces of height
heights_fit = np.linspace(0, 36000, 2000)
# Fitted pressures from model
pressures_fit = exponential_model(heights_fit, P0, H)

# Predict pressure at height h 
def predict_pressure(h):
    return P0 * np.exp(-h / H)

print(predict_pressure(21000))

# Fit temperatures to a cubic
coefficients = np.polyfit(height, temperature, 3)
a, b, c, d = coefficients

# Predict the temperature at height h
def predict_temp(h):
    return a * h**3 + b * h**2 + c * h + d

print(predict_temp(21000))
temps_fit = predict_temp(heights_fit)

volume_at_room_temp = tracer.moles_helium * GAS_CONSTANT * 293.15 / 101325  # m^3
full_volume = 4/3 * np.pi * radius**3  # m^3

density_at_room_temp = mass_helium / volume_at_room_temp  # kg/m^3

coefficients_humidity = np.polyfit(height, specific_humidity, 3)
e, f, i, j = coefficients_humidity

def predict_specific_humidity(h):
    val = e * h**3 + f * h**2 + i * h + j
    return 0 if val < 0 else val

print(predict_specific_humidity(21000))
humidity_fit = [predict_specific_humidity(ele) for ele in heights_fit]

# Predict wind speed at height

def predict_wind_speed(h):
    if h <= height[0]:
        return wind_speed[0]
    if h >= height[-1]:
        return wind_speed[-1]
    index = 0
    for i in range(1, len(height)):
        if h <= height[i]:
            index = i
            break
    slope = (wind_speed[index] - wind_speed[index - 1]) / (height[index] - height[index - 1])
    b = wind_speed[index - 1] - slope * height[index - 1]
    
    return slope * h + b

print(f"Predicted Wind Speed at 21000m : {predict_wind_speed(21000)}")

def predicted_wind_direction(h):
    if h <= height[0]:
        return wind_direction[0]
    if h >= height[-1]:
        return wind_direction[-1]
    index = 0
    for i in range(1, len(height)):
        if h <= height[i]:
            index = i
            break
    slope = (wind_direction[index] - wind_direction[index - 1]) / (height[index] - height[index - 1])
    b = wind_direction[index - 1] - slope * height[index - 1]
    
    return slope * h + b

def vectorize_wind_direction(h):
    return np.array([-math.cos((predicted_wind_direction(h)+90)/180 * math.pi), -math.sin((predicted_wind_direction(h)-90)/180 * math.pi), 0])

print(f"Predicted Wind Direction at 21000m : {predicted_wind_direction(21000)}")
print(f"Predicted Wind Vector at 21000m : <{vectorize_wind_direction(21000)[0]},  {vectorize_wind_direction(21000)[1]}>")
print(f"Predicted Wind Direction at 1000m : {predicted_wind_direction(1000)}")
print(f"Predicted Wind Vector at 1000m : <{vectorize_wind_direction(1000)[0]},  {vectorize_wind_direction(1000)[1]}>")
print(f"Predicted Wind Direction at 10000m : {predicted_wind_direction(10000)}")
print(f"Predicted Wind Vector at 10000m : <{vectorize_wind_direction(10000)[0]},  {vectorize_wind_direction(10000)[1]}>")





def molar_mass_humid_air(spec_humid):
    r = spec_humid / (1 - spec_humid)
    X_w = r / (r + MOLAR_MASS_DRY_AIR / MOLAR_MASS_WATER_VAPOR)
    X_d = 1 - X_w
    return X_d * MOLAR_MASS_DRY_AIR + X_w * MOLAR_MASS_WATER_VAPOR

print(f"Molar mass of humid air: {molar_mass_humid_air(predict_specific_humidity(21000))} at 283.90 K and 1002 mB")
print(f"Molar mass of humid air: {molar_mass_humid_air(0.0086600)} at 285.20 K and 1000 mB")
print(f"Molar mass of dry air: {MOLAR_MASS_DRY_AIR} at 283.90 K and 1002 mB")


# # Function to find the height where densities are equal (neutral buoyancy height) 
# # considering the denisty of the balloon at room temp is constant
# def find_neutral_buoyancy_height(h):
#     return (predict_pressure(h) * MOLAR_MASS_DRY_AIR / (gas_constant * predict_temp(h))) - density_at_room_temp

# # Guess 15000 m
# initial_guess_height = 15000

# # Solve for the height where densities are equal (neutral buoyancy height)
# h_neutral_buoyancy = fsolve(find_neutral_buoyancy_height, initial_guess_height)[0]

# print(f"Height for Neutral Buoyancy: {h_neutral_buoyancy} meters")
# print(f"Actual: {find_neutral_buoyancy_height(h_neutral_buoyancy)}")

# Find balloon volume at height
def balloon_volume_at_height(h):
    volume =  tracer.moles_helium * GAS_CONSTANT * predict_temp(h) / predict_pressure(h)
    return full_volume if volume > full_volume else volume
#Check THIS!!

def predict_air_density(h):
    return predict_pressure(h) * molar_mass_humid_air(predict_specific_humidity(h)) / (GAS_CONSTANT * predict_temp(h))

def predict_balloon_density(h):
    return mass_helium / balloon_volume_at_height(h)
    
def bouyant_force(h):
    return GRAVITY * balloon_volume_at_height(h) * (predict_air_density(h) - predict_balloon_density(h))

def gravitational_force():
    return GRAVITY * mass_balloon + GRAVITY * mass_payload

# VARY THE CROSS SECTIONAL AREA
def drag_force(h, relative_velocity_squared):
    return 0.5 * tracer.drag_coefficient * tracer.cross_sectional_area * predict_air_density(h) * relative_velocity_squared

# Function to find the height where densities are equal (neutral buoyancy height) 
# considering the fully inflated balloon volume
def find_true_neutral_buoyancy_height(h):
    # return (predict_pressure(h) * molar_mass_dry_air / (gas_constant * predict_temp(h))) - (mass_helium / balloon_volume_at_height(h))
    return bouyant_force(h) - gravitational_force()

initial_guess_height = 15000  # Adjust as needed based on your application

# Solve for the height where densities are equal (neutral buoyancy height)
h_neutral_buoyancy = fsolve(find_true_neutral_buoyancy_height, initial_guess_height)[0]

print(f"Height for Neutral Buoyancy: {h_neutral_buoyancy} meters")
print(f"Predicted volume at neutral bouyancy height: {balloon_volume_at_height(h_neutral_buoyancy)}")
print(f"Full volume at neutral bouyancy height: {full_volume}")

def plot_trajectory():
    f = open("trajectory.txt", "w")
    f.write(f"x y z\n")
    f.write(f"{tracer.x} {tracer.y} {tracer.z}\n")
    time_step = 1  # seconds
    total_time = 1000000  # seconds
    # for _ in range(total_time // time_step):
    for i in range(20):
        print(f'\n############### ITERATION {i+1} ##################\n')
        # Calculate the wind velocity and velocity relative to balloon
        wind_velocity = predict_wind_speed(tracer.z) * vectorize_wind_direction(tracer.z)
        print(f"Wind Velocity: {wind_velocity}")
        tracer_velocity = [tracer.vx, tracer.vy, tracer.vz]
        relative_velocity = np.array([tracer_velocity[0] - wind_velocity[0], tracer_velocity[1] - wind_velocity[1], tracer_velocity[2] - wind_velocity[2]])
        print(f"Relative Velocity: {relative_velocity}")
        velocity_squared = sum([i**2 for i in relative_velocity])
        print(f"Velocity Squared: {velocity_squared}")
        # Calculate drag force
        drag = drag_force(tracer.z, velocity_squared)
        print(f"Drag: {drag}")
        # Calculate drag vector
        drag_vector = drag * relative_velocity / math.sqrt(velocity_squared)
        print(f"Drag Vector: {drag_vector}")
        # Calculate bouyant force
        bouyant = bouyant_force(tracer.z)
        print(f"Bouyant: {bouyant}")
        bouyant_vector = bouyant * np.array([0, 0, 1])
        print(f"Bouyant Vector: {bouyant_vector}")
        # Calculate gravitational force
        gravitational = gravitational_force()
        print(f"Gravitational: {gravitational}")
        gravitational_vector = gravitational_force() * np.array([0, 0, -1])
        print(f"Gravitational Vector: {gravitational_vector}")
        # Terminal Rise Velocity
        terminal_rise_velocity_squared = math.sqrt((bouyant - gravitational) / (tracer.drag_coefficient * tracer.cross_sectional_area))
        print(f"Terminal Rise Velocity: {terminal_rise_velocity_squared}")
        # Calculate net force
        net_force = drag_vector + bouyant_vector + gravitational_vector
        print(f"Net Force: {net_force}")
        net_acceleration = net_force / (mass_helium + mass_balloon + mass_payload)
        print(f"Net Acceleration: {net_acceleration}")
        # Calculate new position
        tracer.x += tracer.vx * time_step + 0.5 * net_acceleration[0] * time_step**2
        tracer.y += tracer.vy * time_step + 0.5 * net_acceleration[1] * time_step**2
        tracer.z += tracer.vz * time_step + 0.5 * net_acceleration[2] * time_step**2
        print(f'New Position: {tracer.x}, {tracer.y}, {tracer.z}')
        # Calculate new velocities
        tracer.vx = net_acceleration[0] * time_step
        tracer.vy = net_acceleration[1] * time_step
        tracer.vz = net_acceleration[2] * time_step
        print(f'New Velocities: {tracer.vx}, {tracer.vy}, {tracer.vz}')
        # Write coordinates to file
        f.write(f"{tracer.x} {tracer.y} {tracer.z}\n")
        

    f.close()

plot_trajectory()
        



# # Plot the data as subplots within a single figure
# fig, axs = plt.subplots(2, 2, figsize=(8, 8))

# # Pressure vs. Height
# axs[0, 0].scatter(height, pressure, color='red', label='Data')
# axs[0, 0].plot(heights_fit, pressures_fit, color='blue', label='Fit')
# axs[0, 0].set_xlabel('Height (m)')
# axs[0, 0].set_ylabel('Pressure (Pa)')
# axs[0, 0].set_title('Exponential Fit to Pressure vs. Height Data')
# axs[0, 0].legend()
# axs[0, 0].grid(True)

# # Temperature vs. Height
# axs[0, 1].scatter(height, temperature, color='red', label='Data')
# axs[0, 1].plot(heights_fit, temps_fit, color='blue', label='Fit')
# axs[0, 1].set_xlabel('Height (m)')
# axs[0, 1].set_ylabel('Temperature (K)')
# axs[0, 1].set_title('Cubic Fit to Temperature vs. Height Data')
# axs[0, 1].legend()
# axs[0, 1].grid(True)

# # Specific Humidity vs. Height
# axs[1, 0].scatter(height, specific_humidity, color='red', label='Data')
# axs[1, 0].plot(heights_fit, humidity_fit, color='blue', label='Fit')
# axs[1, 0].set_xlabel('Height (m)')
# axs[1, 0].set_ylabel('Specific Humidity (kg/kg)')
# axs[1, 0].set_title('Cubic Fit to Specific Humidity vs. Height Data')
# axs[1, 0].legend()
# axs[1, 0].grid(True)

# # Adjust layout
# plt.tight_layout()
# plt.show()
