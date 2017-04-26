from PyQt4.QtCore import Qt, pyqtSignal
from qgis.gui import QgsMapToolIdentifyFeature
from qgis.core import QgsPoint
from qgis.utils import iface

class SendPointTool(QgsMapToolIdentifyFeature):
    featureClicked = pyqtSignal( ['QgsPoint', 'QgsVectorLayer', 'QgsFeature'] )
    voidClicked = pyqtSignal( 'QgsPoint' )
    def __init__(self, canvas):
        """ Constructor."""
        QgsMapToolIdentifyFeature.__init__(self, canvas)
        self.clickedPoint = QgsPoint()
        self.setCursor(Qt.CrossCursor)

    def canvasReleaseEvent(self, e):
        self.clickedPoint = self.toMapCoordinates( e.pos() )
        results = self.identify(e.x(), e.y(), self.LayerSelection, self.VectorLayer)
        if len(results) > 0:
            self.featureClicked.emit(self.clickedPoint, results[0].mLayer, results[0].mFeature)
        else:
            self.voidClicked.emit(self.clickedPoint)
