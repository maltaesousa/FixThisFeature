# -*- coding: utf-8 -*-
"""
/***************************************************************************
 FixThisFeature
                                  A QGIS plugin
 Creates a point geometry reprensenting an issue on a map.
                              -------------------
        begin                : 2017-04-06
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Stéphane Malta e Sousa
        email                : sos@ylb.ch
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
from qgis.core import QgsFeature, QgsGeometry
from fix_this_feature_dialog import FixThisFeatureDialog
from send_point_tool import SendPointTool
import os.path
import resources, resources_rc

class FixThisFeature:
    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # saving parameters
        self.editLayerName = "qg_issue"
        self.featureLayerAttribute = "feature_layer"
        self.featureIdAttribute = "feature_id"
        self.featureDescriptionAttribute = "description"
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'FixThisFeature_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&FixThisFeature')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'FixThisFeature')
        self.toolbar.setObjectName(u'FixThisFeature')
        
        # Connect to signals for button behaviour
        self.iface.currentLayerChanged.connect(self.toggle)
        
        self.canvas = self.iface.mapCanvas()



    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('FixThisFeature', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=False,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = FixThisFeatureDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action


    def toggle(self):
        """Toggles the button to enabled if current layer URI matches editLayerName"""
        layer = self.canvas.currentLayer()
        if layer <> None:
            currentURI = layer.dataProvider().dataSourceUri()
            if self.editLayerName in currentURI:
                if layer.isEditable():
                    self.actions[0].setEnabled(True)
                    layer.editingStopped.connect(self.toggle)
                    try:
                        layer.editingStarted.disconnect(self.toggle)
                    except TypeError:
                        pass
                else:
                    self.actions[0].setEnabled(False)
                    layer.editingStarted.connect(self.toggle)
                    try:
                        layer.editingStopped.disconnect(self.toggle)
                        self.tool = None
                    except TypeError:
                        pass


    def selectFeature(self):
        """Enables a clicking tool that will retrieves clicked information"""
        self.dlg.hide()
        self.tool = SendPointTool(self.canvas)
        # if user clicks on a feature, this signal will be emitted
        self.tool.featureClicked.connect(self.fillDialog)
        # if user clicks in the backgroud, this signal will be emitted
        self.tool.voidClicked.connect(self.fillDialog)
        self.canvas.setMapTool(self.tool)


    def fillDialog(self, pt, *args):
        """Fills the dialog with parameters found with the clicking tool in selectFeature"""
        self.newPoint = pt
        if len(args) == 2:
            layerCilcked = args[0].name()
            featureCilcked = args[1]
            self.dlg.lineEdit.clear()
            # inserts the first field value, supposed to be the id
            self.dlg.lineEdit.insert(str(featureCilcked[0]))

            index = self.dlg.comboBox.findText(layerCilcked)
            self.dlg.comboBox.setCurrentIndex(index)
            self.dlg.comboBox.setEnabled(False)
            self.dlg.toolButton.setEnabled(True)
        self.saveData()


    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        icon_path = ':/plugins/FixThisFeature/icon.svg'
        self.add_action(
            icon_path,
            text=self.tr(u'Report an issue'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        self.iface.currentLayerChanged.disconnect(self.toggle)
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&FixThisFeature'),
                action)
            self.iface.removeToolBarIcon(action)
        del self.toolbar


    def run(self):
        """Run method that performs all the real work"""
        # Getting all the layers into the comboBox
        layers = self.iface.legendInterface().layers()
        layer_set = set([])
        for layer in layers:
            layer_set.add(layer.name())
        self.dlg.comboBox.addItems(list(layer_set))
        # connecting the pickup tool to the button
        self.dlg.toolButton.clicked.connect(self.selectFeature)
        self.selectFeature()


    def saveData(self):
        """Saves the data"""
        # Run the dialog event loop
        result = self.dlg.exec_()
        # Sets focus to the only editable widget in dialog
        self.dlg.plainTextEdit.setFocus(True)
        self.dlg.plainTextEdit.selectAll()
        # See if OK was pressed
        if result:
            layer = self.canvas.currentLayer()
            newFeature = QgsFeature(layer.pendingFields())
            # Set attributes to the new feature
            newFeature.setAttribute(self.featureIdAttribute, self.dlg.lineEdit.text())
            newFeature.setAttribute(self.featureLayerAttribute, self.dlg.comboBox.currentText())
            newFeature.setAttribute(self.featureDescriptionAttribute, self.dlg.plainTextEdit.toPlainText())
            # Assign the point geometry (clicked point)
            newFeature.setGeometry(QgsGeometry.fromPoint(self.newPoint))
            # TODO check if everything went ok
            (res, outFeats) = layer.dataProvider().addFeatures([newFeature])
            self.canvas.refresh()
