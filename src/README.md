ITERATION 3 (Current version in progress)
- After testing the scanning and plotting feature implemented in iteration 2, we realized that the plotting algorithm needs to change. Location data is received relative to the Walabot's origin only. If we want to plot the data to resemble the actual in wall objects, we have to hard code the recieved data to be plotted relative an origin that we set. 

- megascripty.py: Scanning and plotting programs are combined into one megascript so that there is no need for a bash script or manual execution. The megascript.py program gives the user options to run certain functionalities via keyboard input (scan, increment arena in the x or y direction, plot, kill program).

- pipe_plotting directory: Uses DBScan to cluster the point cloud. Outputs .txt files with xy of start and end location of pipe segment

- generate_ifc directory: Take .txt file outputed by pipe_plotting to generate .ifc file. On Yi Qian's computer, she must be in an anaconda environment in order to install necessesary packages and run the program: 'conda activate name-of-env'. Use https://viewer.sortdesk.com/ to temporarily view outputted .ifc if no Revit

- Wall scanning method change: On April 25th we changed the scanning/data collection method from snaking left and right to go from the top to the bottom to just resetting on the left side each time we moved down
