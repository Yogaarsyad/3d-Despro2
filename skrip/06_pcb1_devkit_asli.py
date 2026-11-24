import FreeCAD, Import, Part, json, zipfile, math
V=FreeCAD.Vector
W="C:/Users/calvi/Favorites/Downloads/DESPRO_2/3d-Despro2/"
G="C:/Users/calvi/Favorites/Downloads/DESPRO_2/pandu-capstone/hardware/jlcpcba/2026-11-23/"
T=V(9.49,-40.04,9.0)           # gerber -> kerangka casing PCB1
STANDOFF=2.9                    # papan DevKit di atas atas-PCB (mm); pin 10.5 mm di bawah papan modul
out=[]
def P(*a):
    s=" ".join(str(x) for x in a); print(s); out.append(s)
d=FreeCAD.newDocument("dk"); Import.insert(W+"modul/esp32-devkit-v1.step",d.Name); seen=set(); sh=[]
for o in d.Objects:
    if o.TypeId=="Part::Feature" and o.Shape.Solids:
        s=o.Shape.copy(); s.Placement=o.getGlobalPlacement(); b=s.BoundBox
        k=(round(s.Volume,2),round(b.XMin,2),round(b.YMin,2),round(b.ZMin,2))
        if k in seen: continue
        seen.add(k); sh.append(s)
FreeCAD.closeDocument(d.Name)
pins=json.loads(zipfile.ZipFile(G+"Gerber_PCB1_modul_2026-11-23.zip").read("FlyingProbeTesting.json"))
pads=sorted(set((round(r[2]*0.0254+T.x,3),round(r[3]*0.0254+T.y,3)) for r in pins["pins"]["rows"] if r[1].startswith("U3_")))
P("pad U3: %d titik, x %s, y %.2f..%.2f"%(len(pads),sorted(set(p[0] for p in pads)),min(p[1] for p in pads),max(p[1] for p in pads)))
# model: baris pin x=+-12.7, y 9.75..45.31, USB di y=0 (daya VIN dan 3V3 di ujung USB = pad y terkecil), tanpa putaran
ox=(min(p[0] for p in pads)+max(p[0] for p in pads))/2
oy=min(p[1] for p in pads)-9.75
zc=10.6+STANDOFF
mv=V(ox,oy,zc)
dk=[]
for s in sh:
    x=s.copy(); x.translate(mv); dk.append(x)
# cek pin vs pad
pn=[s for s in dk if s.BoundBox.ZMin<zc-9 and s.BoundBox.XLength<4 and s.BoundBox.YLength<4]
err=[]
for s in pn:
    cx,cy=(s.BoundBox.XMin+s.BoundBox.XMax)/2,(s.BoundBox.YMin+s.BoundBox.YMax)/2
    err.append(min(math.hypot(cx-px,cy-py) for px,py in pads))
P("cek pin: %d pin model, jarak ke pad terdekat max %.2f mm, rata %.2f mm (TERBUKTI cocok bila ~0)"%(len(err),max(err),sum(err)/len(err)))
comp=Part.makeCompound(dk); b=comp.BoundBox
P("DevKit: x[%.1f,%.1f] y[%.1f,%.1f] z[%.1f,%.1f]; ujung USB di y=%.1f (menghadap -y, dinding depan y=0 berjarak %.0f mm)"%(b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax,b.YMin,b.YMin))
P("ujung pin z=%.2f; lantai Base z=2.5 -> celah %.2f mm; pin menembus PCB (z 9.0-10.6) dan menonjol %.2f mm di bawahnya"%(b.ZMin,b.ZMin-2.5,9.0-b.ZMin))
asm=FreeCAD.openDocument(W+"perakitan/assembly_PCB1_v5_usb-extend.FCStd")
base=asm.getObject("Base_v4").Shape; lid=asm.getObject("Tutup_v2_tertutup").Shape
P("--- tabrakan DevKit asli (mm3 > 0.5) ---")
n=0
for o in asm.Objects:
    if o.Name in ("Base_v4","Tutup_v2_tertutup","Baut_PCB_Ref","U3_MODUL") or not hasattr(o,"Shape") or not o.Shape.Solids: continue
    if o.Name.startswith("EasyEDA"): continue
    v=comp.common(o.Shape).Volume
    if v>0.5: P("  DevKit x %s: %.1f mm3"%(o.Label,v)); n+=1
for nm,s in (("Base",base),("Tutup",lid)):
    v=comp.common(s).Volume
    if v>0.5: P("  DevKit x %s: %.1f mm3"%(nm,v)); n+=1
if not n: P("  tidak ada")
P("  puncak DevKit z=%.1f; bawah pelat tutup z=34.0; sisa %.1f mm"%(b.ZMax,34.0-b.ZMax))
nd=FreeCAD.newDocument("assy_pcb1_v6")
for o in asm.Objects:
    if o.Name=="U3_MODUL": continue
    if hasattr(o,"Shape") and o.Shape.Solids:
        f=nd.addObject("Part::Feature",o.Name); f.Shape=o.Shape.copy()
    elif o.TypeId=="Mesh::Feature":
        f=nd.addObject("Mesh::Feature",o.Name); f.Mesh=o.Mesh
f=nd.addObject("Part::Feature","U3_DEVKIT_asli"); f.Shape=comp
nd.recompute(); nd.saveAs(W+"perakitan/assembly_PCB1_v6_devkit-asli.FCStd")
open(W+"laporan/_tahap5_devkit_report.txt","w").write("\n".join(out))
