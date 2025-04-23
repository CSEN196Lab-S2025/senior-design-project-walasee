import numpy as np
import sys
import matplotlib.pyplot as plt

# ------------ Pass 1: Zigzag connection ------------

def read_pass1_input(filename):
    points = []
    with open(filename, 'r') as f:
        for line in f:
            try:
                x, y, _ = map(float, line.strip().split(',')[:3])
                points.append((x, y))
            except:
                continue
    return np.array(points)

def run_pass1(raw_filename):
    points = read_pass1_input(raw_filename)
    x_range = np.max(points[:, 0]) - np.min(points[:, 0])
    y_range = np.max(points[:, 1]) - np.min(points[:, 1])

    # Decide dominant direction
    if x_range > y_range:
        sorted_points = sorted(points, key=lambda p: p[0])  # left to right
    else:
        sorted_points = sorted(points, key=lambda p: -p[1])  # top to bottom

    sorted_points = np.array(sorted_points)

    with open("pass1_zigzag.txt", "w") as f:
        for x, y in sorted_points:
            f.write(f"{x:.4f}, {y:.4f}\n")

    plt.figure(figsize=(10, 8))
    plt.scatter(sorted_points[:, 0], sorted_points[:, 1], color='red', label='Raw Points')
    plt.plot(sorted_points[:, 0], sorted_points[:, 1], color='gray', linewidth=1, label='Zigzag Path')
    plt.xlabel("X (cm)")
    plt.ylabel("Y (cm)")
    plt.title("Pass 1: Zigzag Path")
    plt.legend()
    plt.axis('equal')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("pass1_zigzag.png")
    plt.close()

# ------------ Pass 2: Simplify bends ------------

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

def read_pass2_input(filename):
    points = []
    with open(filename, 'r') as f:
        for line in f:
            try:
                x, y = map(float, line.strip().split(','))
                points.append((x, y))
            except:
                continue
    return np.array(points)

def run_pass2(filename):
    points = read_pass2_input(filename)
    simplified = to_axis_aligned_path(points)
    with open("pass2_simplified.txt", "w") as f:
        for x, y in simplified:
            f.write(f"{x:.4f}, {y:.4f}\n")

    plt.figure(figsize=(10, 8))
    plt.plot(points[:, 0], points[:, 1], color='gray', linestyle='--', label='Zigzag Path')
    plt.scatter(points[:, 0], points[:, 1], color='red')
    for i in range(len(simplified) - 1):
        x = [simplified[i][0], simplified[i+1][0]]
        y = [simplified[i][1], simplified[i+1][1]]
        plt.plot(x, y, color='blue', linewidth=3)
    plt.xlabel("X (cm)")
    plt.ylabel("Y (cm)")
    plt.title("Pass 2: Simplified Segments (≤3 bends)")
    plt.axis('equal')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("pass2_simplified.png")
    plt.close()

# ------------ Pass 3: Final pipe enforcement ------------

def plot_pass3(original, simplified):
    assert len(simplified) == 3
    A, B, C = simplified

    x_vals = [A[0], B[0], C[0]]
    y_vals = [A[1], B[1], C[1]]
    x_range = max(x_vals) - min(x_vals)
    y_range = max(y_vals) - min(y_vals)

    # Straight pipe case
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

    with open("final_pipe.txt", "w") as f:
        for x, y in pipe_path:
            f.write(f"{x:.4f}, {y:.4f}\n")

    plt.figure(figsize=(10, 8))
    plt.plot(original[:, 0], original[:, 1], linestyle='--', color='gray', label='Input from Pass 2')
    plt.scatter(original[:, 0], original[:, 1], color='red', s=20)
    plt.plot(pipe_path[:, 0], pipe_path[:, 1], color='blue', linewidth=5, label='Final Pipe')
    plt.xlabel("X (cm)")
    plt.ylabel("Y (cm)")
    plt.title("Pass 3: Final Pipe (Auto-shaped 3 segment, 90° only)")
    plt.axis('equal')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("pass3_final.png")
    plt.close()

def run_pass3(filename):
    points = read_pass2_input(filename)
    simplified = to_axis_aligned_path(points)
    plot_pass3(points, simplified)

# ------------ Runner ------------

def run_all_pipeline():
    if len(sys.argv) != 2:
        print("Usage: python process.py <data.txt>")
        sys.exit(1)
    input_file = sys.argv[1]
    run_pass1(input_file)
    run_pass2("pass1_zigzag.txt")
    run_pass3("pass2_simplified.txt")

if __name__ == "__main__":
    run_all_pipeline()
