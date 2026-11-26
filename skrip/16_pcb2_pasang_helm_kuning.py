import FreeCAD, Part, Mesh
import numpy as np
V=FreeCAD.Vector
W_="C:/Users/calvi/Favorites/Downloads/DESPRO_2/3d-Despro2/"
out=[]
def P(*a):
    s=" ".join(str(x) for x in a); print(s); out.append(s)
SLOT_L_MM=30.0; SLOT_DEPTH_MM=15.0       # dari Calvin (ukur helm fisik)
SLOT_L_U=0.059                            # panjang jendela slot samping di model (satuan model), diukur dari titik jendela
SLOT_C_PC2,SLOT_C_PC3=-0.0075,0.0565      # tengah jendela slot (satuan model, kerangka PCA)
CX,CY=27.3,118.0; PAD_BOT=-8.0
S=SLOT_L_MM/SLOT_L_U
# ---- baca helm kuning
v=[];fa={}
cur=None
for l in open(W_+"mekanik/helm/Safety_Helmet_3/Safety_Helmet_3.obj"):
    if l.startswith("v "): v.append([float(t) for t in l.split()[1:4]])
    elif l.startswith("o "): cur=l.split()[1]; fa.setdefault(cur,[])
    elif l.startswith("f "):
        idx=[int(t.split("/")[0])-1 for t in l.split()[1:]]
        for k in range(1,len(idx)-1): fa[cur].append([idx[0],idx[k],idx[k+1]])
v=np.array(v)
shell=np.array(fa["Object017_Material__3_0"]); susp=np.array(fa["Object016_Material__5_0"]+fa["Object016_Material__2_0"])
used=np.unique(shell); c=v[used].mean(0)
u,s,vt=np.linalg.svd(v[used]-c,full_matrices=False)
E=np.array([-vt[1],vt[2],vt[0]]); P("kerangka helm: det=%.3f (harus +1)"%np.linalg.det(E))
H=(v-c)@E.T                                 # x depan-belakang, y atas, z keluar (sisi slot +z)
# permukaan luar dinding di tengah slot: z maksimum titik cangkang di sekitar jendela
sx,sy=-SLOT_C_PC2,SLOT_C_PC3
near=np.array([i for i in used if abs(H[i,0]-sx)<0.02 and abs(H[i,1]-sy)<0.015 and H[i,2]>0.12])
zout=H[near,2].max(); zin=H[near,2].min()
P("skala %.1f mm per satuan model (slot 30 mm = %.3f satuan). Lebar helm %.0f mm, panjang %.0f mm, tinggi %.0f mm"%(S,SLOT_L_U,np.ptp(H[used,0])*S if False else 0,0,0) if False else "skala %.1f mm per satuan model (slot 30 mm = %.3f satuan)"%(S,SLOT_L_U))
ext=np.ptp(H[used],axis=0)*S
P("ukuran helm hasil skala: depan-belakang %.0f mm, tinggi %.0f mm, lebar %.0f mm (diukur dari cangkang)"%(ext[0],ext[1],ext[2]))
P("dinding di slot di model: tebal sekitar %.1f mm (z %.3f..%.3f satuan); Calvin bilang kedalaman 15 mm"%((zout-zin)*S,zin,zout))
T=lambda H_: np.stack([H_[:,0]*S+CX-sx*S, H_[:,1]*S+CY-sy*S, H_[:,2]*S-zout*S+PAD_BOT],axis=1)
C=T(H)
# ---- lidah: lebar 29.0 mm (celah 0.5 mm per sisi di slot 30)
d=FreeCAD.openDocument(W_+"casing/3D-pcb2_v9_lidah-ujung.FCStd")
tongue=d.getObject("Lidah_terpasang").Shape
cut=Part.makeBox(20,10,60,V(CX-14.5-20,CY-5,-40))
cut2=Part.makeBox(20,10,60,V(CX+14.5,CY-5,-40))
t2=tongue.cut(cut).cut(cut2); tb=t2.BoundBox
P("lidah dipersempit: lebar %.1f mm (slot 30), tebal %.1f, z[%.1f,%.1f]; valid=%s"%(tb.XLength,tb.YLength,tb.ZMin,tb.ZMax,t2.isValid()))
base=d.getObject("Base_v9").Shape
# ---- cek tabrakan: titik helm di dalam casing
def inside_count(idx,name):
    pts=C[np.unique(idx)]; hit=[p for p in pts if -9<p[0]<64 and -9<p[1]<131 and -9<p[2]<35 and base.isInside(V(*p),1e-6,True)]
    P("%s: titik helm di dalam Base: %d"%(name,len(hit)))
    if hit:
        h=np.array(hit); P("   sebaran: x[%.1f,%.1f] y[%.1f,%.1f] z[%.1f,%.1f] (bantalan: x %.1f..%.1f, y %.1f..%.1f, z -8..0)"%(h[:,0].min(),h[:,0].max(),h[:,1].min(),h[:,1].max(),h[:,2].min(),h[:,2].max(),CX-23,CX+23,CY-5.5,CY+5.5))
    return len(hit)
