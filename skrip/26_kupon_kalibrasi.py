import FreeCAD, Part, os
V=FreeCAD.Vector
W_="C:/Users/calvi/Favorites/Downloads/DESPRO_2/3d-Despro2/"
K=W_+"casing/kupon/"
os.makedirs(K,exist_ok=True)
def box(x0,y0,z0,x1,y1,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def cyl(x,y,z0,z1,d): return Part.makeCylinder(d/2,z1-z0,V(x,y,z0))
def dots(sh,x,y,z,n):
    for m in range(n): sh=sh.fuse(cyl(x+(m-(n-1)/2.0)*3.0,y,z-0.01,z+0.6,2.0))
    return sh
def save(name,sh):
    b=sh.BoundBox
    print("%s valid=%s solid=%d ukuran %.1f x %.1f x %.1f"%(name,sh.isValid(),len(sh.Solids),b.XLength,b.YLength,b.ZLength))
    sh.exportStl(K+name+".stl")
# 1) ukuran: siku 100 x 100 mm (cek penyusutan X dan Y pakai penggaris)
s=box(0,0,0,100,8,2).fuse(box(0,0,0,8,100,2))
for t in (25,50,75):                       # takik tiap 25 mm
    s=s.cut(box(t-0.3,6,-1,t+0.3,9,3)).cut(box(6,t-0.3,-1,9,t+0.3,3))
save("Kal_1_ukuran_100mm",s)
# 2) lubang: baris A pilot sekrup, baris B lolos sekrup, baris C tempat kepala sekrup. 1/2/3 titik = kecil/pas/besar
s=box(0,0,0,54,50,8)
for i,x in enumerate((9,27,45)):
    s=s.cut(cyl(x,8,-1,9,(2.3,2.5,2.7)[i]))
    s=s.cut(cyl(x,24,-1,9,(3.2,3.4,3.6)[i]))
    s=s.cut(cyl(x,38,-1,9,3.4)).cut(cyl(x,38,8-1.4,9,(5.8,6.0,6.2)[i]))
    s=dots(s,x,46.5,8,i+1)
save("Kal_2_lubang_sekrup",s)
# 3) slot helm tiruan: celah tembus 30 mm panjang, dalam 14 mm; lebar 3.3 / 3.5 / 3.7 (1/2/3 titik)
parts=None
for i,w in enumerate((3.3,3.5,3.7)):
    b=box(0,0,0,38,12,14).cut(box(4,6-w/2,-1,34,6+w/2,15))
    b=dots(b,19,1.8,14,i+1); b.translate(V(0,i*16,0))
    save("Kal_3_slot_helm_%.1f"%w,b)
# 4) alur O-ring dan lekukan membran: alur 1.5 dalam, lebar 2.4 / 2.6 / 2.8 (1/2/3 titik) + lekukan d12 x 1.0
s=box(0,0,0,62,40,4)
for i,w in enumerate((2.4,2.6,2.8)):
    y=7+i*9
    s=s.cut(box(4,y-w/2,4-1.5,46,y+w/2,5))
    for m in range(i+1): s=s.fuse(cyl(49+m*2.6,y,3.99,4.6,2.0))
s=s.cut(cyl(52,32,4-1.0,5,12.0))
save("Kal_4_alur_oring_membran",s)
