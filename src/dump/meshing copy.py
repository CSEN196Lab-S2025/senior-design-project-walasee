import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay
import open3d as o3d
import ifcopenshell

# === Step 1: Load CSV points ===
def load_points(csv_file):
    return np.loadtxt(csv_file, delimiter=',')

# === Step 2: Perform 2D Delaunay Triangulation ===
def delaunay_mesh_2d(points_3d):
    points_2d = points_3d[:, :2]  # Take only X and Y for triangulation
    tri = Delaunay(points_2d)
    return tri

def delaunay_with_distance_limit(points, max_edge_length):
    points_2d = points[:, :2]  # Assuming 2D triangulation for wall data
    tri = Delaunay(points_2d)
    
    # Build a list of valid triangles
    valid_triangles = []
    for simplex in tri.simplices:
        pts = points[simplex]
        # Compute edge lengths
        d01 = np.linalg.norm(pts[0] - pts[1])
        d12 = np.linalg.norm(pts[1] - pts[2])
        d20 = np.linalg.norm(pts[2] - pts[0])

        if d01 <= max_edge_length and d12 <= max_edge_length and d20 <= max_edge_length:
            valid_triangles.append(simplex)

    return np.array(valid_triangles)


# === Step 3: Export to .PLY ===
def save_as_ply(points, simplices, output_ply):
    mesh = o3d.geometry.TriangleMesh()
    mesh.vertices = o3d.utility.Vector3dVector(points)
    mesh.triangles = o3d.utility.Vector3iVector(simplices)
    o3d.io.write_triangle_mesh(output_ply, mesh)

# === Step 4: Create IFC Model (legacy method) ===
def create_ifc(points, simplices, output_ifc):
    model = ifcopenshell.file()

    # Create essential IFC project structure
    project = model.create_entity("IfcProject", GlobalId="2z$8kd4D55hABYh5gAJBz3", Name="DelaunayMeshProject")
    site = model.create_entity("IfcSite", GlobalId="1B6W2lVRL0K9uYk3zv$PaL", Name="Site")
    building = model.create_entity("IfcBuilding", GlobalId="2F$4O4VET1aOb4XiBlXBcb", Name="Building")
    storey = model.create_entity("IfcBuildingStorey", GlobalId="3UjLF3Nv1Fbfxs__7I4n4v", Name="Ground Floor")

    # Assign relationships manually
    rel_agg_site = model.create_entity("IfcRelAggregates", GlobalId="agg-site", RelatingObject=project, RelatedObjects=[site])
    rel_agg_building = model.create_entity("IfcRelAggregates", GlobalId="agg-building", RelatingObject=site, RelatedObjects=[building])
    rel_agg_storey = model.create_entity("IfcRelAggregates", GlobalId="agg-storey", RelatingObject=building, RelatedObjects=[storey])

    # Create mesh objects as IfcBuildingElementProxy
    for idx, simplex in enumerate(simplices):
        vertices = points[simplex]

        # For legacy compatibility, you usually store geometry as IfcFacetedBrep or Proxy without full mesh here
        mesh_element = model.create_entity(
            "IfcBuildingElementProxy",
            GlobalId=f"mesh-{idx:05d}",
            Name=f"MeshElement_{idx}"
        )

        # Add to storey
        model.create_entity(
            "IfcRelContainedInSpatialStructure",
            GlobalId=f"rel-contain-{idx:05d}",
            RelatingStructure=storey,
            RelatedElements=[mesh_element]
        )

    model.write(output_ifc)

# Plot Delaunay Mesh
def plot2D(save_path="delaunay_2d_plot.png"):
    points = np.loadtxt("wall_points.csv", delimiter=',')
    points_2d = points[:, :2]
    tri = Delaunay(points_2d)

    plt.figure(figsize=(8, 8))
    plt.triplot(points_2d[:, 0], points_2d[:, 1], tri.simplices, color='blue')
    plt.plot(points_2d[:, 0], points_2d[:, 1], 'ro')
    plt.title("2D Delaunay Mesh")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.axis("equal")
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"✅ 2D Delaunay plot saved as: {save_path}")

def plot3D():
    # Load the mesh from your saved file
    mesh = o3d.io.read_triangle_mesh("output_mesh.ply")

    # Simple viewer
    o3d.visualization.draw_geometries([mesh])

# === Main Execution ===
if __name__ == "__main__":
    input_csv = "wall_points.csv"  # <-- Your input file
    output_ply = "output_mesh.ply"
    output_ifc = "output_building.ifc"

    points = load_points(input_csv)
    tri = delaunay_mesh_2d(points)  # 2D triangulation for flat wall data
    save_as_ply(points, tri.simplices, output_ply)
    create_ifc(points, tri.simplices, output_ifc)

    max_allowed_edge = 0.5  # Set your own physical distance threshold (meters? cm?)
    filtered_simplices = delaunay_with_distance_limit(points, max_allowed_edge)

    print(f"✅ Triangles after filtering: {len(filtered_simplices)}")


    print("✅ Mesh exported to:", output_ply)
    print("✅ IFC file saved as:", output_ifc)

    plot2D()
    # plot3D()