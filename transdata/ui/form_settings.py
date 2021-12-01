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

        # Connexion à la base de données
        self.db = QtSql.QSqlDatabase.addDatabase("QPSQL")
        # QPSQL = nom du pilote postgreSQL
        self.db.setHostName("192.168.1.12")
        self.db.setPort(5432)
        self.db.setDatabaseName("bdcenpicardie")
        self.db.setUserName("postgres")
        self.db.setPassword("burotec")
        ok = self.db.open()
        if not ok:
            QtWidgets.QMessageBox.warning(
                self, "Alerte", u"La connexion est échouée" + self.db.hostName())

        self.btn_recherch.clicked.connect(self.remplissList)

    def remplissList(self):
        """Remplissage de la liste"""
        self.lst_cibles.clear()
        queryFillList = QtSql.QSqlQuery(self.db)
        qFillList = u"SELECT codesitep, nomsitep FROM bd_site_cen.site_cen_hdf ORDER BY codesitep"
        ok = queryFillList.exec_(qFillList)
        while queryFillList.next():
            # print (query.value(1).toPyDate().strftime("%Y-%m-%d"))
            self.cbx_listcible.addItem(
                str(queryFillList.value(0))
                + " / "
                + str(queryFillList.value(1)),
                int(queryFillList.value(0)),
            )
        # 1er paramètre = ce qu'on affiche,
        # 2ème paramètre = ce qu'on garde en mémoire pour plus tard
        if not ok:
            QtWidgets.QMessageBox.warning(
                self, "Alerte", u"Requête remplissage liste cibles ratée"
            )
        self.cbx_listcible.setCurrentIndex(0)