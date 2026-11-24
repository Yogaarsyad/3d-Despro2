import FreeCAD, Part, math
V=FreeCAD.Vector
W_="C:/Users/calvi/Favorites/Downloads/DESPRO_2/3d-Despro2/"
EXT=3.5                       # penebalan dinding ke luar
CORD,GW,GD=2.0,2.6,1.5        # kabel O-ring d2.0; alur lebar 2.6, dalam 1.5
LIP=1.7                       # tepi alur ke tepi luar
SCR_D,CB_D,CB_H=3.4,7.2,1.4   # lubang sekrup tutup, counterbore untuk ring karet, dalam counterbore
PLATE=3.0; PIL_D=2.5; PIL_DEPTH=16.0
out=[]
def P(*a):
    s=" ".join(str(x) for x in a); print(s); out.append(s)
def box(x0,y0,z0,x1,y1,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def cyl(x,y,z0,z1,d): return Part.makeCylinder(d/2,z1-z0,V(x,y,z0))
def build(name,Base,Lid,Wd,Dp,H,corners,extras,usb,recess,extra_fn=None):
    P("=====",name,"W=%.1f D=%.1f H=%.1f"%(Wd,Dp,H))
    # 1. dinding ke luar
    ring=box(-EXT,-EXT,0,Wd+EXT,Dp+EXT,H).cut(box(0,0,-1,Wd,Dp,H+1))
    b=Base.fuse(ring)
    # 2. alur O-ring di muka atas dinding
    g0=-EXT+LIP
    g_out=box(g0,g0,H-GD,Wd-g0,Dp-g0,H+0.2); g_in=box(g0+GW,g0+GW,H-GD-1,Wd-g0-GW,Dp-g0-GW,H+1)
    b=b.cut(g_out.cut(g_in))
    cl=(Wd-2*g0-GW+0)+(Dp-2*g0-GW+0)   # panjang sisi tengah alur
    per=2*((Wd-2*g0-GW)+(Dp-2*g0-GW)) if False else 2*(((Wd-2*(g0+GW/2))+(Dp-2*(g0+GW/2))))
    P("alur O-ring: lebar %.1f dalam %.1f, tengah alur %.1f mm dari tepi luar; panjang kabel O-ring sekitar %.0f mm (d%.1f silikon, lem ujungnya)"%(GW,GD,LIP+GW/2,per,CORD))
    # 3. boss sekrup tambahan (menempel ke dinding)
    for (x,y) in extras:
        b=b.fuse(cyl(x,y,1.5,H,6.0))
    for (x,y) in extras:
        b=b.cut(cyl(x,y,H-PIL_DEPTH,H+0.1,PIL_D))
    b=usb(b)
    b=b
    # 4. tutup: pelat melebar ke luar
    pl=box(-EXT,-EXT,H,Wd+EXT,Dp+EXT,H+PLATE).cut(box(0,0,H-1,Wd,Dp,H+PLATE+1))
    l=Lid.fuse(pl)
    for (x,y) in extras: l=l.cut(cyl(x,y,H-2.1,H+0.0,7.2))      # bibir tutup dilubangi di sekitar boss
    for (x,y) in corners+extras:
        l=l.cut(cyl(x,y,H-0.2,H+PLATE+0.2,SCR_D)); l=l.cut(cyl(x,y,H+PLATE-CB_H,H+PLATE+0.2,CB_D))
    for (x,y) in recess:
        l=l.cut(cyl(x,y,H+PLATE-0.8,H+PLATE+0.2,12.0))
    l=l
    P("Base baru: bbox x[%.1f,%.1f] y[%.1f,%.1f] z[%.1f,%.1f] vol %.0f"%(b.BoundBox.XMin,b.BoundBox.XMax,b.BoundBox.YMin,b.BoundBox.YMax,b.BoundBox.ZMin,b.BoundBox.ZMax,b.Volume))
    P("Tutup baru: bbox x[%.1f,%.1f] y[%.1f,%.1f] z[%.1f,%.1f] vol %.0f"%(l.BoundBox.XMin,l.BoundBox.XMax,l.BoundBox.YMin,l.BoundBox.YMax,l.BoundBox.ZMin,l.BoundBox.ZMax,l.Volume))
    # 5. verifikasi alur: menerus (kosong di dalam alur), dasar alur utuh, tutup menutup alur
    cx0=g0+GW/2; pts=[]
    for i in range(int((Wd-2*cx0)/1.0)+1): pts+= [(cx0+i,cx0),(cx0+i,Dp-cx0)]
    for j in range(int((Dp-2*cx0)/1.0)+1): pts+= [(cx0,cx0+j),(Wd-cx0,cx0+j)]
    e1=sum(1 for x,y in pts if b.isInside(V(x,y,H-GD/2),1e-6,True))
    e2=sum(1 for x,y in pts if not b.isInside(V(x,y,H-GD-0.5),1e-6,True))
    e3=sum(1 for x,y in pts if not l.isInside(V(x,y,H+PLATE/2),1e-6,True))
    P("cek alur (%d titik di tengah alur): bahan di dalam alur = %d, lubang di bawah alur (dasar tidak utuh) = %d, tutup tidak menutup alur = %d (semua harus 0)"%(len(pts),e1,e2,e3))
    P("validitas geometri: Base=%s Tutup=%s (harus True)"%(b.isValid(),l.isValid()))
    P("tabrakan Base x Tutup: %.2f mm3"%b.common(l).Volume)
    return b,l
def flip_print(l):
    t=l.copy(); bb=t.BoundBox
    t.rotate(V(0,(bb.YMin+bb.YMax)/2,(bb.ZMin+bb.ZMax)/2),V(1,0,0),180); t.translate(V(0,0,-t.BoundBox.ZMin)); return t
def check_parts(asm,skip,b,l,extra_solids,label):
    P("--- tabrakan boss/dinding baru dengan isi (%s), mm3 > 0.5 ---"%label); n=0
    for o in asm.Objects:
        if o.Name in skip or not hasattr(o,"Shape") or not o.Shape.Solids: continue
        v=o.Shape.common(b).Volume+o.Shape.common(l).Volume
        if v>0.5: P("  %s: %.1f mm3"%(o.Label,v)); n+=1
    if not n: P("  tidak ada")
# ================= PCB1 =================
src=FreeCAD.openDocument(W_+"casing/3d-pcb1_v5_sensor-di-tutup.FCStd")
Base=src.getObject("Base_v5").Shape; Lid=src.getObject("Tutup_v5_tertutup").Shape
Wd,Dp,H=126.9,114.2,34.0
corners=[(6.0,6.0),(120.9,6.0),(6.0,108.2),(120.9,108.2)]
extras=[(44.3,5.0),(82.6,5.0),(44.3,Dp-5.0),(82.6,Dp-5.0),(5.0,40.07),(5.0,74.13),(Wd-5.0,40.07),(Wd-5.0,74.13)]
def usb1(b): return b.cut(Part.makeCylinder(4.5,10.0,V(46.5,-5.0,7.0),V(0,1,0)))
# lubang USB sudah ada di v5; potong ulang menembus dinding baru yang lebih tebal
sw=[(77.49,95.96),(97.49,95.96)]
b1,l1=build("PCB1",Base,Lid,Wd,Dp,H,corners,extras,usb1,sw)
# pin tombol baru: batang d4.0 dari puncak plunger (z=19.6) sampai dasar cekungan membran
zrec=H+PLATE-0.8
pins=[Part.makeCylinder(2.0,zrec-19.6,V(x,y,19.6)) for x,y in sw]
a1=FreeCAD.openDocument(W_+"perakitan/assembly_PCB1_v9_sensor-di-tutup.FCStd")
check_parts(a1,("Base_v5","Tutup_v5_tertutup","Baut_PCB_Ref","KLIP_CHEST_SlimeVR")+tuple(o.Name for o in a1.Objects if o.Name.startswith("Pin")),b1,l1,None,"PCB1")
for (x,y) in extras: pass
P("pin tombol baru: batang d4.0 panjang %.1f mm, puncak z=%.1f (menyentuh membran di dasar cekungan); tidak menonjol"%(zrec-19.6,zrec))
t1=flip_print(l1)
doc=FreeCAD.newDocument("pcb1_wp")
for n,s in (("Base_v6",b1),("Tutup_v6_tertutup",l1),("Tutup_v6_cetak",t1)): f=doc.addObject("Part::Feature",n); f.Shape=s
for i,p in enumerate(pins): f=doc.addObject("Part::Feature","Pin_tombol_%d"%(i+1)); f.Shape=p
doc.recompute(); doc.saveAs(W_+"casing/3d-pcb1_v6_waterproof.FCStd")
b1.exportStep(W_+"casing/PCB1_v6_Base.step"); b1.exportStl(W_+"casing/PCB1_v6_Base.stl"); t1.exportStep(W_+"casing/PCB1_v6_Tutup_cetak.step"); t1.exportStl(W_+"casing/PCB1_v6_Tutup_cetak.stl"); pins[0].exportStl(W_+"casing/PCB1_v6_Pin_tombol.stl")
nd=FreeCAD.newDocument("assy_pcb1_v10")
for n,s in (("Base_v6",b1),("Tutup_v6_tertutup",l1)): f=nd.addObject("Part::Feature",n); f.Shape=s
for o in a1.Objects:
    if o.Name in ("Base_v5","Tutup_v5_tertutup") or o.Name.startswith("Pin"): continue
    if hasattr(o,"Shape") and o.Shape.Solids: f=nd.addObject("Part::Feature",o.Name); f.Shape=o.Shape.copy()
    elif o.TypeId=="Mesh::Feature": f=nd.addObject("Mesh::Feature",o.Name); f.Mesh=o.Mesh
for i,p in enumerate(pins): f=nd.addObject("Part::Feature","Pin_tombol_%d"%(i+1)); f.Shape=p
nd.recompute(); nd.saveAs(W_+"perakitan/assembly_PCB1_v10_waterproof.FCStd")
# ================= PCB2 =================
src2=FreeCAD.openDocument(W_+"casing/3D-pcb2_v4_baterai-bawah.FCStd")
Base2=src2.getObject("Base_v4").Shape; Lid2=src2.getObject("Tutup_v4_tertutup").Shape
Wd2,Dp2,Hold,H2=54.6,122.0,32.3,33.9
# wadah dinding naik Hold -> H2 (plunger SW1 harus sejajar dasar cekungan membran)
z0=31.5
slab=Base2.common(box(-5,-5,z0,70,140,z0+0.5))
faces=[f for f in slab.Faces if abs(f.BoundBox.ZMin-z0)<1e-6 and abs(f.BoundBox.ZMax-z0)<1e-6 and f.normalAt(0,0).z<-0.9]
for f in faces: Base2=Base2.fuse(f.extrude(V(0,0,H2-z0)))
Base2=Base2
# takik USB lama (terbuka ke atas) ditutup, diganti lubang bulat panel-mount
Base2=Base2.fuse(box(-0.1,20.9,26.3,2.5,33.9,H2))
Lid2=Lid2.copy(); Lid2.translate(V(0,0,H2-Hold))
corners2=[(7.0,7.0),(47.6,7.0),(7.0,115.03),(47.6,115.03)]
extras2=[(5.0,43.0),(5.0,79.0),(Wd2-5.0,43.0),(Wd2-5.0,79.0)]
def usb2(b):
    b=b.cut(Part.makeCylinder(4.5,10.0,V(-5.0,27.4,25.0),V(1,0,0)))
    for (x,y) in corners2: b=b.fuse(cyl(x,y,0.3,3.0,2.6))   # lubang pilot sudut yang tembus lantai ditutup dari bawah
    return b
b2,l2=build("PCB2",Base2,Lid2,Wd2,Dp2,H2,corners2,extras2,usb2,[(30.95,42.85)])
t2=flip_print(l2)
a2=FreeCAD.openDocument(W_+"perakitan/assembly_PCB2_v4_baterai-bawah.FCStd")
check_parts(a2,("Base_v4","Tutup_v4_tertutup","Baut_PCB_Ref"),b2,l2,None,"PCB2")
sw1=a2.getObject("SW1").Shape
P("SW1 puncak plunger z=%.1f, dasar cekungan membran z=%.1f (selisih %.2f mm)"%(sw1.BoundBox.ZMax,H2+PLATE-0.8,H2+PLATE-0.8-sw1.BoundBox.ZMax))
P("lubang pilot sudut PCB2 ditutup di bawah: titik (7,7,1.0) bahan = %s"%b2.isInside(V(7.0,7.0,1.0),1e-6,True))
doc=FreeCAD.newDocument("pcb2_wp")
for n,s in (("Base_v5",b2),("Tutup_v5_tertutup",l2),("Tutup_v5_cetak",t2)): f=doc.addObject("Part::Feature",n); f.Shape=s
doc.recompute(); doc.saveAs(W_+"casing/3D-pcb2_v5_waterproof.FCStd")
b2.exportStep(W_+"casing/PCB2_v5_Base.step"); b2.exportStl(W_+"casing/PCB2_v5_Base.stl"); t2.exportStep(W_+"casing/PCB2_v5_Tutup_cetak.step"); t2.exportStl(W_+"casing/PCB2_v5_Tutup_cetak.stl")
nd=FreeCAD.newDocument("assy_pcb2_v5")
for n,s in (("Base_v5",b2),("Tutup_v5_tertutup",l2)): f=nd.addObject("Part::Feature",n); f.Shape=s
for o in a2.Objects:
    if o.Name in ("Base_v4","Tutup_v4_tertutup"): continue
    if hasattr(o,"Shape") and o.Shape.Solids: f=nd.addObject("Part::Feature",o.Name); f.Shape=o.Shape.copy()
nd.recompute(); nd.saveAs(W_+"perakitan/assembly_PCB2_v5_waterproof.FCStd")
open(W_+"laporan/_tahap6_waterproof_report.txt","w").write("\n".join(out))
