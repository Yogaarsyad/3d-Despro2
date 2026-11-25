import FreeCAD, Part, math
V=FreeCAD.Vector
W_="C:/Users/calvi/Favorites/Downloads/DESPRO_2/3d-Despro2/"
EXT=8.5                         # dinding ke luar: zona sekrup 6.0 + zona alur 2.5 (dinding lama 2.5 tetap)
GW,GD=2.6,1.5                   # alur kabel O-ring d2.0: lebar 2.6, dalam 1.5, tengah alur di x=0 (garis dinding lama)
SX=-5.5                         # garis tengah sekrup (di luar alur)
PLATE=3.0; SCR_D,CB_D,CB_H=3.4,6.2,1.4; PIL_D,PIL_DEPTH=2.5,16.0
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
    b=pre(Base)                                     # tutup semua lubang lama (USB, lantai)
    ring=box(-EXT,-EXT,0,Wd+EXT,Dp+EXT,H).cut(box(0,0,-1,Wd,Dp,H+1))
    b=b.fuse(ring)
    g=GW/2
    b=b.cut(box(-g,-g,H-GD,Wd+g,Dp+g,H+0.2).cut(box(g,g,H-GD-1,Wd-g,Dp-g,H+1)))
    sp=positions(Wd,Dp)
    for (x,y) in sp: b=b.cut(cyl(x,y,H-PIL_DEPTH,H+0.1,PIL_D))
    per=2*(Wd+Dp)
    P("sekrup tutup: %d buah, sela %.0f mm; alur O-ring tengah di garis dinding lama, panjang kabel O-ring sekitar %.0f mm (d2.0)"%(len(sp),36.0,per))
    pl=box(-EXT,-EXT,H,Wd+EXT,Dp+EXT,H+PLATE).cut(box(0,0,H-1,Wd,Dp,H+PLATE+1))
    l=Lid.fuse(pl)
    for (x,y) in old_lid_holes: l=l.fuse(cyl(x,y,H,H+PLATE,6.8))        # lubang sekrup lama di tutup ditutup
    for (x,y) in sp:
        l=l.cut(cyl(x,y,H-0.2,H+PLATE+0.2,SCR_D)); l=l.cut(cyl(x,y,H+PLATE-CB_H,H+PLATE+0.2,CB_D))
    for (x,y) in sleeves_recess: l=l.cut(cyl(x,y,H+PLATE-0.8,H+PLATE+0.2,12.0))
    P("Base valid=%s vol %.0f bbox x[%.1f,%.1f] y[%.1f,%.1f]; Tutup valid=%s vol %.0f; tabrakan Base x Tutup %.2f mm3"%(b.isValid(),b.Volume,b.BoundBox.XMin,b.BoundBox.XMax,b.BoundBox.YMin,b.BoundBox.YMax,l.isValid(),l.Volume,b.common(l).Volume))
    return b,l,sp
def flip_print(l):
    t=l.copy(); bb=t.BoundBox
    t.rotate(V(0,(bb.YMin+bb.YMax)/2,(bb.ZMin+bb.ZMax)/2),V(1,0,0),180); t.translate(V(0,0,-t.BoundBox.ZMin)); return t
def flood(name,b,l,Wd,Dp,H,seed_in,plugs):
    """isi grid 1.5 mm; air dari luar menyebar ke sel kosong; apakah mencapai rongga dalam?"""
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
# ===== PCB1 =====
s1=FreeCAD.openDocument(W_+"casing/3d-pcb1_v5_sensor-di-tutup.FCStd")
Base=s1.getObject("Base_v5").Shape; Lid=s1.getObject("Tutup_v5_tertutup").Shape
def pre1(b):
    b=b.fuse(Part.makeCylinder(4.55,2.5,V(46.5,0.0,7.0),V(0,1,0)))                  # lubang USB d9
    for (x,y) in ((40.41,56.49),(86.37,56.49)): b=b.fuse(cyl(x,y,0.0,2.5,5.0))      # lubang sekrup klip chest (+counterbore)
    return b
Wd,Dp,H=126.9,114.2,34.0
sw=[(77.49,95.96),(97.49,95.96)]
b1,l1,sp1=build("PCB1",Base,Lid,Wd,Dp,H,[(6.0,6.0),(120.9,6.0),(6.0,108.2),(120.9,108.2)],sw,pre1)
# cek lubang lama benar2 tertutup (pindai penampang)
def scan_hole(shape,axis,a,z,r,t0,t1):
    bad=n=0
    for i in range(int((t1-t0)/0.5)):
        t=t0+0.25+i*0.5
        for dx in (-r+0.2,-r/2,0.0,r/2,r-0.2):
            for dz in (-r+0.2,-r/2,0.0,r/2,r-0.2):
                if dx*dx+dz*dz>r*r: continue
                p=V(a+dx,t,z+dz) if axis=="y" else V(t,a+dx,z+dz) if axis=="x" else None
                if p is None: continue
                n+=1
                if not shape.isInside(p,1e-6,True): bad+=1
    return bad,n
