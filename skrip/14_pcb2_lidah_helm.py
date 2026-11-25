import FreeCAD, Import, Part
V=FreeCAD.Vector; M=FreeCAD.Matrix
W_="C:/Users/calvi/Favorites/Downloads/DESPRO_2/3d-Despro2/"
CX,CY=27.3,61.0                 # tengah lantai PCB2 (garis dinding lama, simetris)
PAD_W,PAD_L,PAD_T=46.0,20.0,8.0  # bantalan di bawah lantai: lebar x, panjang y (vertikal di helm), tebal z
POCK_D=6.0                       # kantong buntu untuk pangkal lidah, dalam
TW,TT,TL=30.0,3.5,31.3           # lebar pangkal, tebal, panjang lidah hasil crop
CLR=0.2                          # celah lem per sisi
out=[]
def P(*a):
    s=" ".join(str(x) for x in a); print(s); out.append(s)
def box(x0,y0,z0,x1,y1,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
src=FreeCAD.openDocument(W_+"casing/3D-pcb2_v7_tanpa-bolongan.FCStd")
base=src.getObject("Base_v7").Shape; lid=src.getObject("Tutup_v7_tertutup").Shape; lidp=src.getObject("Tutup_v7_cetak").Shape
P("Base v7: valid=%s bbox x[%.1f,%.1f] y[%.1f,%.1f] z[%.1f,%.1f]"%(base.isValid(),base.BoundBox.XMin,base.BoundBox.XMax,base.BoundBox.YMin,base.BoundBox.YMax,base.BoundBox.ZMin,base.BoundBox.ZMax))
pad=box(CX-PAD_W/2,CY-PAD_L/2,-PAD_T,CX+PAD_W/2,CY+PAD_L/2,0.0)
pocket=box(CX-TW/2-CLR,CY-TT/2-CLR,-PAD_T-0.1,CX+TW/2+CLR,CY+TT/2+CLR,-PAD_T+POCK_D)
b8=base.fuse(pad).cut(pocket)
P("bantalan %.0f x %.0f x %.0f mm di bawah lantai, kantong buntu %.1f x %.1f, dalam %.1f (sisa %.1f mm di atas kantong + lantai 2.5)"%(PAD_W,PAD_L,PAD_T,TW+2*CLR,TT+2*CLR,POCK_D,PAD_T-POCK_D))
P("Base v8: valid=%s vol %.0f -> %.0f"%(b8.isValid(),base.Volume,b8.Volume))
# lidah dari crop (x lebar +-16.5, y panjang 0..31.3 dengan ujung y=0, z tebal 0..3.5) -> lidah menembus slot ke arah -z, tebal sepanjang y (vertikal di helm)
d=FreeCAD.newDocument("l"); Import.insert(W_+"mekanik/helm/adaptor_slot/lidah_slot_ibew.step",d.Name)
tg=[]
for o in d.Objects:
    if o.TypeId=="Part::Feature" and o.Shape.Solids:
        s=o.Shape.copy(); s.Placement=o.getGlobalPlacement(); tg.append(s)
FreeCAD.closeDocument(d.Name)
tongue0=Part.makeCompound(tg); b0=tongue0.BoundBox
P("lidah crop: %.1f x %.1f x %.1f mm (x lebar, y panjang, z tebal)"%(b0.XLength,b0.YLength,b0.ZLength))
zbase=-(PAD_T-POCK_D)                     # pangkal lidah menempel ke atas kantong (z=-2.0)
m=M(1,0,0,CX, 0,0,-1,CY+b0.ZLength/2, 0,1,0,zbase-b0.YLength, 0,0,0,1)
tg2=[]
for s in tg:
    x=s.copy(); x.translate(V(-(b0.XMin+b0.XMax)/2,-b0.YMin,-b0.ZMin)); x.transformShape(m); tg2.append(x)
tongue=Part.makeCompound(tg2); tb=tongue.BoundBox
P("lidah terpasang: x[%.1f,%.1f] y[%.1f,%.1f] z[%.1f,%.1f]; menjulur %.1f mm di bawah bantalan (z=%.1f), ujung berduri di z=%.1f"%(tb.XMin,tb.XMax,tb.YMin,tb.YMax,tb.ZMin,tb.ZMax,-PAD_T-tb.ZMin,-PAD_T,tb.ZMin))
# pas di kantong? bagian lidah di dalam z -8..-2 tidak boleh menyentuh bantalan
inside=tongue.common(box(-50,-50,-PAD_T,100,200,zbase+0.01))
P("bagian lidah di dalam kantong: %.0f mm3; menabrak bantalan: %.3f mm3 (harus 0)"%(inside.Volume,inside.common(b8).Volume))
P("lidah x Base v8 total: %.3f mm3"%tongue.common(b8).Volume)
# lantai di atas kantong utuh (tidak ada lubang tembus)
bad=0;n=0
for dx in (-12,-6,0,6,12):
    for dy in (-1.5,0,1.5):
        for z in (0.3,1.2,2.2):
            n+=1
            if not b8.isInside(V(CX+dx,CY+dy,z),1e-6,True): bad+=1
P("lantai di atas kantong: titik kosong %d dari %d (harus 0)"%(bad,n))
# simpan
doc=FreeCAD.newDocument("pcb2_helm")
for nme,s in (("Base_v8",b8),("Tutup_v7_tertutup",lid),("Tutup_v7_cetak",lidp),("Lidah_terpasang",tongue),("Lidah_cetak",tongue0)):
    f=doc.addObject("Part::Feature",nme); f.Shape=s
doc.recompute(); doc.saveAs(W_+"casing/3D-pcb2_v8_helm-lidah.FCStd")
b8.exportStep(W_+"casing/PCB2_v8_Base.step"); b8.exportStl(W_+"casing/PCB2_v8_Base.stl")
a2=FreeCAD.openDocument(W_+"perakitan/assembly_PCB2_v7_tanpa-bolongan.FCStd")
nd=FreeCAD.newDocument("assy_pcb2_v8")
f=nd.addObject("Part::Feature","Base_v8"); f.Shape=b8
for o in a2.Objects:
    if o.Name=="Base_v7": continue
    if hasattr(o,"Shape") and o.Shape.Solids: f=nd.addObject("Part::Feature",o.Name); f.Shape=o.Shape.copy()
f=nd.addObject("Part::Feature","Lidah_helm"); f.Shape=tongue
nd.recompute(); nd.saveAs(W_+"perakitan/assembly_PCB2_v8_helm-lidah.FCStd")
open(W_+"laporan/_tahap5_helm_lidah_report.txt","w").write("\n".join(out))
