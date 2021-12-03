#! python3  # noqa: E265

"""
    Plugin settings form.
"""

# standard
from pathlib import Path

# PyQGIS
from qgis.core import QgsProviderRegistry, QgsAbstractDatabaseProviderConnection
from qgis.PyQt import QtSql, uic
from qgis.PyQt.QtWidgets import QWidget
from qgis.utils import pluginDirectory

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

    DB_CONN_NAMES = ("bdcen", "bdcen_admin", "CEN Picardie User - pgservice")
    DB_TYPES = ("postgres",)

    def __init__(self, parent=None):
        """Constructor."""
        super().__init__(parent)
        self.log = PlgLogger().log
        self.plg_folder = pluginDirectory("transdata")
        # initialisation de l'interface de la boite de dialogue
        self.setupUi(self)

        # remplissage des widgets
        self.renvoie_base_cible()

        # connexion des signaux
        self.btn_recherch.clicked.connect(self.remplissage_liste)

    def recup_selected_features(self, selected_features: list):
        self.selected_features = selected_features
        self.show()

    def renvoie_base_cible(self):
        """Retourne la base de données cible.

        Liste les connexions des types de bases de données définis en attribut de classe.
        Remplit la liste déroulante.
        Vérifie que la connexion par défaut est bien présente :
            - Si oui, bloque la liste déroulante sur cette connexion.
            - Sinon, laisse le choix à l'utilisateur de sélectionner une connexion."""
        for db_type in self.DB_TYPES:
            # retrouver les connections du type de base de données
            connections = (
                QgsProviderRegistry.instance()
                .providerMetadata(db_type)
                .connections(cached=False)
            )

        if not len(connections):
            self.log(
                message="Aucune connexion de type {} trouvée".format(db_type),
                log_level=1,
                push=True,
            )  # Run the dialog event loop
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

    def remplissage_liste_old(self):
        """Remplissage de la liste"""
        with open(Path(self.plg_folder) / "sql/recup_sites.sql", "r") as f:
            sql = f.read()

        result = self.connection.executeSql(sql)
        print(self.connection)
        print(result)

        if (
            self.cbx_typCible.currentData(self.cbx_typCible.currentIndex())
            == "Site CEN"
        ):
            self.lst_cibles.clear()

            # queryFillList = QtSql.QSqlQuery(self.db)
            # qFillList = "SELECT codesitep, nomsitep FROM bd_site_cen.site_cen_hdf ORDER BY codesitep"
            # ok = queryFillList.exec_(qFillList)
            # while queryFillList.next():
            #     # print (query.value(1).with open(Path(self.plg_folder) / "sql/recup_sites.sql", "r") as f:
            sql = f.read()
        # if not ok:
        #     self.log(
        #         message="Requête remplissage liste cibles ratée",
        #         log_level=1,
        #         push=True,
        #     )
        else:
            self.lst_cibles.clear()
            self.lst_cibles.addItem("Raté!!! ;-p")
        self.lst_cibles.setCurrentRow(0)

    def remplissage_liste(self):
        """Récupérer la couche cible choisie par l'utilisateur.
        On récupère la connexion affichée dans la liste déroulante.
        On lance la requête qui va récupérer des lignes dans la vue "view_transdata" et la table "secteurs" (dans le schéma bdfauneflore)
        Remplissage de la liste de choix en fonction du choix de l'utilisateur
        Filtre sur l'emprise du canevas"""

        table_cible = self.cbx_typCible.currentText()
        connexion = self.cbb_database.itemData(self.cbb_database.currentIndex())
        req = "SELECT PostGIS_Version();"
        result = connexion.executeSql(req)
        self.log(
                message=result,
                log_level=4,
            )
