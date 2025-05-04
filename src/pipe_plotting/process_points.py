import numpy as np
import matplotlib.pyplot as plt
import sys

# ---- CONFIGURATION ----
X_TOLERANCE = 4.0  # maximum X distance between points to be in same vertical cluster (cm)
Y_TOLERANCE = 4.0  # maximum Y distance between points to be in same horizontal cluster (cm)
MIN_SEGMENT_LENGTH = 5.0  # minimum length of a segment to be valid (cm)

# # ---- COMMAND LINE ARGUMENTS ----
# if len(sys.argv) != 4:
#     print("Usage: python detect_pipe.py input_file output_file output_png")
#     sys.exit(1)

# input_file = sys.argv[1]
# output_file = 'segments.txt'
# output_png = 'plot.png'


# ---- STEP 1: READ XYZ POINT DATA FROM FILE ----
def read_points(filename):
    points = []
    with open(filename, 'r') as f:
        for line in f:
            parts = line.strip().split(',')
            if len(parts) >= 3:
                x, y, z = map(float, parts[:3])
                points.append([x, y, z])
    return np.array(points)


# ---- STEP 2: CLUSTER POINTS ALONG AN AXIS ----
def cluster_by_axis(points, axis_idx, tolerance):    
    sorted_points = points[np.argsort(points[:, axis_idx])]  #sort points along axis
    clusters = []
    current_cluster = [sorted_points[0]]
    current_val = sorted_points[0][axis_idx]

    for pt in sorted_points[1:]:
        if abs(pt[axis_idx] - current_val) <= tolerance:
            current_cluster.append(pt)
        else:
            clusters.append(np.array(current_cluster))
            current_cluster = [pt]
            current_val = pt[axis_idx]
    clusters.append(np.array(current_cluster))  # add last cluster
    return clusters

