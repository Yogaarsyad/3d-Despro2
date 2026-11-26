import FreeCAD, Part, Mesh, Import
import numpy as np
V=FreeCAD.Vector
W_="C:/Users/calvi/Favorites/Downloads/DESPRO_2/3d-Despro2/"
out=[]
def P(*a):
    s=" ".join(str(x) for x in a); print(s); out.append(s)
# ---- slot helm = saluran vertikal terbuka ke atas, diukur dari irisan mesh (kerangka PCA helm kuning, satuan model):
#  dinding helm (muka luar) pc1=0.174, dinding luar saluran (muka dalam) pc1=0.183, mulut saluran pc3=0.046, dasar tertutup pc3=0.065
#  panjang saluran pc2 sekitar 0.059 (30 mm dari Calvin), +pc3 = ke arah pinggiran bawah, jadi atas helm = -pc3
SLOT_L_MM=30.0; SLOT_L_U=0.059; SLOT_C_PC2=-0.0075
PC1_WALL,PC1_OUTER,PC3_MOUTH,PC3_FLOOR=0.174,0.183,0.046,0.065
S=SLOT_L_MM/SLOT_L_U
DEPTH_USER=14.0                     # kedalaman dari Calvin (ukur helm asli)
PL_W,PL_T,PL_L=33.0,3.1,13.5      # tebal dikurangi dari 3.5 (celah asli 3.5 mm); panjang turun 13.5 (kedalaman asli 14 mm)
GAP_REAL,DEPTH_REAL=3.5,14.0        # lebar (y), tebal (z), panjang turun (x) pelat lidah
BACK_OFF=0.3                        # celah punggung casing ke muka luar dinding helm
X_BOT=-8.5                          # tepi bawah casing = mulut saluran (casing bertumpu di tepi atas dinding luar saluran)
v=[];fa={};cur=None
for l in open(W_+"mekanik/helm/Safety_Helmet_3/Safety_Helmet_3.obj"):
    if l.startswith("v "): v.append([float(t) for t in l.split()[1:4]])
    elif l.startswith("o "): cur=l.split()[1]; fa.setdefault(cur,[])
    elif l.startswith("f "):
        idx=[int(t.split("/")[0])-1 for t in l.split()[1:]]
        for k in range(1,len(idx)-1): fa[cur].append([idx[0],idx[k],idx[k+1]])