bu,nu=scan_hole(b1,"y",46.5,7.0,4.4,0.0,2.5)
P("PCB1 lubang USB d9 (x=46.5 z=7): titik kosong %d dari %d"%(bu,nu))
bf=nf=0
for (x,y) in ((40.41,56.49),(86.37,56.49)):
    for i in range(5):
        for dxy in ((0,0),(1.2,0),(-1.2,0),(0,1.2),(0,-1.2),(2.2,0),(0,2.2)):
            for z in (0.3+i*0.5,):
                nf+=1
                if not b1.isInside(V(x+dxy[0],y+dxy[1],z),1e-6,True): bf+=1
P("PCB1 lubang sekrup klip chest di lantai: titik kosong %d dari %d"%(bf,nf))
bl=nl=0
for (x,y) in [(6.0,6.0),(120.9,6.0),(6.0,108.2),(120.9,108.2)]:
    for dxy in ((0,0),(2.0,0),(-2.0,0),(0,2.0),(0,-2.0),(2.8,0),(0,2.8)):
        for z in (34.3,35.5,36.7):
            nl+=1
            if not l1.isInside(V(x+dxy[0],y+dxy[1],z),1e-6,True): bl+=1
P("PCB1 lubang sekrup lama di tutup (4 sudut): titik kosong %d dari %d"%(bl,nl))
pins=[Part.makeCylinder(2.0,H+PLATE-0.8-19.6,V(x,y,19.6)) for x,y in sw]
t1=flip_print(l1)
doc=FreeCAD.newDocument("pcb1_tb")
for n,s in (("Base_v8",b1),("Tutup_v8_tertutup",l1),("Tutup_v8_cetak",t1)): f=doc.addObject("Part::Feature",n); f.Shape=s
for i,p in enumerate(pins): f=doc.addObject("Part::Feature","Pin_tombol_%d"%(i+1)); f.Shape=p
doc.recompute(); doc.saveAs(W_+"casing/3d-pcb1_v8_tanpa-bolongan.FCStd")
b1.exportStep(W_+"casing/PCB1_v8_Base.step"); b1.exportStl(W_+"casing/PCB1_v8_Base.stl"); t1.exportStep(W_+"casing/PCB1_v8_Tutup_cetak.step"); t1.exportStl(W_+"casing/PCB1_v8_Tutup_cetak.stl"); pins[0].exportStl(W_+"casing/PCB1_v8_Pin_tombol.stl")
a1=FreeCAD.openDocument(W_+"perakitan/assembly_PCB1_v10_waterproof.FCStd")
nd=FreeCAD.newDocument("assy_pcb1_v12")
for n,s in (("Base_v8",b1),("Tutup_v8_tertutup",l1)): f=nd.addObject("Part::Feature",n); f.Shape=s
for o in a1.Objects:
    if o.Name in ("Base_v6","Tutup_v6_tertutup") or o.Name.startswith("Pin"): continue
    if hasattr(o,"Shape") and o.Shape.Solids: f=nd.addObject("Part::Feature",o.Name); f.Shape=o.Shape.copy()
    elif o.TypeId=="Mesh::Feature": f=nd.addObject("Mesh::Feature",o.Name); f.Mesh=o.Mesh
for i,p in enumerate(pins): f=nd.addObject("Part::Feature","Pin_tombol_%d"%(i+1)); f.Shape=p
nd.recompute(); nd.saveAs(W_+"perakitan/assembly_PCB1_v12_tanpa-bolongan.FCStd")
plug1=[(x,y,19.0,H+PLATE+0.9,2.4) for x,y in sw]+[(x,y,H+PLATE-0.9,H+PLATE+0.9,6.1) for x,y in sw]
run1=flood("PCB1",b1,l1,Wd,Dp,H,(63.45,57.1,20.0),plug1)
r=run1(False); P("uji aliran air PCB1 (grid 1.5 mm), rancangan apa adanya: rongga dalam terjangkau dari luar = %s (%d sel udara)"%r)
r=run1(True); P("uji aliran air PCB1, kedua tombol disumbat: rongga dalam terjangkau dari luar = %s (%d sel udara) -> harus False"%r)
# ===== PCB2 =====
s2=FreeCAD.openDocument(W_+"casing/3D-pcb2_v4_baterai-bawah.FCStd")
Base2=s2.getObject("Base_v4").Shape; Lid2=s2.getObject("Tutup_v4_tertutup").Shape
Wd2,Dp2,Hold,H2=54.6,122.0,32.3,33.9
z0=31.5
slab=Base2.common(box(-5,-5,z0,70,140,z0+0.5))
faces=[f for f in slab.Faces if abs(f.BoundBox.ZMin-z0)<1e-6 and abs(f.BoundBox.ZMax-z0)<1e-6 and f.normalAt(0,0).z<-0.9]
for f in faces: Base2=Base2.fuse(f.extrude(V(0,0,H2-z0)))
Lid2=Lid2.copy(); Lid2.translate(V(0,0,H2-Hold))
def pre2(b):
    b=b.fuse(box(-0.1,20.9,26.3,2.5,33.9,H2))                                        # takik USB lama
    for (x,y) in ((7.0,7.0),(47.6,7.0),(7.0,115.03),(47.6,115.03)): b=b.fuse(cyl(x,y,0.3,3.0,2.6))   # pilot sudut tembus lantai
    return b
