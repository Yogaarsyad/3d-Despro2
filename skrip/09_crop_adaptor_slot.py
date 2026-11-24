import FreeCAD, Part, Mesh, os
V=FreeCAD.Vector
W="C:/Users/calvi/Favorites/Downloads/DESPRO_2/3d-Despro2/"
H=W+"mekanik/helm/"
OUT=W+"mekanik/helm/adaptor_slot/"
os.makedirs(OUT,exist_ok=True)
out=[]
def P(*a):
    s=" ".join(str(x) for x in a); print(s); out.append(s)
def faces_from_slice(mesh,z):
    """irisan horizontal mesh pada z -> sisi 2D (aturan genap-ganjil untuk lubang)"""
    secs=mesh.crossSections([(V(0,0,z),V(0,0,1))],0.0005)[0]
    wires=[]
    for pl in secs:
        if len(pl)<3: continue
        pts=[V(p.x,p.y,0) for p in pl]
        if (pts[0]-pts[-1]).Length>1e-3: pts.append(pts[0])
        try: wires.append(Part.Wire(Part.makePolygon(pts)))
        except Exception as e: pass
    fs=[]
    for w in wires:
        try: fs.append(Part.Face(w))
        except Exception: pass
    fs.sort(key=lambda f:-f.Area)
    res=None; depth=[]
    for i,f in enumerate(fs):
        c=f.CenterOfMass if f.isValid() else V(0,0,0)
        n=sum(1 for g in fs[:i] if g.isInside(f.Vertexes[0].Point,1e-3,True))
        depth.append(n)
    res=Part.Shape()
    solid=None
    for f,n in zip(fs,depth):
        if n%2==0: solid=f if solid is None else solid.fuse(f)
    for f,n in zip(fs,depth):
        if n%2==1 and solid is not None: solid=solid.cut(f)
    P("  irisan z=%.2f: %d lingkaran, luas %.1f mm2"%(z,len(fs),solid.Area if solid else 0))
    return solid
def crop(name,stl,zmid,thick,zbase,box):
    m=Mesh.Mesh(stl)
    bb=m.BoundBox
    P("%s: %d segitiga, bbox x[%.1f,%.1f] y[%.1f,%.1f] z[%.2f,%.2f]"%(name,m.CountFacets,bb.XMin,bb.XMax,bb.YMin,bb.YMax,bb.ZMin,bb.ZMax))
    f=faces_from_slice(m,zmid)
    solid=f.extrude(V(0,0,thick)); solid.translate(V(0,0,zbase))
    keep=Part.makeBox(box[1]-box[0],box[3]-box[2],box[5]-box[4],V(box[0],box[2],box[4]))
    s=solid.common(keep)
    s=s.removeSplitter()
    b=s.BoundBox
    P("  hasil %s: %.1f x %.1f x %.1f mm, volume %.0f mm3, solid valid=%s, jumlah solid %d"%(name,b.XLength,b.YLength,b.ZLength,s.Volume,s.isValid(),len(s.Solids)))
    # pindahkan ke asal: x tengah=0, y terkecil=0, z terkecil=0
    s.translate(V(-(b.XMin+b.XMax)/2,-b.YMin,-b.ZMin))
    s.exportStep(OUT+name+".step"); s.exportStl(OUT+name+".stl")
    return s
# klip IBEW: lidah y -39.4..-8 (tebal z -5.61..-2.11), kepala bertulisan dibuang
t=crop("lidah_slot_ibew",H+"ibew-105-hard-hat-clip/105hardhatclip.stl",-3.86,3.5,-5.61,(-30,30,-39.5,-8.0,-6,0))
# sayap: pelat dasar y<38 (z 0..3.0), sayap hiasan dibuang
w=crop("pelat_slot_sayap",H+"wings-for-the-hardhat/helmetwing_left.stl",1.5,3.0,0.0,(100,300,20.0,38.0,-1,4))
doc=FreeCAD.newDocument("adaptor_slot")
for n,s in (("lidah_slot_ibew",t),("pelat_slot_sayap",w)):
    f=doc.addObject("Part::Feature",n); f.Shape=s
doc.recompute(); doc.saveAs(OUT+"adaptor_slot.FCStd")
open(W+"laporan/_tahap5_crop_slot_report.txt","w").write("\n".join(out))
