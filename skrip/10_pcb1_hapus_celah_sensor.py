import FreeCAD, Part
V=FreeCAD.Vector
W="C:/Users/calvi/Favorites/Downloads/DESPRO_2/3d-Despro2/"
UX,SW=82.65,7.3          # UX = tengah U10 (82.65), SW melebihi celah asli (7.0) supaya tambalan menumpuk ke bahan utuh          # tengah dan lebar celah kabel sensor air yang dihapus
H=34.0
out=[]
def P(*a):
    s=" ".join(str(x) for x in a); print(s); out.append(s)
src=FreeCAD.openDocument(W+"casing/3d-pcb1_v4_usb-extend.FCStd")
base=src.getObject("Base_v4").Shape.copy(); lid=src.getObject("Tutup_v2_tertutup").Shape.copy()
def wall_open(shape,y,z):
    """True bila titik (UX,y,z) berada di luar bahan (celah)"""
    return not shape.isInside(V(UX,y,z),1e-4,True)
P("sebelum: titik dinding (x=%.1f,y=1.2,z=28) terbuka? %s ; bibir tutup (y=3.5,z=33) terbuka? %s"%(UX,wall_open(base,1.2,28),wall_open(lid,3.5,33)))
# isi kembali dinding: x UX+-3.5, y 0..2.5, z 22..34 ; bibir tutup: y 2.8..4.3, z 32..34
b5=base.fuse(Part.makeBox(SW,2.5,H-22.0,V(UX-SW/2,0.0,22.0))).removeSplitter()
t5=lid.fuse(Part.makeBox(SW,1.5,2.0,V(UX-SW/2,2.8,H-2.0)))                       # bibir tutup
t5=t5.fuse(Part.makeBox(SW,3.0,0.2,V(UX-SW/2,2.0,H))).removeSplitter()      # alur 0.1 mm di bawah pelat (potongan lama menembus 0.1 mm)
P("sesudah: dinding terbuka? %s ; bibir tutup terbuka? %s"%(wall_open(b5,1.2,28),wall_open(t5,3.5,33)))
def scan(shape,y,z,x0=UX-4.5,x1=UX+4.5):
    bad=[round(x0+i*0.02,2) for i in range(int((x1-x0)/0.02)) if not shape.isInside(V(x0+i*0.02,y,z),1e-6,True)]
    return bad
P("pindai x %.1f..%.1f tiap 0.02 mm: dinding y=1.2 z=23/28/33.9 titik kosong = %d/%d/%d ; bibir tutup y=3.5 z=32.5/33.5 = %d/%d ; bawah pelat y=3.5 z=34.05 = %d"%(UX-4.5,UX+4.5,len(scan(b5,1.2,23)),len(scan(b5,1.2,28)),len(scan(b5,1.2,33.9)),len(scan(t5,3.5,32.5)),len(scan(t5,3.5,33.5)),len(scan(t5,3.5,34.05))))
P("volume Base %.0f -> %.0f (+%.0f, harapan >= %.0f); Tutup %.0f -> %.0f (+%.0f, harapan %.0f)"%(base.Volume,b5.Volume,b5.Volume-base.Volume,SW*2.5*(H-22.0),lid.Volume,t5.Volume,t5.Volume-lid.Volume,SW*1.5*2.0))
P("lubang USB d9 tetap ada: titik (46.5,1.2,7.0) di luar bahan = %s"%(not b5.isInside(V(46.5,1.2,7.0),1e-4,True)))
P("Base v5 vs Tutup tabrakan: %.2f mm3"%b5.common(t5).Volume)
tp=t5.copy(); bb=tp.BoundBox
tp.rotate(V(0,(bb.YMin+bb.YMax)/2,(bb.ZMin+bb.ZMax)/2),V(1,0,0),180); tp.translate(V(0,0,-tp.BoundBox.ZMin))
doc=FreeCAD.newDocument("casing_pcb1_v5")
for o in src.Objects:
    if o.Name in ("Base_v4","Tutup_v2_tertutup","Tutup_v2_cetak"): continue
    if hasattr(o,"Shape") and o.Shape.Solids:
        f=doc.addObject("Part::Feature",o.Name); f.Shape=o.Shape.copy()
for n,s in (("Base_v5",b5),("Tutup_v5_tertutup",t5),("Tutup_v5_cetak",tp)):
    f=doc.addObject("Part::Feature",n); f.Shape=s
doc.recompute(); doc.saveAs(W+"casing/3d-pcb1_v5_sensor-di-tutup.FCStd")
b5.exportStep(W+"casing/PCB1_v5_Base.step"); b5.exportStl(W+"casing/PCB1_v5_Base.stl")
tp.exportStep(W+"casing/PCB1_v5_Tutup_cetak.step"); tp.exportStl(W+"casing/PCB1_v5_Tutup_cetak.stl")
asm=FreeCAD.openDocument(W+"perakitan/assembly_PCB1_v8_gps-antena.FCStd")
nd=FreeCAD.newDocument("assy_pcb1_v9")
for o in asm.Objects:
    if o.Name=="Base_v4": f=nd.addObject("Part::Feature","Base_v5"); f.Shape=b5
    elif o.Name=="Tutup_v2_tertutup": f=nd.addObject("Part::Feature","Tutup_v5_tertutup"); f.Shape=t5
    elif hasattr(o,"Shape") and o.Shape.Solids: f=nd.addObject("Part::Feature",o.Name); f.Shape=o.Shape.copy()
    elif o.TypeId=="Mesh::Feature": f=nd.addObject("Mesh::Feature",o.Name); f.Mesh=o.Mesh
nd.recompute(); nd.saveAs(W+"perakitan/assembly_PCB1_v9_sensor-di-tutup.FCStd")
open(W+"laporan/_tahap5_sensor_air_report.txt","w").write("\n".join(out))
