import bpy
from mathutils import Vector

COLLECTION = "Tactical_Gear"

# ---------- helpers ----------
def bbox_world(obj):
    pts = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    xs = [p.x for p in pts]; ys = [p.y for p in pts]; zs = [p.z for p in pts]
    return (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))

def find_human_mesh():
    # Prefer MPFB-style names
    preferred = []
    fallback = []
    for o in bpy.context.scene.objects:
        if o.type != 'MESH':
            continue
        name = o.name.lower()
        if "human" in name or "body" in name:
            preferred.append(o)
        else:
            fallback.append(o)
    candidates = preferred or fallback
    if not candidates:
        raise RuntimeError("No mesh object found. Create/select an MPFB human first.")
    # choose tallest mesh in world space
    return max(candidates, key=lambda o: bbox_world(o)[5] - bbox_world(o)[4])

def get_collection():
    old = bpy.data.collections.get(COLLECTION)
    if old:
        for obj in list(old.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(old)
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
    for p in o.data.polygons:
        p.use_smooth = True
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

# ---------- detect MPFB body ----------
human = find_human_mesh()
xmin, xmax, ymin, ymax, zmin, zmax = bbox_world(human)
H = zmax - zmin
W = xmax - xmin
D = ymax - ymin
cx = (xmin + xmax) / 2
cy = (ymin + ymax) / 2

# ratios relative to detected body
chest_z = zmin + H * 0.72
waist_z = zmin + H * 0.54
knee_z = zmin + H * 0.28
head_z = zmin + H * 0.92

gear_col = get_collection()
olive = material("TAC_Olive", (0.10, 0.11, 0.075))
dark = material("TAC_Dark", (0.025, 0.03, 0.025), roughness=0.55)
fabric = material("TAC_Fabric", (0.15, 0.14, 0.105), roughness=0.85)
metal = material("TAC_Metal", (0.035, 0.04, 0.035), metallic=0.55, roughness=0.38)

front_y = ymin - D * 0.03
back_y = ymax + D * 0.03

# Plate carrier
cube("TAC_PlateCarrier_Front", (cx, front_y, chest_z), (W*0.29, D*0.08, H*0.145), olive, H*0.012)
cube("TAC_PlateCarrier_Back", (cx, back_y, chest_z), (W*0.29, D*0.08, H*0.145), olive, H*0.012)

# Shoulder pads
cube("TAC_ShoulderPad_L", (cx-W*0.34, cy, chest_z+H*0.07), (W*0.08, D*0.16, H*0.035), olive, H*0.008)
cube("TAC_ShoulderPad_R", (cx+W*0.34, cy, chest_z+H*0.07), (W*0.08, D*0.16, H*0.035), olive, H*0.008)

# Mag pouches
for i, xoff in enumerate((-0.16, 0.0, 0.16), 1):
    cube(f"TAC_MagPouch_{i}", (cx+W*xoff, front_y-D*0.07, chest_z-H*0.06), (W*0.065, D*0.055, H*0.055), fabric, H*0.005)

# Belt + utilities
cube("TAC_Belt", (cx, cy, waist_z), (W*0.34, D*0.15, H*0.018), dark, H*0.004)
cube("TAC_Utility_L", (cx-W*0.33, cy, waist_z-H*0.025), (W*0.075, D*0.09, H*0.05), olive, H*0.006)
cube("TAC_Utility_R", (cx+W*0.33, cy, waist_z-H*0.025), (W*0.075, D*0.09, H*0.05), olive, H*0.006)
cube("TAC_Holster", (cx+W*0.39, cy-D*0.02, waist_z-H*0.11), (W*0.055, D*0.08, H*0.075), dark, H*0.005)

# Knee pads
cube("TAC_KneePad_L", (cx-W*0.12, front_y-D*0.03, knee_z), (W*0.09, D*0.05, H*0.05), dark, H*0.008)
cube("TAC_KneePad_R", (cx+W*0.12, front_y-D*0.03, knee_z), (W*0.09, D*0.05, H*0.05), dark, H*0.008)

# Helmet + headset
sphere("TAC_Helmet", (cx, cy, head_z), (W*0.18, D*0.19, H*0.07), olive)
cube("TAC_NVG_Mount", (cx, front_y-D*0.02, head_z), (W*0.045, D*0.022, H*0.022), metal, H*0.003)
cyl("TAC_EarCup_L", (cx-W*0.19, cy, head_z-H*0.02), W*0.045, D*0.05, dark, (0,1.5708,0))
cyl("TAC_EarCup_R", (cx+W*0.19, cy, head_z-H*0.02), W*0.045, D*0.05, dark, (0,1.5708,0))

# Backpack + radio
cube("TAC_Backpack", (cx, back_y+D*0.08, chest_z-H*0.02), (W*0.23, D*0.12, H*0.16), olive, H*0.012)
cube("TAC_Radio", (cx-W*0.27, back_y+D*0.04, chest_z), (W*0.055, D*0.05, H*0.055), dark, H*0.005)
cyl("TAC_RadioAntenna", (cx-W*0.27, back_y+D*0.04, chest_z+H*0.08), W*0.008, H*0.13, dark)

for obj in gear_col.objects:
    obj["dronecall_asset"] = "tactical_gear"
    obj["fitted_to"] = human.name
    obj["detected_height"] = H

print(f"Detected human: {human.name}")
print(f"Bounds H={H:.4f} W={W:.4f} D={D:.4f}")
print(f"Created {len(gear_col.objects)} fitted tactical gear objects.")
