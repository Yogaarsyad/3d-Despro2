import FreeCAD, Part, Mesh, Import, math, os
V=FreeCAD.Vector
W_="C:/Users/calvi/Favorites/Downloads/DESPRO_2/3d-Despro2/"
EXT=9.5                         # dinding ke luar (v8: 8.5): sisa dinding counterbore ke tepi luar jadi 1.0 mm
GW,GD=2.6,1.5                   # alur kabel O-ring d2.0: lebar 2.6, dalam 1.5, tengah alur di x=0 (garis dinding lama)
SX=-5.5                         # garis tengah sekrup (di luar alur)
PLATE=3.0; SCR_D,CB_D,CB_H=3.4,6.0,1.4; REC_D=1.0; PIL_D,PIL_DEPTH=2.5,16.0   # counterbore 6.0 (kepala ISO 7380 M3 = 5.7), lekukan membran 1.0 (karet 1 mm)
out=[]
def P(*a):
    s=" ".join(str(x) for x in a); print(s); out.append(s)
def box(x0,y0,z0,x1,y1,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def cyl(x,y,z0,z1,d): return Part.makeCylinder(d/2,z1-z0,V(x,y,z0))
def positions(Wd,Dp,maxgap=36.0):
    x0,x1,y0,y1=SX,Wd-SX,SX,Dp-SX
    pts=[]
    def line(a,b,fixed,axis):
        n=max(1,math.ceil((b-a)/maxgap))
        for i in range(n+1):
            t=a+(b-a)*i/n
            pts.append((t,fixed) if axis=="x" else (fixed,t))
    line(x0,x1,y0,"x"); line(x0,x1,y1,"x"); line(y0,y1,x0,"y"); line(y0,y1,x1,"y")
    u=[]
    for p in pts:
        if all(abs(p[0]-q[0])>0.01 or abs(p[1]-q[1])>0.01 for q in u): u.append(p)
    return u
def build(name,Base,Lid,Wd,Dp,H,old_lid_holes,sleeves_recess,pre):
    P("=====",name,"W=%.1f D=%.1f H=%.1f; garis sekrup di %.1f mm dari dinding lama"%(Wd,Dp,H,-SX))
    b=pre(Base)
    ring=box(-EXT,-EXT,0,Wd+EXT,Dp+EXT,H).cut(box(0,0,-1,Wd,Dp,H+1))
    b=b.fuse(ring)
    g=GW/2
    b=b.cut(box(-g,-g,H-GD,Wd+g,Dp+g,H+0.2).cut(box(g,g,H-GD-1,Wd-g,Dp-g,H+1)))
    sp=positions(Wd,Dp)
    for (x,y) in sp: b=b.cut(cyl(x,y,H-PIL_DEPTH,H+0.1,PIL_D))
    per=2*(Wd+Dp)
    P("sekrup tutup: %d buah, sela maks 36 mm; panjang kabel O-ring sekitar %.0f mm (d2.0)"%(len(sp),per))
    pl=box(-EXT,-EXT,H,Wd+EXT,Dp+EXT,H+PLATE).cut(box(0,0,H-1,Wd,Dp,H+PLATE+1))
    l=Lid.fuse(pl)
    for (x,y) in old_lid_holes: l=l.fuse(cyl(x,y,H,H+PLATE,6.8))
    for (x,y) in sp:
        l=l.cut(cyl(x,y,H-0.2,H+PLATE+0.2,SCR_D)); l=l.cut(cyl(x,y,H+PLATE-CB_H,H+PLATE+0.2,CB_D))
    for (x,y) in sleeves_recess: l=l.cut(cyl(x,y,H+PLATE-REC_D,H+PLATE+0.2,12.0))
    P("Base valid=%s vol %.0f bbox x[%.1f,%.1f] y[%.1f,%.1f]; Tutup valid=%s vol %.0f; tabrakan Base x Tutup %.2f mm3"%(b.isValid(),b.Volume,b.BoundBox.XMin,b.BoundBox.XMax,b.BoundBox.YMin,b.BoundBox.YMax,l.isValid(),l.Volume,b.common(l).Volume))
    return b,l,sp
def flip_print(l):
    t=l.copy(); bb=t.BoundBox
    t.rotate(V(0,(bb.YMin+bb.YMax)/2,(bb.ZMin+bb.ZMax)/2),V(1,0,0),180); t.translate(V(0,0,-t.BoundBox.ZMin)); return t
def flood(name,b,l,Wd,Dp,H,seed_in,plugs):
    st=1.5; x0,x1,y0,y1,z0,z1=-EXT-6,Wd+EXT+6,-EXT-6,Dp+EXT+6,-3.0,H+PLATE+4
    nx,ny,nz=int((x1-x0)/st)+1,int((y1-y0)/st)+1,int((z1-z0)/st)+1
    cache={}
    bbx=FreeCAD.BoundBox(b.BoundBox); bbx.add(l.BoundBox)
    def solid(i,j,k):
        key=(i,j,k)
        if key in cache: return cache[key]
        p=V(x0+i*st,y0+j*st,z0+k*st)
        if not bbx.isInside(p): cache[key]=False; return False
        r=b.isInside(p,1e-7,True) or l.isInside(p,1e-7,True)
        cache[key]=r; return r
    def plugged(i,j,k):
        p=V(x0+i*st,y0+j*st,z0+k*st)
        for (px,py,pz0,pz1,rad) in plugs:
            if (p.x-px)**2+(p.y-py)**2<=rad*rad and pz0<=p.z<=pz1: return True
        return False
    def run(use_plugs):
        seen=set(); stack=[(0,0,nz//2)]
        ii,jj,kk=int((seed_in[0]-x0)/st),int((seed_in[1]-y0)/st),int((seed_in[2]-z0)/st)
        while stack:
            c=stack.pop()
            if c in seen: continue
            i,j,k=c
            if not(0<=i<nx and 0<=j<ny and 0<=k<nz): continue
            if solid(i,j,k) or (use_plugs and plugged(i,j,k)): continue
            seen.add(c)
            stack += [(i+1,j,k),(i-1,j,k),(i,j+1,k),(i,j-1,k),(i,j,k+1),(i,j,k-1)]
        return (ii,jj,kk) in seen, len(seen)
    return run

# ===== PCB1 v10: C-notch diperbaiki, dudukan klip pelat terpisah, lekukan membran 1.0 mm, kupon uji =====
P("sisa dinding counterbore ke tepi luar: %.2f mm (harus >= 1.0; v8 = -0.10)"%(EXT+SX-CB_D/2))
s1=FreeCAD.openDocument(W_+"casing/3d-pcb1_v5_sensor-di-tutup.FCStd")
Base=s1.getObject("Base_v5").Shape; Lid=s1.getObject("Tutup_v5_tertutup").Shape
def pre1(b):
    b=b.fuse(Part.makeCylinder(4.55,2.5,V(46.5,0.0,7.0),V(0,1,0)))
    for (x,y) in ((40.41,56.49),(86.37,56.49)): b=b.fuse(cyl(x,y,0.0,2.5,5.0))
    return b
Wd,Dp,H=126.9,114.2,34.0
sw=[(77.49,95.96),(97.49,95.96)]
b1,l1,sp1=build("PCB1",Base,Lid,Wd,Dp,H,[(6.0,6.0),(120.9,6.0),(6.0,108.2),(120.9,108.2)],sw,pre1)
bb=b1.BoundBox; P("ukuran luar PCB1: %.1f x %.1f mm, tinggi dasar %.1f (v8: 143.9 x 131.2)"%(bb.XLength,bb.YLength,bb.ZLength))
def scan(shape,pts,dz):
    bad=n=0
    for (x,y,z) in pts:
        for d in dz:
            n+=1
            if not shape.isInside(V(x+d[0],y+d[1],z),1e-6,True): bad+=1
    return bad,n
bu,nu=scan(b1,[(46.5,t,7.0) for t in (0.25,1.0,1.75,2.25)],[(0,0),(2,0),(-2,0),(0,2),(0,-2),(3.5,0)])
P("lubang USB tertutup: titik kosong %d dari %d"%(bu,nu))
bf,nf=scan(b1,[(x,y,z) for (x,y) in ((40.41,56.49),(86.37,56.49)) for z in (0.3,0.8,1.3,1.8,2.3)],[(0,0),(1.2,0),(-1.2,0),(0,1.2),(0,-1.2),(2.2,0),(0,2.2)])
P("lubang klip di lantai tertutup: titik kosong %d dari %d"%(bf,nf))
bl,nl=scan(l1,[(x,y,z) for (x,y) in [(6.0,6.0),(120.9,6.0),(6.0,108.2),(120.9,108.2)] for z in (34.3,35.5,36.7)],[(0,0),(2.0,0),(-2.0,0),(0,2.0),(0,-2.0),(2.8,0),(0,2.8)])
P("lubang sekrup lama di tutup tertutup: titik kosong %d dari %d"%(bl,nl))
bad=0
for (x,y) in sp1:
    for ang in range(0,360,15):
        px,py=x+(CB_D/2)*math.cos(math.radians(ang)),y+(CB_D/2)*math.sin(math.radians(ang))
        if not (-EXT<px<Wd+EXT and -EXT<py<Dp+EXT): bad+=1
P("titik tepi counterbore yang keluar dari tepi luar tutup: %d dari %d (harus 0)"%(bad,len(sp1)*24))
pins=[Part.makeCylinder(2.0,H+PLATE-REC_D-19.6,V(x,y,19.6)) for x,y in sw]
t1=flip_print(l1)
# ---- dudukan klip: pelat terpisah, muka atas rata ditempel ke lantai
a13=FreeCAD.openDocument(W_+"perakitan/assembly_PCB1_v13_dudukan-chest.FCStd")
clip=a13.getObject("KLIP_CHEST_SlimeVR").Mesh; cbb=clip.BoundBox
CLR,MARG,PAD_T,POCK_D=0.3,4.0,3.0,1.5
px0,px1,py0,py1=cbb.XMin-CLR-MARG,cbb.XMax+CLR+MARG,cbb.YMin-CLR-MARG,cbb.YMax+CLR+MARG
dock=box(px0,py0,-PAD_T,px1,py1,0.0).cut(box(cbb.XMin-CLR,cbb.YMin-CLR,-PAD_T-0.1,cbb.XMax+CLR,cbb.YMax+CLR,-PAD_T+POCK_D))
P("dudukan klip: %.1f x %.1f x %.1f mm, kantong %.1f x %.1f dalam %.1f; posisi di lantai: x %.1f..%.1f, y %.1f..%.1f (dari titik nol casing)"%(px1-px0,py1-py0,PAD_T,cbb.XLength+2*CLR,cbb.YLength+2*CLR,POCK_D,px0,px1,py0,py1))
dock_p=dock.copy(); dock_p.rotate(V(0,0,0),V(1,0,0),180); dock_p.translate(V(0,0,-dock_p.BoundBox.ZMin))
P("dudukan klip cetak: valid=%s, kantong menghadap atas (tanpa support), tinggi %.1f"%(dock_p.isValid(),dock_p.BoundBox.ZLength))
os.makedirs(W_+"casing/kupon",exist_ok=True)
doc=FreeCAD.newDocument("pcb1_v10")
for n,s in (("Base_v10",b1),("Tutup_v10_tertutup",l1),("Tutup_v10_cetak",t1),("Dudukan_klip",dock),("Dudukan_klip_cetak",dock_p)): f=doc.addObject("Part::Feature",n); f.Shape=s
for i,p in enumerate(pins): f=doc.addObject("Part::Feature","Pin_tombol_%d"%(i+1)); f.Shape=p
doc.recompute(); doc.saveAs(W_+"casing/3d-pcb1_v10_celah-fix.FCStd")
b1.exportStep(W_+"casing/PCB1_v10_Base.step"); b1.exportStl(W_+"casing/PCB1_v10_Base.stl")
t1.exportStep(W_+"casing/PCB1_v10_Tutup_cetak.step"); t1.exportStl(W_+"casing/PCB1_v10_Tutup_cetak.stl")
pins[0].exportStl(W_+"casing/PCB1_v10_Pin_tombol.stl")
dock_p.exportStep(W_+"casing/PCB1_v10_Dudukan_klip_cetak.step"); dock_p.exportStl(W_+"casing/PCB1_v10_Dudukan_klip_cetak.stl")
# ---- perakitan
a1=FreeCAD.openDocument(W_+"perakitan/assembly_PCB1_v10_waterproof.FCStd")
nd=FreeCAD.newDocument("assy_pcb1_v14")
for n,s in (("Base_v10",b1),("Tutup_v10_tertutup",l1),("Dudukan_klip",dock)): f=nd.addObject("Part::Feature",n); f.Shape=s
for o in a1.Objects:
    if o.Name in ("Base_v6","Tutup_v6_tertutup") or o.Name.startswith("Pin") or o.Name.startswith("KLIP"): continue
    if hasattr(o,"Shape") and not o.Shape.isNull() and o.Shape.Solids: f=nd.addObject("Part::Feature",o.Name); f.Shape=o.Shape.copy()
    elif o.TypeId=="Mesh::Feature": f=nd.addObject("Mesh::Feature",o.Name); f.Mesh=o.Mesh
f=nd.addObject("Mesh::Feature","KLIP_CHEST_SlimeVR"); f.Mesh=clip
for i,p in enumerate(pins): f=nd.addObject("Part::Feature","Pin_tombol_%d"%(i+1)); f.Shape=p
nd.recompute(); nd.saveAs(W_+"perakitan/assembly_PCB1_v14_final.FCStd")
# uji aliran air dipindah ke 24_pcb1_v10_uji_aliran.py (lama, jalan terpisah)
# ---- kupon sudut: sekrup, alur O-ring, dinding
cor=box(-EXT-1,-EXT-1,0,32,32,H); corl=box(-EXT-1,-EXT-1,H,32,32,H+PLATE)
kb=b1.common(cor); kl=flip_print(l1.common(corl))
P("kupon sudut: dasar valid=%s, tutup valid=%s, sekrup di kupon: %d"%(kb.isValid(),kl.isValid(),sum(1 for (x,y) in sp1 if x<32 and y<32)))
kb.exportStl(W_+"casing/kupon/Kupon_sudut_dasar.stl"); kl.exportStl(W_+"casing/kupon/Kupon_sudut_tutup.stl")
# ---- kupon lidah IBEW: 3 tebal (2.9, 3.1, 3.3 mm), rebah di bed, ujung kaki di y=0
d=FreeCAD.newDocument("l"); Import.insert(W_+"mekanik/helm/adaptor_slot/lidah_slot_ibew.step",d.Name)
tg=[]
for o in d.Objects:
    if o.TypeId=="Part::Feature" and o.Shape.Solids:
        s_=o.Shape.copy(); s_.Placement=o.getGlobalPlacement(); tg.append(s_)
FreeCAD.closeDocument(d.Name)
t0=Part.makeCompound(tg); b0=t0.BoundBox
parts=[]
for k,th in enumerate((2.9,3.1,3.3)):
    comp=Part.makeCompound([s_.copy() for s_ in tg]); comp.translate(V(-(b0.XMin+b0.XMax)/2,-b0.YMin,-b0.ZMin))
    z0=(3.5-th)/2
    sh=comp.common(box(-20,-1,z0,20,40,z0+th)); sh.translate(V(k*40,0,-z0))
    for m in range(k+1): sh=sh.fuse(cyl(k*40-8+m*5.0,25.0,th,th+0.6,2.0))
    sh.exportStl(W_+"casing/kupon/Kupon_lidah_%.1fmm.stl"%th); parts.append(sh)
Part.makeCompound(parts).exportStl(W_+"casing/kupon/Kupon_lidah_3tebal.stl")
P("kupon lidah: 2.9 (1 titik), 3.1 (2 titik), 3.3 (3 titik) mm; panjang 31.3, lebar 33")
open(W_+"laporan/_tahap15_pcb1_v10_report.txt","w").write("\n".join(out))
