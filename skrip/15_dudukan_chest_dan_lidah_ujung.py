import FreeCAD, Import, Part, Mesh
V=FreeCAD.Vector; M=FreeCAD.Matrix
W_="C:/Users/calvi/Favorites/Downloads/DESPRO_2/3d-Despro2/"
out=[]
def P(*a):
    s=" ".join(str(x) for x in a); print(s); out.append(s)
def box(x0,y0,z0,x1,y1,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def objs(doc): return [(o.Name,o.Shape.copy()) for o in doc.Objects if hasattr(o,"Shape") and not o.Shape.isNull() and o.Shape.Solids]
# ===== PCB1: dudukan klip chest di punggung =====
PAD_T,POCK_D,MARG,CLR=3.0,1.5,4.0,0.3
s1=FreeCAD.openDocument(W_+"casing/3d-pcb1_v8_tanpa-bolongan.FCStd")
a1=FreeCAD.openDocument(W_+"perakitan/assembly_PCB1_v12_tanpa-bolongan.FCStd")
clip=a1.getObject("KLIP_CHEST_SlimeVR").Mesh; cb=clip.BoundBox
P("klip chest x[%.1f,%.1f] y[%.1f,%.1f] z[%.1f,%.1f]"%(cb.XMin,cb.XMax,cb.YMin,cb.YMax,cb.ZMin,cb.ZMax))
# isi penampang klip di z=-1 (bidang yang menempel): luas vs kotak bbox
try:
    cs=clip.crossSections([((0,0,-1.0),(0,0,1))],0.01)[0]
    import math
    A=0
    for w in cs:
        if len(w)>3:
            A+=abs(sum(w[i].x*w[(i+1)%len(w)].y-w[(i+1)%len(w)].x*w[i].y for i in range(len(w))))/2
    P("penampang klip di z=-1: %d kontur, luas total (kasar, tanpa pengurangan lubang) %.0f mm2 dari kotak %.0f mm2"%(len(cs),A,(cb.XMax-cb.XMin)*(cb.YMax-cb.YMin)))
except Exception as e: P("penampang klip gagal:",e)
base1=s1.getObject("Base_v8").Shape
px0,px1=cb.XMin-CLR-MARG,cb.XMax+CLR+MARG; py0,py1=cb.YMin-CLR-MARG,cb.YMax+CLR+MARG
pad=box(px0,py0,-PAD_T,px1,py1,0.0)
pocket=box(cb.XMin-CLR,cb.YMin-CLR,-PAD_T-0.1,cb.XMax+CLR,cb.YMax+CLR,-PAD_T+POCK_D)
b9=base1.fuse(pad).cut(pocket)
P("PCB1 Base v9: valid=%s vol %.0f -> %.0f; bantalan x[%.1f,%.1f] y[%.1f,%.1f] z[-%.1f,0], kantong %.1f x %.1f dalam %.1f"%(b9.isValid(),base1.Volume,b9.Volume,px0,px1,py0,py1,PAD_T,cb.XLength+2*CLR,cb.YLength+2*CLR,POCK_D))
# lantai di atas kantong utuh?
bad=n=0
for x in range(int(cb.XMin)+3,int(cb.XMax)-2,8):
    for y in range(int(cb.YMin)+3,int(cb.YMax)-2,8):
        for z in (0.3,1.2,2.2):
            n+=1
            if not b9.isInside(V(x,y,z),1e-6,True): bad+=1
P("lantai di atas kantong PCB1: titik kosong %d dari %d (harus 0, selain bagian dasar yang memang kosong)"%(bad,n))
clip9=Mesh.Mesh(clip); clip9.translate(0,0,-POCK_D)
P("klip digeser turun %.1f mm: bagian atas klip %.1f mm masuk kantong, klip z[%.1f,%.1f]"%(POCK_D,POCK_D,cb.ZMin-POCK_D,cb.ZMax-POCK_D))
doc=FreeCAD.newDocument("pcb1_dudukan")
for nme,s in objs(s1):
    f=doc.addObject("Part::Feature","Base_v9" if nme=="Base_v8" else nme); f.Shape=b9 if nme=="Base_v8" else s
doc.recompute(); doc.saveAs(W_+"casing/3d-pcb1_v9_dudukan-chest.FCStd")
b9.exportStep(W_+"casing/PCB1_v9_Base.step"); b9.exportStl(W_+"casing/PCB1_v9_Base.stl")
nd=FreeCAD.newDocument("assy_pcb1_v13")
f=nd.addObject("Part::Feature","Base_v9"); f.Shape=b9
for o in a1.Objects:
    if o.Name=="Base_v8": continue
    if o.Name=="KLIP_CHEST_SlimeVR": f=nd.addObject("Mesh::Feature",o.Name); f.Mesh=clip9
    elif hasattr(o,"Shape") and not o.Shape.isNull() and o.Shape.Solids: f=nd.addObject("Part::Feature",o.Name); f.Shape=o.Shape.copy()
    elif o.TypeId=="Mesh::Feature": f=nd.addObject("Mesh::Feature",o.Name); f.Mesh=o.Mesh
nd.recompute(); nd.saveAs(W_+"perakitan/assembly_PCB1_v13_dudukan-chest.FCStd")
# ===== PCB2: lidah di ujung sisi panjang (ujung atas, y besar) =====
CX,CY=27.3,118.0
PAD_W,PAD_L,PAD_T2=46.0,20.0,8.0; POCK2=6.0; TW,TT,CLR2=30.0,3.5,0.2
s2=FreeCAD.openDocument(W_+"casing/3D-pcb2_v7_tanpa-bolongan.FCStd")
base2=s2.getObject("Base_v7").Shape
P("PCB2 Base v7 bbox y[%.1f,%.1f]"%(base2.BoundBox.YMin,base2.BoundBox.YMax))
pad2=box(CX-PAD_W/2,CY-PAD_L/2,-PAD_T2,CX+PAD_W/2,CY+PAD_L/2,0.0)
pocket2=box(CX-TW/2-CLR2,CY-TT/2-CLR2,-PAD_T2-0.1,CX+TW/2+CLR2,CY+TT/2+CLR2,-PAD_T2+POCK2)
b9b=base2.fuse(pad2).cut(pocket2)
P("PCB2 Base v9: valid=%s vol %.0f -> %.0f; bantalan y[%.1f,%.1f] (lantai luar sampai y=%.1f)"%(b9b.isValid(),base2.Volume,b9b.Volume,CY-PAD_L/2,CY+PAD_L/2,base2.BoundBox.YMax))
d=FreeCAD.newDocument("l"); Import.insert(W_+"mekanik/helm/adaptor_slot/lidah_slot_ibew.step",d.Name)
tg=[]
for o in d.Objects:
    if o.TypeId=="Part::Feature" and o.Shape.Solids:
        s=o.Shape.copy(); s.Placement=o.getGlobalPlacement(); tg.append(s)
FreeCAD.closeDocument(d.Name)
t0=Part.makeCompound(tg); b0=t0.BoundBox
zbase=-(PAD_T2-POCK2)
m=M(1,0,0,CX, 0,0,-1,CY+b0.ZLength/2, 0,1,0,zbase-b0.YLength, 0,0,0,1)
tg2=[]
for s in tg:
    x=s.copy(); x.translate(V(-(b0.XMin+b0.XMax)/2,-b0.YMin,-b0.ZMin)); x.transformShape(m); tg2.append(x)
tongue=Part.makeCompound(tg2); tb=tongue.BoundBox
P("lidah terpasang x[%.1f,%.1f] y[%.1f,%.1f] z[%.1f,%.1f]"%(tb.XMin,tb.XMax,tb.YMin,tb.YMax,tb.ZMin,tb.ZMax))
P("lidah x Base v9: %.3f mm3 (harus 0)"%tongue.common(b9b).Volume)
bad=n=0
for dx in (-12,-6,0,6,12):
    for dy in (-1.5,0,1.5):
        for z in (0.3,1.2,2.2):
            n+=1
            if not b9b.isInside(V(CX+dx,CY+dy,z),1e-6,True): bad+=1
P("lantai di atas kantong PCB2: titik kosong %d dari %d (harus 0)"%(bad,n))
doc=FreeCAD.newDocument("pcb2_ujung")
for nme,s in objs(s2):
    f=doc.addObject("Part::Feature","Base_v9" if nme=="Base_v7" else nme); f.Shape=b9b if nme=="Base_v7" else s
f=doc.addObject("Part::Feature","Lidah_terpasang"); f.Shape=tongue
doc.recompute(); doc.saveAs(W_+"casing/3D-pcb2_v9_lidah-ujung.FCStd")
b9b.exportStep(W_+"casing/PCB2_v9_Base.step"); b9b.exportStl(W_+"casing/PCB2_v9_Base.stl")
a2=FreeCAD.openDocument(W_+"perakitan/assembly_PCB2_v7_tanpa-bolongan.FCStd")
nd=FreeCAD.newDocument("assy_pcb2_v9")
f=nd.addObject("Part::Feature","Base_v9"); f.Shape=b9b
for o in a2.Objects:
    if o.Name=="Base_v7": continue
    if hasattr(o,"Shape") and not o.Shape.isNull() and o.Shape.Solids: f=nd.addObject("Part::Feature",o.Name); f.Shape=o.Shape.copy()
f=nd.addObject("Part::Feature","Lidah_helm"); f.Shape=tongue
nd.recompute(); nd.saveAs(W_+"perakitan/assembly_PCB2_v9_lidah-ujung.FCStd")
open(W_+"laporan/_tahap7_dudukan_chest_lidah_ujung_report.txt","w").write("\n".join(out))
