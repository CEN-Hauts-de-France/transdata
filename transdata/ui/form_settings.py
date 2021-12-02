#! python3  # noqa: E265

"""
    Plugin settings form.
"""

# standard
from pathlib import Path

# PyQGIS
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets, QtSql
from qgis.PyQt.QtWidgets import QWidget

# Plugin package
from transdata.utils.log_handler import PlgLogger

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
        self.log = PlgLogger().log
        # initialisation de l'interface de la boite de dialogue
        self.setupUi(self)

        self.setupUi(self)
        self.lbl_title.setText("Paramètres du plugin")

        # Connexion à la base de données

        
        ok = self.db.open()
        if not ok:
            QtWidgets.QMessageBox.warning(
                self, "Alerte", u"La connexion est échouée" + self.db.hostName())

        self.btn_recherch.clicked.connect(self.remplissList)

    def remplissList(self):
        """Remplissage de la liste"""
        if self.cbx_typCible.currentData(self.cbx_typCible.currentIndex()) == 'Site CEN':
            self.lst_cibles.clear()
            queryFillList = QtSql.QSqlQuery(self.db)
            qFillList = u"SELECT codesitep, nomsitep FROM bd_site_cen.site_cen_hdf ORDER BY codesitep"
            ok = queryFillList.exec_(qFillList)
            while queryFillList.next():
                # print (query.value(1).toPyDate().strftime("%Y-%m-%d"))
               self.lst_cibles.addItem(
                    str(queryFillList.value(0))
                    + " / "
                    + str(queryFillList.value(1))
                )
            if not ok:
                QtWidgets.QMessageBox.warning(
                    self, "Alerte", u"Requête remplissage liste cibles ratée"
                )
        else:
            self.lst_cibles.clear()
            self.lst_cibles.addItem('Raté!!! ;-p')
        self.lst_cibles.setCurrentRow(0)