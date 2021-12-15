#! python3  # noqa: E265

# PyQGIS
from qgis.gui import QgisInterface
from qgis.core import QgsFeatureRequest
from qgis.PyQt.QtWidgets import QAction

# Plugin package
from transdata.ui.form_settings import FormSettings
from transdata.utils.log_handler import PlgLogger

malist=['sig_flore_point','sig_faune_point']

class CenTransdataPlugin:
    def __init__(self, iface: QgisInterface):
        """Constructor.

        :param iface: An interface instance that will be passed to this \
        class which provides the hook by which you can manipulate the QGIS \
        application at run time.
        :type iface: QgsInterface
        """
        self.iface = iface
        self.log = PlgLogger().log


    def initGui(self):
        self.action = QAction("Go!", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action

    def run(self):
        # show the dialog

        # check s'il y a une couche active
        active_layer = self.iface.activeLayer()
        if not active_layer:
            self.log(message="Aucune couche sélectionnée", log_level=2, push=True)
            return

        # récup nom de la couche active
        Layer_Name = (self.iface.activeLayer().source()).split('"')[3]
        print(Layer_Name)

        # check couche active = sig_flore_point ou sig_faune_point
        if (Layer_Name not in malist):
            self.log(message='Vous avez sélectionné la couche ' +Layer_Name +'. Veuillez sélectionner la couche sig_flore_point ou sig_faune_point',log_level=2, push=True)
            return

        # check s'il y a des objets sélectionnés
        selected_features = active_layer.selectedFeatures()
        if not len(selected_features):
            self.log(message="Aucun objet sélectionné", log_level=2, push=True)
            return

        # moissonnage des id
        Mesid = ','.join([str(f['objectid']) for f in selected_features])
        print(Mesid)

<<<<<<< HEAD
=======
        # Filtrer sur l'emprise courante du canevas
        # Nota VD, 14/12/21 : Ca, ça marche. Merci Marie! ;-)  de rien :)
        # en vrai, on veut filtrer la couche des secteurs/sites, on est d'accord? oui c'est bien çà :)
        extent = self.iface.mapCanvas().extent()
        request = QgsFeatureRequest()
        request.setFilterRect(extent)
        layer = self.iface.activeLayer()
        for feature in layer.getFeatures(request):
            print(feature["objectid"])

>>>>>>> f9b25a9a0cffcdd9cea570ea0d5ec931da2360f2
        # lancement de la fenêtre de configuration
        self.trsfgeom_form = FormSettings(self.iface)
        self.trsfgeom_form.recup_selected_features(selected_features)
        self.trsfgeom_form.recup_selected_mesid(Mesid)
        self.trsfgeom_form.recup_active_layer_name(Layer_Name)
