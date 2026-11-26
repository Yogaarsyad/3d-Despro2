# Uji aliran air di komputer (voxel) untuk PCB1 v10. Pakai python biasa (numpy + scipy), baca STL Base dan Tutup posisi terpasang.
# Argumen: base.stl tutup.stl. Ini hanya memeriksa "tidak ada lubang yang terlupa" pada grid, BUKAN uji air.
import sys, numpy as np, struct, re
from scipy import ndimage
def stl(f):
    b=open(f,'rb').read()
    if b[:5]==b'solid' and b'facet' in b[:600]: return np.array(re.findall(rb'vertex\s+(\S+)\s+(\S+)\s+(\S+)',b),float).reshape(-1,3,3)
    n=struct.unpack('<I',b[80:84])[0]; a=np.frombuffer(b[84:84+50*n],dtype=np.dtype([('n','<3f4'),('v','<9f4'),('a','<u2')])); return a['v'].reshape(-1,3,3).astype(float)
EXT,Wd,Dp,H,PLATE,REC=9.5,126.9,114.2,34.0,3.0,1.0
ST=0.75
xs=np.arange(-EXT-3,Wd+EXT+3,ST)+0.013; ys=np.arange(-EXT-3,Dp+EXT+3,ST)+0.017; zs=np.arange(-2.0,H+PLATE+3,ST)+0.011
def vox(t):
    hits=[[[] for _ in ys] for _ in xs]
    for a,b,c in t:
        mn=np.minimum(np.minimum(a,b),c); mx=np.maximum(np.maximum(a,b),c)
        i0,i1=np.searchsorted(xs,mn[0]),np.searchsorted(xs,mx[0]); j0,j1=np.searchsorted(ys,mn[1]),np.searchsorted(ys,mx[1])
        if i1<=i0 or j1<=j0: continue
        den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(den)<1e-12: continue
        X,Y=np.meshgrid(xs[i0:i1],ys[j0:j1],indexing='ij')
        l1=((b[1]-c[1])*(X-c[0])+(c[0]-b[0])*(Y-c[1]))/den; l2=((c[1]-a[1])*(X-c[0])+(a[0]-c[0])*(Y-c[1]))/den; l3=1-l1-l2
        ins=(l1>=0)&(l2>=0)&(l3>=0)
        Z=l1*a[2]+l2*b[2]+l3*c[2]
        for i,j in zip(*np.nonzero(ins)): hits[i0+i][j0+j].append(Z[i,j])
    occ=np.zeros((len(xs),len(ys),len(zs)),bool); odd=0
    for i in range(len(xs)):
        for j in range(len(ys)):
            h=sorted(hits[i][j])
            if len(h)%2: odd+=1
            for k in range(0,len(h)-1,2): occ[i,j,(zs>=h[k])&(zs<=h[k+1])]=True
    return occ,odd
bo,o1=vox(stl(sys.argv[1])); lo,o2=vox(stl(sys.argv[2])); solid=bo|lo
print("grid %.2f mm, %d x %d x %d sel; kolom dengan jumlah potong ganjil: base %d, tutup %d (harus 0)"%(ST,len(xs),len(ys),len(zs),o1,o2))
X,Y,Z=np.meshgrid(xs,ys,zs,indexing='ij')
sw=[(77.49,95.96),(97.49,95.96)]
plug=np.zeros_like(solid)
for x,y in sw:
    r2=(X-x)**2+(Y-y)**2
    plug|=(r2<=2.4**2)&(Z>=19.0)&(Z<=H+PLATE+0.9); plug|=(r2<=6.1**2)&(Z>=H+PLATE-REC-0.1)&(Z<=H+PLATE+0.9)
seed=(np.argmin(abs(xs-63.45)),np.argmin(abs(ys-57.1)),np.argmin(abs(zs-20.0)))
for label,s in (("apa adanya",solid),("kedua tombol disumbat",solid|plug)):
    lab,_=ndimage.label(~s); out_id=lab[0,0,0]; in_id=lab[seed]
    print("%s: titik tengah rongga kosong=%s; air dari luar sampai ke rongga dalam = %s (volume rongga terhubung %.0f cm3)"%(label,bool(in_id),bool(in_id and in_id==out_id),(lab==in_id).sum()*ST**3/1000))
