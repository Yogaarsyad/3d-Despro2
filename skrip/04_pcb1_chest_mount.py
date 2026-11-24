import FreeCAD, Part, Mesh, numpy as np
V=FreeCAD.Vector
W="C:/Users/calvi/Favorites/Downloads/DESPRO_2/3d-Despro2/"
STL=W+"mekanik/chest/slimevr-chest-mount-clip_thing6545989/files/ChestMountClip_SlimeBackCoverV1.stl"
out=[]
def P(*a):
    s=" ".join(str(x) for x in a); print(s); out.append(s)
# --- ukur boss langsung dari STL
d=open(STL,"rb").read(); n=int(np.frombuffer(d[80:84],dtype="<u4")[0])
a=np.frombuffer(d[84:],dtype=np.dtype([("n","<f4",3),("v","<f4",(3,3)),("a","<u2")]),count=n)
vv=np.unique(a["v"].reshape(-1,3).round(3),axis=0)
bos=[]
for c0 in ((-142.0,10.5),(-96.0,10.5)):
    c=np.array(c0)
    for it in range(6):
        m=(np.hypot(vv[:,0]-c[0],vv[:,1]-c[1])<4.2)&(vv[:,2]>10.9)
        pts=vv[m]; c=np.array([(pts[:,0].min()+pts[:,0].max())/2,(pts[:,1].min()+pts[:,1].max())/2])
    r=np.hypot(pts[:,0]-c[0],pts[:,1]-c[1]); zz=pts[:,2]
    h,e=np.histogram(r[zz>12.0],bins=42,range=(0,4.2))
    peaks=[(round(float(e[i]),1),int(h[i])) for i in range(len(h)) if h[i]>0.04*h.max()]
    bos.append(c); P("boss pusat (%.2f,%.2f); histogram radius (r:jumlah titik) %s"%(c[0],c[1],peaks))
mx=(bos[0][0]+bos[1][0])/2; by=bos[0][1]
P("jarak antar boss %.2f mm"%(bos[1][0]-bos[0][0]))
# --- tray: rim atas z=15.55 dipasang rata dengan sisi bawah lantai Base (z=0)
tray_cx=-118.95; tray_cy=(-13.8+36.0)/2
fx,fy=126.9/2,114.2/2
off=(fx-tray_cx,fy-tray_cy,-15.55)
P("offset model->casing: (%.2f, %.2f, %.2f)"%off)
holes=[(b[0]+off[0],b[1]+off[1]) for b in bos]
P("lubang di lantai Base (casing): "+", ".join("(%.2f, %.2f)"%h for h in holes))
# --- lubang di Base v2
src=FreeCAD.openDocument(W+"casing/3d-pcb1_v2_baterai-atas.FCStd")
base=src.getObject("Base_v2").Shape.copy()
HD,CB=2.6,4.8
b3=base
for (hx,hy) in holes:
    b3=b3.cut(Part.makeCylinder(HD/2,5.0,V(hx,hy,-1.0)))
    b3=b3.cut(Part.makeCylinder(CB/2,1.0+0.2,V(hx,hy,1.5)))   # counterbore dari atas, kedalaman 1.0 (lantai 2.5)
P("Base v3 vol %.0f (v2 %.0f); selisih %.1f mm3"%(b3.Volume,base.Volume,base.Volume-b3.Volume))
exp=3.14159*(HD/2)**2*2.5+3.14159*(CB/2)**2*1.0-3.14159*(HD/2)**2*1.0
P("  perkiraan volume dibuang %.1f mm3 (2 lubang: %.1f)"%(exp*2,exp*2))
# --- cek: apa yang ada di sekitar lubang pada papan (modul bawah dll)
a1=FreeCAD.openDocument(W+"perakitan/assembly_PCB1_v3_baterai-atas.FCStd")
for (hx,hy) in holes:
    cyl=Part.makeCylinder(3.0,8.0,V(hx,hy,2.5))
    for o in a1.Objects:
        if o.Name in ("Base_v2","Tutup_v2_tertutup","Baut_PCB_Ref") or o.Name.startswith("Pin"): continue
        v=o.Shape.common(cyl).Volume
        if v>0.5: P("  di atas lubang (%.1f,%.1f) z 2.5..10.5, ada %s: %.1f mm3"%(hx,hy,o.Label,v))
    # jarak dari kepala sekrup (z=2.5+1.6) ke bagian terdekat di atasnya
    zmin=min([o.Shape.BoundBox.ZMin for o in a1.Objects if o.Name not in ("Base_v2","Tutup_v2_tertutup","Baut_PCB_Ref") and not o.Name.startswith("Pin") and o.Shape.BoundBox.XMin<hx+3 and o.Shape.BoundBox.XMax>hx-3 and o.Shape.BoundBox.YMin<hy+3 and o.Shape.BoundBox.YMax>hy-3] or [99])
    P("  bagian terendah di atas lubang (%.1f,%.1f): z=%.1f (kepala sekrup M2.5 ~z=%.1f)"%(hx,hy,zmin,2.5+1.6))
# --- simpan casing v3
doc=FreeCAD.newDocument("casing_pcb1_v3")
for o in src.Objects:
    if o.Name=="Base_v2": continue
    if hasattr(o,"Shape") and o.Shape.Solids:
        f=doc.addObject("Part::Feature",o.Name); f.Shape=o.Shape.copy()
f=doc.addObject("Part::Feature","Base_v3"); f.Shape=b3
doc.recompute(); doc.saveAs(W+"casing/3d-pcb1_v3_chest-mount.FCStd")
b3.exportStep(W+"casing/PCB1_v3_Base.step"); b3.exportStl(W+"casing/PCB1_v3_Base.stl")
# --- perakitan: ganti Base, tambah klip chest (mesh disederhanakan)
nd=FreeCAD.newDocument("assy_pcb1_v4")
for o in a1.Objects:
    if o.Name=="Base_v2":
        f=nd.addObject("Part::Feature","Base_v3"); f.Shape=b3
    elif hasattr(o,"Shape") and o.Shape.Solids:
        f=nd.addObject("Part::Feature",o.Name); f.Shape=o.Shape.copy()
mesh=Mesh.Mesh(STL)
P("mesh klip: %d segitiga"%mesh.CountFacets)
try:
    mesh.decimate(0.0,0.97)
    P("  setelah decimate: %d segitiga"%mesh.CountFacets)
except Exception as e:
    P("  decimate gagal:",e)
mesh.translate(*off)
mo=nd.addObject("Mesh::Feature","KLIP_CHEST_SlimeVR"); mo.Mesh=mesh
bb=mesh.BoundBox
P("klip di casing: x[%.1f,%.1f] y[%.1f,%.1f] z[%.1f,%.1f] (lantai Base z=0)"%(bb.XMin,bb.XMax,bb.YMin,bb.YMax,bb.ZMin,bb.ZMax))
# amplop klip vs Base (harus sentuh di z=0 saja)
env=Part.makeBox(bb.XLength,bb.YLength,bb.ZLength,V(bb.XMin,bb.YMin,bb.ZMin))
P("  amplop klip x Base: %.2f mm3 (0 = hanya menempel di bawah lantai)"%env.common(b3).Volume)
P("  klip x tepi Base: x klip [%.1f,%.1f] dalam [0,126.9]; y klip [%.1f,%.1f] dalam [0,114.2]"%(bb.XMin,bb.XMax,bb.YMin,bb.YMax))
nd.recompute(); nd.saveAs(W+"perakitan/assembly_PCB1_v4_chest-mount.FCStd")
open(W+"laporan/_tahap5_chest_report.txt","w").write("\n".join(out))
