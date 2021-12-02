#! python3  # noqa: E265

# PyQGIS
from qgis.gui import QgisInterface
from qgis.PyQt.QtWidgets import QAction

# Plugin package
from transdata.ui.form_settings import FormSettings
from transdata.utils.log_handler import PlgLogger


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

        # check s'il y a des objets sélectionnés
        selected_features = active_layer.selectedFeatures()
        if not len(selected_features):
            self.log(message="Aucun objet sélectionné", log_level=2, push=True)
            return

        # lancement de la fenêtre de configuration
        self.trsfgeom_form = FormSettings()
        self.trsfgeom_form.recup_selected_features(selected_features)
