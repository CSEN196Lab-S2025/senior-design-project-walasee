import numpy as np
from scipy.spatial import Delaunay
import open3d as o3d
import ifcopenshell
import ifcopenshell.api

# === Step 1: Load CSV points ===
def load_points(csv_file):
    return np.loadtxt(csv_file, delimiter=',')

# === Step 2: Perform Delaunay Triangulation ===
def delaunay_mesh(points):
    tri = Delaunay(points)
    return tri

# === Step 3: Export to .PLY ===
def save_as_ply(points, simplices, output_ply):
    mesh = o3d.geometry.TriangleMesh()
    mesh.vertices = o3d.utility.Vector3dVector(points)
    mesh.triangles = o3d.utility.Vector3iVector(simplices)
    o3d.io.write_triangle_mesh(output_ply, mesh)

# === Step 4: Convert to IFC ===
def create_ifc(points, simplices, output_ifc):
    model = ifcopenshell.api.run("model.create_empty", schema_identifier="IFC4")
    project = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcProject", name="DelaunayMeshProject")
    context = ifcopenshell.api.run("context.add_context", model, context_type="Model")
    site = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcSite", name="Site")
    building = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcBuilding", name="Building")
    storey = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcBuildingStorey", name="Ground Floor")
    ifcopenshell.api.run("aggregate.assign_object", model, relating_object=project, product=site)
    ifcopenshell.api.run("aggregate.assign_object", model, relating_object=site, product=building)
    ifcopenshell.api.run("aggregate.assign_object", model, relating_object=building, product=storey)

    for idx, simplex in enumerate(simplices):
        vertices = points[simplex]
        mesh_proxy = ifcopenshell.api.run(
            "geometry.add_mesh",
            model,
            context=context,
            vertices=vertices.tolist(),
            faces=[[0,1,2]],
            name=f"MeshElement_{idx}"
        )
        ifcopenshell.api.run("aggregate.assign_object", model, relating_object=storey, product=mesh_proxy)

    model.write(output_ifc)

# === Main Execution ===
if __name__ == "__main__":
    input_csv = "wall_points.csv"  # <-- Your input file
    output_ply = "output_mesh.ply"
    output_ifc = "output_building.ifc"

    points = load_points(input_csv)
    tri = delaunay_mesh(points)
    save_as_ply(points, tri.simplices, output_ply)
    create_ifc(points, tri.simplices, output_ifc)

    print("✅ Mesh exported to:", output_ply)
    print("✅ IFC file saved as:", output_ifc)