inside_count(shell,"cangkang"); inside_count(susp,"suspensi")
sel=C[np.unique(shell)]
foot=(sel[:,0]>-8.5)&(sel[:,0]<63.1)&(sel[:,1]>-8.5)&(sel[:,1]<130.5)&~((abs(sel[:,0]-CX)<PAD_W if False else abs(sel[:,0]-CX)<23)&(abs(sel[:,1]-CY)<5.5))
P("jarak cangkang helm ke punggung casing (z=0) di luar bantalan: titik terdekat z=%.1f mm (positif = menembus ke casing, harus < 0)"%(sel[foot,2].max() if foot.any() else float('nan')))
# jarak lidah ke suspensi dan cangkang bagian dalam (lidah masuk helm)
tpts=np.array([[x,y,z] for x in (CX-14.5,CX,CX+14.5) for y in (CY-1.75,CY+1.75) for z in np.linspace(-33.3,-8,12)])
for nm,idx in (("cangkang",shell),("suspensi",susp)):
    pp=C[np.unique(idx)]
    dmin=min(np.min(np.linalg.norm(pp-q,axis=1)) for q in tpts)
    P("jarak titik terdekat lidah (kasar, vertex) ke %s: %.1f mm"%(nm,dmin))
ztip=-33.3; wall_in=PAD_BOT-SLOT_DEPTH_MM
P("dinding 15 mm: sisi dalam di z=%.1f, ujung lidah z=%.1f -> lidah menjulur %.1f mm ke dalam helm"%(wall_in,ztip,wall_in-ztip))
# ---- simpan perakitan
def mesh_of(F_,pts):
    return Mesh.Mesh([[tuple(pts[i]) for i in f] for f in F_])
nd=FreeCAD.newDocument("assy_pcb2_v10")
a2=FreeCAD.openDocument(W_+"perakitan/assembly_PCB2_v9_lidah-ujung.FCStd")
for o in a2.Objects:
    if o.Name=="Lidah_helm": f=nd.addObject("Part::Feature","Lidah_helm"); f.Shape=t2
    elif hasattr(o,"Shape") and not o.Shape.isNull() and o.Shape.Solids: f=nd.addObject("Part::Feature",o.Name); f.Shape=o.Shape.copy()
f=nd.addObject("Mesh::Feature","HELM_kuning_cangkang"); f.Mesh=mesh_of(shell,C)
f=nd.addObject("Mesh::Feature","HELM_kuning_suspensi"); f.Mesh=mesh_of(susp,C)
nd.recompute(); nd.saveAs(W_+"perakitan/assembly_PCB2_v10_helm-kuning.FCStd")
open(W_+"laporan/_tahap8_pcb2_helm_kuning_report.txt","w").write("\n".join(out))
