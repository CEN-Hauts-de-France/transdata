#! python3  # noqa: E265

# PyQGIS
from qgis.gui import QgisInterface
from qgis.PyQt.QtWidgets import QAction

# Plugin package
from .ui.form_settings import FormSettings
from .utils.sql_executor import SqlExecutor


class CenTransdataPlugin:
    def __init__(self, iface: QgisInterface):
        """Constructor.

        :param iface: An interface instance that will be passed to this \
        class which provides the hook by which you can manipulate the QGIS \
        application at run time.
        :type iface: QgsInterface
        """
        self.iface = iface
        self.sql_xtor = SqlExecutor()
        self.trsfgeom_form = FormSettings()

    def initGui(self):
        self.action = QAction("Go!", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action

    def run(self):
        # show the dialog
        self.trsfgeom_form.show()
        # Run the dialog event loop
        #result = self.exec_()
