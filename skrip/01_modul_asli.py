import FreeCAD, Import, Part, json, zipfile, collections, math
R="C:/Users/calvi/Favorites/Downloads/DESPRO_2/"; W=R+"3d-Despro2/"
G=R+"pandu-capstone/hardware/jlcpcba/2026-11-23/"
V=FreeCAD.Vector; M=FreeCAD.Matrix
out=[]
def P(*a):
    s=" ".join(str(x) for x in a); print(s); out.append(s)
def load(path):
    d=FreeCAD.newDocument("m"); Import.insert(path,d.Name); seen=set(); res=[]
    for o in d.Objects:
        if o.TypeId!="Part::Feature" or not o.Shape.Solids: continue
        s=o.Shape.copy(); s.Placement=o.getGlobalPlacement(); b=s.BoundBox
        k=(round(s.Volume,2),round(b.XMin,2),round(b.YMin,2),round(b.ZMin,2),round(b.XMax,2),round(b.YMax,2),round(b.ZMax,2))
        if k in seen: continue
        seen.add(k); res.append((o.Label,s))
    FreeCAD.closeDocument(d.Name); return res
def bb(shapes):
    b=None
    for s in shapes:
        if b is None: b=FreeCAD.BoundBox(s.BoundBox)
        else: b.add(s.BoundBox)
    return b
