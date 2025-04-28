import numpy as np
import ifcopenshell
from datetime import datetime
import os

# ------------ Read coordinates from a text file
def read_coordinates_from_txt(file_path):
    coordinates = []
    with open(file_path, "r") as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) == 3:  # Ensure the line contains exactly 3 values
                x, y, z = map(float, parts)
                coordinates.append([x, y, z])
    if len(coordinates) != 2:
        raise ValueError("The input text file must contain exactly two rows of coordinates (start and end points).")
    return np.array(coordinates[0]), np.array(coordinates[1])

# --------- Input: Read start and end points from text file
input_file = "coordinates.txt"  # Replace with your input text file path
start, end = read_coordinates_from_txt(input_file)

# --------- Compute direction and length
vector = end - start
length = np.linalg.norm(vector)

if length == 0:
    raise ValueError("Start and end points are identical! Cannot create a pipe.")

direction = vector / length  # Unit vector

# ----------- Create ifc model 
model = ifcopenshell.file()

# ifc Structure: Project, Site, Building, Storey
project = model.create_entity("IfcProject", GlobalId="0RANDOMGUID01", Name="DetectedPipeProject")
site = model.create_entity("IfcSite", GlobalId="0RANDOMGUID02", Name="Site")
building = model.create_entity("IfcBuilding", GlobalId="0RANDOMGUID03", Name="Building")
storey = model.create_entity("IfcBuildingStorey", GlobalId="0RANDOMGUID04", Name="Floor 1")

model.create_entity("IfcRelAggregates", GlobalId="rel01", RelatingObject=project, RelatedObjects=[site])
model.create_entity("IfcRelAggregates", GlobalId="rel02", RelatingObject=site, RelatedObjects=[building])
model.create_entity("IfcRelAggregates", GlobalId="rel03", RelatingObject=building, RelatedObjects=[storey])

# ------------ Create Pipe Object
pipe = model.create_entity("IfcFlowSegment", GlobalId="PIPEGUID1234", Name="DetectedMetalPipe")

# Assign the pipe to the storey
model.create_entity(
    "IfcRelContainedInSpatialStructure",
    GlobalId="rel04",
    RelatingStructure=storey,
    RelatedElements=[pipe]
)

# ----------- Create placement (position and orientation) 
placement = model.create_entity(
    "IfcLocalPlacement",
    PlacementRelTo=None,
    RelativePlacement=model.create_entity(
        "IfcAxis2Placement3D",
        Location=model.create_entity("IfcCartesianPoint", Coordinates=start.tolist()),  # Fixed
        Axis=model.create_entity("IfcDirection", DirectionRatios=direction.tolist()),  # Fixed
        RefDirection=model.create_entity("IfcDirection", DirectionRatios=[1.0, 0.0, 0.0])  # Fixed
    )
)
pipe.ObjectPlacement = placement

# ------------ Create Geometry: Circular profile + extrusion
# Define a 5cm radius profile for the pipe cross-section
profile = model.create_entity(
    "IfcCircleProfileDef",
    ProfileType="AREA",
    Radius=0.05  # Adjust radius as needed
)

# Extrude along z axis (0,0,1) for the length of the pipe
extruded_solid = model.create_entity(
    "IfcExtrudedAreaSolid",
    SweptArea=profile,
    Position=model.create_entity(
        "IfcAxis2Placement3D",
        Location=model.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0)),
        Axis=model.create_entity("IfcDirection", DirectionRatios=(0.0, 0.0, 1.0)),
        RefDirection=model.create_entity("IfcDirection", DirectionRatios=(1.0, 0.0, 0.0))
    ),
    ExtrudedDirection=model.create_entity("IfcDirection", DirectionRatios=(0.0, 0.0, 1.0)),
    Depth=length
)

# Create a geometric representation context
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

# Wrap the geometry in a ShapeRepresentation
shape_rep = model.create_entity(
    "IfcShapeRepresentation",
    ContextOfItems=context,  # Use the created context
    RepresentationIdentifier="Body",
    RepresentationType="SweptSolid",
    Items=[extruded_solid]
)

# Assign to the pipe
pipe.Representation = model.create_entity(
    "IfcProductDefinitionShape",
    Representations=[shape_rep]
)

# ----------- Export the ifc file
# Create a dedicated directory for ifc files
output_dir = "ifc_outputs"
os.makedirs(output_dir, exist_ok=True)

# Generate a timestamped filename
timestamp_for_file = datetime.now().strftime("%m%d%y_%H%M")
output_file = os.path.join(output_dir, f"straight_pipe_{timestamp_for_file}.ifc")

# Save the ifc file
model.write(output_file)

print(f"IFC file created and saved as: {output_file}")