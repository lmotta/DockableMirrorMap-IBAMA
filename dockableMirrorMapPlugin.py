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

from dockableMirrorMap import DockableMirrorMap

import resources_rc

class DockableMirrorMapPlugin:

	def __init__(self, iface):
		# Save a reference to the QGIS iface
		self.iface = iface
		self.mapCanvas = self.iface.mapCanvas()
		self.numMirror = 0
		self.entryPluginQgs = {
        'plugin': "Plugin_DockableMirrorMap_v1",
        'numMirrors': "/numMirrors",
        'mirror_floating': "/mirror%d/floating",
        'mirror_position': "/mirror%d/position",
        'mirror_size': "/mirror%d/size",
        'mirror_scaleFactor': "/mirror%d/scaleFactor",
        'mirror_layerids': "/mirror%d/layerids",
        'mirror_layerchecks': "/mirror%d/layerchecks"
		} 
		
	def initGui(self):
		self.dockableMirrors = []
		#
		self.dockableAction = QAction(QIcon(":/plugins/DockableMirrorMap/icons/dockablemirrormap.png"), "Dockable MirrorMap", self.iface.mainWindow())
		self.dockableAction.triggered.connect( self.runDockableMirror )
		#
		self.aboutAction = QAction(QIcon(":/plugins/DockableMirrorMap/icons/about.png"), "About", self.iface.mainWindow())
		self.aboutAction.triggered.connect( self.about )
		# Add to the plugin menu and toolbar
		self.iface.addPluginToMenu("Dockable MirrorMap", self.dockableAction)
		self.iface.addPluginToMenu("Dockable MirrorMap", self.aboutAction)
		self.iface.addToolBarIcon(self.dockableAction)
		#
		QgsProject.instance().readProject.connect( self.onReadProject )
		QgsProject.instance().writeProject.connect( self.onWriteProject )
	
	def unload(self):
		QgsProject.instance().readProject .disconnect( self.onReadProject )
		QgsProject.instance().writeProject.disconnect( self.onWriteProject )
		#
		self.removeDockableMirrors()
		# Remove the plugin
		self.iface.removePluginMenu("Dockable MirrorMap",self.dockableAction)
		self.iface.removePluginMenu("Dockable MirrorMap",self.aboutAction)
		self.iface.removeToolBarIcon(self.dockableAction)

	def about(self):
		from DlgAbout import DlgAbout
		DlgAbout(self.iface.mainWindow()).exec_()

	def removeDockableMirrors(self):
		for d in list(self.dockableMirrors):
			d.close()
		self.dockableMirrors = []

	def runDockableMirror(self):
		def setupDockWidget( wdg ):
			othersize = QGridLayout().verticalSpacing()
			if len( self.dockableMirrors ) <= 0:
				width = self.mapCanvas.size().width()/2 - othersize
				wdg.onDockLocationChanged( Qt.RightDockWidgetArea )
				wdg.setMinimumWidth( width )
				wdg.setMaximumWidth( width )
	
			elif len( self.dockableMirrors ) == 1:
				height = self.dockableMirrors[0].size().height()/2 - othersize/2
				wdg.onDockLocationChanged( Qt.RightDockWidgetArea )
				wdg.setMinimumHeight( height )
				wdg.setMaximumHeight( height )
	
			elif len(self.dockableMirrors) == 2:
				height = self.mapCanvas.size().height()/2 - othersize/2
				wdg.onDockLocationChanged( Qt.BottomDockWidgetArea )
				wdg.setMinimumHeight( height )
				wdg.setMaximumHeight( height )
	
			else:
				wdg.onDockLocationChanged( Qt.BottomDockWidgetArea )
				wdg.setFloating( True )
				wdg.move(50, 50)	# move the widget to the center
	#
		self.numMirror += 1
		wdg = DockableMirrorMap(self.iface.mainWindow(), self.numMirror)
		#
		mirror = wdg.getMirror()
		mirror.connectCanvas( False )
		mirror.populateLegend()
		mirror.populateTootipStack()
		#
		minsize = wdg.minimumSize()
		maxsize = wdg.maximumSize()
		#
		setupDockWidget(wdg)
		self._addDockWidget( wdg )
		#
		wdg.setMinimumSize(minsize)
		wdg.setMaximumSize(maxsize)
		#
		mirror.scaleFactorSpin.setValue( 1 )
		mirror.connectCanvas()
		self.mapCanvas.extentsChanged.emit( )

	def _addDockWidget(self, wdg ):
		QObject.connect(wdg, SIGNAL( "closed(PyQt_PyObject)" ), self.onCloseDockableMirror)
		#
		self.dockableMirrors.append( wdg )
		self.iface.addDockWidget( wdg.getLocation(), wdg )

	def onCloseDockableMirror(self, wdg):
		if self.dockableMirrors.count( wdg ) > 0:
			self.dockableMirrors.remove( wdg )

	def onWriteProject(self, domproject):
		if len(self.dockableMirrors) <= 0:
			return

		proj = QgsProject.instance()
		#
		proj.writeEntry( self.entryPluginQgs['plugin'], self.entryPluginQgs['numMirrors'], len( self.dockableMirrors) )
		for id, wdg in enumerate( self.dockableMirrors ):
			# save position and geometry
			floating = wdg.isFloating()
			proj.writeEntryBool( self.entryPluginQgs['plugin'], self.entryPluginQgs['mirror_floating'] % id, floating )
			if floating:
				position = "%s %s" % ( wdg.pos().x(), wdg.pos().y() )
			else:
				position = u"%s" % wdg.getLocation()
			proj.writeEntry( self.entryPluginQgs['plugin'], self.entryPluginQgs['mirror_position'] % id, str( position)  )

			size = "%s %s" % ( wdg.size().width(), wdg.size().height() )
			proj.writeEntry( self.entryPluginQgs['plugin'], self.entryPluginQgs['mirror_size'] % id, str( size ) )

			# save the layer list
			( layerIds, layerChecks ) = wdg.getMirror().getLayersCanvas()
			proj.writeEntry( self.entryPluginQgs['plugin'], self.entryPluginQgs['mirror_layerids'] % id, layerIds )
			proj.writeEntry( self.entryPluginQgs['plugin'], self.entryPluginQgs['mirror_layerchecks'] % id, layerChecks )

			scaleFactor = wdg.getMirror().scaleFactorSpin.value()
			proj.writeEntryDouble( self.entryPluginQgs['plugin'], self.entryPluginQgs['mirror_scaleFactor'] % id, scaleFactor )

	def onReadProject(self, domproject):
		def setupDockWidget( wdg ):
			# restore position
			floating, ok = proj.readBoolEntry( self.entryPluginQgs['plugin'], self.entryPluginQgs['mirror_floating'] % index )
			if ok: 
				wdg.setFloating( floating )
				position, ok = proj.readEntry( self.entryPluginQgs['plugin'], self.entryPluginQgs['mirror_position'] % index )
				if ok: 
					try:
						if floating:
							parts = position.split(" ")
							if len(parts) >= 2:
								wdg.move( int(parts[0]), int(parts[1]) )
						else:
							wdg.onDockLocationChanged( int(position) )
					except ValueError:
						pass
			# restore geometry
			wdg.setFixedSize( wdg.geometry().width(), wdg.geometry().height() )
			size, ok = proj.readEntry( self.entryPluginQgs['plugin'], self.entryPluginQgs['mirror_size'] % index )
			if ok:
				try:
					parts = size.split(" ")
					wdg.setFixedSize( int(parts[0]), int(parts[1]) )
				except ValueError:
					pass

		def getSettingMirror( mirror ):
			scaleFactor, ok = proj.readDoubleEntry( self.entryPluginQgs['plugin'], self.entryPluginQgs['mirror_scaleFactor'] % index, 1.0 )
			if not ok:
				return None
			layerIds, ok = proj.readListEntry( self.entryPluginQgs['plugin'], self.entryPluginQgs['mirror_layerids'] % index )
			if not ok:
				return None
			layerChecks, ok = proj.readListEntry( self.entryPluginQgs['plugin'], self.entryPluginQgs['mirror_layerchecks'] % index )
			if not ok:
				return None
			#
			return ( scaleFactor, layerIds, layerChecks )

		proj = QgsProject.instance()
		#
		num, ok = proj.readNumEntry( self.entryPluginQgs['plugin'], self.entryPluginQgs['numMirrors'])
		if not ok or num <= 0:
			return
		# remove all mirrors
		self.removeDockableMirrors()
		self.numMirror = 0
		# load mirrors
		for index in range( num ):
			# MapCanvas Render
			if num >= 2:
				if index == 0: 
					prevFlag = self.mapCanvas.renderFlag()
					self.mapCanvas.setRenderFlag( False )
				elif index == num-1:
					self.mapCanvas.setRenderFlag( True )
			#
			self.numMirror += 1
			wdg = DockableMirrorMap( self.iface.mainWindow(), self.numMirror )
			#
			mirror = wdg.getMirror()
			mirror.connectCanvas( False )
			( scaleFactor, layerIds, layerChecks ) = getSettingMirror( mirror )
			mirror.setLayersCanvas( layerIds, layerChecks )
			mirror.populateTootipStack()
			#
			minsize = wdg.minimumSize()
			maxsize = wdg.maximumSize()
			#
			setupDockWidget( wdg )
			self._addDockWidget( wdg )
			#
			wdg.setMinimumSize(minsize)
			wdg.setMaximumSize(maxsize)
			#
			mirror.scaleFactorSpin.setValue( scaleFactor )
			mirror.connectCanvas()
			self.mapCanvas.extentsChanged.emit( )
