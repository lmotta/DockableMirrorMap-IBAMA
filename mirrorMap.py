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
from qgis import utils

import locale

class LegendWdg( QWidget ):
	def __init__( self, parent ):
		super( LegendWdg, self ).__init__( parent )
		self._setupUi( parent )
	#
	def _setupUi( self, parent ):
		def setModelTreeView():
			self.model = QgsLayerTreeModel( ltg )
			self.tview = QgsLayerTreeView(self)
			#
			self.tview.setSelectionMode( QAbstractItemView.ExtendedSelection )
			self.model.setFlag( QgsLayerTreeModel.AllowNodeReorder )
			self.model.setFlag( QgsLayerTreeModel.AllowNodeChangeVisibility, True )
			self.tview.setModel( self.model )
		#
		def setGridLayout():
			gridLayout.setContentsMargins( 0, 0, gridLayout.verticalSpacing(), gridLayout.verticalSpacing() )
			#
			showSelectedLayersBtn = QToolButton(self)
			( iniY, iniX, spanY, spanX ) = ( 0, 0, 1, 1 )
			action = utils.iface.actionShowSelectedLayers()
			showSelectedLayersBtn.setIcon( action.icon() )
			showSelectedLayersBtn.setToolTip( action.iconText() )
			showSelectedLayersBtn.clicked.connect( self.onClickedShow )
			gridLayout.addWidget( showSelectedLayersBtn, iniY, iniX, spanY, spanX )
			#
			hideSelectedLayersBtn = QToolButton(self)
			iniX += 1
			action = utils.iface.actionHideSelectedLayers()
			hideSelectedLayersBtn.setIcon( action.icon() )
			hideSelectedLayersBtn.setToolTip( action.iconText() )
			hideSelectedLayersBtn.clicked.connect( self.onClickedHide )
			gridLayout.addWidget( hideSelectedLayersBtn, iniY, iniX, spanY, spanX )
			#
			( iniY, iniX, spanY, spanX ) = ( 1, 0, 1, 3 )
			gridLayout.addWidget( self.tview, iniY, iniX, spanY, spanX )
		#
		ltg = parent.getLayerTreeGroup()
		setModelTreeView( )
		gridLayout = QGridLayout(self)
		setGridLayout()
		#
		self.tview.currentLayerChanged.connect( parent.onCurrentLayerChanged )
	#
	def _checkedLayers( self, lyrs, checked ):
		for item in lyrs:
			item.setVisible( checked )
	#
	def onClickedShow(self):
		lyrs = self.tview.selectedLayerNodes()
		if len( lyrs ) > 0:
			self._checkedLayers( lyrs, Qt.Checked )
	#
	def onClickedHide(self):
		lyrs = self.tview.selectedLayerNodes()
		if len( lyrs ) > 0:
			self._checkedLayers( lyrs, Qt.Unchecked )
	#
	def currentLayer(self):
		return self.tview.currentLayer()
		