v=np.array(v); shell=np.array(fa["Object017_Material__3_0"]); susp=np.array(fa["Object016_Material__5_0"]+fa["Object016_Material__2_0"])
used=np.unique(shell); c=v[used].mean(0); u,s,vt=np.linalg.svd(v[used]-c,full_matrices=False)
E=np.array([-vt[1],vt[2],vt[0]]); H=(v-c)@E.T                    # H: x depan(visor)+, y = pc3, z keluar = pc1
sx=-SLOT_C_PC2
# tepi atas dinding luar saluran (titik dengan pc3 terkecil di dinding luar, sekitar saluran) = mulut sebenarnya
ow=np.array([i for i in used if PC1_OUTER<=H[i,2]<=PC1_OUTER+0.008 and abs(H[i,0]-sx)<0.035 and 0.03<H[i,1]<0.07])
PC3_MOUTH=H[ow,1].min()
xmin,xmax=H[used,0].min(),H[used,0].max()
gap_c=(PC1_WALL+PC1_OUTER)/2
P("mulut saluran (tepi atas dinding luar) di pc3=%.4f"%PC3_MOUTH)
P("celah di model %.1f mm, helm asli %.1f mm -> lidah %.1f mm, sisa %.2f mm per sisi; kedalaman model %.1f mm, asli %.0f mm, lidah masuk %.1f mm"%((PC1_OUTER-PC1_WALL)*S,GAP_REAL,PL_T,(GAP_REAL-PL_T)/2,(PC3_FLOOR-PC3_MOUTH)*S,DEPTH_REAL,PL_L))
base0=FreeCAD.openDocument(W_+"casing/3D-pcb2_v7_tanpa-bolongan.FCStd").getObject("Base_v7").Shape
def box(x0,y0,z0,x1,y1,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def ibew_plate(YC,zc,thick):
    z0=zc-1.75
    d=FreeCAD.newDocument("l"); Import.insert(W_+"mekanik/helm/adaptor_slot/lidah_slot_ibew.step",d.Name)
    tg=[]
    for o in d.Objects:
        if o.TypeId=="Part::Feature" and o.Shape.Solids:
            s_=o.Shape.copy(); s_.Placement=o.getGlobalPlacement(); tg.append(s_)
    FreeCAD.closeDocument(d.Name)
    t0=Part.makeCompound(tg); b0=t0.BoundBox
    out_=[]
    for s_ in tg:
        x=s_.copy(); x.translate(V(-(b0.XMin+b0.XMax)/2,-b0.YMin,-b0.ZMin))     # tengah di x=0, ujung kaki di y=0, tebal z 0..3.5
        x.rotate(V(0,0,0),V(0,0,1),-90)                                          # kaki ke bawah (x negatif), lebar sepanjang y
        x.translate(V(X_BOT-PL_L,YC,z0))                                         # ujung kaki di x=X_BOT-PL_L
        out_.append(x)
    comp=Part.makeCompound(out_); bb=comp.BoundBox
    keep=box(X_BOT-PL_L-1,YC-30,zc-thick/2,X_BOT+2.5,YC+30,zc+thick/2)                # potong bagian pelat yang lebih panjang dari PL_L
    return comp.common(keep), b0
def build(YC,label):
    zc=(gap_c-PC1_WALL)*S+BACK_OFF; z0=zc-PL_T/2
    P("=== %s: pelat di y=%.1f; pelat z[%.2f,%.2f], x[%.1f,%.1f] ==="%(label,YC,z0,z0+PL_T,X_BOT-PL_L,X_BOT))
    plate,b0=ibew_plate(YC,zc,PL_T)
    P('lidah IBEW: x[%.1f,%.1f] y[%.1f,%.1f] z[%.2f,%.2f] vol %.0f'%(plate.BoundBox.XMin,plate.BoundBox.XMax,plate.BoundBox.YMin,plate.BoundBox.YMax,plate.BoundBox.ZMin,plate.BoundBox.ZMax,plate.Volume))
    b=base0.fuse(plate)
    P("Base valid=%s vol %.0f -> %.0f"%(b.isValid(),base0.Volume,b.Volume))
    # kerangka casing: x naik = ke arah mahkota helm (-pc3), +y = visor, z keluar
    T=lambda H_: np.stack([-(H_[:,1]-PC3_MOUTH)*S+X_BOT, (H_[:,0]-sx)*S+YC, (H_[:,2]-PC1_WALL)*S+BACK_OFF],axis=1)
    C=T(H)
    for nm,idx in (("cangkang",shell),("suspensi",susp)):
        pts=C[np.unique(idx)]
        hit=np.array([p for p in pts if -30<p[0]<64 and -9<p[1]<131 and -10<p[2]<35 and b.isInside(V(*p),1e-6,True)]); n=len(hit)
        P("titik %s helm di dalam Base+pelat: %d (harus 0)"%(nm,n))
        if n:
            P("   sebaran x[%.1f,%.1f] y[%.1f,%.1f] z[%.1f,%.1f]"%(hit[:,0].min(),hit[:,0].max(),hit[:,1].min(),hit[:,1].max(),hit[:,2].min(),hit[:,2].max()))
            hh=hit[(hit[:,0]>X_BOT-(PC3_FLOOR-PC3_MOUTH)*S+0.5)&(hit[:,0]<X_BOT-0.05)]
            if len(hh):
                hist=np.histogram(hh[:,1]-YC,bins=np.arange(-16,17,2))[0]; P("   histogram y-YC (bin 2 mm, -16..16): %s"%list(hist))
                hx=np.histogram(hh[:,0],bins=np.arange(-20,-8,2))[0]; P("   histogram x (-20..-8, bin 2): %s"%list(hx))
            P("   pelat di dalam saluran (di luar dasar): %d titik; y-YC[%.1f,%.1f] z[%.1f,%.1f] x[%.1f,%.1f]"%(len(hh),*(hh[:,1].min()-YC,hh[:,1].max()-YC,hh[:,2].min(),hh[:,2].max(),hh[:,0].min(),hh[:,0].max())) if len(hh) else "   pelat di dalam saluran (di luar dasar): 0 titik")
    sel=C[used]; inb=(sel[:,0]>=X_BOT)&(sel[:,0]<63.1)&(sel[:,1]>-8.5)&(sel[:,1]<130.5)
    P("punggung casing (z=0) vs cangkang di atas mulut saluran: titik terdekat z=%.1f mm (harus < 0 supaya nggak menabrak; makin dekat 0 makin menempel)"%sel[inb,2].max())
    for nm,(y0,y1) in (("ujung y kecil (belakang)",(-8.5,5)),("ujung y besar (depan)",(118,130.5))):
        m=inb&(sel[:,1]>y0)&(sel[:,1]<y1)
        P("jarak punggung casing ke helm di %s: %s"%(nm,("%.0f mm"%(-sel[m,2].max()) if m.any() else "tidak ada helm di sana")))
    ys=np.array([-8.5,130.5]); xh=sx+(ys-YC)/S
    P("ujung casing jatuh di %.0f dan %.0f mm dari tengah helm (helm: %.0f ke depan, %.0f ke belakang)"%(xh[0]*S,xh[1]*S,xmax*S,-xmin*S))
    P("casing berdiri di atas saluran: tinggi casing 71.6 mm ke arah mahkota (x dari -8.5 sampai 63.1)")
    pb=plate.BoundBox; pp=np.array([[x,y,z] for x in (pb.XMin,pb.XMax) for y in (pb.YMin,pb.YMax) for z in (pb.ZMin,pb.ZMax)])
    for nm,idx in (("cangkang",shell),("suspensi",susp)):
        q=C[np.unique(idx)]
        P("jarak terdekat pelat ke %s (kasar): %.1f mm"%(nm,min(np.min(np.linalg.norm(q-p,axis=1)) for p in pp)))
    tip=X_BOT-PL_L; floor_x=X_BOT-(PC3_FLOOR-PC3_MOUTH)*S
    P("ujung pelat di x=%.1f; dasar saluran di model x=%.1f -> pelat %s %.1f mm"%(tip,floor_x,"menembus dasar model" if tip<floor_x else "berhenti sebelum dasar",abs(tip-floor_x)))
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
build(60.0,"v16_ibew-3p5x14-tengah")
build(16.5,"v16b_ibew-3p5x14-ujung")
open(W_+"laporan/_tahap13_ibew_ukuran_asli_report.txt","w").write("\n".join(out))
