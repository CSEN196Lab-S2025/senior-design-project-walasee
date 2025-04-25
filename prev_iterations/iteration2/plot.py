import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np
import os
import sys

# Read text from txt file to create individual x, y, and z np.arrays of their corresponding Walabot outputted values
def read_data(filename):
    x, y, z = np.array([]), np.array([]), np.array([])

    with open(filename, 'r') as f:
        for line in f:
            if line.startswith("  x:"):  # Ensuring we parse valid coordinate lines
                parts = line.replace("cm", "").split(",")  # Remove 'cm' and split
                x_val = float(parts[0].split(":")[1].strip())
                y_val = float(parts[1].split(":")[1].strip())
                z_val = float(parts[2].split(":")[1].strip())

                # Append values properly
                x = np.append(x, x_val)
                y = np.append(y, y_val)
                z = np.append(z, z_val)

    print(f"Total coordinates read: {len(x)}")
    return x, y, z

# Plot output using plotly.graph_objects (3D) and save to HTML
def plot_data_plotly(x, y, z, save_path):
    fig = go.Figure(data=[go.Scatter3d(
        x=x, y=y, z=z,
        mode='markers',
        marker=dict(
            size=5,
            color=x,                # set color to an array/list of desired values
            colorscale='Viridis',   # choose a colorscale
            opacity=0.8
        )
    )])

    fig.update_layout(scene=dict(
                        xaxis_title='X Axis',
                        yaxis_title='Y Axis',
                        zaxis_title='Z Axis'),
                      margin=dict(r=20, b=10, l=10, t=35),
                      title='3D Visualization of Walabot Outputted x, y, and z Coordinates',
                      title_x=0.5)

    fig.write_html(save_path)  # Save as interactive HTML file
    print(f"3D plot saved as: {save_path}")

# Plot output using matplotlib (2D) and save to PNG
def plot_data_matplotlib(x, y, save_path):
    plt.figure(figsize=(10, 6))
    plt.scatter(x, y, c='blue', marker='o')
    plt.title('2D Visualization of Walabot Outputted x and y Coordinates')
    plt.xlabel('X Axis')
    plt.ylabel('Y Axis')
    plt.grid(True)
    
    plt.savefig(save_path, dpi=300)  # Save as PNG file
    plt.close()  # Close the plot to free memory
    print(f"2D plot saved as: {save_path}")

# Ensure the script gets a file as input
if len(sys.argv) < 2:
    print("Error: No file specified.")
    sys.exit(1)

# Get the file path from the command line argument
file_path = sys.argv[1]

# Ensure the file exists before reading
if not os.path.exists(file_path):
    print(f"Error: File '{file_path}' not found.")
    sys.exit(1)

# Read the data
x, y, z = read_data(file_path)
print("np array 'x' length:", len(x))
print("np array 'y' length:", len(y))
print("np array 'z' length:", len(z))

# Create the outputs directory if it doesn’t exist
output_dir = "outputs"
os.makedirs(output_dir, exist_ok=True)

# Generate unique output filenames based on input file name
filename_base = os.path.basename(file_path).replace(".txt", "")
save_path_2D = f"{output_dir}/{filename_base}_2D.png"
save_path_3D = f"{output_dir}/{filename_base}_3D.html"

# Generate and save plots
plot_data_matplotlib(x, y, save_path_2D)
plot_data_plotly(x, y, z, save_path_3D)

