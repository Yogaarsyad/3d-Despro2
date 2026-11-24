import FreeCAD, Part
V=FreeCAD.Vector
W="C:/Users/calvi/Favorites/Downloads/DESPRO_2/3d-Despro2/"
out=[]
def P(*a):
    s=" ".join(str(x) for x in a); print(s); out.append(s)
def fill(base,axis,c,r,t0,t1,name):
    """isi lubang bulat d9 di dinding. axis 'y' atau 'x'; c=(a,z); t0..t1 = rentang dinding sepanjang sumbu"""
    a,z=c
    if axis=="y": cy=Part.makeCylinder(r,t1-t0,V(a,t0,z),V(0,1,0)); probe=lambda t:V(a,t,z)
    else:        cy=Part.makeCylinder(r,t1-t0,V(t0,a,z),V(1,0,0)); probe=lambda t:V(t,a,z)
    before=[round(t0+0.25+i*0.5,2) for i in range(int((t1-t0)/0.5)) if not base.isInside(probe(t0+0.25+i*0.5),1e-6,True)]
    nb=base.fuse(cy)
    # pindai seluruh penampang lubang: setiap 0.5 mm di dalam d9, sepanjang dinding
    bad=0; n=0
    for i in range(int((t1-t0)/0.5)):
        t=t0+0.25+i*0.5
        for dx in (-4.0,-2.0,0.0,2.0,4.0):
            for dz in (-4.0,-2.0,0.0,2.0,4.0):
                if dx*dx+dz*dz>16.0: continue
                p=V(a+dx,t,z+dz) if axis=="y" else V(t,a+dx,z+dz)
                n+=1
                if not nb.isInside(p,1e-6,True): bad+=1
    P("%s: sebelum, titik di sumbu lubang yang kosong = %d dari %d; sesudah, titik kosong di seluruh penampang d9 = %d dari %d; valid=%s; vol %.0f -> %.0f (%+.0f, harapan +%.0f)"%(name,len(before),int((t1-t0)/0.5),bad,n,nb.isValid(),base.Volume,nb.Volume,nb.Volume-base.Volume,3.14159*r*r*(t1-t0)))
    return nb
# ---- PCB1: lubang d9 di dinding depan, tengah x=46.5 z=7.0, dinding y -3.5..2.5
s1=FreeCAD.openDocument(W+"casing/3d-pcb1_v6_waterproof.FCStd")
b1=fill(s1.getObject("Base_v6").Shape,"y",(46.5,7.0),4.55,-3.5,2.5,"PCB1")
lid1=s1.getObject("Tutup_v6_tertutup").Shape; lid1p=s1.getObject("Tutup_v6_cetak").Shape
pins=[o.Shape for o in s1.Objects if o.Name.startswith("Pin_tombol")]
doc=FreeCAD.newDocument("pcb1_tanpa_usb")
for n,sh in (("Base_v7",b1),("Tutup_v6_tertutup",lid1),("Tutup_v6_cetak",lid1p)): f=doc.addObject("Part::Feature",n); f.Shape=sh
for i,p in enumerate(pins): f=doc.addObject("Part::Feature","Pin_tombol_%d"%(i+1)); f.Shape=p
doc.recompute(); doc.saveAs(W+"casing/3d-pcb1_v7_tanpa-usb.FCStd")
b1.exportStep(W+"casing/PCB1_v7_Base.step"); b1.exportStl(W+"casing/PCB1_v7_Base.stl")
a1=FreeCAD.openDocument(W+"perakitan/assembly_PCB1_v10_waterproof.FCStd")
nd=FreeCAD.newDocument("assy_pcb1_v11")
f=nd.addObject("Part::Feature","Base_v7"); f.Shape=b1
for o in a1.Objects:
    if o.Name=="Base_v6": continue
    if hasattr(o,"Shape") and o.Shape.Solids: f=nd.addObject("Part::Feature",o.Name); f.Shape=o.Shape.copy()
    elif o.TypeId=="Mesh::Feature": f=nd.addObject("Mesh::Feature",o.Name); f.Mesh=o.Mesh
nd.recompute(); nd.saveAs(W+"perakitan/assembly_PCB1_v11_tanpa-usb.FCStd")
# ---- PCB2: lubang d9 di dinding kiri, tengah y=27.4 z=25.0, dinding x -3.5..2.5
s2=FreeCAD.openDocument(W+"casing/3D-pcb2_v5_waterproof.FCStd")
b2=fill(s2.getObject("Base_v5").Shape,"x",(27.4,25.0),4.55,-3.5,2.5,"PCB2")
lid2=s2.getObject("Tutup_v5_tertutup").Shape; lid2p=s2.getObject("Tutup_v5_cetak").Shape
doc=FreeCAD.newDocument("pcb2_tanpa_usb")
for n,sh in (("Base_v6",b2),("Tutup_v5_tertutup",lid2),("Tutup_v5_cetak",lid2p)): f=doc.addObject("Part::Feature",n); f.Shape=sh
doc.recompute(); doc.saveAs(W+"casing/3D-pcb2_v6_tanpa-usb.FCStd")
b2.exportStep(W+"casing/PCB2_v6_Base.step"); b2.exportStl(W+"casing/PCB2_v6_Base.stl")
a2=FreeCAD.openDocument(W+"perakitan/assembly_PCB2_v5_waterproof.FCStd")
nd=FreeCAD.newDocument("assy_pcb2_v6")
f=nd.addObject("Part::Feature","Base_v6"); f.Shape=b2
for o in a2.Objects:
    if o.Name=="Base_v5": continue
    if hasattr(o,"Shape") and o.Shape.Solids: f=nd.addObject("Part::Feature",o.Name); f.Shape=o.Shape.copy()
nd.recompute(); nd.saveAs(W+"perakitan/assembly_PCB2_v6_tanpa-usb.FCStd")
# alur O-ring tetap menerus?
for nm,b,Wd,Dp,H,lid in (("PCB1",b1,126.9,114.2,34.0,lid1),("PCB2",b2,54.6,122.0,33.9,lid2)):
    g0=-3.5+1.7; cx0=g0+1.3; pts=[]
    for i in range(int((Wd-2*cx0)/1.0)+1): pts+=[(cx0+i,cx0),(cx0+i,Dp-cx0)]
    for j in range(int((Dp-2*cx0)/1.0)+1): pts+=[(cx0,cx0+j),(Wd-cx0,cx0+j)]
    e1=sum(1 for x,y in pts if b.isInside(V(x,y,H-0.75),1e-6,True)); e2=sum(1 for x,y in pts if not b.isInside(V(x,y,H-2.0),1e-6,True))
    P("%s alur O-ring (%d titik): bahan di alur=%d, dasar tidak utuh=%d (harus 0); tabrakan Base x Tutup %.2f mm3; Base valid=%s"%(nm,len(pts),e1,e2,b.common(lid).Volume,b.isValid()))
open(W+"laporan/_tahap6_tanpa_usb_report.txt","w").write("\n".join(out))
