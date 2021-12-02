#! python3  # noqa: E265

"""
    Plugin settings form.
"""

# standard
from pathlib import Path

# PyQGIS
from qgis.core import QgsProviderRegistry
from qgis.PyQt import QtSql, QtWidgets, uic
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

    DB_CONN_NAMES = ("bdcen", "bdcen_admin")
    DB_TYPES = ("postgres",)

    def __init__(self, parent=None):
        """Constructor."""
        super().__init__(parent)
        self.log = PlgLogger().log
        # initialisation de l'interface de la boite de dialogue
        self.setupUi(self)

        # remplissage des widgets
        self.renvoie_base_cible()

        # connexion des signaux
        self.btn_recherch.clicked.connect(self.remplissage_liste)

    def renvoie_base_cible(self):
        """Retourne la base de données cible."""
        for db_type in self.DB_TYPES:
            # retrouver les connections du type de base de données
            connections = (
                QgsProviderRegistry.instance()
                .providerMetadata(db_type)
                .connections(cached=False))

        if not len(connections):
            self.log(
                message="Aucune connection de type {} trouvée".format(db_type),
                log_level=1,
                push=True
            )
            return

        flag_connexion_reperee = False
        for connection_name in connections:

            self.cbb_database.addItem(
                connections.get(connection_name).icon(),
                connection_name,
                connections.get(connection_name),
            )

            if connection_name in self.DB_CONN_NAMES:
                flag_connexion_reperee = True
                self.cbb_database.setCurrentText(connection_name)

        if not flag_connexion_reperee:
            self.cbb_database.setEnabled(True)

    def remplissage_liste(self):
        """Remplissage de la liste"""
        if (
            self.cbx_typCible.currentData(self.cbx_typCible.currentIndex())
            == "Site CEN"
        ):
            self.lst_cibles.clear()
            queryFillList = QtSql.QSqlQuery(self.db)
            qFillList = u"SELECT codesitep, nomsitep FROM bd_site_cen.site_cen_hdf ORDER BY codesitep"
            ok = queryFillList.exec_(qFillList)
            while queryFillList.next():
                # print (query.value(1).toPyDate().strftime("%Y-%m-%d"))
                self.lst_cibles.addItem(
                    str(queryFillList.value(0)) + " / " + str(queryFillList.value(1))
                )
            if not ok:
                QtWidgets.QMessageBox.warning(
                    self, "Alerte", u"Requête remplissage liste cibles ratée"
                )
        else:
            self.lst_cibles.clear()
            self.lst_cibles.addItem("Raté!!! ;-p")
        self.lst_cibles.setCurrentRow(0)
