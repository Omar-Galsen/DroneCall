import bpy, math
from mathutils import Vector
COL="TAC_Helmet_Component"

def bounds(o):
 p=[o.matrix_world@Vector(v) for v in o.bound_box]
 return min(v.x for v in p),max(v.x for v in p),min(v.y for v in p),max(v.y for v in p),min(v.z for v in p),max(v.z for v in p)

def human():
 meshes=[o for o in bpy.context.scene.objects if o.type=="MESH" and not o.name.startswith("TAC_")]
 pref=[o for o in meshes if "human" in o.name.lower() or "body" in o.name.lower()]
 q=pref or meshes
 if not q: raise RuntimeError("No MPFB human mesh found.")
 return max(q,key=lambda o:bounds(o)[5]-bounds(o)[4])

def mat(n,c,metal=0,rough=.55):
 m=bpy.data.materials.get(n) or bpy.data.materials.new(n);m.use_nodes=True
 p=m.node_tree.nodes.get("Principled BSDF");p.inputs["Base Color"].default_value=(*c,1);p.inputs["Metallic"].default_value=metal;p.inputs["Roughness"].default_value=rough
 return m

old=bpy.data.collections.get(COL)
if old:
 for o in list(old.objects): bpy.data.objects.remove(o,do_unlink=True)
 bpy.data.collections.remove(old)
C=bpy.data.collections.new(COL);bpy.context.scene.collection.children.link(C)

def move(o):
 for c in list(o.users_collection): c.objects.unlink(o)
 C.objects.link(o)
def cube(n,l,s,m,r=(0,0,0),b=.006):
 bpy.ops.mesh.primitive_cube_add(location=l,rotation=r);o=bpy.context.object;o.name=n;o.scale=s
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 x=o.modifiers.new("Bevel","BEVEL");x.width=b;x.segments=3;o.data.materials.append(m);move(o);return o

h=human();xmin,xmax,ymin,ymax,zmin,zmax=bounds(h);H=zmax-zmin;W=xmax-xmin;D=ymax-ymin
cx=(xmin+xmax)/2;cy=(ymin+ymax)/2
# Approximate skull from top portion of MPFB body. All helmet dimensions scale with character height.
head_h=H*.135; head_w=H*.095; head_d=H*.11
cz=zmax-head_h*.43
shellmat=mat("Helmet_Olive",(.10,.115,.075),0,.62);rail=mat("Helmet_Rail",(.025,.028,.025),.15,.42);metal=mat("Helmet_Metal",(.035,.038,.035),.65,.32);rub=mat("Helmet_Rubber",(.018,.02,.018),0,.78)

bpy.ops.mesh.primitive_uv_sphere_add(segments=64,ring_count=32,location=(cx,cy,cz+head_h*.13))
o=bpy.context.object;o.name="Helmet_Shell";o.scale=(head_w*.64,head_d*.63,head_h*.60);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
bpy.context.view_layer.objects.active=o;bpy.ops.object.mode_set(mode="EDIT");bpy.ops.mesh.select_all(action="DESELECT");bpy.ops.object.mode_set(mode="OBJECT")
for v in o.data.vertices:
 if v.co.z < -head_h*.12 or (v.co.z<head_h*.03 and abs(v.co.x)>head_w*.46): v.select=True
bpy.ops.object.mode_set(mode="EDIT");bpy.ops.mesh.delete(type="VERT");bpy.ops.object.mode_set(mode="OBJECT")
s=o.modifiers.new("ShellThickness","SOLIDIFY");s.thickness=H*.0035
b=o.modifiers.new("EdgeSoftness","BEVEL");b.width=H*.0018;b.segments=2
for p in o.data.polygons:p.use_smooth=True
o.data.materials.append(shellmat);move(o)

front=ymin-D*.04
cube("Helmet_FrontRim",(cx,front,cz),(head_w*.43,D*.025,head_h*.07),shellmat,b=H*.004)
for side in (-1,1):
 cube(f"Helmet_SideRail_{side}",(cx+side*head_w*.56,cy,cz+head_h*.05),(H*.007,head_d*.32,head_h*.10),rail,r=(0,0,side*math.radians(4)),b=H*.003)
cube("Helmet_NVG_Shroud",(cx,front-D*.025,cz+head_h*.20),(head_w*.18,D*.018,head_h*.13),rail,b=H*.003)
cube("Helmet_NVG_Center",(cx,front-D*.045,cz+head_h*.20),(head_w*.065,D*.014,head_h*.055),metal,b=H*.002)
cube("Helmet_Velcro_Top",(cx,cy-D*.02,cz+head_h*.59),(head_w*.22,head_d*.20,H*.0015),rub,b=H*.003)
cube("Helmet_RearRetention",(cx,ymax+D*.03,cz+head_h*.02),(head_w*.22,D*.022,head_h*.10),rail,b=H*.003)

for x in C.objects:
 x["dronecall_component"]="helmet";x["fitted_to"]=h.name
bpy.ops.object.select_all(action="DESELECT")
for x in C.objects:x.select_set(True)
print("Helmet fitted to",h.name,"height",H)
