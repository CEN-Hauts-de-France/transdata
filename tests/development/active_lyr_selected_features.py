from sys import exit

# check s'il y a une couche active
active_layer = iface.activeLayer()
if not active_layer:
    print("Aucune couche sélectionnée")

print("Couche sélectionnée : ", active_layer.name())

# check s'il y a des objets sélectionnés
selected_features = active_layer.selectedFeatures()
if not len(selected_features):
    print("Aucun objet sélectionné")

print(f"{len(selected_features)} objets sélectionnés dans la couche {active_layer.name()}")

memory_layer = active_layer.materialize(QgsFeatureRequest().setFilterFids(active_layer.selectedFeatureIds()))
memory_layer.setName("youpi")
QgsProject.instance().addMapLayer(memory_layer)
