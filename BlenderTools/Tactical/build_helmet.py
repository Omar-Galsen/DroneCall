import bpy, math
from mathutils import Vector
COL="TAC_Helmet_V2"

def bounds(o):
    p=[o.matrix_world@Vector(v) for v in o.bound_box]
    return min(v.x for v in p),max(v.x for v in p),min(v.y for v in p),max(v.y for v in p),min(v.z for v in p),max(v.z for v in p)

def find_human():
    meshes=[o for o in bpy.context.scene.objects if o.type=="MESH" and not o.name.startswith(("Helmet_","TAC_"))]
    pref=[o for o in meshes if "human" in o.name.lower() or "body" in o.name.lower()]
    if not (pref or meshes): raise RuntimeError("Create/open the MPFB human first.")
    return max(pref or meshes,key=lambda o:bounds(o)[5]-bounds(o)[4])

def mat(n,c,metal=0,rough=.55):
    m=bpy.data.materials.get(n) or bpy.data.materials.new(n);m.use_nodes=True
    p=m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value=(*c,1);p.inputs["Metallic"].default_value=metal;p.inputs["Roughness"].default_value=rough
    return m

def fresh_collection():
    for name in ("TAC_Helmet_Component","TAC_Helmet_V2"):
        old=bpy.data.collections.get(name)
        if old:
            for o in list(old.objects): bpy.data.objects.remove(o,do_unlink=True)
            bpy.data.collections.remove(old)
    c=bpy.data.collections.new(COL);bpy.context.scene.collection.children.link(c);return c

def move(o):
    for c in list(o.users_collection): c.objects.unlink(o)
    C.objects.link(o)

def bevel(o,w,n=3):
    b=o.modifiers.new("Bevel","BEVEL");b.width=w;b.segments=n

def cube(n,l,s,m,r=(0,0,0),bev=.004):
    bpy.ops.mesh.primitive_cube_add(location=l,rotation=r);o=bpy.context.object;o.name=n;o.scale=s
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);bevel(o,bev);o.data.materials.append(m);move(o);return o

def cylinder(n,l,rad,depth,m,r=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=rad,depth=depth,location=l,rotation=r)
    o=bpy.context.object;o.name=n;o.data.materials.append(m);bevel(o,rad*.12,2);move(o);return o

h=find_human();xmin,xmax,ymin,ymax,zmin,zmax=bounds(h);H=zmax-zmin
cx=(xmin+xmax)/2;cy=(ymin+ymax)/2
# Character-relative head estimate
head_h=H*.135; head_w=H*.092; head_d=H*.105
cz=zmax-head_h*.43
front=cy-head_d*.56; rear=cy+head_d*.56

C=fresh_collection()
shellmat=mat("HelmetV2_Olive",(.105,.115,.075),0,.68)
railmat=mat("HelmetV2_Rail",(.025,.028,.024),.08,.48)
metal=mat("HelmetV2_Metal",(.045,.047,.042),.6,.32)
rubber=mat("HelmetV2_Rubber",(.018,.019,.017),0,.82)

# V2 shell: flatter/lower than V1.
bpy.ops.mesh.primitive_uv_sphere_add(segments=72,ring_count=36,location=(cx,cy,cz+head_h*.10))
shell=bpy.context.object;shell.name="Helmet_V2_Shell"
shell.scale=(head_w*.62,head_d*.61,head_h*.48)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)

# High-cut profile: trim bottom and raise openings near ears.
bpy.context.view_layer.objects.active=shell;bpy.ops.object.mode_set(mode="EDIT");bpy.ops.mesh.select_all(action="DESELECT");bpy.ops.object.mode_set(mode="OBJECT")
for v in shell.data.vertices:
    side=abs(v.co.x)/(head_w*.62)
    cut=-head_h*.075
    if side>.58: cut=head_h*(-.01 + .075*(side-.58)/.42)
    if v.co.z<cut: v.select=True
bpy.ops.object.mode_set(mode="EDIT");bpy.ops.mesh.delete(type="VERT");bpy.ops.object.mode_set(mode="OBJECT")
sol=shell.modifiers.new("BallisticShellThickness","SOLIDIFY");sol.thickness=H*.0032
bevel(shell,H*.0016,2)
for p in shell.data.polygons:p.use_smooth=True
shell.data.materials.append(shellmat);move(shell)

# Integrated front brow/rim.
cube("Helmet_V2_FrontBrow",(cx,front-H*.003,cz-head_h*.015),(head_w*.39,H*.0075,head_h*.042),shellmat,bev=H*.003)

# Curved-looking modular ARC rail assemblies: three overlapping pieces per side.
for side in (-1,1):
    sx=cx+side*head_w*.575
    for i,(yy,zz,ang) in enumerate(((cy-head_d*.20,cz+head_h*.08,-8),(cy,cz+head_h*.02,0),(cy+head_d*.19,cz-head_h*.015,8))):
        cube(f"Helmet_V2_Rail_{side}_{i}",(sx,yy,zz),(H*.006,head_d*.13,head_h*.065),railmat,
             r=(math.radians(side*ang),0,0),bev=H*.0035)
    # accessory rail slots
    for i,yy in enumerate((cy-head_d*.20,cy,cy+head_d*.20)):
        cube(f"Helmet_V2_RailSlot_{side}_{i}",(cx+side*head_w*.61,yy,cz+head_h*.025),
             (H*.003,head_d*.045,head_h*.014),metal,bev=H*.0015)

# Flush NVG shroud: layered trapezoid impression, much closer to shell.
cube("Helmet_V2_NVG_Base",(cx,front-H*.010,cz+head_h*.13),(head_w*.18,H*.006,head_h*.105),railmat,bev=H*.0035)
cube("Helmet_V2_NVG_Lock",(cx,front-H*.018,cz+head_h*.13),(head_w*.06,H*.005,head_h*.045),metal,bev=H*.002)
for side in (-1,1):
    cylinder(f"Helmet_V2_NVG_Bolt_{side}",(cx+side*head_w*.13,front-H*.018,cz+head_h*.10),H*.006,H*.006,metal,r=(math.pi/2,0,0))

# Velcro panels follow crown visually.
cube("Helmet_V2_VelcroTop",(cx,cy-head_d*.02,cz+head_h*.48),(head_w*.20,head_d*.20,H*.0014),rubber,bev=H*.003)
for side in (-1,1):
    cube(f"Helmet_V2_VelcroSide_{side}",(cx+side*head_w*.48,cy+head_d*.05,cz+head_h*.19),
         (H*.002,head_d*.15,head_h*.075),rubber,bev=H*.002)

# Rear retention / occipital adjustment unit.
cube("Helmet_V2_RearRetention",(cx,rear+H*.006,cz-head_h*.015),(head_w*.20,H*.007,head_h*.075),railmat,bev=H*.003)
cylinder("Helmet_V2_AdjustDial",(cx,rear+H*.016,cz-head_h*.015),H*.017,H*.010,metal,r=(math.pi/2,0,0))

# Chin strap anchors.
for side in (-1,1):
    cube(f"Helmet_V2_StrapAnchor_{side}",(cx+side*head_w*.43,cy+head_d*.22,cz-head_h*.15),
         (H*.006,H*.006,head_h*.035),rubber,r=(0,0,side*math.radians(15)),bev=H*.002)

for o in C.objects:
    o["dronecall_component"]="helmet_v2";o["reference"]="References/Tactical/Helmet_V2.png";o["fitted_to"]=h.name
bpy.ops.object.select_all(action="DESELECT")
for o in C.objects:o.select_set(True)
print("Helmet V2 built and fitted to",h.name)
