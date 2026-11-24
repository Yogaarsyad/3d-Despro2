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
# --- model holder (bbox 77.3 x 21.0 x 22.0, badan z[-22,0], pin sampai z=+2.0)
d=FreeCAD.newDocument("hold"); Import.insert(W+"modul/18650-holder-02b.step",d.Name)
hs=[]
for o in d.Objects:
    if o.TypeId=="Part::Feature" and o.Shape.Solids:
        s=o.Shape.copy(); s.Placement=o.getGlobalPlacement(); hs.append(s)
FreeCAD.closeDocument(d.Name)
cu=38.6; cv=-10.5   # tengah panjang dan tengah lebar (model)
def holder(top,cx,cy,zplane):
    if top: sh=place(hs,(1,0,0),(0,-1,0),(0,0,-1),cu,-cv,0.0,90,V(cx,cy,zplane))   # badan di atas bidang pasang
    else:   sh=place(hs,(1,0,0),(0,1,0),(0,0,1),cu,cv,0.0,90,V(cx,cy,zplane))      # badan di bawah bidang pasang
    body=max(sh,key=lambda q:q.Volume); env=body.BoundBox
    box=Part.makeBox(env.XLength,env.YLength,env.ZLength,V(env.XMin,env.YMin,env.ZMin))
    return Part.makeCompound(sh),box
# ================= PCB2: baterai di BAWAH papan =================
old=FreeCAD.openDocument(W+"casing/3D-pcb2.FCStd")
base=old.getObject("Base").Shape.copy(); tut=old.getObject("Tutup").Shape.copy(); bolt=old.getObject("Baut_PCB_Ref").Shape.copy()
# tinggi lantai (atas)
lo,hi=0.5,3.0
for _ in range(14):
    mid=(lo+hi)/2; n=len([w for w in base.slice(V(0,0,1),mid) if w.BoundBox.XLength>40 and w.BoundBox.YLength>100])
    if n>1: hi=mid
    else: lo=mid
floor=round(hi,2); P("lantai Base setebal ~%.2f mm"%floor)
HOLD=22.0; GAP=1.0
DZ=math.ceil((floor+HOLD+GAP-7.5)*2)/2.0
H=14.3+DZ
P("PCB2: dudukan PCB naik %.1f mm (7.5 -> %.1f); dinding baru %.1f mm; baterai menggantung z[%.1f,%.1f]"%(DZ,7.5+DZ,H,7.5+DZ-HOLD,7.5+DZ))
def faces_at(shape,z,filt=lambda f:True):
    slab=shape.common(Part.makeBox(70,140,0.5,V(-5,-5,z)))
    return [f for f in slab.Faces if abs(f.BoundBox.ZMin-z)<1e-6 and abs(f.BoundBox.ZMax-z)<1e-6 and f.normalAt(0,0).z<-0.9 and filt(f)]
b2=base
f_ring=faces_at(base,10.6)
f_stand=faces_at(base,5.0,lambda f:f.BoundBox.XLength<6.0 and f.BoundBox.XLength>4.0)
P("penampang: dinding+tiang sudut %d muka, tiang PCB %d muka"%(len(f_ring),len(f_stand)))
for f in f_ring: b2=b2.fuse(f.extrude(V(0,0,H-10.6)))
for f in f_stand: b2=b2.fuse(f.extrude(V(0,0,7.5+DZ-5.0)))
b2=b2.removeSplitter()
cy=27.4; w=13.0
b2=b2.cut(Part.makeBox(5.0,w,H+0.2-(8.35+DZ),V(-1.0,cy-w/2,8.35+DZ)))
t=tut.copy(); bb=t.BoundBox
t.rotate(V(0,(bb.YMin+bb.YMax)/2,(bb.ZMin+bb.ZMax)/2),V(1,0,0),180); bb=t.BoundBox
t.translate(V(0,-bb.YMin+base.BoundBox.YMin,(H-2.0)-bb.ZMin))
t=t.cut(Part.makeBox(4.0,4.0,5.0,V(30.95-2.0,42.85-2.0,H-1.0)))
t=t.cut(Part.makeBox(3.0,w,2.2,V(2.0,cy-w/2,H-2.1)))
tp=t.copy(); bb=tp.BoundBox
tp.rotate(V(0,(bb.YMin+bb.YMax)/2,(bb.ZMin+bb.ZMax)/2),V(1,0,0),180); tp.translate(V(0,0,-tp.BoundBox.ZMin))
bolt.translate(V(0,0,DZ))
P("Base v4: z[%.1f,%.1f] vol %.0f; Tutup z[%.1f,%.1f]"%(b2.BoundBox.ZMin,b2.BoundBox.ZMax,b2.Volume,t.BoundBox.ZMin,t.BoundBox.ZMax))
# papan + modul (dari perakitan v2) digeser DZ ke atas; H2 (header dummy) diganti holder
ad=FreeCAD.openDocument(W+"perakitan/assembly_PCB2_v2_modul-asli.FCStd")
parts={}
for o in ad.Objects:
    if o.Name in ("Base","Tutup","Baut_PCB_Ref","H2"): continue
    s=o.Shape.copy(); s.translate(V(0,0,DZ)); parts[o.Label]=s
