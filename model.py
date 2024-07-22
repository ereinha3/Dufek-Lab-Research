import numpy as np
from scipy.optimize import curve_fit, fsolve
import matplotlib.pyplot as plt
from ncep_scraper import retrieve_table
import math
from sklearn.preprocessing import StandardScaler
import tensorflow as tf


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
data = retrieve_table(2024, 7, 16, 0, 45, -125)
data1 = retrieve_table(2024, 7, 16, 6, 45, -125)
data2 = retrieve_table(2024, 7, 16, 12, 45, -125)
data3 = retrieve_table(2024, 7, 16, 18, 45, -125)

# Create numpy arrays from the data above
height = np.array([data[i][1] for i in range(len(data))])
pressure = np.array([(data[i][0] * 100) for i in range(len(data))]) # convert to Pa from mB
temperature = np.array([data[i][2] for i in range(len(data))])
specific_humidity = np.array([data[i][3] if data[i][3] != -999.0 else 0 for i in range(len(data))])
wind_speed = np.array([data[i][5] for i in range(len(data))])
wind_direction = np.array([data[i][6] for i in range(len(data))])

height1 = np.array([data1[i][1] for i in range(len(data1))])
height2 = np.array([data2[i][1] for i in range(len(data2))])
height3 = np.array([data3[i][1] for i in range(len(data3))])

pressure1 = np.array([(data1[i][0] * 100) for i in range(len(data1))]) # convert to Pa from mB
pressure2 = np.array([(data2[i][0] * 100) for i in range(len(data2))]) # convert to Pa from mB
pressure3 = np.array([(data3[i][0] * 100) for i in range(len(data3))]) # convert to Pa from mB

all_heights = np.array([height, height1, height2, height3])
all_pressures = np.array([pressure, pressure1, pressure2, pressure3])
times = [0, 6, 12, 18]