def mul(B,A): return [[sum(B[i][k]*A[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
def place(shapes,u,v,h,cu,cv,h0,bottom,theta,t):
    U,Vv,Hh=[V(*x) for x in (u,v,h)]
    A=[[U.x,U.y,U.z],[Vv.x,Vv.y,Vv.z],[Hh.x,Hh.y,Hh.z]]
    if bottom: A=mul([[1,0,0],[0,-1,0],[0,0,-1]],A)
    c,s_=math.cos(math.radians(theta)),math.sin(math.radians(theta))
    A=mul([[c,-s_,0],[s_,c,0],[0,0,1]],A)
    c0=U*cu+Vv*cv+Hh*h0
    tr=[t.x-(A[0][0]*c0.x+A[0][1]*c0.y+A[0][2]*c0.z),t.y-(A[1][0]*c0.x+A[1][1]*c0.y+A[1][2]*c0.z),t.z-(A[2][0]*c0.x+A[2][1]*c0.y+A[2][2]*c0.z)]
    m=M(A[0][0],A[0][1],A[0][2],tr[0], A[1][0],A[1][1],A[1][2],tr[1], A[2][0],A[2][1],A[2][2],tr[2], 0,0,0,1)
    res=[]
    for s in shapes:
        x=s.copy(); x.transformShape(m); res.append(x)
    return res
def lab(ms,*keys):
    return [s for l,s in ms if any(k.lower() in l.lower() for k in keys)]
MOD=W+"modul/"
mod={n:load(MOD+f) for n,f in dict(mt="mt3608-boost.step",tp="tp4056-typec.step",gy="gy521-mpu6050.step",sm="esp32c3-supermini_v5.step",hd="header-male-1x4.step").items()}
mtb=bb(lab(mod["mt"],"Converter PCB")); P("MT3608 board bbox",mtb)
tpb=bb(lab(mod["tp"],"board")); P("TP4056 board bbox",tpb)
gyb=bb([s for l,s in mod["gy"]]); P("GY521 all bbox",gyb)
low=[s for l,s in mod["sm"] if s.BoundBox.YMin<3.25 and s.BoundBox.YLength<0.4]; smp=bb(low); P("SuperMini pad solids",len(low),smp)
smb=bb([s for l,s in mod["sm"]]); P("SuperMini all bbox",smb)
hdb=bb([s for l,s in mod["hd"]]); P("Header all bbox",hdb)
def mdef(key):
    if key=="mt": return ((1,0,0),(0,0,-1),(0,1,0),(mtb.XMin+mtb.XMax)/2,-(mtb.ZMin+mtb.ZMax)/2,0.0)
    if key=="tp": return ((1,0,0),(0,1,0),(0,0,1),(tpb.XMin+tpb.XMax)/2,(tpb.YMin+tpb.YMax)/2,0.0)
    if key=="gy": return ((1,0,0),(0,1,0),(0,0,1),(gyb.XMin+gyb.XMax)/2,6.5,-4.2)
    if key=="sm": return ((0,0,1),(1,0,0),(0,1,0),(smp.ZMin+smp.ZMax)/2,(smb.XMin+smb.XMax)/2,3.10)
    if key=="hd": return ((1,0,0),(0,0,-1),(0,1,0),(hdb.XMin+hdb.XMax)/2,-(hdb.ZMin+hdb.ZMax)/2,0.0)
cfg={
 "PCB1":dict(step=W+"pcb/3D_PCB1_2026-11-24.step",old=W+"casing/3d-pcb1.FCStd",gz=G+"Gerber_PCB1_modul_2026-11-23.zip",T=V(9.49,-40.04,9.0),
   real={"U2":("mt",0,False),"U7":("tp",0,True),"U8":("gy",90,False),"U10":("hd",90,False)},
   generic={"U3":(51.5,28.2,11.0),"U9":(36.0,23.0,12.0)}),
 "PCB2":dict(step=W+"pcb/3D_PCB2_2026-11-24.step",old=W+"casing/3D-pcb2.FCStd",gz=G+"Gerber_PCB2_j1sambung_2026-11-23.zip",T=V(-5.4,121.85,7.5),
   real={"U1":("sm",90,False),"U7":("tp",180,False)},generic={}),
}
for n,c in cfg.items():
    old=FreeCAD.openDocument(c["old"])
    sh={k:old.getObject(k).Shape.copy() for k in ("Base","Tutup","Baut_PCB_Ref")}
    base=sh["Base"]; tut=sh["Tutup"]; ztop=base.BoundBox.ZMax
    tut.translate(V(0,-(tut.BoundBox.YMin-base.BoundBox.YMin),ztop-tut.BoundBox.ZMin))
    d=FreeCAD.newDocument("imp"); Import.insert(c["step"],d.Name); parts={}
    for o in list(d.Objects):
        if o.TypeId!="Part::Feature": continue
        s=o.Shape.copy(); s.Placement=o.getGlobalPlacement(); s.translate(c["T"])
        chain=[]; p=o
        while p.getParentGeoFeatureGroup() is not None:
            p=p.getParentGeoFeatureGroup(); chain.append(p.Label.split('~')[0])
        key=(chain[-2] if len(chain)>1 else (chain[0] if chain else o.Label)).split('~')[0]
        parts.setdefault(key,[]).append(s)
    FreeCAD.closeDocument(d.Name)
    pins=json.loads(zipfile.ZipFile(c["gz"]).read("FlyingProbeTesting.json"))
    pb=collections.defaultdict(list)
    for r in pins["pins"]["rows"]: pb[r[1].split("_")[0]].append((r[1],r[2]*0.0254+c["T"].x,r[3]*0.0254+c["T"].y))
    zb=c["T"].z; ptop=zb+1.6; modkeys=[]
    P("=====",n)
    for ref,(key,theta,bot) in c["real"].items():
        xs=[p[1] for p in pb[ref]]; ys=[p[2] for p in pb[ref]]
        cx=(min(xs)+max(xs))/2; cy=(min(ys)+max(ys))/2
        u,v,h,cu,cv,h0=mdef(key)
        z=zb if bot else ptop
        sh2=place([s for l,s in mod[key]],u,v,h,cu,cv,h0,bot,theta,V(cx,cy,z))
        parts[ref+"_MODUL"]=sh2; b=bb(sh2); modkeys.append(ref+"_MODUL")
        P(f"  {ref} model {key} theta={theta} {'bawah' if bot else 'atas'} pusat pad ({cx:.1f},{cy:.1f}) -> bbox x[{b.XMin:.1f},{b.XMax:.1f}] y[{b.YMin:.1f},{b.YMax:.1f}] z[{b.ZMin:.1f},{b.ZMax:.1f}]")
    for ref,(L,Wd,Hh) in c["generic"].items():
        xs=[p[1] for p in pb[ref]]; ys=[p[2] for p in pb[ref]]
        cx=(min(xs)+max(xs))/2; cy=(min(ys)+max(ys))/2
        if (max(xs)-min(xs))<(max(ys)-min(ys)): L,Wd=Wd,L
        b=Part.makeBox(L,Wd,Hh,V(cx-L/2,cy-Wd/2,ptop)); parts[ref+"_MODUL"]=[b]; modkeys.append(ref+"_MODUL")
        P(f"  {ref} blok GENERIK {L}x{Wd}x{Hh} (belum ada model asli yang cocok)")
    for ref in ("U8","U10"):
        if ref not in c["real"]: continue
        padxy=[(p[1],p[2]) for p in pb[ref]]
        pinsol=[s for s in parts[ref+"_MODUL"] if s.BoundBox.XLength<1.0 and s.BoundBox.YLength<1.0 and s.BoundBox.ZLength>3]
        errs=[]
        for s in pinsol:
            cx_,cy_=(s.BoundBox.XMin+s.BoundBox.XMax)/2,(s.BoundBox.YMin+s.BoundBox.YMax)/2
            errs.append(min(math.hypot(cx_-px,cy_-py) for px,py in padxy))
        if errs: P(f"  cek pin {ref}: {len(errs)} pin model, jarak ke pad terdekat max {max(errs):.2f} mm rata {sum(errs)/len(errs):.2f}")
        else: P(f"  cek pin {ref}: tidak ada solid pin terdeteksi")
    P("  Base z[%.1f,%.1f] Tutup z[%.1f,%.1f]"%(base.BoundBox.ZMin,base.BoundBox.ZMax,tut.BoundBox.ZMin,tut.BoundBox.ZMax))
    comps={k:Part.makeCompound(v) for k,v in parts.items()}
    pcbk=[k for k in comps if k.startswith("EasyEDA")]
    maxz=0; top=None
    for k,cs in sorted(comps.items()):
        b=cs.BoundBox
        cb=cs.common(base).Volume; ct=cs.common(tut).Volume; fl=[]
        if cb>0.5: fl.append(f"nabrak Base {cb:.0f} mm3")
        if ct>0.5: fl.append(f"nabrak Tutup {ct:.0f} mm3")
        if b.ZMin<base.BoundBox.ZMin: fl.append(f"di bawah lantai z={b.ZMin:.1f}")
        if b.ZMax>maxz: maxz=b.ZMax; top=k
        P(f"  {k:26} z[{b.ZMin:.1f},{b.ZMax:.1f}] x[{b.XMin:.1f},{b.XMax:.1f}] y[{b.YMin:.1f},{b.YMax:.1f}] {'; '.join(fl) or 'ok'}")
    P(f"  tertinggi {top} z={maxz:.1f}; bawah tutup z={tut.BoundBox.ZMin:.1f}; sisa {tut.BoundBox.ZMin-maxz:.1f} mm")
    P("  tabrakan modul x bagian lain (>1 mm3):")
    cnt=0
    for mk in modkeys:
        for k,cs in comps.items():
            if k==mk or k in pcbk: continue
            if k in modkeys and k<mk: continue
            vol=comps[mk].common(cs).Volume
            if vol>1: P(f"    {mk} x {k}: {vol:.0f} mm3"); cnt+=1
    if not cnt: P("    (tidak ada)")
    doc=FreeCAD.newDocument(n+"_v2")
    for k in ("Base","Tutup","Baut_PCB_Ref"):
        f=doc.addObject("Part::Feature",k); f.Shape=tut if k=="Tutup" else sh[k]
    for k,cs in comps.items():
        f=doc.addObject("Part::Feature",k.replace("-","_").replace("(","_").replace(")","_").replace(" ","_")[:40]); f.Shape=cs
    doc.recompute(); doc.saveAs(W+f"perakitan/assembly_{n}_v2_modul-asli.FCStd")
open(W+"laporan/_tahap5_modul_asli_report.txt","w").write("\n".join(out))
