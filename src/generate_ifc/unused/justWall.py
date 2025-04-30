# ''' Useful links: 
# https://wiki.osarch.org/index.php?title=IfcOpenShell_code_examples#Samples_from_web'''

# import numpy as np
# import ifcopenshell
# from datetime import datetime
# import os

# O = 0., 0., 0.
# X = 1., 0., 0.
# Y = 0., 1., 0.
# Z = 0., 0., 1.

# # ------------ Read coordinates from a text file
# def read_coordinates_from_txt(file_path):
#     coordinates = []
#     with open(file_path, "r") as file:
#         for line in file:
#             parts = line.strip().split(",")
#             if len(parts) == 3:  # Ensure the line contains exactly 3 values
#                 x, y, z = map(float, parts)
#                 coordinates.append([x, y, z])
#     if len(coordinates) != 2:
#         raise ValueError("The input text file must contain exactly two rows of coordinates (start and end points).")
#     return np.array(coordinates[0]), np.array(coordinates[1])

# # --------- Input: Read start and end points from text file
# input_file = "coordinates.txt"  # Replace with your input text file path
# start, end = read_coordinates_from_txt(input_file)

# # --------- Compute direction and length
# vector = end - start
# length = np.linalg.norm(vector)

# if length == 0:
#     raise ValueError("Start and end points are identical! Cannot create a pipe.")

# direction = vector / length  # Unit vector

# # ----------- Create empty ifc file 
# model = ifcopenshell.file()

# # ---------- Create new ifc elements
# wall = model.create_entity('IfcWall', GlobalId=ifcopenshell.guid.new(), Name='Wall') #type: IfcWall
# print(wall.get_info())

# # Add element from one IFC file to another:
# '''
# wall = ifc.by_type('IfcWall')[0]
# new_ifc = ifcopenshell.file()
# new_ifc.add(wall)
# '''
import ifcopenshell
import os
from datetime import datetime

# -------- Input Wall Dimensions in centimeters
length_cm = 500  # Length of wall in cm
height_cm = 300  # Height of wall in cm
thickness_cm = 20  # Thickness of wall in cm

# -------- Convert to meters (IFC works in meters)
length = length_cm / 100.0
height = height_cm / 100.0
thickness = thickness_cm / 100.0

# -------- Create IFC Model
model = ifcopenshell.file(schema="IFC4")

# -------- Create Project Structure
project = model.create_entity("IfcProject", GlobalId="0RANDOMGUID01", Name="WallProject")
site = model.create_entity("IfcSite", GlobalId="0RANDOMGUID02", Name="Site")
building = model.create_entity("IfcBuilding", GlobalId="0RANDOMGUID03", Name="Building")
storey = model.create_entity("IfcBuildingStorey", GlobalId="0RANDOMGUID04", Name="Floor 1")

model.create_entity("IfcRelAggregates", GlobalId="rel01", RelatingObject=project, RelatedObjects=[site])
model.create_entity("IfcRelAggregates", GlobalId="rel02", RelatingObject=site, RelatedObjects=[building])
model.create_entity("IfcRelAggregates", GlobalId="rel03", RelatingObject=building, RelatedObjects=[storey])

# -------- Create Wall
wall = model.create_entity("IfcWallStandardCase", GlobalId="WALLGUID1234", Name="SimpleWall")

# Assign Wall to Storey
model.create_entity(
    "IfcRelContainedInSpatialStructure",
    GlobalId="rel04",
    RelatingStructure=storey,
    RelatedElements=[wall]
)

# -------- Placement
placement = model.create_entity(
    "IfcLocalPlacement",
    PlacementRelTo=None,
    RelativePlacement=model.create_entity(
        "IfcAxis2Placement3D",
        Location=model.create_entity("IfcCartesianPoint", Coordinates=[0.0, 0.0, 0.0]),
        Axis=model.create_entity("IfcDirection", DirectionRatios=[0.0, 0.0, 1.0]),
        RefDirection=model.create_entity("IfcDirection", DirectionRatios=[1.0, 0.0, 0.0])
    )
)
wall.ObjectPlacement = placement

# -------- Geometry: Create Wall Profile and Extrusion
profile = model.create_entity(
    "IfcArbitraryClosedProfileDef",
    ProfileType="AREA",
    OuterCurve=model.create_entity(
        "IfcPolyline",
        Points=[
            model.create_entity("IfcCartesianPoint", Coordinates=[0.0, 0.0, 0.0]),
            model.create_entity("IfcCartesianPoint", Coordinates=[length, 0.0, 0.0]),
            model.create_entity("IfcCartesianPoint", Coordinates=[length, thickness, 0.0]),
            model.create_entity("IfcCartesianPoint", Coordinates=[0.0, thickness, 0.0]),
            model.create_entity("IfcCartesianPoint", Coordinates=[0.0, 0.0, 0.0]),
        ]
    )
)

extruded_solid = model.create_entity(
    "IfcExtrudedAreaSolid",
    SweptArea=profile,
    Position=model.create_entity(
        "IfcAxis2Placement3D",
        Location=model.create_entity("IfcCartesianPoint", Coordinates=[0.0, 0.0, 0.0]),
        Axis=model.create_entity("IfcDirection", DirectionRatios=[0.0, 0.0, 1.0]),
        RefDirection=model.create_entity("IfcDirection", DirectionRatios=[1.0, 0.0, 0.0])
    ),
    ExtrudedDirection=model.create_entity("IfcDirection", DirectionRatios=[0.0, 0.0, 1.0]),
    Depth=height
)

# Context and Shape
context = model.create_entity(
    "IfcGeometricRepresentationContext",
    ContextIdentifier="Body",
    ContextType="Model",
    CoordinateSpaceDimension=3,
    Precision=1.0e-5,
    WorldCoordinateSystem=model.create_entity(
        "IfcAxis2Placement3D",
        Location=model.create_entity("IfcCartesianPoint", Coordinates=[0.0, 0.0, 0.0])
    )
)

shape_rep = model.create_entity(
    "IfcShapeRepresentation",
    ContextOfItems=context,
    RepresentationIdentifier="Body",
    RepresentationType="SweptSolid",
    Items=[extruded_solid]
)

wall.Representation = model.create_entity(
    "IfcProductDefinitionShape",
    Representations=[shape_rep]
)

# -------- Export IFC
output_dir = "ifc_outputs"
os.makedirs(output_dir, exist_ok=True)
timestamp_for_file = datetime.now().strftime("%m%d%y_%H%M")
output_file = os.path.join(output_dir, f"simple_wall_{timestamp_for_file}.ifc")
model.write(output_file)

print(f"IFC file created and saved as: {output_file}")
