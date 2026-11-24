# Dipakai oleh _buka_*.py: membuka perakitan, menampilkan semua objek, dan mewarnai per bagian.
import FreeCAD, FreeCADGui
from PySide import QtCore

WARNA = [  # (awalan nama objek, (r,g,b), transparansi %)
    ("Base",(0.78,0.78,0.80),30), ("Tutup",(0.55,0.70,0.90),70), ("Baut",(0.9,0.1,0.1),0),
    ("EasyEDA",(0.05,0.45,0.20),0),
    ("U1_",(0.95,0.55,0.10),0),          # SuperMini
    ("U2_",(0.10,0.30,0.85),0),          # MT3608
    ("U3_",(0.15,0.15,0.18),0),          # DevKit
    ("U7_",(0.10,0.75,0.75),0),          # TP4056
    ("U8_",(0.65,0.25,0.75),0),          # GY-521
    ("U9_",(0.85,0.10,0.10),0),          # GPS
    ("U10",(0.95,0.85,0.10),0),          # header sensor air
    ("U6",(0.95,0.95,0.95),0),           # Ra-02
    ("BAT",(0.30,0.30,0.35),20),         # holder 18650
    ("SW",(0.95,0.95,0.95),0),
    ("KLIP",(1.0,0.45,0.0),0), ("Pin",(1.0,0.9,0.1),0),
]
def _warna(nama):
    for pre,c,t in WARNA:
        if nama.startswith(pre): return c,t
    return (0.20,0.20,0.20),0      # komponen kecil (R, C, Q, D, H)

def tampil(path):
    def kerja():
        d = FreeCAD.openDocument(path)
        FreeCAD.setActiveDocument(d.Name)
        for o in d.Objects:
            v = o.ViewObject
            if v is None: continue
            v.Visibility = True
            c, t = _warna(o.Name)
            try:
                v.ShapeColor = c; v.Transparency = t
            except Exception:
                pass
        FreeCADGui.ActiveDocument = FreeCADGui.getDocument(d.Name)
        FreeCADGui.SendMsgToActiveView("ViewFit")
        FreeCADGui.activeView().viewIsometric()
    QtCore.QTimer.singleShot(4000, kerja)
