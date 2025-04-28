import numpy as np
import sys
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from sklearn.cluster import DBSCAN

# ------------ Read Input Directly ------------

def read_input(filename):
    points = []
    with open(filename, 'r') as f:
        for line in f:
            try:
                x, y, z = map(float, line.strip().split(',')[:3])
                points.append((x, y, z))
            except:
                continue
    return np.array(points)

# ------------ Smart Clustering and Best Fit Lines ------------

def smart_partition(points):
    points2d = points[:, :2]

    clustering = DBSCAN(eps=3.0, min_samples=2).fit(points2d)
    labels = clustering.labels_

    unique_labels = set(labels)
    segments = []

    for label in unique_labels:
        if label == -1:
            continue
        cluster = points2d[labels == label]

        x_spread = np.max(cluster[:,0]) - np.min(cluster[:,0])
        y_spread = np.max(cluster[:,1]) - np.min(cluster[:,1])

        if x_spread > y_spread:
            avg_y = np.mean(cluster[:,1])
            cluster = np.array([[np.min(cluster[:,0]), avg_y], [np.max(cluster[:,0]), avg_y]])
        else:
            avg_x = np.mean(cluster[:,0])
            cluster = np.array([[avg_x, np.min(cluster[:,1])], [avg_x, np.max(cluster[:,1])]])

        segments.append(cluster)

    return segments

# ------------ Run Pass 2 ------------

def run_pass2(filename):
    points = read_input(filename)
    segments = smart_partition(points)

    keypoints = []
    for seg in segments:
        keypoints.append(seg[0])
    keypoints.append(segments[-1][-1])

    keypoints = np.array(keypoints)

    np.savetxt("pass2_simplified.txt", keypoints, fmt="%.4f, %.4f")

    plt.figure(figsize=(10,8))
    plt.scatter(points[:,0], points[:,1], color='red')
    for seg in segments:
        plt.plot(seg[:,0], seg[:,1], linewidth=3)
    plt.title("Pass 2: Smart Clustered Segments")
    plt.xlabel("X (cm)")
    plt.ylabel("Y (cm)")
    plt.grid(True)
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig("pass2_simplified.png")
    plt.close()

    fig = go.Figure()
    fig.add_trace(go.Scatter3d(x=points[:,0], y=points[:,1], z=points[:,2], mode='markers'))
    for seg in segments:
        fig.add_trace(go.Scatter3d(x=seg[:,0], y=seg[:,1], z=np.full(seg.shape[0],8), mode='lines'))
    fig.update_layout(title="Pass 2: Smart Clustered Segments 3D", scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z'))
    fig.write_html("pass2_simplified.html")

# ------------ Final Clean Snap with Real Bend Detection and 90 Degree Correction ------------

def run_pass3(filename):
    points2d = []
    with open(filename, 'r') as f:
        for line in f:
            try:
                x, y = map(float, line.strip().split(','))
                points2d.append((x, y))
            except:
                continue
    points2d = np.array(points2d)
    z_vals = np.full(points2d.shape[0], 8.0)
    points = np.column_stack((points2d, z_vals))

    points = points[np.lexsort((-points[:,1], points[:,0]))]

    snapped_path = []
    A = points[0]
    snapped_path.append([A[0], A[1], A[2]])

    for i in range(1, len(points)):
        B = points[i]
        prev = snapped_path[-1]
        dx = abs(B[0] - prev[0])
        dy = abs(B[1] - prev[1])
        big_movement_threshold = 5.0  # cm

        if dx > big_movement_threshold and dy > big_movement_threshold:
            # First move horizontally, then vertically
            snapped_path.append([B[0], prev[1], B[2]])
            snapped_path.append([B[0], B[1], B[2]])
        elif dx > big_movement_threshold:
            snapped_path.append([B[0], prev[1], B[2]])
        elif dy > big_movement_threshold:
            snapped_path.append([prev[0], B[1], B[2]])

    snapped_path = np.array(snapped_path)

    np.savetxt("pass3_final.txt", snapped_path, fmt="%.4f, %.4f, %.4f")

    plt.figure(figsize=(10,8))
    plt.plot(snapped_path[:,0], snapped_path[:,1], color='green', marker='o')
    plt.title("Pass 3: Final Correct 90 Degree Path")
    plt.xlabel("X (cm)")
    plt.ylabel("Y (cm)")
    plt.grid(True)
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig("pass3_final.png")
    plt.close()

    fig = go.Figure()
    fig.add_trace(go.Scatter3d(x=snapped_path[:,0], y=snapped_path[:,1], z=snapped_path[:,2], mode='lines+markers'))
    fig.update_layout(title="Pass 3: Final 3D Pipe", scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z'))
    fig.write_html("pass3_final.html")

# ------------ Runner ------------

def run_all_pipeline():
    if len(sys.argv) != 2:
        print("Usage: python process.py <data.txt>")
        sys.exit(1)
    input_file = sys.argv[1]
    run_pass2(input_file)
    run_pass3("pass2_simplified.txt")

if __name__ == "__main__":
    run_all_pipeline()
