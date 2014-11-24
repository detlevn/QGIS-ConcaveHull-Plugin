# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ConcaveHull
                                 A QGIS plugin
 Computes a concave hull containing a set of features
                             -------------------
        begin                : 2014-11-11
        copyright            : (C) 2014 by Detlev Neumann,
                               Dr. Neumann Consulting - Geospatial Services
        email                : dneumann@geospatial-services.de 
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""

def classFactory(iface):
    # load ConcaveHull class from file ConcaveHull
    from concavehull import ConcaveHull
    return ConcaveHull(iface)
