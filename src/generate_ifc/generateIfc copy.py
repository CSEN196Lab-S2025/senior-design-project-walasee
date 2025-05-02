import ifcopenshell
import os
from datetime import datetime
import math

'''
IMPORTANT: All inputted coordinates are blown up by 100 because the online ifc viewer could
show anything if I put anything less than 1 meter. We shall see if Revit allows exact dimensions.

WALL, 5000, 4000, 200 (WALL, length, width/thickness, height)
PIPE, 1200.1667, 3200.0000, 800.0000, 1200.1667, 1900.7923, 800.0000 (PIPE, x, y, z, x1, y2, z2)
PIPE, 1200.1667, 1900.7923, 800.0000, 3700.6447, 1900.7923, 800.0000
PIPE, 3700.6447, 1900.7923, 800.0000, 3700.6447, 900.0000, 800.0000

'''
#def generateIfcFile(input_file):
    # -------- Parse input
input_file = "coordsForIfc.txt"
custom_pipe_segments = []

with open(input_file, "r") as f:
    for line in f:
        parts = line.strip().split(",")
        if parts[0].strip().upper() == "WALL":
            length_cm = float(parts[1])
            height_cm = float(parts[2])
            thickness_cm = float(parts[3])
        elif parts[0].strip().upper() == "PIPE":
            coords = list(map(float, parts[1:]))
            start = (coords[0], coords[1], coords[2])
            end = (coords[3], coords[4], coords[5])
            custom_pipe_segments.append((start, end))

# -------- Convert to meters
length = length_cm /100
height = height_cm / 100
thickness = thickness_cm / 100
pipe_radius_cm = 100 # 100 meters right now, online ifc viewer can't show smt that small
pipe_radius = pipe_radius_cm / 100
custom_pipe_segments = [
    ((x1/100, z1/100, y1/100), (x2/100, z2/100, y2/100))
    for (x1, y1, z1), (x2, y2, z2) in custom_pipe_segments
]

# -------- Create blank IFC model
model = ifcopenshell.file(schema="IFC4")

# -------- Project structure
project = model.create_entity("IfcProject", GlobalId="0RANDOMGUID01", Name="WallWithPipesProject")
site = model.create_entity("IfcSite", GlobalId="0RANDOMGUID02", Name="Site")
building = model.create_entity("IfcBuilding", GlobalId="0RANDOMGUID03", Name="Building")
storey = model.create_entity("IfcBuildingStorey", GlobalId="0RANDOMGUID04", Name="Floor 1")

model.create_entity("IfcRelAggregates", GlobalId="rel01", RelatingObject=project, RelatedObjects=[site])
model.create_entity("IfcRelAggregates", GlobalId="rel02", RelatingObject=site, RelatedObjects=[building])
model.create_entity("IfcRelAggregates", GlobalId="rel03", RelatingObject=building, RelatedObjects=[storey])

# -------- Wall
wall = model.create_entity("IfcWallStandardCase", GlobalId="WALLGUID1234", Name="SimpleWall")

model.create_entity(
    "IfcRelContainedInSpatialStructure",
    GlobalId="rel04",
    RelatingStructure=storey,
    RelatedElements=[wall]
)

wall.ObjectPlacement = model.create_entity(
    "IfcLocalPlacement",
    PlacementRelTo=None,
    RelativePlacement=model.create_entity(
        "IfcAxis2Placement3D",
        Location=model.create_entity("IfcCartesianPoint", Coordinates=[0.0, 0.0, 0.0]),
        Axis=model.create_entity("IfcDirection", DirectionRatios=[0.0, 0.0, 1.0]),
        RefDirection=model.create_entity("IfcDirection", DirectionRatios=[1.0, 0.0, 0.0])
    )
)

