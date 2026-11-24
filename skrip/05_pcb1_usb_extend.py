import FreeCAD, Part
V=FreeCAD.Vector
W="C:/Users/calvi/Favorites/Downloads/DESPRO_2/3d-Despro2/"
HX,HZ,HD=46.5,7.0,9.0     # tengah lubang di dinding y=0: x, z, diameter (ubah sesuai ukuran rubber plug)
out=[]
def P(*a):
    s=" ".join(str(x) for x in a); print(s); out.append(s)
src=FreeCAD.openDocument(W+"casing/3d-pcb1_v3_chest-mount.FCStd")
base=src.getObject("Base_v3").Shape.copy()
# lubang bulat tembus dinding depan (y 0..2.5), sumbu searah y
hole=Part.makeCylinder(HD/2,6.0,V(HX,-1.0,HZ),V(0,1,0))
b4=base.cut(hole)
P("lubang kabel USB: d%.1f di dinding y=0, tengah x=%.1f z=%.1f (dasar z=%.1f, lantai z=2.5)"%(HD,HX,HZ,HZ-HD/2))
P("Base v4 vol %.0f (v3 %.0f), dibuang %.0f mm3 (perkiraan silinder x tebal dinding 2.5 = %.0f)"%(b4.Volume,base.Volume,base.Volume-b4.Volume,3.14159*(HD/2)**2*2.5))
asm=FreeCAD.openDocument(W+"perakitan/assembly_PCB1_v4_chest-mount.FCStd")
parts=[o for o in asm.Objects if hasattr(o,"Shape") and o.Shape.Solids and o.Name not in ("Base_v3","Tutup_v2_tertutup","Baut_PCB_Ref")]
u7=[o for o in parts if o.Name=="U7_MODUL"][0].Shape; bb=u7.BoundBox
P("U7 TP4056 (bawah papan): x[%.1f,%.1f] y[%.1f,%.1f] z[%.1f,%.1f]; ujung USB di x=%.1f"%(bb.XMin,bb.XMax,bb.YMin,bb.YMax,bb.ZMin,bb.ZMax,bb.XMax))
# jalur kabel: kabel d4.0, dua ruas. Ruas A lurus ke -y dari muka USB, ruas B menuju lubang (naik ke z=7 di dinding)
cy=(bb.YMin+bb.YMax)/2
def seg(p0,p1,r=2.0):
    return Part.makeCylinder(r,(p1-p0).Length,p0,(p1-p0).normalize())
pA0=V(44.7,cy,5.0); pA1=V(HX-0.5,34.0,5.0); pB1=V(HX,3.0,HZ)
tube=seg(pA0,pA1).fuse(seg(pA1,pB1))
P("jalur kabel d4.0: (%.1f,%.1f,%.1f) -> (%.1f,%.1f,%.1f) -> (%.1f,%.1f,%.1f)"%(pA0.x,pA0.y,pA0.z,pA1.x,pA1.y,pA1.z,pB1.x,pB1.y,pB1.z))
n=0
for o in parts:
    v=tube.common(o.Shape).Volume
    if v>0.1: P("  jalur kabel nabrak %s: %.1f mm3"%(o.Label,v)); n+=1
vb=tube.common(b4).Volume
if vb>0.1: P("  jalur kabel nabrak Base: %.1f mm3"%vb); n+=1
if not n: P("  jalur kabel bebas tabrakan dengan semua bagian dan Base")
P("  jarak dasar lubang ke papan: PCB bawah z=9.0, atas lubang z=%.1f"%(HZ+HD/2))
doc=FreeCAD.newDocument("casing_pcb1_v4")
for o in src.Objects:
    if o.Name=="Base_v3": continue
    if hasattr(o,"Shape") and o.Shape.Solids:
        f=doc.addObject("Part::Feature",o.Name); f.Shape=o.Shape.copy()
f=doc.addObject("Part::Feature","Base_v4"); f.Shape=b4
doc.recompute(); doc.saveAs(W+"casing/3d-pcb1_v4_usb-extend.FCStd")
b4.exportStep(W+"casing/PCB1_v4_Base.step"); b4.exportStl(W+"casing/PCB1_v4_Base.stl")
nd=FreeCAD.newDocument("assy_pcb1_v5")
for o in asm.Objects:
    if o.Name=="Base_v3": f=nd.addObject("Part::Feature","Base_v4"); f.Shape=b4
    elif hasattr(o,"Shape") and o.Shape.Solids: f=nd.addObject("Part::Feature",o.Name); f.Shape=o.Shape.copy()
    elif o.TypeId=="Mesh::Feature": f=nd.addObject("Mesh::Feature",o.Name); f.Mesh=o.Mesh
nd.recompute(); nd.saveAs(W+"perakitan/assembly_PCB1_v5_usb-extend.FCStd")
open(W+"laporan/_tahap5_usb_pcb1_report.txt","w").write("\n".join(out))
