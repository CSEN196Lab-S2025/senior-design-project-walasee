from __future__ import print_function
from sys import platform
from os import makedirs
from importlib.machinery import SourceFileLoader
from os.path import join
from datetime import datetime
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np
import os

import pipe_plotting.process_points as proc
import generate_ifc.generate_ifc as ifc

if platform == 'win32':
    modulePath = join('C:/', 'Program Files', 'Walabot', 'WalabotSDK', 'python', 'WalabotAPI.py')
elif platform.startswith('linux'):
    modulePath = join('/usr', 'share', 'walabot', 'python', 'WalabotAPI.py')

wlbt = SourceFileLoader('WalabotAPI', modulePath).load_module()
wlbt.Init()

# set up directories, files, and locations
timestamp_for_file = datetime.now().strftime("%m%d%y_%H%M")
output_dir1 = 'walabotOut_txt'
makedirs(output_dir1, exist_ok=True)
unprocessed_filename = join(output_dir1, f'walabotOut_{timestamp_for_file}.txt')
cleaned_filename = join(output_dir1, f'walabotClean_{timestamp_for_file}.txt')

output_dir2 = 'pipe_plotting/pipeOut_txt'
makedirs(output_dir2, exist_ok=True)
processed_filename = join(output_dir2, f'segments_{timestamp_for_file}.txt')

output_dir3 = 'pipe_plotting/pipeOut_plots'
makedirs(output_dir3, exist_ok=True)
processed_plot_png = join(output_dir3, f'{timestamp_for_file}.png')

output_dir4 = 'generate_ifc/input_labelled'
makedirs(output_dir4, exist_ok=True)
ifcCoords_filename = join(output_dir4, f'coordsForifc_{timestamp_for_file}.txt')

output_dir5 = 'generate_ifc/output_ifc'
makedirs(output_dir5, exist_ok=True)
ifc_filename = join(output_dir5, f"wall_with_pipes_{timestamp_for_file}.ifc")


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

def plot_data_plotly(x, y, z, is_hit, save_path):
    colors = np.where(is_hit, 'red', 'gray')
    fig = go.Figure(data=[go.Scatter3d(
        x=x, y=y, z=z,
        mode='markers',
        marker=dict(size=5, color=colors, opacity=0.8)
    )])
    fig.update_layout(
        scene=dict(xaxis_title='X Axis', yaxis_title='Y Axis', zaxis_title='Z Axis'),
        margin=dict(r=20, b=10, l=10, t=35),
        title='3D Visualization of Walabot Readings',
        title_x=0.5
    )
    fig.write_html(save_path)
    print(f"3D plot saved as: {save_path}")

def plot_data_matplotlib(x, y, is_hit, save_path):
    plt.figure(figsize=(10, 6))
    for xi, yi, hit in zip(x, y, is_hit):
        color = 'red' if hit else 'gray'
        plt.scatter(xi, yi, c=color, marker='o')
    plt.title('2D Visualization of Walabot Readings')
    plt.xlabel('X Axis')
    plt.ylabel('Y Axis')
    plt.grid(True)
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"2D plot saved as: {save_path}")

def PrintSensorTargets(targets, xL, yL):
    with open(unprocessed_filename, 'a') as f:
        if targets:
            for target in targets:
                xVal = xL + target.xPosCm
                yVal = yL - target.yPosCm
                line = f"x: {xVal} cm, y: {yVal} cm, z: {target.zPosCm} cm, a: {target.amplitude} cm"
                print(line)
                f.write(line + '\n')
        else:
            xVal = xL
            yVal = yL
            line = f"No Target Detected at x: {xVal} cm, y: {yVal} cm, z: 0.0 cm"
            print(line)
            f.write(line + '\n')