hold,env=holder(False,27.16,60.56,7.5+DZ)
P("holder: bbox x[%.1f,%.1f] y[%.1f,%.1f] z[%.1f,%.1f]"%(hold.BoundBox.XMin,hold.BoundBox.XMax,hold.BoundBox.YMin,hold.BoundBox.YMax,hold.BoundBox.ZMin,hold.BoundBox.ZMax))
P("--- cek tabrakan PCB2 v4 (mm3 > 0.5) ---")
allp=dict(parts); allp["BAT_HOLDER"]=hold
for k,s in allp.items():
    cb=s.common(b2).Volume; ct=s.common(t).Volume; fl=[]
    if cb>0.5: fl.append("Base %.1f"%cb)
    if ct>0.5: fl.append("Tutup %.1f"%ct)
    P("  %-20s z[%.1f,%.1f] %s"%(k,s.BoundBox.ZMin,s.BoundBox.ZMax,"; ".join(fl) or "ok"))
P("  amplop holder (kotak penuh) x Base: %.1f mm3, x Tutup: %.1f mm3"%(env.common(b2).Volume,env.common(t).Volume))
for k in ("U1_MODUL","U7_MODUL","SW1","C1","C2","R1"):
    P("  amplop holder x %s: %.1f mm3"%(k,env.common(parts[k]).Volume))
P("  amplop holder x PCB: %.1f mm3 (pin menembus PCB: wajar bila kecil)"%env.common(parts["EasyEDA_PCB_Model"]).Volume)
P("  lantai ke dasar holder: %.1f mm"%(7.5+DZ-HOLD-floor))
P("  SW1 puncak z=%.1f, atas tutup z=%.1f -> menonjol %.1f mm"%(parts["SW1"].BoundBox.ZMax,t.BoundBox.ZMax,parts["SW1"].BoundBox.ZMax-t.BoundBox.ZMax))
# simpan
doc=FreeCAD.newDocument("casing_v4")
for n,s in (("Base_v4",b2),("Tutup_v4_tertutup",t),("Tutup_v4_cetak",tp),("Baut_PCB_Ref",bolt)):
    f=doc.addObject("Part::Feature",n); f.Shape=s
doc.recompute(); doc.saveAs(W+"casing/3D-pcb2_v4_baterai-bawah.FCStd")
b2.exportStep(W+"casing/PCB2_v4_Base.step"); tp.exportStep(W+"casing/PCB2_v4_Tutup_cetak.step")
b2.exportStl(W+"casing/PCB2_v4_Base.stl"); tp.exportStl(W+"casing/PCB2_v4_Tutup_cetak.stl")
nd=FreeCAD.newDocument("assy_v4")
for n,s in (("Base_v4",b2),("Tutup_v4_tertutup",t),("Baut_PCB_Ref",bolt)):
    f=nd.addObject("Part::Feature",n); f.Shape=s
for k,s in allp.items():
    f=nd.addObject("Part::Feature",k.replace("-","_").replace(" ","_")); f.Shape=s
nd.recompute(); nd.saveAs(W+"perakitan/assembly_PCB2_v4_baterai-bawah.FCStd")
# ================= PCB1: baterai di ATAS papan (ganti BT1) =================
a1=FreeCAD.openDocument(W+"perakitan/assembly_PCB1_v2_modul-asli.FCStd")
base1=a1.getObject("Base").Shape; tut1=a1.getObject("Tutup").Shape
hold1,env1=holder(True,26.89,67.02,10.6)
P("=== PCB1: holder di atas papan: bbox x[%.1f,%.1f] y[%.1f,%.1f] z[%.1f,%.1f]"%(hold1.BoundBox.XMin,hold1.BoundBox.XMax,hold1.BoundBox.YMin,hold1.BoundBox.YMax,hold1.BoundBox.ZMin,hold1.BoundBox.ZMax))
P("  bawah tutup z=%.1f (BT1 lama mentok di 29.2), holder baru puncak z=%.1f -> kurang %.1f mm"%(tut1.BoundBox.ZMin,hold1.BoundBox.ZMax,hold1.BoundBox.ZMax-tut1.BoundBox.ZMin))
for o in a1.Objects:
    if o.Name in ("Base","Tutup","Baut_PCB_Ref","BT1"): continue
    v=env1.common(o.Shape).Volume
    if v>0.5: P("  amplop holder x %s: %.0f mm3"%(o.Label,v))
P("  amplop holder x Base: %.0f mm3"%env1.common(base1).Volume)
open(W+"laporan/_tahap4_baterai_report.txt","w").write("\n".join(out))