wall_profile = model.create_entity(
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

wall_solid = model.create_entity(
    "IfcExtrudedAreaSolid",
    SweptArea=wall_profile,
    Position=model.create_entity(
        "IfcAxis2Placement3D",
        Location=model.create_entity("IfcCartesianPoint", Coordinates=[0.0, 0.0, 0.0]),
        Axis=model.create_entity("IfcDirection", DirectionRatios=[0.0, 0.0, 1.0]),
        RefDirection=model.create_entity("IfcDirection", DirectionRatios=[1.0, 0.0, 0.0])
    ),
    ExtrudedDirection=model.create_entity("IfcDirection", DirectionRatios=[0.0, 0.0, 1.0]),
    Depth=height
)

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

wall_shape = model.create_entity(
    "IfcShapeRepresentation",
    ContextOfItems=context,
    RepresentationIdentifier="Body",
    RepresentationType="SweptSolid",
    Items=[wall_solid]
)

wall.Representation = model.create_entity(
    "IfcProductDefinitionShape",
    Representations=[wall_shape]
)

# -------- Pipes
pipe_counter = 0

for (start, end) in custom_pipe_segments:
    '''
        start = (1, 2, 3)  # (x, y, z)
        (x1, z1, y1) = start
        print(x1, z1, y1)  # Output: 1, 3, 2
    '''
    # not just naming convention, actually swaps y and z ^^
    (x1, y1, z1) = start
    (x2, y2, z2) = end

    # Compute direction vector (swapped y and z)
    dx = x2 - x1
    dz = z2 - z1
    dy = y2 - y1
    length = math.sqrt(dx**2 + dy**2 + dz**2)

    # Normalize direction
    if length == 0:
        raise ValueError("Pipe start and end points cannot be the same.")

    dir_x = dx / length
    dir_y = dy / length
    dir_z = dz / length

    pipe = model.create_entity("IfcPipeSegment", GlobalId=f"PIPEGUID{pipe_counter:04d}", Name=f"Pipe{pipe_counter}")

    model.create_entity(
        "IfcRelContainedInSpatialStructure",
        GlobalId=f"relPipe{pipe_counter:04d}",
        RelatingStructure=storey,
        RelatedElements=[pipe]
    )

    pipe.ObjectPlacement = model.create_entity(
        "IfcLocalPlacement",
        PlacementRelTo=None,
        RelativePlacement=model.create_entity(
            "IfcAxis2Placement3D",
            Location=model.create_entity("IfcCartesianPoint", Coordinates=[x1, y1, z1]),
            Axis=model.create_entity("IfcDirection", DirectionRatios=[dir_x, dir_y, dir_z]),
            RefDirection=model.create_entity("IfcDirection", DirectionRatios=[0.0, 1.0, 0.0])
        )
    )

    pipe_profile = model.create_entity(
        "IfcCircleProfileDef",
        ProfileType="AREA",
        Radius=pipe_radius
    )

    pipe_solid = model.create_entity(
        "IfcExtrudedAreaSolid",
        SweptArea=pipe_profile,
        Position=model.create_entity(
            "IfcAxis2Placement3D",
            Location=model.create_entity("IfcCartesianPoint", Coordinates=[0.0, 0.0, 0.0]),
            Axis=model.create_entity("IfcDirection", DirectionRatios=[0.0, 0.0, 1.0]),
            RefDirection=model.create_entity("IfcDirection", DirectionRatios=[1.0, 0.0, 0.0])
        ),
        ExtrudedDirection=model.create_entity("IfcDirection", DirectionRatios=[0.0, 0.0, 1.0]),
        Depth=length
    )

    pipe_shape = model.create_entity(
        "IfcShapeRepresentation",
        ContextOfItems=context,
        RepresentationIdentifier="Body",
        RepresentationType="SweptSolid",
        Items=[pipe_solid]
    )

    pipe.Representation = model.create_entity(
        "IfcProductDefinitionShape",
        Representations=[pipe_shape]
    )

    pipe_counter += 1

# -------- Export IFC
output_dir = "ifc_outputs"
os.makedirs(output_dir, exist_ok=True)
timestamp_for_file = datetime.now().strftime("%m%d%y_%H%M")
output_file = os.path.join(output_dir, f"wall_with_pipes_{timestamp_for_file}.ifc")
model.write(output_file)

print(f"IFC file created and saved as: {output_file}")