def InWallApp():
    xArenaMin, xArenaMax, xArenaRes = -3, 4, 0.5
    yArenaMin, yArenaMax, yArenaRes = -6, 4, 0.5
    zArenaMin, zArenaMax, zArenaRes = 3, 8, 0.5
    xLength = -xArenaMin
    yLength = 0
    print("Please enter desired spacing: ")
    xspacing = input()
    xspacing = float(xspacing)
    first = True

    wlbt.Initialize()
    wlbt.ConnectAny()
    wlbt.SetProfile(wlbt.PROF_SHORT_RANGE_IMAGING)
    wlbt.SetArenaX(xArenaMin, xArenaMax, xArenaRes)
    wlbt.SetArenaY(yArenaMin, yArenaMax, yArenaRes)
    wlbt.SetArenaZ(zArenaMin, zArenaMax, zArenaRes)
    wlbt.SetDynamicImageFilter(wlbt.FILTER_TYPE_NONE)
    wlbt.SetThreshold(80)
    wlbt.Start()

    print("Type C to calibrate")
    response = input()
    if response.lower() == "c":
        wlbt.StartCalibration()
        while wlbt.GetStatus()[0] == wlbt.STATUS_CALIBRATING:
            wlbt.Trigger()

    while True:
        print("Press Enter to record wall image\n2: start a new y line\n3: generate ifc\n4: end program")
        response = input()

        if response == "":
            if not first:
                xLength += float(xspacing)
            first = False
            wlbt.Trigger()
            targets = wlbt.GetImagingTargets()
            wlbt.GetRawImageSlice()
            PrintSensorTargets(targets, xLength, yLength)

            x, y, z, is_hit = read_data(unprocessed_filename)
            outputs_dir = "walabotOut_plots"
            os.makedirs(outputs_dir, exist_ok=True)
            plot_data_matplotlib(x, y, is_hit, f"{outputs_dir}/{timestamp_for_file}.png")
            plot_data_plotly(x, y, z, is_hit, f"{outputs_dir}/{timestamp_for_file}.html")

        elif response == "2":
            # Don't click enter until the Walabot is in proper position
            print("Specify height you are moving by on wall. Use negative to indicate moving down")
            yChange = input()
            yLength += float(yChange)
            xLength = -xArenaMin
            wlbt.Trigger()
            targets = wlbt.GetImagingTargets()
            wlbt.GetRawImageSlice()
            PrintSensorTargets(targets, xLength, yLength)

            x, y, z, is_hit = read_data(unprocessed_filename)
            outputs_dir = "walabotOut_plots"
            os.makedirs(outputs_dir, exist_ok=True)
            plot_data_matplotlib(x, y, is_hit, f"{outputs_dir}/{timestamp_for_file}.png")
            plot_data_plotly(x, y, z, is_hit, f"{outputs_dir}/{timestamp_for_file}.html")
            

        elif response == "3":
            # -------------- The action -> and the file that's outputted from that action
            # 1) Clean data txt file, aka removes "No Target Detected" -> 'walabotOut_txt/walaboutClean_{time}.txt'
            # 2) Run cleaned data through ML pipe_plotting/process_points.py -> 'pipe_plotting/pass3_final.txt'
            # 3) Reformat 'pass3_final.txt' to use for IFC generation -> 'generate_ifc/coordinates/coordsForIfc_{time}.txt'
            # 4) Run reformatted data through generate_ifc/generate_ifc.py -> 'generate_ifc/outputted_ifc/wall_with_pipes_{time}.txt'

            # read uncleaned data
            x, y, z, is_hit = read_data(unprocessed_filename)

            # transforms -y to +y and make so min(y) is always 0
            low_y = min(y)
            if low_y < 0:
                for i in range(len(y)):
                    y[i] -= low_y

            # before data is cleaned and after y all made positive, grab the max xyz of all data collected (even if no target) to get wall dimensions
            wall_dim = (max(x), max(y), max(z) - 6) #max(z) always 8, so subtract 6 to get 2cm thick wall

            # clean the unprocessed data by getting rid of No Target Detected x: y: z: cm, and a: with anything after it
            with open(unprocessed_filename, "r") as infile, open(cleaned_filename, "w") as outfile:
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
            proc.run_all(cleaned_filename, processed_filename, processed_plot_png) #saves ML processed points as /pipe_plotting/segments_{time}.txt

            # reformat segments.txt for ifcCoords.txt, aka make all negative y positive
            with open(processed_filename, 'r') as infile, open(ifcCoords_filename, 'w') as outfile:
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
            ifc.generate(ifcCoords_filename, ifc_filename)

        elif response == "4":
            break

        else:
            print("Please type a valid input.")

    wlbt.Stop()
    wlbt.Disconnect()
    wlbt.Clean()
    print('Terminated successfully')

if __name__ == '__main__':
    InWallApp()
