import FreeCAD, Import, Part, math
V=FreeCAD.Vector; M=FreeCAD.Matrix
W="C:/Users/calvi/Favorites/Downloads/DESPRO_2/3d-Despro2/"
out=[]
def P(*a):
    s=" ".join(str(x) for x in a); print(s); out.append(s)
def mul(B,A): return [[sum(B[i][k]*A[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
def place(shapes,u,v,h,cu,cv,h0,theta,t):
    U,Vv,Hh=[V(*x) for x in (u,v,h)]
    A=[[U.x,U.y,U.z],[Vv.x,Vv.y,Vv.z],[Hh.x,Hh.y,Hh.z]]
    c,s_=math.cos(math.radians(theta)),math.sin(math.radians(theta))
    A=mul([[c,-s_,0],[s_,c,0],[0,0,1]],A)
    c0=U*cu+Vv*cv+Hh*h0
    tr=[t.x-(A[0][0]*c0.x+A[0][1]*c0.y+A[0][2]*c0.z),t.y-(A[1][0]*c0.x+A[1][1]*c0.y+A[1][2]*c0.z),t.z-(A[2][0]*c0.x+A[2][1]*c0.y+A[2][2]*c0.z)]
    m=M(A[0][0],A[0][1],A[0][2],tr[0], A[1][0],A[1][1],A[1][2],tr[1], A[2][0],A[2][1],A[2][2],tr[2], 0,0,0,1)
    res=[]
    for s in shapes:
        x=s.copy(); x.transformShape(m); res.append(x)
    return res
d=FreeCAD.newDocument("hold"); Import.insert(W+"modul/18650-holder-02b.step",d.Name)
hs=[]
for o in d.Objects:
    if o.TypeId=="Part::Feature" and o.Shape.Solids:
        s=o.Shape.copy(); s.Placement=o.getGlobalPlacement(); hs.append(s)
FreeCAD.closeDocument(d.Name)
sh=place(hs,(1,0,0),(0,-1,0),(0,0,-1),38.6,10.5,0.0,90,V(26.89,67.02,10.6))
hold=Part.makeCompound(sh); body=max(sh,key=lambda q:q.Volume); eb=body.BoundBox
env=Part.makeBox(eb.XLength,eb.YLength,eb.ZLength,V(eb.XMin,eb.YMin,eb.ZMin))
P("holder (atas papan): bbox x[%.1f,%.1f] y[%.1f,%.1f] z[%.1f,%.1f]; badan z[%.1f,%.1f]"%(hold.BoundBox.XMin,hold.BoundBox.XMax,hold.BoundBox.YMin,hold.BoundBox.YMax,hold.BoundBox.ZMin,hold.BoundBox.ZMax,eb.ZMin,eb.ZMax))
old=FreeCAD.openDocument(W+"casing/3d-pcb1.FCStd")
base=old.getObject("Base").Shape.copy(); tut=old.getObject("Tutup").Shape.copy(); bolt=old.getObject("Baut_PCB_Ref").Shape.copy()
ad=FreeCAD.openDocument(W+"perakitan/assembly_PCB1_v2_modul-asli.FCStd")
parts={o.Label:o.Shape.copy() for o in ad.Objects if o.Name not in ("Base","Tutup","Baut_PCB_Ref","BT1")}
P("bagian di perakitan:",", ".join(sorted(parts)))
H0=base.BoundBox.ZMax
H=math.ceil((eb.ZMax+1.0)*2)/2.0
P("dinding lama %.1f -> baru %.1f mm (puncak holder %.1f + celah 1.0)"%(H0,H,eb.ZMax))
# 1) dalamkan dinding dan tiang sudut
z0=28.5
slab=base.common(Part.makeBox(140,130,0.5,V(-5,-5,z0)))
faces=[f for f in slab.Faces if abs(f.BoundBox.ZMin-z0)<1e-6 and abs(f.BoundBox.ZMax-z0)<1e-6 and f.normalAt(0,0).z<-0.9]
P("penampang yang diekstrusi:",len(faces),"muka")
b2=base
for f in faces: b2=b2.fuse(f.extrude(V(0,0,H-z0)))
b2=b2.removeSplitter()
# 2) posisi plunger SW1/SW2
sw={}
for k in parts:
    if k.startswith("SW"):
        ws=parts[k].slice(V(0,0,1),16.0)
        bb=FreeCAD.BoundBox()
        for w in ws: bb.add(w.BoundBox)
        sw[k]=((bb.XMin+bb.XMax)/2,(bb.YMin+bb.YMax)/2,bb.XLength,bb.YLength,parts[k].BoundBox.ZMax)
        P("  %s plunger tengah (%.2f,%.2f) ukuran %.1f x %.1f, puncak z=%.1f"%(k,*sw[k][:2],*sw[k][2:4],sw[k][4]))
# 3) tutup tertutup (pelat 3.0 di atas, bibir 2.0 ke bawah)
t=tut.copy(); bb=t.BoundBox
t.rotate(V(0,(bb.YMin+bb.YMax)/2,(bb.ZMin+bb.ZMax)/2),V(1,0,0),180); bb=t.BoundBox
t.translate(V(0,-bb.YMin+base.BoundBox.YMin,(H-2.0)-bb.ZMin))
P("tutup tertutup z[%.1f,%.1f]"%(t.BoundBox.ZMin,t.BoundBox.ZMax))
SL_OD,SL_ID=8.0,4.4; sleeve_bot=None
pins=[]
for k,(cx,cy,_,_,ztop) in sw.items():
    zb_=ztop+0.5; sleeve_bot=zb_
    tube=Part.makeCylinder(SL_OD/2,H+1.0-zb_,V(cx,cy,zb_)).cut(Part.makeCylinder(SL_ID/2,H+3.5-zb_,V(cx,cy,zb_-0.5)))
    t=t.fuse(tube)
    t=t.cut(Part.makeCylinder(SL_ID/2,6.0,V(cx,cy,H-1.0)))      # lubang tembus pelat
    lid_top=t.BoundBox.ZMax
    stem=Part.makeCylinder(2.0,(lid_top+1.0)-ztop,V(cx,cy,ztop))
    head=Part.makeCylinder(3.5,1.5,V(cx,cy,lid_top+1.0))
    pins.append((k,stem.fuse(head)))
t=t.removeSplitter()
P("sleeve OD %.1f ID %.1f dari z=%.1f ke %.1f; pin: batang d4.0, kepala d7.0 x1.5, menonjol 1.0 di atas tutup (tutup atas z=%.1f)"%(SL_OD,SL_ID,sleeve_bot,H,t.BoundBox.ZMax))
# 4) celah kabel sensor air (U10, header di x~82.65, y~26.8) lewat dinding y=0
ux=(parts["U10_MODUL"].BoundBox.XMin+parts["U10_MODUL"].BoundBox.XMax)/2
slot_w=7.0; slot_z=22.0
b2=b2.cut(Part.makeBox(slot_w,4.0,H+0.2-slot_z,V(ux-slot_w/2,-1.0,slot_z)))
t=t.cut(Part.makeBox(slot_w,3.0,2.2,V(ux-slot_w/2,2.0,H-2.1)))
P("celah kabel sensor air: lebar %.0f mm, dasar z=%.0f, tengah x=%.1f di dinding y=0"%(slot_w,slot_z,ux))
# versi cetak tutup (pelat di bawah)
tp=t.copy(); bb=tp.BoundBox
tp.rotate(V(0,(bb.YMin+bb.YMax)/2,(bb.ZMin+bb.ZMax)/2),V(1,0,0),180); tp.translate(V(0,0,-tp.BoundBox.ZMin))
P("Base v2 z[%.1f,%.1f] vol %.0f; Tutup v2 vol %.0f"%(b2.BoundBox.ZMin,b2.BoundBox.ZMax,b2.Volume,t.Volume))
# 5) cek tabrakan
P("--- cek tabrakan PCB1 (mm3 > 0.5) ---")
allp=dict(parts); allp["BAT_HOLDER"]=hold
for k,s in allp.items():
    cb=s.common(b2).Volume; ct=s.common(t).Volume; fl=[]
    if cb>0.5: fl.append("Base %.1f"%cb)
    if ct>0.5: fl.append("Tutup %.1f"%ct)
    if fl or k in ("BAT_HOLDER","U2_MODUL","U7_MODUL","U8_MODUL","U10_MODUL","SW1","SW2(SOSButton)"):
        P("  %-18s z[%.1f,%.1f] %s"%(k,s.BoundBox.ZMin,s.BoundBox.ZMax,"; ".join(fl) or "ok"))
P("  amplop badan holder x Base %.1f, x Tutup %.1f"%(env.common(b2).Volume,env.common(t).Volume))
for k,s in allp.items():
    if k in ("BAT_HOLDER","EasyEDA PCB Model"): continue
    v=env.common(s).Volume
    if v>0.5: P("  amplop holder x %s: %.1f mm3"%(k,v))
top=max((s.BoundBox.ZMax,k) for k,s in allp.items() if k!="EasyEDA PCB Model")
P("  komponen tertinggi %s z=%.1f; bawah pelat tutup z=%.1f; sisa %.1f mm"%(top[1],top[0],H,H-top[0]))
for k,pn in pins:
    P("  pin %s: x tutup %.1f, x Base %.1f, x papan/komp %.1f"%(k,pn.common(t).Volume,pn.common(b2).Volume,sum(pn.common(s).Volume for kk,s in allp.items() if not kk.startswith("SW"))))
P("  tutup x Base %.2f mm3"%t.common(b2).Volume)
# 6) simpan
doc=FreeCAD.newDocument("casing_pcb1_v2")
for n,s in (("Base_v2",b2),("Tutup_v2_tertutup",t),("Tutup_v2_cetak",tp),("Baut_PCB_Ref",bolt)):
    f=doc.addObject("Part::Feature",n); f.Shape=s
for k,pn in pins:
    f=doc.addObject("Part::Feature","Pin_tombol_"+k.replace("(","_").replace(")","_")); f.Shape=pn
doc.recompute(); doc.saveAs(W+"casing/3d-pcb1_v2_baterai-atas.FCStd")
b2.exportStep(W+"casing/PCB1_v2_Base.step"); tp.exportStep(W+"casing/PCB1_v2_Tutup_cetak.step")
b2.exportStl(W+"casing/PCB1_v2_Base.stl"); tp.exportStl(W+"casing/PCB1_v2_Tutup_cetak.stl")
pins[0][1].exportStl(W+"casing/PCB1_v2_Pin_tombol.stl")
nd=FreeCAD.newDocument("assy_pcb1_v3")
for n,s in (("Base_v2",b2),("Tutup_v2_tertutup",t),("Baut_PCB_Ref",bolt)):
    f=nd.addObject("Part::Feature",n); f.Shape=s
for k,s in allp.items():
    f=nd.addObject("Part::Feature",k.replace("-","_").replace(" ","_").replace("(","_").replace(")","_")); f.Shape=s
for k,pn in pins:
    f=nd.addObject("Part::Feature","Pin_"+k.replace("(","_").replace(")","_")); f.Shape=pn
nd.recompute(); nd.saveAs(W+"perakitan/assembly_PCB1_v3_baterai-atas.FCStd")
open(W+"laporan/_tahap4_pcb1_report.txt","w").write("\n".join(out))