b2,l2,sp2=build("PCB2",Base2,Lid2,Wd2,Dp2,H2,[(7.0,7.0),(47.6,7.0),(7.0,115.03),(47.6,115.03)],[(30.95,42.85)],pre2)
bn=0;nn=0
for i in range(int((32.3-26.3)/0.5)):          # di bawah alur O-ring (alur mulai z=32.4)
    z=26.3+0.25+i*0.5
    for y in (21.4,24,27.4,30.8,33.4):
        for x in (0.3,1.2,2.2):
            nn+=1
            if not b2.isInside(V(x,y,z),1e-6,True): bn+=1
P("PCB2 takik USB lama: titik kosong %d dari %d"%(bn,nn))
bf=nf=0
for (x,y) in ((7.0,7.0),(47.6,7.0),(7.0,115.03),(47.6,115.03)):
    for z in (0.5,1.2,2.0):
        for dxy in ((0,0),(0.6,0),(-0.6,0),(0,0.6),(0,-0.6)):
            nf+=1
            if not b2.isInside(V(x+dxy[0],y+dxy[1],z),1e-6,True): bf+=1
P("PCB2 lubang pilot sudut di lantai: titik kosong %d dari %d"%(bf,nf))
bl=nl=0
for (x,y) in [(7.0,7.0),(47.6,7.0),(7.0,115.03),(47.6,115.03)]:
    for dxy in ((0,0),(2.0,0),(-2.0,0),(0,2.0),(0,-2.0),(2.8,0),(0,2.8)):
        for z in (H2+0.3,H2+1.5,H2+2.7):
            nl+=1
            if not l2.isInside(V(x+dxy[0],y+dxy[1],z),1e-6,True): bl+=1
P("PCB2 lubang sekrup lama di tutup (4 sudut): titik kosong %d dari %d"%(bl,nl))
t2=flip_print(l2)
doc=FreeCAD.newDocument("pcb2_tb")
for n,s in (("Base_v7",b2),("Tutup_v7_tertutup",l2),("Tutup_v7_cetak",t2)): f=doc.addObject("Part::Feature",n); f.Shape=s
doc.recompute(); doc.saveAs(W_+"casing/3D-pcb2_v7_tanpa-bolongan.FCStd")
b2.exportStep(W_+"casing/PCB2_v7_Base.step"); b2.exportStl(W_+"casing/PCB2_v7_Base.stl"); t2.exportStep(W_+"casing/PCB2_v7_Tutup_cetak.step"); t2.exportStl(W_+"casing/PCB2_v7_Tutup_cetak.stl")
a2=FreeCAD.openDocument(W_+"perakitan/assembly_PCB2_v5_waterproof.FCStd")
nd=FreeCAD.newDocument("assy_pcb2_v7")
for n,s in (("Base_v7",b2),("Tutup_v7_tertutup",l2)): f=nd.addObject("Part::Feature",n); f.Shape=s
for o in a2.Objects:
    if o.Name in ("Base_v5","Tutup_v5_tertutup"): continue
    if hasattr(o,"Shape") and o.Shape.Solids: f=nd.addObject("Part::Feature",o.Name); f.Shape=o.Shape.copy()
nd.recompute(); nd.saveAs(W_+"perakitan/assembly_PCB2_v7_tanpa-bolongan.FCStd")
plug2=[(30.95,42.85,H2-1.0,H2+PLATE+0.9,3.2),(30.95,42.85,H2+PLATE-0.9,H2+PLATE+0.9,6.1)]
run2=flood("PCB2",b2,l2,Wd2,Dp2,H2,(27.3,60.0,20.0),plug2)
r=run2(False); P("uji aliran air PCB2 (grid 1.5 mm), rancangan apa adanya: rongga dalam terjangkau dari luar = %s (%d sel udara)"%r)
r=run2(True); P("uji aliran air PCB2, tombol SW1 disumbat: rongga dalam terjangkau dari luar = %s (%d sel udara) -> harus False"%r)
open(W_+"laporan/_tahap6_tanpa_bolongan_report.txt","w").write("\n".join(out))
