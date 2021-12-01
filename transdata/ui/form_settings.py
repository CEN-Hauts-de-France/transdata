#! python3  # noqa: E265

"""
    Plugin settings form.
"""

# standard
from pathlib import Path

# PyQGIS
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QWidget, QDialog


# ############################################################################
# ########## Globals ###############
# ##################################

FORM_CLASS, _ = uic.loadUiType(
    Path(__file__).parent / "{}.ui".format(Path(__file__).stem)
)

# ############################################################################
# ########## Classes ###############
# ##################################


class FormSettings(FORM_CLASS, QWidget):
    """Settings form."""

    def __init__(self, parent=None):
        """Constructor."""
        super().__init__(parent)

        self.setupUi(self)
        self.lbl_title.setText("Paramètres du plugin")

        self.btn_rech.clicked.connect(remplissList)

    def remplissList(self):
        """Remplissage de la liste"""
        self.lst_cibles.clear()
        queryFillList = QtSql.QSqlQuery(self.db)
        qFillList = u"SELECT codesitep, nomsitep FROM bd_site_cen.site_cen_hdf ORDER BY codesitep"
        ok = queryFillList.exec_(qFillList)
        while queryFillList.next():
            # print (query.value(1).toPyDate().strftime("%Y-%m-%d"))
            self.ui.cbx_listcible.addItem(
                str(query.value(0))
                + " / "
                + str(query.value(1))
               ,
                int(query.value(0)),
            )
        # 1er paramètre = ce qu'on affiche,
        # 2ème paramètre = ce qu'on garde en mémoire pour plus tard
        if not ok:
            QtWidgets.QMessageBox.warning(
                self, "Alerte", u"Requête remplissage liste cibles ratée"
            )
        self.ui.cbx_listcible.setCurrentIndex(0)