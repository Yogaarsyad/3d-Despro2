# Jalankan lewat: FreeCAD.exe _buka_PCB2_v3.py  (membuka perakitan PCB2 v3 dan menampilkan semua objek)
import FreeCAD, FreeCADGui
from PySide import QtCore

def tampil():
    d = FreeCAD.openDocument(r"C:\Users\calvi\Favorites\Downloads\DESPRO_2\3d-Despro2\perakitan\assembly_PCB2_v3_casing-baru.FCStd")
    FreeCAD.setActiveDocument(d.Name)
    for o in d.Objects:
        v = o.ViewObject
        if v is None:
            continue
        v.Visibility = True
        if o.Name.startswith("Tutup"):
            v.Transparency = 70
        elif o.Name.startswith("Base"):
            v.Transparency = 30
    FreeCADGui.ActiveDocument = FreeCADGui.getDocument(d.Name)
    FreeCADGui.SendMsgToActiveView("ViewFit")
    FreeCADGui.activeView().viewIsometric()

QtCore.QTimer.singleShot(4000, tampil)
