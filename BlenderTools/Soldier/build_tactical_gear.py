import bpy
from mathutils import Vector

# Tactical gear builder for an existing MPFB human.
# Select the MPFB body or rig, then run this script.
# Gear is deliberately separate from the human so it can be refined/replaced later.

COLLECTION = "Tactical_Gear"

def get_collection():
    c = bpy.data.collections.get(COLLECTION)
    if not c:
        c = bpy.data.collections.new(COLLECTION)
        bpy.context.scene.collection.children.link(c)
    return c

def material(name, color, metallic=0.0, roughness=0.65):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return m

def move_to_collection(obj, collection):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)

def cube(name, loc, scale, mat, bevel=0.02):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        b = o.modifiers.new("Bevel", "BEVEL")
        b.width = bevel
        b.segments = 3
    o.data.materials.append(mat)
    move_to_collection(o, gear_col)
    return o

def sphere(name, loc, scale, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=40, ring_count=20, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for p in o.data.polygons: p.use_smooth = True
    o.data.materials.append(mat)
    move_to_collection(o, gear_col)
    return o

def cyl(name, loc, radius, depth, mat, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=depth, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(mat)
    move_to_collection(o, gear_col)
    return o

gear_col = get_collection()
olive = material("TAC_Olive", (0.10, 0.11, 0.075))
dark = material("TAC_Dark", (0.025, 0.03, 0.025), roughness=0.55)
fabric = material("TAC_Fabric", (0.15, 0.14, 0.105), roughness=0.85)
metal = material("TAC_Metal", (0.035,0.04,0.035), metallic=0.55, roughness=0.38)

# Dimensions assume the default MPFB human is around 1.7-1.8 m tall.
# Plate carrier
cube("TAC_PlateCarrier_Front", (0,-0.145,1.32), (0.27,0.055,0.27), olive, 0.035)
cube("TAC_PlateCarrier_Back", (0,0.145,1.32), (0.27,0.055,0.27), olive, 0.035)
cube("TAC_ShoulderPad_L", (-0.31,0,1.48), (0.095,0.13,0.07), olive, 0.03)
cube("TAC_ShoulderPad_R", (0.31,0,1.48), (0.095,0.13,0.07), olive, 0.03)

# Magazine pouches
for i, x in enumerate((-0.16, 0.0, 0.16), 1):
    cube(f"TAC_MagPouch_{i}", (x,-0.215,1.22), (0.062,0.04,0.115), fabric, 0.015)

# Belt and utility pouches
cube("TAC_Belt", (0,0,0.98), (0.31,0.12,0.035), dark, 0.012)
cube("TAC_Utility_L", (-0.29,0,0.93), (0.075,0.09,0.10), olive, 0.02)
cube("TAC_Utility_R", (0.29,0,0.93), (0.075,0.09,0.10), olive, 0.02)
cube("TAC_Holster", (0.34,-0.01,0.77), (0.055,0.075,0.15), dark, 0.018)

# Knee pads
cube("TAC_KneePad_L", (-0.105,-0.105,0.48), (0.095,0.035,0.105), dark, 0.035)
cube("TAC_KneePad_R", (0.105,-0.105,0.48), (0.095,0.035,0.105), dark, 0.035)

# Helmet, side rails and NVG mount
helmet = sphere("TAC_Helmet", (0,0,1.79), (0.155,0.14,0.105), olive)
cube("TAC_HelmetRail_L", (-0.145,0,1.79), (0.018,0.085,0.035), dark, 0.01)
cube("TAC_HelmetRail_R", (0.145,0,1.79), (0.018,0.085,0.035), dark, 0.01)
cube("TAC_NVG_Mount", (0,-0.132,1.80), (0.045,0.018,0.04), metal, 0.008)

# Headset
cyl("TAC_EarCup_L", (-0.16,0,1.73), 0.045, 0.035, dark, (0,1.5708,0))
cyl("TAC_EarCup_R", (0.16,0,1.73), 0.045, 0.035, dark, (0,1.5708,0))

# Backpack and radio
cube("TAC_Backpack", (0,0.205,1.27), (0.235,0.095,0.28), olive, 0.045)
cube("TAC_Radio", (-0.24,0.17,1.30), (0.055,0.045,0.105), dark, 0.015)
cyl("TAC_RadioAntenna", (-0.24,0.17,1.47), 0.008, 0.24, dark)

# Gloves as cuffs (keeps MPFB hands visible)
cube("TAC_GloveCuff_L", (-0.55,0,1.10), (0.055,0.065,0.055), dark, 0.02)
cube("TAC_GloveCuff_R", (0.55,0,1.10), (0.055,0.065,0.055), dark, 0.02)

# Organize metadata
for obj in gear_col.objects:
    obj["dronecall_asset"] = "tactical_gear"
    obj["game_ready_candidate"] = True

print(f"Created {len(gear_col.objects)} tactical gear objects in collection '{COLLECTION}'.")
print("Next: fit these pieces to the MPFB body, then bind/parent them to the final game rig.")
