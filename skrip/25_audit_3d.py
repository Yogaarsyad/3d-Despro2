import FreeCAD, Part, time
W_="C:/Users/calvi/Favorites/Downloads/DESPRO_2/3d-Despro2/"
f=open(W_+"laporan/_audit_3d_report.txt","w")
def P(*a):
    s=" ".join(str(x) for x in a); f.write(s+"\n"); f.flush()
def bbhit(a,b,m=0.0):
    A,B=a.BoundBox,b.BoundBox
    return not (A.XMax+m<B.XMin or B.XMax+m<A.XMin or A.YMax+m<B.YMin or B.YMax+m<A.YMin or A.ZMax+m<B.ZMin or B.ZMax+m<A.ZMin)
def vol(a,b):
    try: return a.common(b).Volume
    except Exception as e: return -1.0
def audit(name,path,base_pre,lid_pre):
    t0=time.time()
    d=FreeCAD.openDocument(W_+path)
    base=lid=None; comps={}; skip=[]
    for o in d.Objects:
        if o.TypeId=="Mesh::Feature": skip.append(o.Name+" (mesh)"); continue
        if not hasattr(o,"Shape") or o.Shape.isNull(): continue
        s=o.Shape.copy(); s.Placement=o.getGlobalPlacement()
        if o.Name.startswith(base_pre): base=s
        elif o.Name.startswith(lid_pre): lid=s
        elif not s.Solids: skip.append(o.Name+" (tanpa solid)")
        else: comps[o.Name]=s
    P("=====",name,path)
    P("objek yang diperiksa: %d komponen; tidak bisa diperiksa: %s"%(len(comps),", ".join(skip) or "-"))
    P("daftar:",", ".join(sorted(comps)))
    P("Base: valid=%s solid=%d | Tutup: valid=%s solid=%d"%(base.isValid(),len(base.Solids),lid.isValid(),len(lid.Solids)))
    P("[1] Base x Tutup tumpang tindih: %.3f mm3"%vol(base,lid))
    P("[2] komponen menembus casing (> 0.05 mm3):")
    n=0
    for k,s in sorted(comps.items()):
        for cn,c in (("Base",base),("Tutup",lid)):
            if bbhit(s,c):
                v=vol(s,c)
                if v>0.05 or v<0:
                    cm=s.common(c).BoundBox if v>0 else None
                    P("    %s x %s: %.2f mm3 %s"%(k,cn,v,"di x[%.1f,%.1f] y[%.1f,%.1f] z[%.1f,%.1f]"%(cm.XMin,cm.XMax,cm.YMin,cm.YMax,cm.ZMin,cm.ZMax) if cm else "(gagal dihitung)")); n+=1
    if n==0: P("    tidak ada")
    P("[3] komponen saling tumpang tindih (> 0.5 mm3; model PCB EasyEDA dikecualikan):")
    ks=sorted(k for k in comps if not k.startswith("EasyEDA")); n=0
    for i,a in enumerate(ks):
        for b in ks[i+1:]:
            if bbhit(comps[a],comps[b]):
                v=vol(comps[a],comps[b])
                if v>0.5 or v<0: P("    %s x %s: %.2f mm3"%(a,b,v)); n+=1
    if n==0: P("    tidak ada")
    P("[4] jarak komponen ke casing di bawah 0.8 mm (tidak menembus):")
    n=0
    for k,s in sorted(comps.items()):
        if k.startswith(("Baut","Pin","EasyEDA","Lidah")): continue
        for cn,c in (("Base",base),("Tutup",lid)):
            if not bbhit(s,c,0.8): continue
            try: dist=s.distToShape(c)[0]
            except Exception: P("    %s -> %s: gagal dihitung"%(k,cn)); continue
            if dist<0.8: P("    %s -> %s: %.2f mm"%(k,cn,dist)); n+=1
    if n==0: P("    tidak ada")
    P("selesai %s dalam %.0f s"%(name,time.time()-t0))
    FreeCAD.closeDocument(d.Name)
audit("PCB1 (Vest) v10","perakitan/assembly_PCB1_v14_final.FCStd","Base","Tutup")
audit("PCB2 (Helmet) v17","perakitan/assembly_PCB2_v17_ibew-kunci-tengah.FCStd","Base","Tutup")
P("SELESAI")
