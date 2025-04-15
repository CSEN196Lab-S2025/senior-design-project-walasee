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

if platform == 'win32':
    modulePath = join('C:/', 'Program Files', 'Walabot', 'WalabotSDK', 'python', 'WalabotAPI.py')
elif platform.startswith('linux'):
    modulePath = join('/usr', 'share', 'walabot', 'python', 'WalabotAPI.py')

wlbt = SourceFileLoader('WalabotAPI', modulePath).load_module()
wlbt.Init()

timestamp_for_file = datetime.now().strftime("%m%d%y_%H%M")
output_dir = 'walabotOut_txt'
makedirs(output_dir, exist_ok=True)
output_filename = join(output_dir, f'walabotOut_{timestamp_for_file}.txt')

def read_data(filename):
    x, y, z = np.array([]), np.array([]), np.array([])
    with open(filename, 'r') as f:
        for line in f:
            if line.strip().startswith("x:"):
                parts = line.replace("cm", "").split(",")
                try:
                    x_val = float(parts[0].split(":")[1].strip())
                    y_val = float(parts[1].split(":")[1].strip())
                    z_val = float(parts[2].split(":")[1].strip())
                    x = np.append(x, x_val)
                    y = np.append(y, y_val)
                    z = np.append(z, z_val)
                except:
                    continue
    return x, y, z

def plot_data_plotly(x, y, z, save_path):
    fig = go.Figure(data=[go.Scatter3d(
        x=x, y=y, z=z,
        mode='markers',
        marker=dict(size=5, color=x, colorscale='Viridis', opacity=0.8)
    )])
    fig.update_layout(
        scene=dict(xaxis_title='X Axis', yaxis_title='Y Axis', zaxis_title='Z Axis'),
        margin=dict(r=20, b=10, l=10, t=35),
        title='3D Visualization of Walabot Outputted x, y, and z Coordinates',
        title_x=0.5
    )
    fig.write_html(save_path)
    print(f"3D plot saved as: {save_path}")

def plot_data_matplotlib(x, y, save_path):
    plt.figure(figsize=(10, 6))
    plt.scatter(x, y, c='blue', marker='o')
    plt.title('2D Visualization of Walabot Outputted x and y Coordinates')
    plt.xlabel('X Axis')
    plt.ylabel('Y Axis')
    plt.grid(True)
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"2D plot saved as: {save_path}")

def PrintSensorTargets(targets, xL, yL): 
    with open(output_filename, 'a') as f:
        if targets:
            for i, target in enumerate(targets):
                xVal = xL + target.xPosCm
                yVal = yL + target.yPosCm
                line = f"x: {xVal} cm, y: {yVal} cm, z: {target.zPosCm} cm, a: {target.amplitude} cm"
                print(line)
                f.write(line + '\n')
        else:
            print("No Target Detected")
            f.write('No Target Detected\n')

def InWallApp(xspacing): # add default xspacing here
    xArenaMin, xArenaMax, xArenaRes = -3, 4, 0.5
    yArenaMin, yArenaMax, yArenaRes = -6, 4, 0.5
    zArenaMin, zArenaMax, zArenaRes = 3, 8, 0.5
    xLength = -xArenaMin
    yLength = 0

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
        print("Press enter to record wall image, type 2 to end program, 3 to generate plots, or 4 to start new y line")
        response = input()

        if response == "":
            wlbt.Trigger()
            targets = wlbt.GetImagingTargets()
            wlbt.GetRawImageSlice()
            PrintSensorTargets(targets, xLength, yLength)
            
            xLength += float(xspacing)

        elif response == "2":
            break

        elif response == "3":
            print("Generating plots...")
            x, y, z = read_data(output_filename)

            outputs_dir = "outputs"
            os.makedirs(outputs_dir, exist_ok=True)

            plot_data_matplotlib(x, y, f"{outputs_dir}/{timestamp_for_file}.png")
            plot_data_plotly(x, y, z, f"{outputs_dir}/{timestamp_for_file}.html")
        
        elif response == "4":
            print("Please specify height you moving by on wall. Use a negative to indicate moving down.")
            yChange = input()
            yLength += yChange

            wlbt.Trigger()
            targets = wlbt.GetImagingTargets()
            wlbt.GetRawImageSlice()
            PrintSensorTargets(targets, xLength, yLength)

            xspacing = -xspacing


        else:
            print("Please type a valid input.")

    wlbt.Stop()
    wlbt.Disconnect()
    wlbt.Clean()
    print('Terminated successfully')

if __name__ == '__main__':
    print("Please enter desired x spacing: ")
    xspacing = input()
    InWallApp(xspacing)
