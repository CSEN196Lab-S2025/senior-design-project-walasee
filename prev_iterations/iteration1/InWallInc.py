from __future__ import print_function # WalabotAPI works on both Python 2 an 3.
from sys import platform
from os import system, makedirs
from importlib.machinery import SourceFileLoader
from os.path import join
from datetime import datetime

if platform == 'win32':
    modulePath = join('C:/', 'Program Files', 'Walabot', 'WalabotSDK',
        'python', 'WalabotAPI.py')
elif platform.startswith('linux'):
    modulePath = join('/usr', 'share', 'walabot', 'python', 'WalabotAPI.py')     

wlbt = SourceFileLoader('WalabotAPI', modulePath).load_module()
wlbt.Init()

# Create the directory if it doesn't exist
output_dir = 'walabotOut_txt'
makedirs(output_dir, exist_ok=True)

# Generate a unique filename with a timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_filename = join(output_dir, f'walabotOut_{timestamp}.txt')



# Writes walabot output to a txt file
def PrintSensorTargets(targets, L):
    with open(output_filename, 'a') as f:
        xVal = L + target.xPosCm
        if targets:
            #print("*********Detected something...")
            for i, target in enumerate(targets):
                print(f" x: {xVal} cm, y: {target.yPosCm} cm, z: {target.zPosCm} cm, a: {target.amplitude} cm")
                f.write(f'  x: {xVal} cm, y: {target.yPosCm} cm, z: {target.zPosCm} cm, a: {target.amplitude} cm\n')
        else:
            print("No Target Detected")
            f.write('No Target Detected\n')

def InWallApp(spacing):
    # wlbt.SetArenaX - input parameters
    xArenaMin, xArenaMax, xArenaRes = -3, 4, 0.5
    # wlbt.SetArenaY - input parameters
    yArenaMin, yArenaMax, yArenaRes = -6, 4, 0.5
    # wlbt.SetArenaZ - input parameters
    zArenaMin, zArenaMax, zArenaRes = 3, 8, 0.5

    ######################### CFONFIRM AXIS #######################
    xLength = -xArenaMin 
    # Currently coded for one pass accross a wall
    
    i = 0

    # Initializes walabot lib
    wlbt.Initialize()
    # 1) Connects: Establish communication with walabot.
    wlbt.ConnectAny()
    # 2) Configure: Set scan profile and arena
    
    # Set Profile - to Short-range.
    wlbt.SetProfile(wlbt.PROF_SHORT_RANGE_IMAGING)
    # Set arena by Cartesian coordinates, with arena resolution
    wlbt.SetArenaX(xArenaMin, xArenaMax, xArenaRes)
    wlbt.SetArenaY(yArenaMin, yArenaMax, yArenaRes)
    wlbt.SetArenaZ(zArenaMin, zArenaMax, zArenaRes)
    # Walabot filtering disable
    wlbt.SetDynamicImageFilter(wlbt.FILTER_TYPE_NONE)
    wlbt.SetThreshold(80)

    # 3) Start: Start the system in preparation for scanning.
    wlbt.Start()
    # calibrates scanning to ignore or reduce the signals
    wlbt.StartCalibration()
    while wlbt.GetStatus()[0] == wlbt.STATUS_CALIBRATING:
        wlbt.Trigger()

    while True:
        print("Press enter to record wall image, type 2 to end program")
        response = input()
        if (response == ""):
            
            appStatus, calibrationProcess = wlbt.GetStatus()
            # 5) Trigger: Scan (sense) according to profile and record signals
            # to be available for processing and retrieval.
            wlbt.Trigger()
            # 6) Get action: retrieve the last completed triggered recording
            targets = wlbt.GetImagingTargets()
            rasterImage, _, _, sliceDepth, power = wlbt.GetRawImageSlice()
            # PrintSensorTargets(targets)
            PrintSensorTargets(targets, xLength)

            i += 1
            if (i > 1):
                xLength += spacing
        elif (response == "2"):
            break
        else:
            print("Please type a valid input")

    # 7) Stop and Disconnect.
    wlbt.Stop()
    wlbt.Disconnect()
    wlbt.Clean()
    print('Terminate successfully')

if __name__ == '__main__':
    print("Please enter desired spacing: ")
    spacing = input()
    InWallApp(spacing)
