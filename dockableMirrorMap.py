# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name                 : Dockable MirrorMap
Description          : Creates a dockable map canvas
Date                 : February 1, 2011 
copyright            : (C) 2011 by Giuseppe Sucameli (Faunalia)
email                : brush.tyler@gmail.com

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

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

from mirrorMap import MirrorMap

class DockableMirrorMap(QDockWidget):

	def __init__(self, parent, numMirror):
		QDockWidget.__init__(self, parent)
		self.setAttribute(Qt.WA_DeleteOnClose)

		self.mainWidget = MirrorMap(self, numMirror)
		
		self.setupUi()
		
		self.location = Qt.RightDockWidgetArea
		
		self.dockLocationChanged.connect( self.onDockLocationChanged )

	def closeEvent(self, event):
		self.mainWidget.close()
		self.emit( SIGNAL( "closed(PyQt_PyObject)" ), self )
		return QDockWidget.closeEvent(self, event)

	def getMirror(self):
		return self.mainWidget

	def getLocation(self):
		return self.location

	def onDockLocationChanged( self, location ):
		self.location = location

	def setupUi(self):
		self.setObjectName( "dockablemirrormap_dockwidget" )
		self.setWidget(self.mainWidget)

