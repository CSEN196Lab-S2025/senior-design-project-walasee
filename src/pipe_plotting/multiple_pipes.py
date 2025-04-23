import numpy as np
import matplotlib.pyplot as plt
import os
import sys
from sklearn.cluster import DBSCAN

# ----------------- Utility Functions -----------------
def read_input(filename):
    points = []
    with open(filename, 'r') as f:
        for line in f:
            try:
                x, y, *_ = map(float, line.strip().split(','))
                points.append((x, y))
            except:
                continue
    return np.array(points)

def get_direction(p1, p2):
    if abs(p2[0] - p1[0]) > abs(p2[1] - p1[1]):
        return 'H'
    elif abs(p2[1] - p1[1]) > abs(p2[0] - p1[0]):
        return 'V'
    return None

def merge_axis_aligned(points):
    merged = [points[0]]
    prev_dir = get_direction(points[0], points[1])
    for i in range(1, len(points) - 1):
        curr_dir = get_direction(points[i], points[i + 1])
        if curr_dir != prev_dir:
            merged.append(points[i])
            prev_dir = curr_dir
    merged.append(points[-1])
    return np.array(merged)

def limit_segments_to_3(points):
    if len(points) <= 3:
        return points
    return np.array([points[0], points[len(points)//2], points[-1]])

def to_axis_aligned_path(points):
    aligned_path = [points[0]]
    for i in range(1, len(points)):
        prev = aligned_path[-1]
        curr = points[i]
        if curr[0] != prev[0]:
            aligned_path.append([curr[0], prev[1]])
        if curr[1] != prev[1]:
            aligned_path.append([curr[0], curr[1]])
    merged = merge_axis_aligned(np.array(aligned_path))
    simplified = limit_segments_to_3(merged)
    return simplified

# ----------------- Clustering Pass -----------------
def cluster_points(points, eps=4.0, min_samples=3):
    if len(points) < min_samples:
        return [points]  # don't try clustering small sets
    clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(points)
    labels = clustering.labels_
    clusters = []
    for label in sorted(set(labels)):
        if label == -1:
            continue
        clusters.append(points[labels == label])
    return clusters

# ----------------- Pass Pipeline -----------------
def process_pipe(points, pipe_id):
    # Pass 1: Sort by dominant direction
    x_range = np.max(points[:, 0]) - np.min(points[:, 0])
    y_range = np.max(points[:, 1]) - np.min(points[:, 1])
    if x_range > y_range:
        sorted_points = sorted(points, key=lambda p: p[0])
    else:
        sorted_points = sorted(points, key=lambda p: -p[1])
    sorted_points = np.array(sorted_points)

    with open(f"pipe{pipe_id}_pass1.txt", "w") as f:
        for x, y in sorted_points:
            f.write(f"{x:.4f}, {y:.4f}\n")

    # Pass 2: Simplify
    simplified = to_axis_aligned_path(sorted_points)
    with open(f"pipe{pipe_id}_pass2.txt", "w") as f:
        for x, y in simplified:
            f.write(f"{x:.4f}, {y:.4f}\n")

    # Pass 3: Final plotting and text
    assert len(simplified) == 3
    A, B, C = simplified
    x_vals = [A[0], B[0], C[0]]
    y_vals = [A[1], B[1], C[1]]
    x_range = max(x_vals) - min(x_vals)
    y_range = max(y_vals) - min(y_vals)

    if y_range < 1.0 and x_range > 2.0:
        pipe_path = np.array([[min(x_vals), np.mean(y_vals)], [max(x_vals), np.mean(y_vals)]])
    elif x_range < 1.0 and y_range > 2.0:
        pipe_path = np.array([[np.mean(x_vals), min(y_vals)], [np.mean(x_vals), max(y_vals)]])
    else:
        def axis_aligned_l_path(p1, p2):
            path = [p1]
            if p1[0] != p2[0]:
                path.append([p2[0], p1[1]])
            if p1[1] != p2[1]:
                path.append([p2[0], p2[1]])
            return path

        pipe_path = []
        pipe_path += axis_aligned_l_path(A, B)[:-1]
        pipe_path += axis_aligned_l_path(B, C)
        pipe_path = np.array(pipe_path)

    with open(f"pipe{pipe_id}_final.txt", "w") as f:
        for x, y in pipe_path:
            f.write(f"{x:.4f}, {y:.4f}\n")

    plt.figure(figsize=(8, 6))
    plt.plot(sorted_points[:, 0], sorted_points[:, 1], linestyle='--', color='gray', label='Sorted Zigzag')
    plt.scatter(sorted_points[:, 0], sorted_points[:, 1], color='red', s=20)
    plt.plot(pipe_path[:, 0], pipe_path[:, 1], color='blue', linewidth=4, label='Final Pipe')
    plt.title(f"Pipe {pipe_id}: Final Shape")
    plt.xlabel("X (cm)")
    plt.ylabel("Y (cm)")
    plt.axis('equal')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"pipe{pipe_id}_final.png")
    plt.close()

# ----------------- Runner -----------------
def main():
    if len(sys.argv) != 2:
        print("Usage: python multi_pipe_processor.py <cleaned.txt>")
        sys.exit(1)

    input_file = sys.argv[1]
    points = read_input(input_file)
    clusters = cluster_points(points)

    print(f"[✓] Detected {len(clusters)} pipe(s). Processing each...")
    for i, cluster in enumerate(clusters):
        process_pipe(cluster, i)

if __name__ == "__main__":
    main()

