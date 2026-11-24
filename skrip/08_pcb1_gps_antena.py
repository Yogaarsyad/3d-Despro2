import FreeCAD, Import, Part, json, zipfile, math
V=FreeCAD.Vector; M=FreeCAD.Matrix
W="C:/Users/calvi/Favorites/Downloads/DESPRO_2/3d-Despro2/"
G="C:/Users/calvi/Favorites/Downloads/DESPRO_2/pandu-capstone/hardware/jlcpcba/2026-11-23/"
T=V(9.49,-40.04,9.0)
out=[]
def P(*a):
    s=" ".join(str(x) for x in a); print(s); out.append(s)
d=FreeCAD.newDocument("gps"); Import.insert(W+"modul/gps-gy-neo6mv2-ant.step",d.Name)
sh=[]
for o in d.Objects:
    if o.TypeId=="Part::Feature" and not o.Shape.isNull():
        s=o.Shape.copy(); s.Placement=o.getGlobalPlacement()
        if s.BoundBox.isValid(): sh.append(s)
FreeCAD.closeDocument(d.Name)
bb=FreeCAD.BoundBox()
for s in sh: bb.add(s.BoundBox)
P("model GY-NEO6MV2+antena: %d solid; x[%.2f,%.2f] y[%.2f,%.2f] z[%.2f,%.2f]"%(len(sh),bb.XMin,bb.XMax,bb.YMin,bb.YMax,bb.ZMin,bb.ZMax))
# papan di bidang x-z, tebal sepanjang y; antena di sisi -y (atas); dasar papan y=ymax
pcb=max(sh,key=lambda s:s.BoundBox.XLength*s.BoundBox.ZLength)
pb=pcb.BoundBox
P("papan (objek terluas): %.1f x %.1f, tebal+komponen %.1f; antena sisi -y sampai y=%.2f, tinggi total di atas dasar %.2f mm"%(pb.XLength,pb.ZLength,pb.YLength,bb.YMin,bb.YMax-bb.YMin))
# pemetaan casing: X=x, Y=z, Z=-y  (rotasi benar, det +1); header diasumsikan di ujung x minimum
pads=sorted(set((round(r[2]*0.0254+T.x,3),round(r[3]*0.0254+T.y,3)) for r in json.loads(zipfile.ZipFile(G+"Gerber_PCB1_modul_2026-11-23.zip").read("FlyingProbeTesting.json"))["pins"]["rows"] if r[1].startswith("U9_")))
cy=(pads[0][1]+pads[-1][1])/2
EDGE=1.56                                    # jarak pin ke tepi papan (dari model NEO-6M)
x0=pads[0][0]-EDGE-pb.XMin                   # casing_x = x + x0
y0=cy-(pb.ZMin+pb.ZMax)/2                    # casing_y = z + y0
z0=10.6+bb.YMax                              # casing_z = -y + z0 (dasar papan di atas PCB host)
m=M(1,0,0,x0, 0,0,1,y0, 0,-1,0,z0, 0,0,0,1)
gps=[]
for s in sh:
    x=s.copy(); x.transformShape(m); gps.append(x)
comp=Part.makeCompound(gps); b=comp.BoundBox
P("GPS terpasang: x[%.1f,%.1f] y[%.1f,%.1f] z[%.1f,%.1f]; silkscreen gerber: x 78.6..113.6, y 39.6..64.6"%(b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax))
asm=FreeCAD.openDocument(W+"perakitan/assembly_PCB1_v6_devkit-asli.FCStd")
base=asm.getObject("Base_v4").Shape
P("--- tabrakan GPS + antena (mm3 > 0.5) ---"); n=0
for o in asm.Objects:
    if o.Name in ("Base_v4","Tutup_v2_tertutup","Baut_PCB_Ref","U9_MODUL") or o.Name.startswith("EasyEDA") or not hasattr(o,"Shape") or not o.Shape.Solids: continue
    v=comp.common(o.Shape).Volume
    if v>0.5: P("  GPS x %s: %.1f mm3"%(o.Label,v)); n+=1
v=comp.common(base).Volume
if v>0.5: P("  GPS x Base: %.1f mm3"%v); n+=1
if not n: P("  tidak ada")
P("  puncak GPS z=%.1f; bawah pelat tutup z=34.0; sisa %.1f mm"%(b.ZMax,34.0-b.ZMax))
P("  tepi GPS terdekat: U2 xmax=%.1f, GPS xmin=%.1f; DevKit xmax=%.1f"%(asm.getObject("U2_MODUL").Shape.BoundBox.XMax,b.XMin,asm.getObject("U3_DEVKIT_asli").Shape.BoundBox.XMax))
nd=FreeCAD.newDocument("assy_pcb1_v8")
for o in asm.Objects:
    if o.Name=="U9_MODUL": continue
    if hasattr(o,"Shape") and o.Shape.Solids:
        f=nd.addObject("Part::Feature",o.Name); f.Shape=o.Shape.copy()
    elif o.TypeId=="Mesh::Feature":
        f=nd.addObject("Mesh::Feature",o.Name); f.Mesh=o.Mesh
f=nd.addObject("Part::Feature","U9_GPS_antena"); f.Shape=comp
nd.recompute(); nd.saveAs(W+"perakitan/assembly_PCB1_v8_gps-antena.FCStd")
open(W+"laporan/_tahap5_gps_antena_report.txt","w").write("\n".join(out))
