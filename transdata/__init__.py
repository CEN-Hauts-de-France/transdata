# -----------------------------------------------------------
# Copyright (C) 2015 Martin Dobias
# -----------------------------------------------------------
# Licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# ---------------------------------------------------------------------

# PyQGIS
from qgis.PyQt.QtWidgets import QAction, QMessageBox,

# Plugin package
from .ui.ui_trsfgeom import TrsfGeom #???
from .utils.sql_executor import SqlExecutor
from .trsfgeom_form import TrsfGeomDialog

def classFactory(iface):
    return MinimalPlugin(iface)


class MinimalPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.sql_xtor = SqlExecutor()
        self.trsfgeom_form = TrsfGeom()

    def initGui(self):
        self.action = QAction("Go!, self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action

    def run(self):
        #show the dialog
        self.trsfgeom_form.show()
        # Run the dialog event loop
        result = self.exec_()
                