class MirrorMap( QWidget ):
	def __init__(self, parent, numMirror):
		super( MirrorMap, self ).__init__( parent )
		self.setAttribute(Qt.WA_DeleteOnClose)
		#
		self.parent = parent
		self.qgisCanvas = utils.iface.mapCanvas()
		self.ltg = QgsLayerTreeGroup('', Qt.Unchecked)
		self.numMirror = numMirror
		self.marker = None
		self.extent = None
		self.bridge = None
		#
		self.setupUi()
		
	def closeEvent(self, event):
		self._connect( False )
		self.emit( SIGNAL( "closed(PyQt_PyObject)" ), self )
		return QWidget.closeEvent(self, event)

	def setupUi(self):
		def setGridLayout():
			def getSettingCanvas():
				settings = QSettings()
				return {
									'enable_anti_aliasing': settings.value( "/qgis/enable_anti_aliasing", False, type=bool ),
									'use_qimage_to_render': settings.value( "/qgis/use_qimage_to_render", False, type=bool ),
									'wheel_action': settings.value( "/qgis/wheel_action", 0, type=int),
									'zoom_factor': settings.value( "/qgis/zoom_factor", 2.0, type=float )
								}
			#
			gridLayout.setContentsMargins( 0, 0, gridLayout.verticalSpacing(), gridLayout.verticalSpacing() )
			#
			self.canvas = QgsMapCanvas(self)
			( iniY, iniX, spanY, spanX ) = ( 0, 1, 1, 9 )
			self.canvas.setCanvasColor( QColor(255,255,255) )
			sc = getSettingCanvas()
			self.canvas.enableAntiAliasing( sc['enable_anti_aliasing'] )
			self.canvas.useImageToRender( sc['use_qimage_to_render'])
			self.wheelActionCanvas = {
															 'action': QgsMapCanvas.WheelAction( sc['wheel_action'] ),
															 'zoom': sc['zoom_factor']
															} 
			self.canvas.setWheelAction( self.wheelActionCanvas['action'],  self.wheelActionCanvas['zoom'] )
			gridLayout.addWidget( self.canvas, iniY, iniX, spanY, spanX )
			#
			self.legend = LegendWdg( self )
			( iniY, iniX, spanY, spanX ) = ( 0, 0, 1, 1 )
			gridLayout.addWidget( self.legend, iniY, iniX, spanY, spanX )
			self.legend.setVisible( False )
			#
			self.stackLayersBtn = QToolButton(self)
			( iniY, iniX, spanY, spanX ) = ( 1, 1, 1, 1 )
			self.stackLayersBtn.setIcon( QIcon(":/plugins/DockableMirrorMap/icons/layers.png") )
			gridLayout.addWidget( self.stackLayersBtn, iniY, iniX, spanY, spanX )
			#
			self.selectLayerBtn = QToolButton(self)
			iniX += 1
			self.selectLayerBtn.setIcon( QIcon(":/plugins/DockableMirrorMap/icons/select.png") )
			self.selectLayerBtn.setEnabled( False )
			gridLayout.addWidget( self.selectLayerBtn, iniY, iniX, spanY, spanX )
			#
			self.renderCheck = QCheckBox( "Render", self )
			self.renderCheck.setChecked( True )
			iniX += 1
			gridLayout.addWidget( self.renderCheck, iniY, iniX, spanY, spanX )
			#
			self.markerCheck = QCheckBox( "Marker", self )
			self.markerCheck.setChecked( False )
			iniX += 1
			gridLayout.addWidget( self.markerCheck, iniY, iniX, spanY, spanX )
			#
			self.extentCheck = QCheckBox( "Extent", self )
			self.extentCheck.setChecked( False )
			iniX += 1
			gridLayout.addWidget( self.extentCheck, iniY, iniX, spanY, spanX )
			#
			self.scaleFactorLabel = QLabel( "Scale factor:", self )
			iniX += 1
			self.scaleFactorLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
			gridLayout.addWidget(self.scaleFactorLabel, iniY, iniX, spanY, spanX )
			#
			self.scaleFactorSpin = QDoubleSpinBox(self)
			iniX += 1
			self.scaleFactorSpin.setMinimum(0.0)
			self.scaleFactorSpin.setMaximum(1000.0)
			self.scaleFactorSpin.setDecimals(3)
			self.scaleFactorSpin.setValue(1)
			self.scaleFactorSpin.setObjectName("scaleFactorSpin")
			self.scaleFactorSpin.setSingleStep(.05)
			gridLayout.addWidget(self.scaleFactorSpin, iniY, iniX, spanY, spanX )
			#
			self.scaleBtn = QToolButton(self)
			iniX += 1
			self.scaleBtn.setText("Scale: ")
			gridLayout.addWidget(self.scaleBtn, iniY, iniX, spanY, spanX )
			#
		#	
		self.setObjectName( "dockablemirrormap_mirrormap" )
		#
		gridLayout = QGridLayout(self)
		self.wheelActionCanvas = QgsMapCanvas.WheelNothing # Change by setGridLayout
		setGridLayout()
		# Add a default pan tool
		self.toolPan = QgsMapToolPan( self.canvas )
		self.canvas.setMapTool( self.toolPan )
		#
		self.parent.setWindowTitle( "%d# " %  self.numMirror )
		#
		self._connect()
		#
		self.onDestinationCrsChanged_MapUnitsChanged()
		self.onHasCrsTransformEnabledChanged( self.qgisCanvas.hasCrsTransformEnabled() )

	def getLayersCanvas(self):
		layerIds = map(lambda x: x.layerId(), self.ltg.findLayers() )
		layerChecks = map(lambda x: str( x.isVisible() ), self.ltg.findLayers() )
		# 
		return ( layerIds, layerChecks )

	def setLayersCanvas(self, layerIds, layerChecks ):
		prevFlag = self.canvas.renderFlag()
		self.canvas.setRenderFlag( False )
		#
		lyrRegs = QgsMapLayerRegistry.instance()
		for id in range( len( layerIds ) ):
			layer = lyrRegs.mapLayer(  layerIds[id] )
			isVisible = int( layerChecks[id] )
			if not layer is None:
				self.ltg.addLayer( layer ).setVisible( isVisible )
		#
		self.canvas.setRenderFlag( prevFlag )

	def populateLegend(self):
		if len( self.ltg.findLayerIds() ) == 0:
			prevFlag = self.canvas.renderFlag()
			self.canvas.setRenderFlag( False )
			#
			for item in QgsProject.instance().layerTreeRoot().findLayers():
				self.ltg.addLayer( item.layer() ).setVisible( item.isVisible() )
			#
			self.canvas.setRenderFlag( prevFlag )

	def populateTootipStack(self):
		layerTrees = self.ltg.findLayers()
		if len( layerTrees ) > 0:
			layersDesc = map(lambda x: "%s %s" % ( '+' if  x.isVisible() == Qt.Checked else "  ", x.layerName() ),  layerTrees )
			toolTip = '\n'.join( layersDesc )
		else:
			toolTip = ''
		self.stackLayersBtn.setToolTip( toolTip )

	def _connect(self, isConnect = True):
		signal_slot = (
		  { 'signal': self.scaleFactorSpin.valueChanged, 'slot': self.onValueChangedScale },
			{ 'signal': self.stackLayersBtn.clicked, 'slot': self.onClickedStackLayersBtn },
			{ 'signal': self.selectLayerBtn.clicked, 'slot': self.onClickedSelectLayerBtn },
			{ 'signal': self.scaleBtn.clicked, 'slot': self.onClickedScale },
			{ 'signal': self.renderCheck.toggled, 'slot': self.onToggledRender },
			{ 'signal': self.markerCheck.toggled, 'slot': self.onToggledMarker },
			{ 'signal': self.extentCheck.toggled, 'slot': self.onToggledExtent },
			{ 'signal': self.canvas.extentsChanged, 'slot': self.onExtentsChangedMirror },
			{ 'signal': self.qgisCanvas.extentsChanged, 'slot': self.onExtentsChangedQgisCanvas },
			{ 'signal': self.qgisCanvas.xyCoordinates, 'slot': self.onXYCoordinates },
			{ 'signal': self.qgisCanvas.destinationCrsChanged, 'slot': self.onDestinationCrsChanged_MapUnitsChanged },
			{ 'signal': self.qgisCanvas.mapUnitsChanged, 'slot': self.onDestinationCrsChanged_MapUnitsChanged },
			{ 'signal': self.qgisCanvas.hasCrsTransformEnabledChanged, 'slot': self.onHasCrsTransformEnabledChanged },
			{ 'signal': QgsMapLayerRegistry.instance().layersWillBeRemoved, 'slot': self.onLayersWillBeRemoved },
			{ 'signal': QgsMapLayerRegistry.instance().layersAdded, 'slot': self.onLayersAdded } 
		)
		if isConnect:
			for item in signal_slot:
				item['signal'].connect( item['slot'] )  
		else:
			for item in signal_slot:
				item['signal'].disconnect( item['slot'] )  

	def connectCanvas(self, isConnect = True):
		signal_slot = (
		  { 'signal': self.scaleFactorSpin.valueChanged, 'slot': self.onValueChangedScale },
			{ 'signal': self.canvas.extentsChanged, 'slot': self.onExtentsChangedMirror },
			{ 'signal': self.qgisCanvas.extentsChanged, 'slot': self.onExtentsChangedQgisCanvas },
			{ 'signal': self.qgisCanvas.xyCoordinates, 'slot': self.onXYCoordinates },
			{ 'signal': self.qgisCanvas.destinationCrsChanged, 'slot': self.onDestinationCrsChanged_MapUnitsChanged },
			{ 'signal': self.qgisCanvas.mapUnitsChanged, 'slot': self.onDestinationCrsChanged_MapUnitsChanged },
			{ 'signal': self.qgisCanvas.hasCrsTransformEnabledChanged, 'slot': self.onHasCrsTransformEnabledChanged }
		)
		if isConnect:
			for item in signal_slot:
				item['signal'].connect( item['slot'] )  
			if self.bridge is None:
				self.bridge = QgsLayerTreeMapCanvasBridge( self.ltg, self.canvas )
		else:
			for item in signal_slot:
				item['signal'].disconnect( item['slot'] )  
			if not self.bridge is None:
				del self.bridge
				self.bridge= None

	def getLayerTreeGroup(self):
		return self.ltg

	def onValueChangedScale(self, scaleFactor):
		if not self.renderCheck.isChecked():
			return
		#
		self._execFunction(
			self.canvas.zoomScale, scaleFactor * self.qgisCanvas.scale(),
			self.canvas.extentsChanged, self.onExtentsChangedMirror
		)
		#
		self._textScaleBtnChanched()

	def onClickedStackLayersBtn(self):
		visible = True if not self.legend.isVisible() else False 
		self.legend.setVisible( visible )
		if not visible: self._tootipStackLayers()
		
	def onClickedSelectLayerBtn(self):
		lyr = self.legend.currentLayer()
		if not lyr is None:
			utils.iface.legendInterface().setCurrentLayer( lyr )	
		
	def onClickedScale(self):
		#
		self._execFunction( 
			  self.qgisCanvas.zoomScale, self.canvas.scale(),
			  self.qgisCanvas.extentsChanged, self.onExtentsChangedQgisCanvas
		)
		#
		self._execFunction(
				self.scaleFactorSpin.setValue, 1.0,
				self.scaleFactorSpin.valueChanged, self.onValueChangedScale
		)
		
	def onToggledRender(self, enabled):
		if enabled:
			self.canvas.setMapTool(self.toolPan)
			self._extentsChanged( self.canvas, self.onExtentsChangedMirror, self.qgisCanvas, self.scaleFactorSpin.value() )
			self._textScaleBtnChanched()
			self.canvas.setWheelAction( self.wheelActionCanvas['action'],  self.wheelActionCanvas['zoom'] )			
		else:
			self.canvas.unsetMapTool(self.toolPan)
			self.canvas.setWheelAction( QgsMapCanvas.WheelNothing )
		self.canvas.setRenderFlag( enabled )
		
	def onToggledMarker(self, enabled):
		def setMarker():
			if not self.marker is None:
				self.canvas.scene().removeItem( self.marker )
			self.marker = QgsVertexMarker( self.canvas )
			self.marker.setColor( QColor( 255, 0 , 0 ) )
			self.marker.setPenWidth( 2 )
			self.marker.setIconSize( 8 )
			self.marker.setIconType( QgsVertexMarker.ICON_CROSS)
		if enabled:
			setMarker()
		else:
			if not self.marker is None:
				self.canvas.scene().removeItem( self.marker )
				self.marker = None

	def onToggledExtent(self, enabled):
		def setExtent():
			if not self.extent is None:
				self.canvas.scene().removeItem( self.extent )
			self.extent = QgsRubberBand( self.canvas, False )
			self.extent.setBorderColor( QColor( 255, 0 , 0 ) )
			self.extent.setWidth( 2 )
			#
			self._extent()
