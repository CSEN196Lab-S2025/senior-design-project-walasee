'''
Use this program in cases where you want to test a specific set of already collected data, or if
you don't have the walabot at hand to run the entire megascript and collect data.

Take any unprocessed walabotOut_$(time).txt file and enter as command line argument
to generate cleaned data, processed data/pipe segments, ifc coordinates (positive y coordinates),
and an ifc file.

python temp.py filename.txt
'''

import sys
import numpy as np
import pipe_plotting.process_points as proc
import generate_ifc.generate_ifc as ifc

def read_data(filename):
    x, y, z, is_hit = [], [], [], []
    with open(filename, 'r') as f:
        for line in f:
            if line.strip().startswith("x:") or "No Target Detected at" in line:
                parts = line.replace("cm", "").replace("No Target Detected at ", "").split(",")
                try:
                    x_val = float(parts[0].split(":")[1].strip())
                    y_val = float(parts[1].split(":")[1].strip())
                    z_val = float(parts[2].split(":")[1].strip())
                    x.append(x_val)
                    y.append(y_val)
                    z.append(z_val)
                    is_hit.append("a:" in line)
                except:
                    continue
    return np.array(x), np.array(y), np.array(z), np.array(is_hit)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python temp.py pathTo/walabotOut_$(time).txt ")
        sys.exit(1)

    unprocessed_filename = sys.argv[1]

    # read uncleaned data
    x, y, z, is_hit = read_data(unprocessed_filename)

    # transforms -y to +y and make so min(y) is always 0
    low_y = min(y)
    if low_y < 0:
        for i in range(len(y)):
            y[i] -= low_y

    # before data is cleaned and after y all made positive, grab the max xyz of all data collected (even if no target) to get wall dimensions
    wall_dim = (max(x), max(y), max(z) - 6) #max(z) always 8, so subtract 6 to get 2cm thick wall

    with open(unprocessed_filename, "r") as infile, open('temp_clean.txt', "w") as outfile:
        for line in infile:
            # Skip lines containing "No Target Detected"
            if "No Target Detected" in line:
                continue                    
            cleaned_line = (
                line.split("a:")[0]  # Remove "a:" and anything after it
                    .replace("x: ", "")
                    .replace(" y:", "")
                    .replace(" z:", "")
                    .replace("cm", "")
                    .strip()
            )           
            outfile.write(cleaned_line + "\n")

    # Input cleaned data through ML algorithm
    proc.run_all('temp_clean.txt', 'temp_segments.txt', 'temp_plot.png') #saves ML processed points as /pipe_plotting/segments.txt


    # reformat segments.txt for ifcCoords.txt, aka make all negative y positive
    with open('temp_segments.txt', 'r') as infile, open('temp_ifcCoords.txt', 'w') as outfile:
        # Write in wall dimensions that were collected a little earlier in this program file
        line = f'WALL, {wall_dim[0]}, {wall_dim[1]}, {wall_dim[2]}'
        outfile.write(line + '\n')

        lines = infile.readlines()
        y_values = []

        # Collect all y1 and y2 values to determine the minimum y
        for line in lines:
            parts = line.strip().split(',')
            y1 = float(parts[1])
            y2 = float(parts[4])
            y_values.extend([y1, y2])

        # Find the minimum y value
        low_y = min(y_values)

        # If the minimum y is negative, adjust all y values
        for line in lines:
            parts = line.strip().split(',')
            x1, y1, z1, x2, y2, z2 = map(float, parts)

            if low_y < 0:
                y1 -= low_y
                y2 -= low_y

            # Write the adjusted line to the output file
            outfile.write(f"PIPE, {x1}, {y1}, {z1}, {x2}, {y2}, {z2}\n")

    # Input reformatted data into ifc generation program
    ifc.generate('temp_ifcCoords.txt', 'temp_wallPipes.ifc')