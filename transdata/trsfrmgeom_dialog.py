# -*- coding: utf-8 -*-
"""
/***************************************************************************
 BdTravauxDialog
                                 A QGIS plugin
 Plugin d'aide à la saisie à destination des gardes-techniciens
                             -------------------
        begin                : 2013-03-27
        copyright            : (C) 2013 by CEN NPdC
        email                : vincent.damoy@espaces-naturels.fr
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from qgis.PyQt import QtCore, QtGui, QtSql, QtWidgets
from .ui_bdtravaux_sortie import #??? Ui_BdTravaux
#from .bdt_composeur import composerClass

# create the dialog 
class TrsfGeomDialog(QtWidgets.QDialog):
    def __init__(self,iface):
        
        QtWidgets.QDialog.__init__(self)
        # Set up the user interface from Designer.
        self.ui = Ui_BdTravaux()
        self.ui.setupUi(self)

       # Référencement de iface dans l'interface (iface = interface de QGIS). Juste pour utiliser le signal layoutDesignerWillBeClosed quand le composeur est fermé.
        self.iface = iface

        #Quand la classe est fermée, elle est effacée. permet de réinitialiser toutes les valeurs si on réappuie sur le bouton.
        #self.setAttribute(QtCore.Qt.WA_QuitOnClose, True)

        # DB type, host, user, password...
        self.db = QtSql.QSqlDatabase.addDatabase("QPSQL") # QPSQL = nom du pilote postgreSQL
        #ici on crée self.db =objet de la classe, et non db=variable, car on veut réutiliser db même en étant sorti du constructeur
        # (une variable n'est exploitable que dans le bloc où elle a été créée)
        self.db.setHostName("127.0.0.1")
        self.db.setPort(5432)
        self.db.setDatabaseName("sitescsn")
        self.db.setUserName("postgres")
        self.db.setPassword("postgres")
        ok = self.db.open()
        if not ok:
            QtWidgets.QMessageBox.warning(self, 'Alerte', u'La connexion est échouée'+self.db.hostName())

        # Remplir les comboboxs "site" (saisie, modification et bordereau terrain) avec les codes et noms de sites 
        # issus de la table "sites"
        query = QtSql.QSqlQuery(self.db)
        # on affecte à la variable query la méthode QSqlQuery (paramètre = nom de l'objet "base")
      #  if query.exec_('select idchamp, codesite, nomsite from sites_cen.t_sitescen order by codesite'):
      #      while query.next():
      #          self.ui.site.addItem(query.value(1) + " " + query.value(2), query.value(1) )
      #          self.ui.cbx_edcodesite.addItem(query.value(1) + " " + query.value(2), query.value(1) )
      #          self.ui.cbx_bordsite.addItem(query.value(1)+ " " + query.value(2), query.value(1) )
            # *Voir la doc de la méthode additem d'une combobox : 1er paramètre = ce qu'on affiche (ici, codesite nomsite), 
            # 2ème paramètre = ce qu'on garde en mémoire pour plus tard


        #Initialisations pour :
        # - objetVisiText (récup "objectif de la visite") 
        #premObjVis = self.ui.lst_objvisit.item(0)
        #premObjVis.setSelected(True)
                

           ## Connexions signaux-slots
        #button.clicked.connect(func)
        self.ui.btn_ok.clicked.connect(self.lancerTrsfGeom)
        self.ui.cbx_typcible.currentIndexChanged[int].connect(self.fillListCible)


    def fillListCible(self):
        self.ui.cbx_listcible.clear()
        queryFillList = QtSql.QSqlQuery(self.db)
        qFillList = u'SELECT ...FROM'
        ok = queryFillList.exec_(qFillList)
        while queryFillList.next():
            #print (query.value(1).toPyDate().strftime("%Y-%m-%d"))
            self.ui.cbx_listcible.addItem(query.value(1).toPyDate().strftime("%Y-%m-%d") + " / " + str(query.value(2)) + " / "+ str(query.value(3))+ " - "+ str(query.value(4))+ " / "+ str(query.value(0)), int (query.value(0)))
        # 1er paramètre = ce qu'on affiche, 
        # 2ème paramètre = ce qu'on garde en mémoire pour plus tard
        if not ok :
            QtWidgets.QMessageBox.warning(self, 'Alerte', u'Requête remplissage liste cibles ratée')
        self.ui.cbx_listcible.setCurrentIndex(0)
        
        
        
        
    def lancerTrsfGeom(self):
        queryTrsfGeom = QtSql.QSqlQuery(self.db)
        qtrsfgeom = u'SELECT ...'

##############################################################################################################

    def sauverInfos(self):
        self.objetVisiClicked()
        self.erreurSaisieSortie = '0'
        # S'il y a plusieurs dates, alors lire les données dans "datefin" et "plsrsdates". Sinon, la date de fin = la date de début et les jours ne sont pas renseignés
        if self.ui.chbox_plsrsjrs.isChecked()==True:
            self.date_fin=self.ui.datefin.selectedDate().toPyDate().strftime("%Y-%m-%d")
            self.jourschan=self.ui.plsrsdates.toPlainText().replace("\'","\'\'")
        else : 
            self.date_fin=self.ui.date.selectedDate().toPyDate().strftime("%Y-%m-%d")
            self.jourschan=""
        #Insertion en base des données saisies par l'utilisateur dans le module "sortie".
        query_save = QtSql.QSqlQuery(self.db)
        query = u'INSERT INTO bdtravaux.sortie (date_sortie, date_fin, redacteur, codesite, jours_chan, chantvol, sortcom, natfaune, natflore, natautre) VALUES (\'{zr_date_sortie}\'::date, \'{zr_date_fin}\'::date, \'{zr_redacteur}\',\'{zr_site}\', \'{zr_jourschan}\', {zr_chantier_vol}, \'{zr_sort_com}\', \'{zr_natfaune}\',\'{zr_natflore}\',\'{zr_natautre}\')'.format(\
        zr_date_sortie=self.ui.date.selectedDate().toPyDate().strftime("%Y-%m-%d"),\
        zr_date_fin=self.date_fin,\
        zr_redacteur=self.ui.cbx_redact.itemText(self.ui.cbx_redact.currentIndex()).split(" /")[0],\
        zr_site = self.ui.site.itemData(self.ui.site.currentIndex()),\
        zr_jourschan = self.jourschan,\
        zr_chantier_vol = self.chantvol,\
        zr_sort_com = self.ui.comm.toPlainText().replace("\'","\'\'"),\
        zr_natfaune=self.ui.natfaune.toPlainText().replace("\'","\'\'"),\
        zr_natflore=self.ui.natflore.toPlainText().replace("\'","\'\'"),\
        zr_natautre=self.ui.natautre.toPlainText().replace("\'","\'\'"))
        print (query)
        ok = query_save.exec_(query)
        if not ok:
            QtWidgets.QMessageBox.warning(self, 'Alerte', u'Requête ratée')
            self.erreurSaisieSortie = '1'
        self.rempliJoin()
        self.chantVol()
        #self.db.close()
        #self.db.removeDatabase("sitescsn")
        if self.erreurSaisieSortie == '0':
            QtWidgets.QMessageBox.information(self, 'Information', u'Données intégrées dans la base.')
        else :
            QtWidgets.QMessageBox.warning(self, 'Alerte', u'Données partiellement ou non intégrées dans la base')
        self.majIdFutSortie()
        self.reinitialiser()
        self.close()

        # contrôle "date" : on utilise la méthode SelectedDate des calendriers : self.ui.date.selectedDate(), toPyDate() pour
        # transformer l'objet QDate en objet "date " de Python, et la méthode Python strftime pour définir le format de sortie.
        # contrôle "site" : c'est une combobox, mais on ne veut pas de texte, on veut la data définie quand on a rempli la combobox (cf. l54)
        # contrôles checkboxes : méthode isChecked renvoie un booléen. on transforme en chaîne (str), ce qui donne True ou False.
        # Or, on veut true ou false pour que PostGreSQl puisse les interprêter. D'où laméthode Python .lower, qui change la casse des chaînes.
        # contrôles "jours_chan" et "comm" : ce qont des QTextEdit. Ils prennent donc le texte saisi au format HTML. 
        # La méthode toPleinText() renvoie du texte classique


    def rempliJoin(self):
    # Remplissage des tables join_salarie et join_objvisit avec les salaries et les objets de la visite sélectionnés dans les QListWidget 
    # "lst_salaries" et "lst_objvisit"
        #récupération de id_oper dans la table "sortie" pour le remettre dans join_salaries et join_objvisit
        queryidsal = QtSql.QSqlQuery(self.db)
        qidsal = u"""select sortie_id from bdtravaux.sortie order by sortie_id desc limit 1"""
        ok2=queryidsal.exec_(qidsal)
        if not ok2:
            QtWidgets.QMessageBox.warning(self, 'Alerte', u'Pas trouvé id de la sortie')
            self.erreurSaisieSortie ='1'
        queryidsal.next()
        self.sortie_id = queryidsal.value(0)

        #remplissage de la table join_salaries : sortie_id, noms du (des) salarié(s) et initiales
        for item in range (len(self.ui.lst_salaries.selectedItems())):
            querysalarie = QtSql.QSqlQuery(self.db)
            qsalarie = u"""insert into bdtravaux.join_salaries (id_joinsal, salaries, sal_initia) values ({zr_idjoinsal}, '{zr_salarie}','{zr_initiales}')""".format (\
            zr_idjoinsal = self.sortie_id,\
            zr_salarie = self.ui.lst_salaries.selectedItems()[item].text().split(" /")[0].replace("\'","\'\'"),\
            zr_initiales=self.ui.lst_salaries.selectedItems()[item].text().split("/")[1])
            ok3 = querysalarie.exec_(qsalarie)
            if not ok3:
               QtWidgets.QMessageBox.warning(self, 'Alerte', u'Saisie des salariés en base ratée')
               self.erreurSaisieSortie ='1'
            querysalarie.next()
        queryredacteur = QtSql.QSqlQuery(self.db)
        qredacteur = u"""insert into bdtravaux.join_salaries (id_joinsal, salaries, sal_initia) values ({zr_idjoinsal}, '{zr_redacteur}','{zr_initialrd}')""".format (\
        zr_idjoinsal = self.sortie_id,\
        zr_redacteur = self.ui.cbx_redact.itemText(self.ui.cbx_redact.currentIndex()).split(" /")[0].replace("\'","\'\'"),\
        zr_initialrd=self.ui.cbx_redact.itemText(self.ui.cbx_redact.currentIndex()).split(" /")[1].replace("\'","\'\'"))
        ok3b = queryredacteur.exec_(qredacteur)
        if not ok3b:
           QtWidgets.QMessageBox.warning(self, 'Alerte', u'Saisie du rédacteur en base ratée')
           self.erreurSaisieSortie ='1'


        #remplissage de la table join_objvisite : sortie_id, objet de la visite et complément si "autre"
        for item in range (len(self.ui.lst_objvisit.selectedItems())):
            if self.ui.lst_objvisit.selectedItems()[item].text() == 'Autre...' :
                self.objviautr = self.ui.txt_objvisautre.text().replace("\'","\'\'")
            else :
                self.objviautr =''
            queryobjvisit = QtSql.QSqlQuery(self.db)
            qobjvis = u"""insert into bdtravaux.join_objvisite (id_joinvis, objvisite, objviautre) values ({zr_idjoinvis}, '{zr_objvisite}', '{zr_objviautr}')""".format(\
            zr_idjoinvis = self.sortie_id,\
            zr_objvisite = self.ui.lst_objvisit.selectedItems()[item].text().replace("\'","\'\'"),\
            zr_objviautr = self.objviautr)
            ok4 = queryobjvisit.exec_(qobjvis)
            if not ok4 :
                QtWidgets.QMessageBox.warning(self, 'Alerte', u'Saisie en base des objectifs de la visite ratée')
                self.erreurSaisieSortie ='1'
            queryobjvisit.next()




    def fillExSortieList(self):
        self.ui.cbx_exsortie.clear()
        # Remplir la QlistWidget "listesortie" avec les champs date_sortie+site de la table "sortie" et le champ sal_initia de la table "join_salaries"
        query = QtSql.QSqlQuery(self.db)  # on affecte à la variable query la méthode QSqlQuery (paramètre = nom de l'objet "base")
        if not query :
            print ('ca nemarche pas')
        querySortie=u"""select sortie_id, date_sortie, codesite, (SELECT string_agg(left(word, 1), '') FROM (select unnest(string_to_array(btrim(redacteur,'_'), ' ')) FROM bdtravaux.sortie b WHERE b.sortie_id=a.sortie_id) t(word)) as redacinit, array_to_string(array(select distinct sal_initia from bdtravaux.join_salaries where id_joinsal=sortie_id), '; ') as salaries from bdtravaux.sortie a order by date_sortie DESC """
        print (querySortie)
        ok = query.exec_(querySortie)
        while query.next():
            #print (query.value(1).toPyDate().strftime("%Y-%m-%d"))
            self.ui.cbx_exsortie.addItem(query.value(1).toPyDate().strftime("%Y-%m-%d") + " / " + str(query.value(2)) + " / "+ str(query.value(3))+ " - "+ str(query.value(4))+ " / "+ str(query.value(0)), int (query.value(0)))
        # 1er paramètre = ce qu'on affiche, 
        # 2ème paramètre = ce qu'on garde en mémoire pour plus tard
        if not ok :
            QtWidgets.QMessageBox.warning(self, 'Alerte', u'Requête remplissage sortie ratée')
        self.ui.cbx_exsortie.setCurrentIndex(0)

## query.value(1).toPyDate().strftime("%Y-%m-%d")


 

    def reinitialiser(self):
    # Réinitialisations après sauvegarde des données en base
        # Objet de la visite
        for child in self.findChildren((QtWidgets.QRadioButton)):
            child.setChecked(False)
            if child.text()=='Travaux sur site (hors chantiers de volontaires)':
                child.setChecked(True)
        # Onglet "chantier de volontaire"
        regex = QtCore.QRegExp("^ch_nb*")
        for child in self.findChildren((QtWidgets.QLineEdit), regex):
            child.setText('0')
        for child in self.findChildren((QtWidgets.QTextEdit)):
            child.clear()
        for child in self.findChildren((QtWidgets.QTableWidget)):
            for row in range(child.rowCount ()):
                for column in range(child.columnCount ()):
                    item = child.item (row, column )
                    item.setText('0')
        self.ui.tab_chantvol.setEnabled(0)
        # Onglet actif = le premier
        self.ui.tab_widget.setCurrentIndex(0)
        # Date par défaut dans les calendriers = aujourd'hui
        for child in self.findChildren((QtWidgets.QCalendarWidget)):
            aujourdhui=QtCore.QDate.currentDate()
            child.setSelectedDate(aujourdhui)