def run_all(input_file, output_file, output_png):
    points = read_points(input_file)

    # Cluster points vertically and horizontally
    vertical_clusters = cluster_by_axis(points, axis_idx=0, tolerance=X_TOLERANCE)
    horizontal_clusters = cluster_by_axis(points, axis_idx=1, tolerance=Y_TOLERANCE)

    segments = []

    # ---- STEP 3: CREATE LINE SEGMENTS FROM CLUSTERS ----
    for cluster in vertical_clusters:
        if len(cluster) < 2:
            continue
        mean_x = np.mean(cluster[:, 0])
        min_y = np.min(cluster[:, 1])
        max_y = np.max(cluster[:, 1])
        z_val = np.mean(cluster[:, 2])
        segment_length = abs(max_y - min_y)
        if segment_length >= MIN_SEGMENT_LENGTH:
            segments.append([mean_x, min_y, mean_x, max_y, z_val, z_val, True])  # True: vertical

    for cluster in horizontal_clusters:
        if len(cluster) < 2:
            continue
        mean_y = np.mean(cluster[:, 1])
        min_x = np.min(cluster[:, 0])
        max_x = np.max(cluster[:, 0])
        z_val = np.mean(cluster[:, 2])
        segment_length = abs(max_x - min_x)
        if segment_length >= MIN_SEGMENT_LENGTH:
            segments.append([min_x, mean_y, max_x, mean_y, z_val, z_val, False])  # False: horizontal

    # ---- STEP 4: SNAP CLOSE ENDPOINTS TO ALIGN THEM ----
    snapped_points = {}  # maps original endpoints to snapped positions
    for i in range(len(segments)):
        for j in range(len(segments)):
            if i == j:
                continue
            xi1, yi1, xi2, yi2, _, _, _ = segments[i]
            xj1, yj1, xj2, yj2, _, _, _ = segments[j]

            endpoints_i = [(xi1, yi1), (xi2, yi2)]
            endpoints_j = [(xj1, yj1), (xj2, yj2)]

            for idx_i, (xi, yi) in enumerate(endpoints_i):
                for idx_j, (xj, yj) in enumerate(endpoints_j):
                    dx = abs(xi - xj)
                    dy = abs(yi - yj)
                    if dx <= X_TOLERANCE and dy <= Y_TOLERANCE:

                        # Snap to the closer coordinate axis
                        snap_x = xi if dx < dy else xj
                        snap_y = yi if dy <= dx else yj

                        # Update segment i endpoint
                        if idx_i == 0:
                            snapped_points[(segments[i][0], segments[i][1])] = (snap_x, snap_y)
                            segments[i][0], segments[i][1] = snap_x, snap_y
                        else:
                            snapped_points[(segments[i][2], segments[i][3])] = (snap_x, snap_y)
                            segments[i][2], segments[i][3] = snap_x, snap_y

                        # Update segment j endpoint
                        if idx_j == 0:
                            snapped_points[(segments[j][0], segments[j][1])] = (snap_x, snap_y)
                            segments[j][0], segments[j][1] = snap_x, snap_y
                        else:
                            snapped_points[(segments[j][2], segments[j][3])] = (snap_x, snap_y)
                            segments[j][2], segments[j][3] = snap_x, snap_y

    # ---- STEP 5: STRAIGHTEN SEGMENTS USING SNAP ANCHORS ----
    for idx, seg in enumerate(segments):
        x1, y1, x2, y2, z1, z2, is_vertical = seg

        anchor = None
        p1 = (x1, y1)
        p2 = (x2, y2)

        # Find anchor point if snapped
        if p1 in snapped_points:
            anchor = snapped_points[p1]
        elif p2 in snapped_points:
            anchor = snapped_points[p2]

        if anchor:
            anchor_x, anchor_y = anchor
            if is_vertical:
                segments[idx][0], segments[idx][2] = anchor_x, anchor_x  # force X constant
            else:
                segments[idx][1], segments[idx][3] = anchor_y, anchor_y  # force Y constant
        else:
            # No snapped anchor: keep original alignment
            if is_vertical:
                segments[idx][0], segments[idx][2] = x1, x1
            else:
                segments[idx][1], segments[idx][3] = y1, y1

    # ---- STEP 6: ALIGN SEGMENTS AT SHARED CORNERS ----
    corner_points = {}  # maps rounded (x,y) → list of segments touching that corner
    for seg in segments:
        for coord in [(seg[0], seg[1]), (seg[2], seg[3])]:
            key = (round(coord[0], 3), round(coord[1], 3))
            if key not in corner_points:
                corner_points[key] = []
            corner_points[key].append(seg)

    for (x_key, y_key), touching_segments in corner_points.items():
        has_horizontal = any(not s[6] for s in touching_segments)
        has_vertical = any(s[6] for s in touching_segments)
        for seg in touching_segments:
            if has_horizontal and not seg[6]:
                seg[1], seg[3] = y_key, y_key  # align Y for horizontal
            if has_vertical and seg[6]:
                seg[0], seg[2] = x_key, x_key  # align X for vertical

    # ---- STEP 7: PLOT RESULTS ----
    plt.figure(figsize=(10, 8))
    plt.scatter(points[:, 0], points[:, 1], color='blue', label='Raw Points')
    for seg in segments:
        x1, y1, x2, y2, _, _, _ = seg
        plt.plot([x1, x2], [y1, y2], color='red', linewidth=4)
    plt.xlabel('X (cm)')
    plt.ylabel('Y (cm)')
    plt.title('Pipe Path Detection')
    #plt.gca().invert_yaxis()  # flip Y axis for top-down view
    plt.axis('equal')
    plt.grid(True)
    plt.savefig(output_png)
    #plt.show()

    # ---- STEP 8: WRITE FINAL SEGMENTS TO FILE ----
    with open(output_file, 'w') as f:
        print("here")
        for seg in segments:
            # x1, y1, z1, x2, y2, z2
            f.write(f"{seg[0]:.4f}, {seg[1]:.4f}, {seg[4]:.4f}, {seg[2]:.4f}, {seg[3]:.4f}, {seg[5]:.4f}\n")

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python process_points.py pathTo/walabotClean_$(time).txt output_filename output_png")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    output_png = sys.argv[3]
    run_all(input_file, output_file, output_png)