heights = np.array(all_heights).flatten()
times = np.repeat(times, len(heights) // len(times))
pressures = np.array(all_pressures).flatten()

X = np.vstack((heights, times)).T
y = pressures

scaler_X = StandardScaler()
scaler_y = StandardScaler()

X_scaled = scaler_X.fit_transform(X)
y_scaled = scaler_y.fit_transform(y.reshape(-1, 1))

predict_pressure = tf.keras.models.Sequential([
    tf.keras.layers.Dense(64, activation='relu', input_shape=(2,)),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(1)
])

predict_pressure.compile(optimizer='adam', loss='mean_squared_error')

predict_pressure.fit(X_scaled, y_scaled, epochs=20, batch_size=10, verbose=0)

# Example prediction inputs
new_heights = [10000, 10000]
new_times = [3, 9]

X_new = np.vstack((new_heights, new_times)).T
X_new_scaled = scaler_X.transform(X_new)

y_new_scaled = predict_pressure.predict(X_new_scaled)
y_new = scaler_y.inverse_transform(y_new_scaled)

print(f"Predicted pressures: {y_new.flatten()}")



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
coefficients = np.polyfit(height, temperature, 4)
a, b, c, d, k = coefficients

# Predict the temperature at height h
def predict_temp(h):
    return a * h**4 + b * h**3 + c * h**2 + d * h + k

print(predict_temp(21000))
temps_fit = predict_temp(heights_fit)

volume_at_room_temp = tracer.moles_helium * GAS_CONSTANT * 293.15 / 101325  # m^3
full_volume = 4/3 * np.pi * radius**3  # m^3

density_at_room_temp = mass_helium / volume_at_room_temp  # kg/m^3

specific_humidity_first_zero_index = np.where(specific_humidity == 0)[0][0]
print(f"First Zero Index : {specific_humidity_first_zero_index}")

coefficients_humidity = np.polyfit(height[:specific_humidity_first_zero_index], specific_humidity[:specific_humidity_first_zero_index], 3)
e, f, i, j = coefficients_humidity

def predict_specific_humidity(h):
    val = e * h**3 + f * h**2 + i * h + j
    return 0 if val < 0 or h > height[specific_humidity_first_zero_index] else val

print(predict_specific_humidity(21000))
humidity_fit = [predict_specific_humidity(ele) for ele in heights_fit]


heights = np.array(all_heights).flatten()
pressures = np.array(all_pressures).flatten()

X = np.vstack((heights, times)).T
y = pressures

scaler_X = StandardScaler()
scaler_y = StandardScaler()

X_scaled = scaler_X.fit_transform(X)
y_scaled = scaler_y.fit_transform(y.reshape(-1, 1))

predict_pressure = tf.keras.models.Sequential([
    tf.keras.layers.Dense(64, activation='relu', input_shape=(2,)),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(1)
])

predict_pressure.compile(optimizer='adam', loss='mean_squared_error')

predict_pressure.fit(X_scaled, y_scaled, epochs=20, batch_size=10, verbose=0)

# Example prediction inputs
new_heights = [10000, 10000]
new_times = [3, 9]

X_new = np.vstack((new_heights, new_times)).T
X_new_scaled = scaler_X.transform(X_new)

y_new_scaled = predict_pressure.predict(X_new_scaled)
y_new = scaler_y.inverse_transform(y_new_scaled)

print(f"Predicted pressures: {y_new.flatten()}")


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

wind_speed_fit = [predict_wind_speed(ele) for ele in heights_fit]

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

wind_direction_fit = [predicted_wind_direction(ele) for ele in heights_fit]

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
    # f.write(f"x y z\n")
    # f.write(f"{tracer.x} {tracer.y} {tracer.z}\n")
    time_step = 1  # seconds
    total_time = 86400  # seconds (24 hours)
    heights = []
    times = []
    elapsed_time = 0
    # for _ in range(total_time // time_step):
    for i in range(total_time // time_step):
        elapsed_time = i * time_step
        # Calculate the wind velocity and velocity relative to balloon
        wind_velocity = predict_wind_speed(tracer.z) * vectorize_wind_direction(tracer.z)
        # Calculate bouyant force
        bouyant = bouyant_force(tracer.z)
        bouyant_vector = bouyant * np.array([0, 0, 1])
        # Calculate gravitational force
        gravitational = gravitational_force()
        gravitational_vector = gravitational_force() * np.array([0, 0, -1])
        # Terminal Rise Velocity
        if (bouyant - gravitational) < 0:
            terminal_rise_velocity = 0
        else: 
            terminal_rise_velocity = math.sqrt((bouyant - gravitational) / (tracer.drag_coefficient * tracer.cross_sectional_area))
        # Calculate new position
        tracer.x += wind_velocity[0] * time_step
        tracer.y += wind_velocity[1] * time_step
        tracer.z += terminal_rise_velocity * time_step
        # Write coordinates to file
        f.write(f"{tracer.x} {tracer.y} {tracer.z}\n")

        heights.append(tracer.z)
        times.append(elapsed_time)
        
        # print(f'\n############### ITERATION {i+1} ##################\n')
        # print(f"Wind Velocity: {wind_velocity}")
        # print(f"Bouyant: {bouyant}")
        # print(f"Bouyant Vector: {bouyant_vector}")
        # print(f"Gravitational: {gravitational}")
        # print(f"Gravitational Vector: {gravitational_vector}")
        # print(f"Terminal Rise Velocity: {terminal_rise_velocity}")
        # print(f'New Position: {tracer.x}, {tracer.y}, {tracer.z}')


    f.close()
    return heights, times

calculated_heights, calculated_times = plot_trajectory()
        



# Plot the data as subplots within a single figure
fig, axs = plt.subplots(2, 3, figsize=(8, 8))

# Pressure vs. Height
axs[0, 0].scatter(height, pressure, color='red', label='Data')
axs[0, 0].plot(heights_fit, pressures_fit, color='blue', label='Fit')
axs[0, 0].set_xlabel('Height (m)')
axs[0, 0].set_ylabel('Pressure (Pa)')
axs[0, 0].set_title('Exponential Fit to Pressure vs. Height Data')
axs[0, 0].legend()
axs[0, 0].grid(True)

# Temperature vs. Height
axs[0, 1].scatter(height, temperature, color='red', label='Data')
axs[0, 1].plot(heights_fit, temps_fit, color='blue', label='Fit')
axs[0, 1].set_xlabel('Height (m)')
axs[0, 1].set_ylabel('Temperature (K)')
axs[0, 1].set_title('Quadric Fit to Temperature vs. Height Data')
axs[0, 1].legend()
axs[0, 1].grid(True)

# Specific Humidity vs. Height
axs[1, 0].scatter(height, specific_humidity, color='red', label='Data')
axs[1, 0].plot(heights_fit, humidity_fit, color='blue', label='Fit')
axs[1, 0].set_xlabel('Height (m)')
axs[1, 0].set_ylabel('Specific Humidity (kg/kg)')
axs[1, 0].set_title('Cubic Fit to Specific Humidity vs. Height Data')
axs[1, 0].legend()
axs[1, 0].grid(True)

# Wind Speed vs. Height
axs[1, 1].scatter(height, wind_speed, color='red', label='Data')
axs[1, 1].plot(heights_fit, wind_speed_fit, color='blue', label='Fit')
axs[1, 1].set_xlabel('Height (m)')
axs[1, 1].set_ylabel('Wind Speed m/s')
axs[1, 1].set_title('Linear Interpolation Fit to Wind Speed vs. Height Data')
axs[1, 1].legend()
axs[1, 1].grid(True)

# Wind Direction vs. Height
axs[0, 2].scatter(height, wind_direction, color='red', label='Data')
axs[0, 2].plot(heights_fit, wind_direction_fit, color='blue', label='Fit')
axs[0, 2].set_xlabel('Height (m)')
axs[0, 2].set_ylabel('Wind Direction (degrees)')
axs[0, 2].set_title('Linear Interpolation Fit to Wind Direction vs. Height Data')
axs[0, 2].legend()
axs[0, 2].grid(True)

# Plot the calculated heights
axs[1, 2].plot([i / 3600 for i in calculated_times], calculated_heights, color='blue', label='Calculated Heights')
axs[1, 2].set_xlabel('Time (hrs)')
axs[1, 2].set_ylabel('Height (m)')
axs[1, 2].set_title('Calculated Heights vs. Time')
axs[1, 2].legend()

# Adjust layout
plt.tight_layout()
plt.show()
