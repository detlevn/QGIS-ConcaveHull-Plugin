# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ConcaveHull
                                 A QGIS plugin
 Computes a concave hull containing a set of features
                              -------------------
        begin                : 2014-11-11
        copyright            : (C) 2014 by Detlev Neumann
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
"""
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from concavehulldialog import ConcaveHullDialog
import os.path
import math


class ConcaveHull:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        localePath = os.path.join(self.plugin_dir, 'i18n', 'concavehull_{}.qm'.format(locale))

        if os.path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = ConcaveHullDialog()

    def initGui(self):
        """
        Create action that will start plugin configuration
        """
        self.action = QAction(
            QIcon(":/plugins/concavehull/icon.png"),
            u"Concave Hull", self.iface.mainWindow())
        # connect the action to the run method
        self.action.triggered.connect(self.run)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&Concave Hull", self.action)

    def unload(self):
        """
        Remove the plugin menu item and icon
        """
        self.iface.removePluginMenu(u"&Concave Hull", self.action)
        self.iface.removeToolBarIcon(self.action)


    def clean_list(self, list_of_points):
        """
        Deletes duplicate points in list_of_points
        """
        return list(set(list_of_points))


    def length(self, vector):
        """
        Returns the number of elements in vector
        """
        return len(vector)


    def find_min_y_point(self, list_of_points):
        """
        gibt denjenigen Punkt der list_of_points mit der kleinsten Y-Koordinate zurück, also den südlichsten Punkt
        """
        min_y_pt = list_of_points[0]
        for point in list_of_points[1:]:
            if point[1] < min_y_pt[1] or (point[1] == min_y_pt[1] and point[0] < min_y_pt[0]):
                min_y_pt = point
        return min_y_pt


    def remove_point(self, vector, element):
        """
        Returns a copy of vector without the given element
        """
        vector.pop(vector.index(element))
        return vector


    def add_point(self, vector, element):
        """
        Returns vector with the given element append to the right
        """
        vector.append(element)
        return vector


    def euclidian_distance(self, point1, point2):
        """
        Returns the euclidian distance of the 2 given points
        """
        return math.sqrt(math.pow(point1[0] - point2[0], 2) + math.pow(point1[1] - point2[1], 2))


    def nearest_points(self, list_of_points, point, k):
        """
        gibt eine Liste mit den Indizes der k nächsten Nachbarn aus list_of_points zum angegebenen Punkt zurück.
        Das Maß für die Nähe ist die euklidische Distanz. Intern wird k auf das Minimum zwischen dem gegebenen Wert
        für k und der Anzahl der Punkte in list_of_points gesetzt
        """
        # Liste aus den Entfernungen zwischen dem aktuellen Punkt point und den übrigen Punkten in list_of_points
        # berechnen und zusammen mit ihrem Listenindex in list_of_distances ablegen
        list_of_distances = []
        for index in range(len(list_of_points)):
            list_of_distances.append((self.euclidian_distance(list_of_points[index], point), index))

        # nach den Abständen sortieren
        list_of_distances.sort()

        # die Indizes der k nächstgelegenen Punkte
        nearest_list = []
        #for index in range(min(k, len(list_of_points)-1)):
        for index in range(min(k, len(list_of_points))):
            nearest_list.append((list_of_points[list_of_distances[index][1]]))
        return nearest_list


    def angle(self, from_point, to_point):
        """
        gibt den Winkel der durch from_point nach to_point gerichteten Strecke in Radiant zurück
        (nach oben gerichtet positiv, nach unten negativ, von rechts beginnend nach links bis Pi zunehmend)
        returns the angle of the line segment in radians
        """
        return math.atan2(to_point[1] - from_point[1], to_point[0] - from_point[0])


    def sort_by_angle(self, list_of_points, last_point, last_angle):
        """
        gibt die Punkte in list_of_points in absteigender Reihenfolge des Winkels zum letzten Segment der Hülle zurück,
        gemessen im Uhrzeigersinn. Es wird also immer der rechteste der benachbarten  Punkte ausgewählt. Der erste
        Punkt dieser Liste wird der nächste Punkt der Hülle.
        """
        def getkey(item):
            return self.angle_difference(last_angle, self.angle(last_point, item))
        vertex_list = sorted(list_of_points, key=getkey, reverse=True)
        return vertex_list


    def angle_difference(self, angle1, angle2):
        """
        gibt die Differenz zwischen den gegebenen Winkeln im Uhrzeigersinn zurück (alles in Radiant)
        Todo: vereinfachen, zusammenfassen wenn möglich
        """
        if (angle1 > 0 and angle2 >= 0) and angle1 > angle2:
            return abs(angle1 - angle2)
        elif (angle1 >= 0 and angle2 > 0) and angle1 < angle2:
            return 2 * math.pi + angle1 - angle2
        elif (angle1 < 0 and angle2 <= 0) and angle1 < angle2:
            return 2 * math.pi + angle1 + abs(angle2)
        elif (angle1 <= 0 and angle2 < 0) and angle1 > angle2:
            return abs(angle1 - angle2)
        elif angle1 <= 0 < angle2:
            return 2 * math.pi + angle1 - angle2
        elif angle1 >= 0 >= angle2:
            return angle1 + abs(angle2)
        else:
            return 0


    def intersect_q(self, line1, line2):
        """
        returns True if the two given lines segments intersect each other, and False otherwise.
        gibt True zurück, wenn sich die gegebenen Strecken schneiden, sonst False
        """
        a1 = line1[1][1] - line1[0][1]
        b1 = line1[0][0] - line1[1][0]
        c1 = a1 * line1[0][0] + b1 * line1[0][1]
        a2 = line2[1][1] - line2[0][1]
        b2 = line2[0][0] - line2[1][0]
        c2 = a2 * line2[0][0] + b2 * line2[0][1]
        tmp = (a1 * b2 - a2 * b1)
        if tmp == 0:
            return False
        sx = (c1 * b2 - c2 * b1) / tmp
        if (sx > line1[0][0] and sx > line1[1][0]) or (sx > line2[0][0] and sx > line2[1][0]) or\
                (sx < line1[0][0] and sx < line1[1][0]) or (sx < line2[0][0] and sx < line2[1][0]):
            return False
        sy = (a1 * c2 - a2 * c1) / tmp
        if (sy > line1[0][1] and sy > line1[1][1]) or (sy > line2[0][1] and sy > line2[1][1]) or\
                (sy < line1[0][1] and sy < line1[1][1]) or (sy < line2[0][1] and sy < line2[1][1]):
            return False
        return True


    def point_in_polygon_q(self, point, list_of_points):
        """
        gibt True zurück, wenn der gegebene Punkt innerhalb des durch die list_of_points bezeichneten Polygons liegt,
        sonst False. Die Funktion prüft, mit wievielen Segmenten sich die Strecke ((0,0), point) schneidet. Bei einer
        ungerade Anzahl von Schnitten liegt der Punkt innerhalb, sonst außerhalb des bezeichneten Polygons.

        Basierend auf der "Ray Casting Method" u.a. beschrieben im Blog
        http://geospatialpython.com/2011/01/point-in-polygon.html von Joel Lawhead

        """
        x = point[0]
        y = point[1]
        poly = [(pt[0], pt[1]) for pt in list_of_points]
        n = len(poly)
        inside = False

        p1x, p1y = poly[0]
        for i in range(n + 1):
            p2x, p2y = poly[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xints:
                            inside = not inside
            p1x, p1y = p2x, p2y
        #if not inside:  print(point) ## Debug
        return inside


    def write_wkt(self, line_string):
        """
        Ausgabe der Hülle als Well Known Text
        """
        file_name = 'hull2.wkt'
        if os.path.isfile(file_name):
            outfile = open(file_name, 'a')
        else:
            outfile = open(file_name, 'w')
            outfile.write('%s\n' % 'WKT')
        wkt = 'POLYGON((' + str(line_string[0][0]) + ' ' + str(line_string[0][1])
        for p in line_string[1:]:
            wkt += ', ' + str(p[0]) + ' ' + str(p[1])
        wkt += '))'
        outfile.write('%s\n' % wkt)
        outfile.close()


    def as_wkt(self, line_string):
        """
        Rückgabe der Hülle als Well Known Text
        """
        wkt = 'POLYGON((' + str(line_string[0][0]) + ' ' + str(line_string[0][1])
        for p in line_string[1:]:
            wkt += ', ' + str(p[0]) + ' ' + str(p[1])
        wkt += '))'
        return wkt


    def write_segments(self, linestring):
        """
        nur zum Debuggen: Ausgabe der Hülle für die reachable-Webseite
        """
        outfile = open("boundData.csv", "w")
        for p in range(len(linestring)-1):
            outfile.write('hull\t%s\t%s\t%s\t%s\n' % (linestring[p][0], linestring[p][1],
                                                            linestring[p+1][0], linestring[p+1][1]))
        outfile.close()


    def concave_hull(self, points_list, k):
        """
        Eingabe: eine Liste von Punkten (points_list) als Liste von Tuplen; Anzahl der Nachbarpunkte (k)
        Ausgabe: eine sortierte Liste von Stützpunkten, die eine Hülle um die Punkte beschreiben
        """
        # wenn die Anzahl der Nachbarn über der Anzahl der gegebenen Punkte liegt bricht das Programm ab,
        # es kann nicht mehr konvergieren
        if k > len(points_list):
             return []  #None

        # die Anzahl der nächsten Nachbarn muss größer als 3 sein
        #kk = max(k, 3)
        kk = max(k, 2)

        # delete duplicate points
        dataset = self.clean_list(points_list)

        # if dataset has less then 3 points no polygon can be created and an empty list will be returned
        if len(dataset) < 3:
            return []  #None

        # bei 3 Punkten besteht die Hüllkurve aus genau diesen Punkten; es wird der erste Punkt noch einmal
        # angefügt, damit ein Polygon gebildet werden kann
        if len(dataset) == 3:
            return self.add_point(dataset, dataset[0])

        # make sure that k neighbours can be found
        kk = min(kk, len(dataset))

        # es wird mit dem untersten Punkt gestarten
        first_point = self.find_min_y_point(dataset)

        # die Hülle wird mit diesem Punkt initialisiert
        hull = [first_point]

        # der erste Punkt ist jetzt der aktuelle Punkt
        current_point = first_point

        # der erste Punkt wird aus dem Datensatz entfernt
        dataset = self.remove_point(dataset, first_point)
        previous_angle = math.pi

        # Step zählt die jeweils neuen Segmente
        step = 2

        # solange die Suche nach der Hülle nicht am Ausgangspunkt angekommen ist oder keine Punkte mehr vorhanden sind
        while (current_point != first_point) or (step == 2) and (len(dataset) > 0):

            # nach 3 Iterationen wird der Startpunkt wieder hinzugefügt, sonst kann ja kein Polygonschluss gebildet werden
            if step == 5:
                dataset = self.add_point(dataset, first_point)

            # die nächsten Nachbarn des aktuellen Punktes suchen
            k_nearest_points = self.nearest_points(dataset, current_point, kk)

            # sort the candidates (neighbours) in descending order of right-hand turn
            # die Kandidaten (Nachbarpunkte) werden in absteigender Reihenfolge ihrer Orientierung zum letzten
            # Segment der Hülle im Uhrzeigersinn sortiert, d.h. die Hülle soll gegen den Uhrzeigersinn durch möglichst
            # viele Punkte konstruiert werden
            c_points = self.sort_by_angle(k_nearest_points, current_point, previous_angle)

            its = True
            i = -1

            # es wird der nächstgelegene Punkt gesucht, dessen Verbindungslinie keines der bereits ermittelten Segmente
            # schneidet
            while its is True and (i < len(c_points)-1):
                i += 1
                if c_points[i] == first_point:
                    last_point = 1
                else:
                    last_point = 0
                j = 2
                its = False

                while its is False and (j < len(hull) - last_point):
                    its = self.intersect_q((hull[step-2], c_points[i]), (hull[step-2-j], hull[step-1-j]))
                    j += 1

            # da offenbar alle Verbindungen mit den Kandidaten bestehende Segmente schneiden würde, kommt also keiner von
            # ihnen in Frage und die Suche wird mit einer größeren Anzahl von Nachbarn erneut gestartet
            # Todo: möglicherweise ist es sinnvoll nicht global die Nachbarschaft zu vergrößern sondern nur lokal, damit
            # Todo: Bereiche, die feiner strukturiert werden können, dadurch nicht generalisiert werden
            # Todo: Solange zurückspringen zu k_nearest_points = nearest_points(dataset, current_point, kk) bis kk==Anzahl
            # Todo: der Punkte. Sollte dann auch kein geeigneter nächster Punkt gefunden werden, dann alle Zähler
            # Todo: zurückstellen und die Rekursion starten.
            #
            # Todo: nachdem eine Hülle gefunden, aber Punkte übrig sind, werden nur diese erneut bearbeitet. Die zusätzliche
            # Todo: Hülle darf sich nicht mit einer bereits gefundenen Hülle schneiden, sonst werden die Punkte gelöscht

            if its is True:
                return self.concave_hull(points_list, kk + 1)

            # der erste Punkt, der die Anforderungen erfüllt, wird zum aktuellen Punkt und an die Hülle angehängt
            current_point = c_points[i]
            hull = self.add_point(hull, current_point)

            # den Winkel des Vektors vom aktuellen Punkt (also jetzt der Endpunkt des letzten Segmentes der Hülle)
            # zum Vorgänger (also im Prinzip das letzte Segment im umgekehrter Richtung) bestimmen
            previous_angle = self.angle(hull[step - 1], hull[step - 2])

            # remove current_point from dataset
            dataset = self.remove_point(dataset, current_point)

            # Schrittzähler erhöhen
            step += 1

        all_inside = True
        i = len(dataset)-1

        # check if all points are within the created polygon
        while (all_inside is True) and (i >= 0):
            all_inside = self.point_in_polygon_q(dataset[i], hull)
            i -= 1

        # since at least one point is out of the computed polygon, try again with a higher number of neighbours
        if all_inside is False:
            return self.concave_hull(points_list, kk + 1)

        # a valid hull has been constructed
        #as_segments(hull) ## Debug
        return [hull]


    def concave_hull2(self, points_list, hull_list, k):
        """
        Eingabe: eine Liste von Punkten (points_list) als Liste von Tuplen; Anzahl der Nachbarpunkte (k)
        Ausgabe: eine sortierte Liste von Stützpunkten, die eine Hülle um die Punkte beschreiben
        """
        # wenn die Anzahl der Nachbarn über der Anzahl der gegebenen Punkte liegt bricht das Programm ab,
        # es kann nicht mehr konvergieren
        if k > len(points_list):
             return hull_list

        # die Anzahl der nächsten Nachbarn muss größer als 3 sein
        #kk = max(k, 3)
        kk = max(k, 2)

        # doppelte Punkte löschen
        dataset = self.clean_list(points_list)
        QMessageBox.information(self.iface.mainWindow(), "424dataset", str(len(dataset)))

        # es werden mindestens 3 Punkte benötigt
        if len(dataset) < 3:
            return hull_list

        # bei 3 Punkten besteht die Hüllkurve aus genau diesen Punkten; es wird der erste Punkt noch einmal
        # angefügt, damit ein Polygon gebildet werden kann
        if len(dataset) == 3:
            hull_list.append(self.add_point(dataset, dataset[0]))
            QMessageBox.information(self.iface.mainWindow(), "434hull_list", str(hull_list))
            return hull_list

        # make sure that k neighbours can be found
        kk = min(kk, len(dataset))

        # es wird mit dem untersten Punkt gestarten
        first_point = self.find_min_y_point(dataset)

        # die Hülle wird mit diesem Punkt initialisiert
        hull = [first_point]

        # der erste Punkt ist jetzt der aktuelle Punkt
        current_point = first_point

        # der erste Punkt wird aus dem Datensatz entfernt
        dataset = self.remove_point(dataset, first_point)
        previous_angle = math.pi

        # Step zählt die jeweils neuen Segmente
        step = 2

        # solange die Suche nach der Hülle nicht am Ausgangspunkt angekommen ist oder keine Punkte mehr vorhanden sind
        while (current_point != first_point) or (step == 2) and (len(dataset) > 0):

            # nach 3 Iterationen wird der Startpunkt wieder hinzugefügt, sonst kann ja kein Polygonschluss gebildet werden
            if step == 5:
                dataset = self.add_point(dataset, first_point)

            # die nächsten Nachbarn des aktuellen Punktes suchen
            # Todo: wenn einer der kk Nachbarn deutlich weiter weg liegt, als die kk-1, dann den kk-1. verwenden
            k_nearest_points = self.nearest_points(dataset, current_point, kk)

            # sort the candidates (neighbours) in descending order of right-hand turn
            # die Kandidaten (Nachbarpunkte) werden in absteigender Reihenfolge ihrer Orientierung zum letzten
            # Segment der Hülle im Uhrzeigersinn sortiert, d.h. die Hülle soll gegen den Uhrzeigersinn durch möglichst
            # viele Punkte konstruiert werden
            c_points = self.sort_by_angle(k_nearest_points, current_point, previous_angle)

            its = True
            i = -1

            # es wird der nächstgelegene Punkt gesucht, dessen Verbindungslinie keines der bereits ermittelten Segmente
            # schneidet
            while its is True and (i < len(c_points)-1):
                i += 1
                if c_points[i] == first_point:
                    last_point = 1
                else:
                    last_point = 0
                j = 2
                its = False

                while its is False and (j < len(hull) - last_point):
                    its = self.intersect_q((hull[step-2], c_points[i]), (hull[step-2-j], hull[step-1-j]))
                    j += 1

            # da offenbar alle Verbindungen mit den Kandidaten bestehende Segmente schneiden würde, kommt also keiner von
            # ihnen in Frage und die Suche wird mit einer größeren Anzahl von Nachbarn erneut gestartet
            #
            # Todo Die zusätzliche Hülle darf sich nicht mit einer bereits gefundenen Hülle schneiden, sonst werden die Punkte gelöscht

            if its is True:
                return self.concave_hull2(points_list, hull_list, kk + 1)

            # der erste Punkt, der die Anforderungen erfüllt, wird zum aktuellen Punkt und an die Hülle angehängt
            current_point = c_points[i]
            hull = self.add_point(hull, current_point)

            # den Winkel des Vektors vom aktuellen Punkt (also jetzt der Endpunkt des letzten Segmentes der Hülle)
            # zum Vorgänger (also im Prinzip das letzte Segment im umgekehrter Richtung) bestimmen
            previous_angle = self.angle(hull[step - 1], hull[step - 2])

            # remove current_point from dataset
            dataset = self.remove_point(dataset, current_point)

            # Schrittzähler erhöhen
            step += 1

        all_inside = True
        i = len(dataset)-1

        hull_list.append(hull)

        # check if all points are within the created polygon
        while (all_inside is True) and (i >= 0):
            all_inside = self.point_in_polygon_q(dataset[i], hull)
            i -= 1

        # Wurde eine Hülle gefunden, sind aber Punkte übrig sind und liegen davon welche außerhalb,
        # erfolgt die Berechnung eines weiteren Polygons für diese Teilmenge .
        QMessageBox.information(self.iface.mainWindow(), "532hull_list", str(hull_list))
        if all_inside is False:

            i = len(dataset)-1
            while i >= 0:
                if self.point_in_polygon_q(dataset[i], hull) is True:
                    dataset.pop(i)
                i -= 1

            QMessageBox.information(self.iface.mainWindow(), "544dataset", str(dataset))
            return self.concave_hull2(dataset, hull_list, 3) # kk?

        # One or more hulls have been constructed
        #as_segments(hull) ## Debug
        return hull_list


    def enableUseOfGlobalCrs(self):
        """
        Set new layers to use the project CRS.
        Code snipped taken from http://pyqgis.blogspot.co.nz/2012/10/basics-automatic-use-of-crs-for-new.html

        :return: string
        """
        settings = QSettings()
        old_behaviour = settings.value('/Projections/defaultBehaviour')
        settings.setValue('/Projections/defaultBehaviour', 'useProject')
        return old_behaviour


    def disableUseOfGlobalCrs(self, default_behaviour='prompt'):
        """
        Enables old settings again. If argument is missing then set behaviour to prompt.

        :param default_behaviour:
        :return: None
        """
        settings = QSettings()
        settings.setValue('/Projections/defaultBehaviour', default_behaviour)
        return None


    def createOutputFeature(self, geom, layer_name='ConcaveHull'):
        """
        Creates a memory layer named layer_name, default name ConcaveHull, using project CRS and
        suppressing the CRS settings dialog

        :param geom: polygon as a WKT string
        :param layer_name: string
        :return: None
        """
        if not QgsMapLayerRegistry.instance().mapLayersByName(layer_name):
            old_behaviour = self.enableUseOfGlobalCrs()
            layer = QgsVectorLayer('Polygon', layer_name, 'memory')
            provider = layer.dataProvider()
            QgsMapLayerRegistry.instance().addMapLayer(layer)
            self.disableUseOfGlobalCrs(old_behaviour)
        else:
            layer = QgsMapLayerRegistry.instance().mapLayersByName(layer_name)[0]
            provider = layer.dataProvider()

        # add a feature
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromWkt(geom))
        provider.addFeatures([feature])

        # because change of extent in provider is not propagated to the layer
        layer.updateExtents()
        layer.triggerRepaint()


    def extractPoints(self, geom):
        """
        Generate list of QgsPoints from QgsGeometry *geom* ( can be point, line, or polygon )
        Code taken from fTools plugin
        """
        multi_geom = QgsGeometry()
        temp_geom = []
        if geom.type() == 0: # it's a point
            if geom.isMultipart():
                temp_geom = geom.asMultiPoint()
            else:
                temp_geom.append(geom.asPoint())
        if geom.type() == 1: # it's a line
            if geom.isMultipart():
                multi_geom = geom.asMultiPolyline() #multi_geog is a multiline
                for i in multi_geom: #i is a line
                    temp_geom.extend( i )
            else:
                temp_geom = geom.asPolyline()
        elif geom.type() == 2: # it's a polygon
            if geom.isMultipart():
                multi_geom = geom.asMultiPolygon() #multi_geom is a multipolygon
                for i in multi_geom: #i is a polygon
                    for j in i: #j is a line
                        temp_geom.extend( j )
            else:
                multi_geom = geom.asPolygon() #multi_geom is a polygon
                for i in multi_geom: #i is a line
                    temp_geom.extend( i )
        return temp_geom


    def getVectorLayersByType(self, geomType=None, skipActive=False):
        """
        Returns a dict of layers [name: id] in the project for the given *geomType*;
        geomTypes are 0: point, 1: line, 2: polygon
        If *skipActive* is True the active Layer is not included.
        code taken from DigitizingTools plugin, (C) 2013 by Bernhard Stroebl
        """
        layerList = {}
        for aLayer in self.iface.legendInterface().layers():
            if 0 == aLayer.type():   # vectorLayer
                if skipActive and (self.iface.mapCanvas().currentLayer().id() == aLayer.id()):
                    continue
                else:
                    if geomType is not None:
                        if isinstance(geomType,  int):
                            if aLayer.geometryType() == geomType:
                                layerList[aLayer.name()] =  aLayer.id()
                        else:
                            layerList[aLayer.name()] =  aLayer.id()
        return layerList


    def setOutputLayerComboBox(self, index=None):
        # Todo: Geometrietyp beruecksichtigen !!
        self.dlg.cb_output.clear()
        layer_list = self.getVectorLayersByType(2, False)
        if len(layer_list) > 0:
            lid = 0
            for aName in layer_list:
                self.dlg.cb_output.addItem("")
                self.dlg.cb_output.setItemText(lid, aName)
                if aName == index:
                    self.dlg.cb_output.setCurrentIndex(lid)
                lid += 1


    # run method that performs all the real work
    def run(self):
        # set dialog widgets
        self.dlg.ls_layers.clear()
        has_selected_features = False

        # all vector layers are added to the list view
        for layer in self.iface.legendInterface().layers():
            if layer.type() == QgsMapLayer.VectorLayer:
                # if there are selected features toggle has_selected_features
                if layer.selectedFeatureCount():
                    has_selected_features = True
                self.dlg.ls_layers.addItem(layer.name())

        # if at least one vector layer has selected features enable checkbutton cb_selected_only
        if has_selected_features:
            self.dlg.cb_selected_only.setEnabled(True)
            self.dlg.cb_selected_only.setChecked(True)
        else:
            self.dlg.cb_selected_only.setEnabled(False)

        # initialize cb_output
        # remember the layer being selected the last time
        lbid = self.dlg.cb_output.currentText()
        # populate the combo box with the polygon layers listed in the current legend
        self.setOutputLayerComboBox(lbid)

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()

        # See if OK was pressed
        if result == 1:
            geom = []
            # read selected list entries and get the map layer
            for layer_name in self.dlg.ls_layers.selectedItems():
                active_layer = QgsMapLayerRegistry.instance().mapLayersByName(layer_name.text())[0]
                # get all or the currently selected features according to state of cb_selected_only
                # convert each feature to points
                if active_layer.selectedFeatureCount() and self.dlg.cb_selected_only.checkState():
                    for feat in active_layer.selectedFeatures():
                        geom.extend(self.extractPoints(feat.geometry()))
                else:
                    for feat in active_layer.getFeatures():
                        geom.extend(self.extractPoints(feat.geometry()))

            # generate the hull geometry
            ##QMessageBox.information(self.iface.mainWindow(), "geom", str(geom))
            the_hull = self.concave_hull(geom, self.dlg.sb_neighbors.value())
            ##the_hull = self.concave_hull2(geom, [], self.dlg.sb_neighbors.value())
            ##QMessageBox.information(self.iface.mainWindow(), "hull711", str(the_hull))

            # write hull geometry to memory layer
            ##self.createOutputFeature(self.as_wkt(the_hull), self.dlg.cb_output.currentText())
            for part in the_hull:
                #QMessageBox.information(self.iface.mainWindow(), "hull", str(the_hull))
                #QMessageBox.information(self.iface.mainWindow(), "part", str(part))
                self.createOutputFeature(self.as_wkt(part), self.dlg.cb_output.currentText())

            pass
