import FreeCAD, Import, Part, json, zipfile, math
V=FreeCAD.Vector; M=FreeCAD.Matrix
W="C:/Users/calvi/Favorites/Downloads/DESPRO_2/3d-Despro2/"
G="C:/Users/calvi/Favorites/Downloads/DESPRO_2/pandu-capstone/hardware/jlcpcba/2026-11-23/"
T=V(9.49,-40.04,9.0)
out=[]
def P(*a):
    s=" ".join(str(x) for x in a); print(s); out.append(s)
# model NEO-6M berisi shell (bukan solid): ambil semua objek Part::Feature
d=FreeCAD.newDocument("gps"); Import.insert(W+"modul/gps-neo6m.step",d.Name)
objs=[]
for o in d.Objects:
    if o.TypeId=="Part::Feature" and not o.Shape.isNull():
        s=o.Shape.copy(); s.Placement=o.getGlobalPlacement()
        if s.BoundBox.isValid(): objs.append((o.Label,s))
FreeCAD.closeDocument(d.Name)
pinobj=[s for l,s in objs if s.BoundBox.ZMax>5.0]
body=[s for l,s in objs if s.BoundBox.ZMax<=5.0]
bb=FreeCAD.BoundBox()
for l,s in objs: bb.add(s.BoundBox)
P("model NEO-6M: %d objek; papan+komponen x[%.2f,%.2f] y[%.2f,%.2f]; z[%.2f,%.2f]; objek pin tinggi: %d"%(len(objs),bb.XMin,bb.XMax,bb.YMin,bb.YMax,bb.ZMin,bb.ZMax,len(pinobj)))
pb=FreeCAD.BoundBox()
for s in pinobj: pb.add(s.BoundBox)
bd=FreeCAD.BoundBox()
for s in body: bd.add(s.BoundBox)
P("  pin: x[%.2f,%.2f] y[%.2f,%.2f] z[%.2f,%.2f]; badan: z[%.2f,%.2f]"%(pb.XMin,pb.XMax,pb.YMin,pb.YMax,pb.ZMin,pb.ZMax,bd.ZMin,bd.ZMax))
# pad U9
pins=json.loads(zipfile.ZipFile(G+"Gerber_PCB1_modul_2026-11-23.zip").read("FlyingProbeTesting.json"))
pads=sorted(set((round(r[2]*0.0254+T.x,3),round(r[3]*0.0254+T.y,3)) for r in pins["pins"]["rows"] if r[1].startswith("U9_")))
px=pads[0][0]; py0=pads[0][1]; py1=pads[-1][1]
P("pad U9: %s"%pads)
# badan di +x dari baris pad (silkscreen gerber: persegi x 69.1..104.1, y 79.6..104.6); pin sepanjang x model, tepi pin y model ~ tengah pin
pcx=(pb.XMin+pb.XMax)/2; pcy=(pb.YMin+pb.YMax)/2
c2=(py0+py1)/2-pcx          # casing_y = model_x + c2
c1=px+pcy                   # casing_x = -model_y + c1
dz=10.6-bd.ZMin if False else 10.6-(-1.08)
m=M(0,-1,0,c1, 1,0,0,c2, 0,0,1,dz, 0,0,0,1)
def tf(s):
    x=s.copy(); x.transformShape(m); return x
gps=[tf(s) for l,s in objs]
comp=Part.makeCompound(gps); b=comp.BoundBox
P("GPS terpasang: x[%.1f,%.1f] y[%.1f,%.1f] z[%.1f,%.1f]"%(b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax))
P("ujung pin z=%.2f (host: atas 10.6, bawah 9.0) -> menonjol %.2f mm di bawah PCB"%(b.ZMin,9.0-b.ZMin))
# cek pin vs pad: pusat tiap objek pin
for s in pinobj:
    t=tf(s); tb=t.BoundBox
    cx,cy=(tb.XMin+tb.XMax)/2,(tb.YMin+tb.YMax)/2
    P("  objek pin pusat (%.2f,%.2f) lebar y %.2f -> pad terdekat jarak %.2f mm"%(cx,cy,tb.YLength,min(math.hypot(cx-p[0],cy-p[1]) for p in pads)))
# amplop padat untuk cek tabrakan (shell tidak bisa di-Boolean)
bt=tf(Part.makeBox(bd.XLength,bd.YLength,bd.ZLength,V(bd.XMin,bd.YMin,bd.ZMin)))
pt=tf(Part.makeBox(pb.XLength,pb.YLength,pb.ZLength,V(pb.XMin,pb.YMin,pb.ZMin)))
env=bt.fuse(pt)
P("amplop padat: badan z[%.2f,%.2f] (tertinggi di papan %.1f mm di atas papan), pin sampai z=%.2f"%(bt.BoundBox.ZMin,bt.BoundBox.ZMax,bt.BoundBox.ZMax-10.6,pt.BoundBox.ZMax))
asm=FreeCAD.openDocument(W+"perakitan/assembly_PCB1_v6_devkit-asli.FCStd")
base=asm.getObject("Base_v4").Shape
P("--- tabrakan GPS asli (mm3 > 0.5) ---"); n=0
for o in asm.Objects:
    if o.Name in ("Base_v4","Tutup_v2_tertutup","Baut_PCB_Ref","U9_MODUL") or o.Name.startswith("EasyEDA") or not hasattr(o,"Shape") or not o.Shape.Solids: continue
    v=env.common(o.Shape).Volume
    if v>0.5: P("  GPS x %s: %.1f mm3"%(o.Label,v)); n+=1
v=env.common(base).Volume
if v>0.5: P("  GPS x Base: %.1f mm3"%v); n+=1
if not n: P("  tidak ada")
P("  jarak ke tepi terdekat modul lain (arah x): U2 xmax=%.1f, GPS xmin=%.1f"%(asm.getObject("U2_MODUL").Shape.BoundBox.XMax,env.BoundBox.XMin))
P("  puncak GPS z=%.1f; bawah pelat tutup z=34.0; sisa %.1f mm"%(env.BoundBox.ZMax,34.0-env.BoundBox.ZMax))
nd=FreeCAD.newDocument("assy_pcb1_v7")
for o in asm.Objects:
    if o.Name=="U9_MODUL": continue
    if hasattr(o,"Shape") and o.Shape.Solids:
        f=nd.addObject("Part::Feature",o.Name); f.Shape=o.Shape.copy()
    elif o.TypeId=="Mesh::Feature":
        f=nd.addObject("Mesh::Feature",o.Name); f.Mesh=o.Mesh
f=nd.addObject("Part::Feature","U9_GPS_asli"); f.Shape=comp
nd.recompute(); nd.saveAs(W+"perakitan/assembly_PCB1_v7_gps-asli.FCStd")
open(W+"laporan/_tahap5_gps_report.txt","w").write("\n".join(out))
