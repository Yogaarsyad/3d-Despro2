import FreeCAD, Part, Mesh
import numpy as np
V=FreeCAD.Vector
W_="C:/Users/calvi/Favorites/Downloads/DESPRO_2/3d-Despro2/"
out=[]
def P(*a):
    s=" ".join(str(x) for x in a); print(s); out.append(s)
# ---- ukuran slot helm: panjang 30 dan dalam 15 mm (Calvin); tinggi jendela di model ~9.7 mm (DUGAAN, belum diukur di helm asli)
SLOT_L_MM,SLOT_DEPTH=30.0,15.0; SLOT_L_U=0.059; SLOT_C_PC2,SLOT_C_PC3=-0.0075,0.0565
S=SLOT_L_MM/SLOT_L_U
WALL_OUT=-1.0                   # permukaan luar dinding helm di slot, di kerangka casing (punggung casing z=0)
HK_W,HK_H,LIP_T,LIP_DN,CLR_IN=28.5,4.0,2.0,4.0,0.5   # lebar kait, tinggi stub, tebal bibir, bibir turun di bawah stub, celah ke sisi dalam dinding
XS=-3.0                         # tengah stub (casing x), dekat tepi atas casing (x=-8.5)
BLK_X0,BLK_X1,BLK_W=-8.5,1.5,36.0
z_in=WALL_OUT-SLOT_DEPTH; z_tip=z_in-CLR_IN-LIP_T
v=[];fa={};cur=None
for l in open(W_+"mekanik/helm/Safety_Helmet_3/Safety_Helmet_3.obj"):
    if l.startswith("v "): v.append([float(t) for t in l.split()[1:4]])
    elif l.startswith("o "): cur=l.split()[1]; fa.setdefault(cur,[])
    elif l.startswith("f "):
        idx=[int(t.split("/")[0])-1 for t in l.split()[1:]]
        for k in range(1,len(idx)-1): fa[cur].append([idx[0],idx[k],idx[k+1]])
