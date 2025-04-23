ITERATION 3 (Current version in progress)
- After testing the scanning and plotting feature implemented in iteration 2, we realized that the plotting algorithm needs to change. Location data is received relative to the Walabot's origin only. If we want to plot the data to resemble the actual in wall objects, we have to hard code the recieved data to be plotted relative an origin that we set. 

- megascripty.py: Scanning and plotting programs are combined into one megascript so that there is no need for a bash script or manual execution. The megascript.py program gives the user options to run certain functionalities via keyboard input (scan, increment arena in the x or y direction, plot, kill program).

- pipe_plotting directory: Coded mathematical calculations to gather xyz points and get a line of best fit to represent a straight section of the detected pipe. Outputs .txt files with xy of start and end location of pipe segment

- generate_ifc directory: Take .txt file outputed by pipe_plotting to generate .ifc file. On Yi Qian's computer, she must be in an anaconda environment in order to install necessesary packages and run the program: 'conda activate name-of-env'. Currently only works when given two coordinates. IFC shows just one straight pipe. Still figuring out how to get it to work on pipes with bends. Use https://viewer.sortdesk.com/ to temporarily view outputted .ifc