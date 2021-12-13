#! python3  # noqa: E265

"""
    Plugin settings form.
"""

# standard
from pathlib import Path

# PyQGIS
from qgis.core import QgsProviderRegistry
from qgis.PyQt import uic
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
    OPTION_TABLE_NAMES = ("Secteur", "Site CEN")

    def __init__(self, parent=None):
        """Constructor."""
        super().__init__(parent)
        self.log = PlgLogger().log
        self.plg_folder = pluginDirectory("transdata")
        # initialisation de l'interface de la boite de dialogue
        self.setupUi(self)

        # remplissage des widgets
            # "cbx_database" (choix de la connexion à la base)
        self.renvoie_base_cible()
            # cbx_table_cible (liste de choix pour que l'utilisateur sélctionne l'entité cible)
        self.cbx_table_cible.addItems(self.OPTION_TABLE_NAMES)
            # lbl_nbObjSel_value (label indiquant le niombre de points sélectionnés)
        self.lbl_nbObjSel_value.setText(self.iface.activeLayer().selectedFeatureCount())

        # connexion des signaux
        self.btn_recherch.clicked.connect(self.remplissage_liste)
        self.btn_exec.clicked.connect(self.btn_executer_click)

    def recup_selected_features(self, selected_features: list):
        self.selected_features = selected_features
        self.show()

    def recup_selected_mesid(self, Mesid: str):
        self.Mesid = Mesid
               
    def recup_active_layer_name(self, Layer_name:str):
        self.Layer_name = Layer_name

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

            self.cbx_database.addItem(
                connections.get(connection_name).icon(),
                connection_name,
                connections.get(connection_name),
            )

            if connection_name in self.DB_CONN_NAMES:
                flag_connexion_reperee = True
                self.cbx_database.setCurrentText(connection_name)

        if not flag_connexion_reperee:
            self.cbx_database.setEnabled(True)

    def remplissage_liste(self):
        """Récupérer la couche cible choisie par l'utilisateur.
        On récupère la connexion affichée dans la liste déroulante.
        On lance la requête qui va récupérer des lignes dans la vue "view_transdata" et la table "secteurs" (dans le schéma bdfauneflore)
        Remplissage de la liste de choix en fonction du choix de l'utilisateur
        Filtre sur l'emprise du canevas"""

        self.lst_cibles.clear()

        table_cible = self.cbx_table_cible.currentText()
        connexion = self.cbx_database.itemData(self.cbx_database.currentIndex())
        if table_cible == "Secteur":
            sql_path = "sql/recup_secteur.sql"
        elif table_cible == "Site CEN":
            sql_path = "sql/recup_site.sql"
        else:
            self.log(message="Table inconnue", log_level=1, push=True)

        with open(Path(self.plg_folder) / sql_path, "r") as f:
            sql = f.read()
            print(sql)

        result = connexion.executeSql(sql)
        for ligne in result:
            self.lst_cibles.addItem("{} ({})".format(ligne[0], ligne[1]))



    def btn_executer_click(self):
        print('Mesid = '+self.Mesid)
        print('Macouche = '+self.Layer_name)
