import math
import re
import matplotlib.pyplot as plt
import numpy as np

def parse(filepath):
    with open(filepath, 'r') as f:
        all_lines = f.readlines()
        particle_count = 0
        all_x = []
        all_y = []
        all_z = []
        all_diameter = []
        extrema = {
            'xMin' : math.inf,
            'xMax' : -math.inf,
            'yMin' : math.inf,
            'yMax' : -math.inf,
            'zMin' : math.inf,
            'zMax' : -math.inf,
        }
        total_density = 0
        total_diameters = 0
        for line in all_lines:
            print(line)
            line = re.sub(r'\s+', ' ', line).strip()
            print(line)
            line = line.split(' ')
            try:
                x = float(line[0])
                y = float(line[1])
                z = float(line[2])
                all_x.append(x)
                all_y.append(y)
                all_z.append(z)
                phase = int(line[3])
                diameter = float(line[4])
                all_diameter.append(diameter)
                density = float(line[5])
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
                total_diameters += diameter
                total_density += density
                particle_count += 1
            except: 
                continue
        avg_density = total_density / particle_count
        avg_diameter = total_diameters / particle_count

    io = 'system_properties_' + filepath.split('_')[1].split('.')[0] + '.txt'
    with open(io, 'w+') as f:
        f.write("Particle Count : " + str(particle_count) + '\n')
        for key in extrema:
            f.write(key + ': ' + str(extrema[key]) + '\n')
        f.write('Average Density : ' + str(avg_density) + '\n')
        f.write('Average Diameter : ' + str(avg_diameter))

    print(len(all_x))
    print(len(all_y))


    # Create a 3D scatter plot
    plt.figure(figsize=(10, 8))

    xs = np.array(all_x)
    ys = np.array(all_y)
    zs = np.array(all_z)
    ds = np.array(all_diameter)
    # Scatter plot with varying sizes
    plt.scatter(xs, ys, c=ds, cmap='viridis', alpha=0.6)

    color_bar = plt.colorbar()
    color_bar.set_label('Diameter')

    # Labels and title
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.title('2D Scatter Plot of Particles with Different Diameters (Cross-Sectional View)')

    plt.savefig(f'{filepath.split('_')[1].split('.')[0]}.png', dpi=300, bbox_inches='tight')


    plt.show()

if __name__ == '__main__':
    f1 = './particle_input.dat'
    f2 = './particle_output.dat'
    parse(f1)
    parse(f2)