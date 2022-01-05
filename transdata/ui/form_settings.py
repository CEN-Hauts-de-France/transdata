#! python3  # noqa: E265

"""
    Plugin settings form.
"""

# standard
from pathlib import Path

#Python
import psycopg2

# PyQGIS
from qgis.gui import QgisInterface
from qgis.core import QgsProviderRegistry, QgsFeatureRequest, QgsDataSourceUri, QgsVectorLayer, QgsProject
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

    # Initialisations
    DB_CONN_NAMES = ("bdcen", "bdcen_admin", "Serveur carto Linux - authdb")
    DB_TYPES = ("postgres",)
    OPTION_TABLE_NAMES = ("Secteur", "Site CEN")

    def __init__(self, iface: QgisInterface, parent=None):
        """Constructor."""
        super().__init__(parent)
        # Utilisation du module log_handler pour envoyer ds messages aux utilisateurs
        self.log = PlgLogger().log
        # Instanciation du chemin vers le dossier du plugion sur le PC
        self.plg_folder = pluginDirectory("transdata")
        # Initialisation de l'interface de la boite de dialogue
        self.setupUi(self)
        """ 
        :param iface: An interface instance that will be passed to this \
        class which provides the hook by which you can manipulate the QGIS \
        application at run time.
        :type iface: QgsInterface
        """
        self.iface = iface

        # remplissage des widgets
        #    "cbx_database" (choix de la connexion à la base)
        self.renvoie_base_cible()
        #    cbx_table_cible (liste de choix pour que l'utilisateur sélctionne l'entité cible)
        self.cbx_table_cible.addItems(self.OPTION_TABLE_NAMES)
        #    lbl_nbObjSel_value (label indiquant le nombre de points sélectionnés)
        self.lbl_nbObjSel_value.setText(str(self.iface.activeLayer().selectedFeatureCount()))

        # connexion des signaux
        self.btn_recherch.clicked.connect(self.remplissage_liste)
        self.btn_exec.clicked.connect(self.btn_executer_click)

    def recup_selected_features(self, selected_features: list):
        # Récupération de la liste des entités sélectionnées depuis main_plugin.py
        self.selected_features = selected_features
        self.show()

    def recup_selected_mesid(self, Mesid: str):
        # Récupération des ID des entités sélectionnées depuis main_plugin.py
        self.Mesid = Mesid
               
    def recup_active_layer_name(self, Layer_name:str):
        # Recupération du nom de la couche active depuis main_plugin.py
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
        # Si aucune connexion trouvée...
        if not len(connections):
            self.log(
                message="Aucune connexion de type {} trouvée".format(db_type),
                log_level=1,
                push=True,
            )  # Run the dialog event loop
            return

        flag_connexion_reperee = False
        # Ajout des connexions trouvées dans le profil de QGIS à la combobox de choix
        for connection_name in connections:

            self.cbx_database.addItem(
                connections.get(connection_name).icon(),
                connection_name,
                connections.get(connection_name),
            )

            # Si le nom d'une des connexions repéres se trouve dans la liste DB_CONN_NAMES, alors
            # la combobox est bloquée dessus
            if connection_name in self.DB_CONN_NAMES:
                flag_connexion_reperee = True
                self.cbx_database.setCurrentText(connection_name)
        # Si aucune connexion n'est listée dans DB_CONN_NAMES, on laisse l'utilisateur en choisir une.
        if not flag_connexion_reperee:
            self.cbx_database.setEnabled(True)

    def remplissage_liste(self):
        """Récupérer la couche cible choisie par l'utilisateur ("view_transdata" ou "secteur").
        On récupère la connexion affichée dans la liste déroulante.
        On affiche la couche choisie, puis on la filtre géoégraphiquement en fonction du canevas de QGIS.
        Remplissage de la liste de choix par les items filtrés de la couche affichée
        """

        self.lst_cibles.clear()

        # Récupération de l'étendue du canevas
        extent = self.iface.mapCanvas().extent()
        request = QgsFeatureRequest()
        request.setFilterRect(extent)

        # Définition des variables "nom de la table et "clé primaire de la table" 
        # en fonction du choix de la table cible par l'utilisateur.
        table_cible = self.cbx_table_cible.currentText()
        if table_cible == 'Secteur':
            tabcibname = 'secteur'
            tabcibpkey = "objectid"
            tabcibcol1 = 'secteur_id'
            tabcibcol2 = 'lieu_dit'
        elif table_cible == 'Site CEN':
            tabcibname = 'view_transdata'
            tabcibpkey = "row_number"
            tabcibcol1 = 'identifiant'
            tabcibcol2 = 'nom'
        connexion = self.cbx_database.itemData(self.cbx_database.currentIndex())



        #QgsDataSourceUri() permet d'aller chercher une table d'une base de données PostGis (cf. PyQGIS cookbook)
        self.uri = QgsDataSourceUri()
        # setConnection configure l'adresse du serveur (hôte), le port, le nom de la base de données, 
        # le SSL ou non, l'utilisateur et le mot de passe (ou, comme c'est le cas ici, le authConfigId).
        self.uri.setConnection("127.0.0.1", "5435", "dev_bdcenpicardie", '', '', False,'5ba2lc0')   #5ba2lc0 #dme471m
        # setDataSource configure le schéma, la table postgis, la colonne géométrique, une requête au format texte et 
        # la clé primaire de la couche à importer dans QGIS
        self.uri.setDataSource("bdfauneflore", tabcibname, "geom", None , tabcibpkey)    
        # Création de la couche ctrs_cible dans QGIS
        self.ctrs_cibles=QgsVectorLayer(self.uri.uri(), "contours_cibles", "postgres")
        # Appel de la table des matières de QGIS dans la variable root
        root = QgsProject.instance().layerTreeRoot()
        # Création d'une couche temporaire à partir de ctrs_cibles, en filtrant sur l'étendue du canevas ("extent")
        # C'est ce que fait "materialize" : cela matérialise la requête dans une couche de type "memory".
        self.ctrs_cible_canvas = self.ctrs_cibles.materialize(QgsFeatureRequest().setFilterRect(extent))
        # S'il y a quelque-chose dans ctrs_cible_canvas, alors on l'ajoute au projet et on l'affiche en haut de la table des matières.
        if self.ctrs_cible_canvas.featureCount()>0:
           QgsProject.instance().addMapLayer(self.ctrs_cible_canvas, False)
           root.insertLayer(0, self.ctrs_cible_canvas)
        # Récupération des attributs de la couche filtrée géographiquement <-(request) et insertion dans la liste de choix
        for feature in self.ctrs_cibles.getFeatures(request):
            #attrs=feature.attributes()
            self.lst_cibles.addItem("{} ({})".format(feature[tabcibcol1], feature[tabcibcol2]))
        tabcibname = tabcibpkey = tabcibcol1 = tabcibcol2 = ''


    def btn_executer_click(self):
        print('Mesid = '+self.Mesid)
        print('Macouche = '+self.Layer_name)


    # Le code commenté ci-dessous est pour mémoire : en fonction du choix de l'utilisateur, on utilise une requête SQL différente.  
    # Celles-ci sont stockées dans des fichiers SQL.
    # Le fichier est lu, et 2 colonnes du résultat de la requête sont utilisés pour remplir la liste de choix.
    # Je n'utilise plus ce code car je suis obligé d'importer les couches dans QGIS pour pouvoir les filtrer géogréphiquement.
    # -> plus besoin des requêtes, stockées ou non dans un fichier.

    # if table_cible == "Secteur":
    #     #sql_path = "sql/recup_secteur.sql"
    # elif table_cible == "Site CEN":
    #     #sql_path = "sql/recup_site.sql"
    # else:
    #     self.log(message="Table inconnue", log_level=1, push=True)

    # with open(Path(self.plg_folder) / sql_path, "r") as f:
    #     sql = f.read()
    #     print(sql)

    # result = connexion.executeSql(sql)
    # for ligne in result:
    #     self.lst_cibles.addItem("{} ({})".format(ligne[0], ligne[1]))


