import sys
import matplotlib.pyplot as plt

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py inputfile.txt")
        sys.exit(1)

    input_file = sys.argv[1]

    x_coords = []
    y_coords = []

    # Read file
    with open(input_file, 'r') as f:
        for line in f:
            parts = line.strip().split(',')
            if len(parts) >= 3:
                try:
                    x = float(parts[0])
                    y = float(parts[1])
                    # z = float(parts[2])  # Ignored
                    x_coords.append(x)
                    y_coords.append(y)
                except ValueError:
                    continue  # skip bad lines

    # Plot
    plt.figure(figsize=(8, 6))
    plt.scatter(x_coords, y_coords, s=40)  # bigger dots
    plt.title('2D Dot Plot of Pipe Points (X vs Y)')
    plt.xlabel('X (cm)')
    plt.ylabel('Y (cm)')
    plt.grid(True)
    plt.axis('equal')
    plt.show()

if __name__ == "__main__":
    main()

