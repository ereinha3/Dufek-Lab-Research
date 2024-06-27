import math
import re
import matplotlib.pyplot as plt
import numpy as np

def parse(filepath):
    # Opening the file from the specified input file 
    with open(filepath, 'r') as f:
        # Parse all lines into one big array
        all_lines = f.readlines()
        # Accumulator for particle count
        particle_count = 0
        # Initialize arrays to store every x, y, and z component
        # Indexes will be the same 
        all_x = []
        all_y = []
        all_z = []
        # Initialize array to store all diameters
        all_diameter = []
        # Create dictionary to store initialized extrema 
        extrema = {
            'xMin' : math.inf,
            'xMax' : -math.inf,
            'yMin' : math.inf,
            'yMax' : -math.inf,
            'zMin' : math.inf,
            'zMax' : -math.inf,
        }
        # Density and diameter accumulators
        total_density = 0
        total_diameters = 0
        # Iterate over every line in the file
        for line in all_lines:
            # Regexing to make it so that big spaces go to single spaces
            line = re.sub(r'\s+', ' ', line).strip()
            # Split into array at spaces
            line = line.split(' ')
            # If you can convert these things to float (ie matches the pattern) then do that
            try:
                # Parse out the x, y, and z variables and type cast to float
                x = float(line[0])
                y = float(line[1])
                z = float(line[2])
                # Append these to accumulator dictionaries
                all_x.append(x)
                all_y.append(y)
                all_z.append(z)
                # Get the rest of the components based on pattern
                phase = int(line[3])
                diameter = float(line[4])
                all_diameter.append(diameter)
                density = float(line[5])
                # Change extrema if any of these x, y, or z and new relative max or min
                if (x > extrema['xMax']):
                    extrema['xMax'] = x
                if (x < extrema['xMin']):
                    extrema['xMin'] = x
                if (y > extrema['yMax']):
                    extrema['yMax'] = y
                if (y < extrema['yMin']):
                    extrema['yMin'] = y
                if (z > extrema['zMax']):
                    extrema['zMax'] = y
                if (z < extrema['zMin']):
                    extrema['zMin'] = z
                # Add to total density and diameter
                total_diameters += diameter
                total_density += density
                # Add one to particle count
                particle_count += 1
            # Ignore exception and go to next iteration
            except: 
                continue
        avg_density = total_density / particle_count
        avg_diameter = total_diameters / particle_count

    # Output file
    # Create a new file path to be system_properties_{input/outpout}.txt
    io = 'system_properties_' + filepath.split('_')[1].split('.')[0] + '.txt'
    # Open this file to write to
    with open(io, 'w+') as f:
        # Print particle count
        f.write("Particle Count : " + str(particle_count) + '\n')
        # Print all extrema
        for key in extrema:
            f.write(key + ': ' + str(extrema[key]) + '\n')
        # Print avg density and diameter
        f.write('Average Density : ' + str(avg_density) + '\n')
        f.write('Average Diameter : ' + str(avg_diameter))

    # Create a rectangular 3D scatter plot 
    plt.figure(figsize=(10, 8))

    # Create numpy arrays of all x, y, and z values as well as all diameters
    # Important for using matplotlib
    xs = np.array(all_x)
    ys = np.array(all_y)
    zs = np.array(all_z)
    ds = np.array(all_diameter)
    # Scatter plot with constant size depicted
    plt.scatter(xs, ys, c=ds, cmap='viridis', alpha=0.6)

    # Create scale for diameter size of particles
    color_bar = plt.colorbar()
    color_bar.set_label('Diameter')

    # Labels and title
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.title('2D Scatter Plot of Particles with Different Diameters (Cross-Sectional View)')

    # Save the figure to input/output.png
    plt.savefig(f'{filepath.split('_')[1].split('.')[0]}.png', dpi=300, bbox_inches='tight')


    plt.show()

# Always run on execution (if __name__ == '__main__' should always run on host environment)
if __name__ == '__main__':
    f1 = './particle_input.dat'
    f2 = './particle_output.dat'
    parse(f1)
    parse(f2)