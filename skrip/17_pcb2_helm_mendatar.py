import FreeCAD, Part, Mesh
import numpy as np
V=FreeCAD.Vector
W_="C:/Users/calvi/Favorites/Downloads/DESPRO_2/3d-Despro2/"
out=[]
def P(*a):
    s=" ".join(str(x) for x in a); print(s); out.append(s)
# ---- masukan dari Calvin: slot samping 30 mm panjang, 15 mm dalam; casing rebah (sisi panjang sejajar tanah)
SLOT_L_MM,SLOT_DEPTH=30.0,15.0; SLOT_L_U=0.059; SLOT_C_PC2,SLOT_C_PC3=-0.0075,0.0565
S=SLOT_L_MM/SLOT_L_U; PAD_BOT=-8.0; PAD_X,PAD_Y,POCK=11.0,46.0,6.0; TT=3.5; CLR=0.2; X0=27.3; CY0=118.0
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
# visor: sisi mana (H.x +/-) yang lebih panjang melewati slot
xmin,xmax=H[used,0].min(),H[used,0].max()
P("depan-belakang helm di sekitar slot: %.0f mm ke +x, %.0f mm ke -x dari slot (slot di %.0f mm dari tengah)"%((xmax-sx)*S,(sx-xmin)*S,sx*S))
base0=FreeCAD.openDocument(W_+"casing/3D-pcb2_v7_tanpa-bolongan.FCStd").getObject("Base_v7").Shape
lid_doc=FreeCAD.openDocument(W_+"perakitan/assembly_PCB2_v10_helm-kuning.FCStd")
tg=lid_doc.getObject("Lidah_helm").Shape.copy()
tg.rotate(V(X0,CY0,0),V(0,0,1),90)       # lebar lidah sekarang sepanjang y casing (sisi panjang), tebal sepanjang x
def box(x0,y0,z0,x1,y1,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def build(CYt,label,toward_visor):
    P("=== %s: lidah di y=%.1f (casing y -8.5..130.5), casing %s dari slot ==="%(label,CYt,"menuju visor" if toward_visor else "menuju belakang helm"))
    pad=box(X0-PAD_X/2,CYt-PAD_Y/2,PAD_BOT,X0+PAD_X/2,CYt+PAD_Y/2,0.0)
    pock=box(X0-TT/2-CLR,CYt-15.0-CLR,PAD_BOT-0.1,X0+TT/2+CLR,CYt+15.0+CLR,PAD_BOT+POCK)
    b=base0.fuse(pad).cut(pock)
    t=tg.copy(); t.translate(V(0,CYt-CY0,0))
    P("Base valid=%s; bantalan y[%.1f,%.1f]; lidah x[%.1f,%.1f] y[%.1f,%.1f] z[%.1f,%.1f]; lidah x Base %.3f mm3 (harus 0)"%(b.isValid(),CYt-PAD_Y/2,CYt+PAD_Y/2,t.BoundBox.XMin,t.BoundBox.XMax,t.BoundBox.YMin,t.BoundBox.YMax,t.BoundBox.ZMin,t.BoundBox.ZMax,t.common(b).Volume))
    # pemetaan: casing y = +-H.x, casing x = -+H.y (tangan kanan), z keluar
    sg=1 if toward_visor is False else -1   # casing y naik ke arah depan (visor) kalau sg=1
    def T(H_):
        return np.stack([-sg*(H_[:,1]-sy)*S+X0, sg*(H_[:,0]-sx)*S+CYt, (H_[:,2]-zout)*S+PAD_BOT],axis=1)
    C=T(H)
    hits={}
    for nm,idx in (("cangkang",shell),("suspensi",susp)):
        pts=C[np.unique(idx)]
        n=sum(1 for p in pts if -9<p[0]<64 and -9<p[1]<131 and -9<p[2]<35 and b.isInside(V(*p),1e-6,True))
        P("titik %s helm di dalam Base: %d (harus 0)"%(nm,n)); hits[nm]=n
    sel=C[used]
    inb=(sel[:,0]>-8.5)&(sel[:,0]<63.1)&(sel[:,1]>-8.5)&(sel[:,1]<130.5)
    pad_zone=(abs(sel[:,0]-X0)<10)&(abs(sel[:,1]-CYt)<PAD_Y/2+2)
    P("punggung casing vs cangkang di luar bantalan: titik terdekat z=%.1f mm (harus < 0)"%sel[inb&~pad_zone,2].max())
    for nm,(y0,y1) in (("ujung y kecil (-8.5..5)",(-8.5,5)),("ujung y besar (118..130.5)",(118,130.5))):
        m=inb&(sel[:,1]>y0)&(sel[:,1]<y1)
        P("jarak casing ke permukaan helm di %s: %s"%(nm,("%.0f mm"%(-sel[m,2].max()) if m.any() else "tidak ada helm di bawahnya (casing menggantung di luar helm)")))
    # ujung casing lewat dari tepi helm?
    ys=np.array([-8.5,130.5]); xh=sx+(ys-CYt)/(sg*S)
    P("ujung casing jatuh di %.0f dan %.0f mm dari tengah helm (panjang helm: %.0f ke +x, %.0f ke -x dari tengah)"%(xh[0]*S,xh[1]*S,xmax*S,-xmin*S))
    for nm,idx in (("cangkang",shell),("suspensi",susp)):
        pp=C[np.unique(idx)]; tp=np.array([[x,y,z] for x in (t.BoundBox.XMin,X0,t.BoundBox.XMax) for y in (t.BoundBox.YMin,t.BoundBox.YMax) for z in np.linspace(-33.3,-8,12)])
        P("jarak terdekat lidah ke %s (kasar): %.1f mm"%(nm,min(np.min(np.linalg.norm(pp-q,axis=1)) for q in tp)))
    mm=lambda F_:Mesh.Mesh([[tuple(C[i]) for i in f] for f in F_])
    nd=FreeCAD.newDocument("a")
    a2=FreeCAD.openDocument(W_+"perakitan/assembly_PCB2_v7_tanpa-bolongan.FCStd")
    f=nd.addObject("Part::Feature","Base_"+label); f.Shape=b
    for o in a2.Objects:
        if o.Name=="Base_v7": continue
        if hasattr(o,"Shape") and not o.Shape.isNull() and o.Shape.Solids: f=nd.addObject("Part::Feature",o.Name); f.Shape=o.Shape.copy()
    f=nd.addObject("Part::Feature","Lidah_helm"); f.Shape=t
    f=nd.addObject("Mesh::Feature","HELM_kuning_cangkang"); f.Mesh=mm(shell)
    f=nd.addObject("Mesh::Feature","HELM_kuning_suspensi"); f.Mesh=mm(susp)
    nd.recompute(); nd.saveAs(W_+"perakitan/assembly_PCB2_%s.FCStd"%label)
    b.exportStep(W_+"casing/PCB2_%s_Base.step"%label); b.exportStl(W_+"casing/PCB2_%s_Base.stl"%label)
build(105.5,"v11_helm-mendatar-ujung",False)
build(105.5,"v11b_helm-mendatar-ujung-ke-visor",True)
build(60.0,"v12_helm-mendatar-tengah",False)
open(W_+"laporan/_tahap9_helm_mendatar_report.txt","w").write("\n".join(out))