v=np.array(v); shell=np.array(fa["Object017_Material__3_0"]); susp=np.array(fa["Object016_Material__5_0"]+fa["Object016_Material__2_0"])
used=np.unique(shell); c=v[used].mean(0); u,s,vt=np.linalg.svd(v[used]-c,full_matrices=False)
E=np.array([-vt[1],vt[2],vt[0]]); H=(v-c)@E.T
sx,sy=-SLOT_C_PC2,SLOT_C_PC3
near=np.array([i for i in used if abs(H[i,0]-sx)<0.02 and abs(H[i,1]-sy)<0.015 and H[i,2]>0.12]); zout=H[near,2].max()
xmin,xmax=H[used,0].min(),H[used,0].max()
base0=FreeCAD.openDocument(W_+"casing/3D-pcb2_v7_tanpa-bolongan.FCStd").getObject("Base_v7").Shape
def box(x0,y0,z0,x1,y1,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def build(YC,label,sg=1):   # sg=1: casing tetap menggantung ke bawah (x naik = turun), +y = arah visor
    P("=== %s: kait di y=%.1f dari y -8.5..130.5, sg=%d ==="%(label,YC,sg))
    blk=box(BLK_X0,YC-BLK_W/2,WALL_OUT,BLK_X1,YC+BLK_W/2,0.0)
    stub=box(XS-HK_H/2,YC-HK_W/2,z_tip,XS+HK_H/2,YC+HK_W/2,WALL_OUT+0.01)
    lip=box(XS-HK_H/2,YC-HK_W/2,z_tip,XS+HK_H/2+LIP_DN,YC+HK_W/2,z_in-CLR_IN)
    hook=blk.fuse(stub).fuse(lip)
    b=base0.fuse(hook)
    P("Base valid=%s vol %.0f -> %.0f; stub x[%.1f,%.1f] z[%.1f,%.1f]; bibir turun sampai x=%.1f, z[%.1f,%.1f]"%(b.isValid(),base0.Volume,b.Volume,XS-HK_H/2,XS+HK_H/2,z_tip,WALL_OUT,XS+HK_H/2+LIP_DN,z_tip,z_in-CLR_IN))
    T=lambda H_: np.stack([-sg*(H_[:,1]-sy)*S+XS, sg*(H_[:,0]-sx)*S+YC, (H_[:,2]-zout)*S+WALL_OUT],axis=1)
    C=T(H)
    for nm,idx in (("cangkang",shell),("suspensi",susp)):
        pts=C[np.unique(idx)]
        hit=np.array([p for p in pts if -9<p[0]<64 and -9<p[1]<131 and -25<p[2]<35 and b.isInside(V(*p),1e-6,True)]); n=len(hit)
        P("titik %s helm di dalam Base+kait: %d (harus 0)"%(nm,n))
        if n: P("   sebaran x[%.1f,%.1f] y[%.1f,%.1f] z[%.1f,%.1f]"%(hit[:,0].min(),hit[:,0].max(),hit[:,1].min(),hit[:,1].max(),hit[:,2].min(),hit[:,2].max()))
    sel=C[used]; inb=(sel[:,0]>-8.5)&(sel[:,0]<63.1)&(sel[:,1]>-8.5)&(sel[:,1]<130.5)
    blkz=(sel[:,0]<BLK_X1+2)&(abs(sel[:,1]-YC)<BLK_W/2+2)
    P("punggung casing vs cangkang di luar blok kait: titik terdekat z=%.1f mm (harus < 0; 0 = menempel)"%sel[inb&~blkz,2].max())
    for nm,(y0,y1) in (("ujung y kecil",(-8.5,5)),("ujung y besar",(118,130.5))):
        m=inb&(sel[:,1]>y0)&(sel[:,1]<y1)&~blkz
        P("jarak casing ke helm di %s: %s"%(nm,("%.0f mm"%(-sel[m,2].max()) if m.any() else "tidak ada helm di bawahnya")))
    ys=np.array([-8.5,130.5]); xh=sx+(ys-YC)/(sg*S)
    P("ujung casing jatuh di %.0f dan %.0f mm dari tengah helm (helm: %.0f ke +x, %.0f ke -x)"%(xh[0]*S,xh[1]*S,xmax*S,-xmin*S))
    # bagian casing di bawah brim: x casing 63 -> turun berapa mm di bawah slot
    P("casing menggantung %.0f mm di bawah tengah slot (x casing -3 sampai 63.1)"%(63.1-XS))
    hp=np.array([[x,y,z] for x in (XS-HK_H/2,XS+HK_H/2+LIP_DN) for y in (YC-HK_W/2,YC+HK_W/2) for z in (z_tip,z_in-CLR_IN)])
    for nm,idx in (("cangkang",shell),("suspensi",susp)):
        pp=C[np.unique(idx)]
        P("jarak terdekat bibir kait ke %s (kasar, vertex): %.1f mm"%(nm,min(np.min(np.linalg.norm(pp-q,axis=1)) for q in hp)))
    mm=lambda F_:Mesh.Mesh([[tuple(C[i]) for i in f] for f in F_])
    nd=FreeCAD.newDocument("a"); a2=FreeCAD.openDocument(W_+"perakitan/assembly_PCB2_v7_tanpa-bolongan.FCStd")
    f=nd.addObject("Part::Feature","Base_"+label); f.Shape=b
    for o in a2.Objects:
        if o.Name=="Base_v7": continue
        if hasattr(o,"Shape") and not o.Shape.isNull() and o.Shape.Solids: f=nd.addObject("Part::Feature",o.Name); f.Shape=o.Shape.copy()
    f=nd.addObject("Mesh::Feature","HELM_kuning_cangkang"); f.Mesh=mm(shell)
    f=nd.addObject("Mesh::Feature","HELM_kuning_suspensi"); f.Mesh=mm(susp)
    nd.recompute(); nd.saveAs(W_+"perakitan/assembly_PCB2_%s.FCStd"%label)
    b.exportStep(W_+"casing/PCB2_%s_Base.step"%label); b.exportStl(W_+"casing/PCB2_%s_Base.stl"%label)
build(60.0,"v13_kait-tengah",1)
build(16.5,"v13b_kait-ujung-ke-visor")
open(W_+"laporan/_tahap10_kait_j_report.txt","w").write("\n".join(out))