# 			self.extent.setIconSize( 8 )
# 			self.extent.setIconType( QgsVertexMarker.ICON_CROSS)
		if enabled:
			setExtent()
		else:
			if not self.extent is None:
				self.canvas.scene().removeItem( self.extent )
				self.extent = None

	def onExtentsChangedMirror(self):
		if not self.renderCheck.isChecked():
			return
		#
		self._extentsChanged( self.qgisCanvas, self.onExtentsChangedQgisCanvas, self.canvas )
		self._textScaleBtnChanched()
		#
		self._execFunction(
				self.scaleFactorSpin.setValue, self.canvas.scale() / self.qgisCanvas.scale(),
				self.scaleFactorSpin.valueChanged, self.onValueChangedScale
		)
		if not self.extent is None: self._extent()

	def onExtentsChangedQgisCanvas(self):
		if not self.renderCheck.isChecked():
			return
		#
		self._extentsChanged( self.canvas, self.onExtentsChangedMirror, self.qgisCanvas, self.scaleFactorSpin.value() )
		self._textScaleBtnChanched()
		if not self.extent is None: self._extent()
		
	def onXYCoordinates(self, point ):
		if not self.marker is None:
			self.marker.setCenter( point )

	def onDestinationCrsChanged_MapUnitsChanged(self):
		prevFlag = self.canvas.renderFlag()
		self.canvas.setRenderFlag( False )
		#
		self.canvas.setDestinationCrs( self.qgisCanvas.mapRenderer().destinationCrs()  )
		self.canvas.setMapUnits( self.qgisCanvas.mapUnits() )
		#
		self.canvas.setRenderFlag( prevFlag )

	def onHasCrsTransformEnabledChanged(self, enabled):
		prevFlag = self.canvas.renderFlag()
		self.canvas.setRenderFlag( False )
		#
		self.canvas.mapRenderer().setProjectionsEnabled( enabled )
		#
		self.canvas.setRenderFlag( prevFlag )
		
	def onLayersWillBeRemoved( self, layerIds ):
		layerIdsLegend = self.ltg.findLayerIds()
		layerIdsRemove = list ( set( layerIds ) & set( layerIdsLegend ) )
		if len( layerIdsRemove ) > 0:
			for item in layerIdsRemove:
				self.ltg.removeChildNode( self.ltg.findLayer( item ) )
			self._tootipStackLayers()

	def onLayersAdded( self, layers ):
		for item in layers:
			self.ltg.addLayer( item )  
		self._tootipStackLayers()

	def onCurrentLayerChanged( self, currentLyr ):
		# Call by LegendWdg
		if not currentLyr is None:
			nameLyr = currentLyr.name()
			title = "%d# %s" % ( self.numMirror, nameLyr )
			enabled = True
		else:
			 title = "%d#" % self.numMirror
			 nameLyr = ''
			 enabled = False
		self.parent.setWindowTitle( title )
		self.selectLayerBtn.setToolTip( nameLyr )
		self.selectLayerBtn.setEnabled( enabled )
	
	def _extentsChanged(self, canvasOrigin, originSlot, canvasDest, scaleFactor=None):
		canvasOrigin.extentsChanged.disconnect( originSlot )
		if scaleFactor is None:
			scale = canvasOrigin.scale()
			canvasOrigin.setExtent( canvasDest.extent() )
			canvasOrigin.zoomScale( scale )
		else:
			canvasOrigin.setExtent( canvasDest.extent() )
			canvasOrigin.zoomScale( scaleFactor * canvasDest.scale() )
		#
		canvasOrigin.extentsChanged.connect( originSlot )

	def _textScaleBtnChanched(self):
		scale = locale.format( "%.0f", self.canvas.scale(), True ) 
		self.scaleBtn.setText("Scale 1:%s" % scale )
		
	def _tootipStackLayers(self):
		layerTrees = self.ltg.findLayers()
		#
		layersDesc = map(lambda x: "%s %s" % ( '+' if  x.isVisible() == Qt.Checked else "  ", x.layerName() ),  layerTrees )\
		if len( layerTrees ) > 0 else ''
		#
		toolTip = '\n'.join( layersDesc )
		self.stackLayersBtn.setToolTip( toolTip )
		
	def _extent(self):
		rect = self.qgisCanvas.extent()
		p1 = QgsPoint( rect.xMinimum() , rect.yMinimum() )
		p2 = QgsPoint( rect.xMinimum() , rect.yMaximum() )
		p3 = QgsPoint( rect.xMaximum() , rect.yMaximum() )
		p4 = QgsPoint( rect.xMaximum() , rect.yMinimum() )
		p5 = QgsPoint( rect.xMinimum() , rect.yMinimum() )
		points = [ p1, p2, p3, p4, p5 ]
		self.extent.setToGeometry(QgsGeometry.fromPolyline (points), None)

	def _execFunction( self, func, arg, signal, slot):
		signal.disconnect( slot )
		func( arg )
		signal.connect( slot )
