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
from qgis.gui import QgsMessageBar

# Initialize Qt resources from file resources.py
import resources_rc

# Import the code for the dialog
from concavehulldialog import ConcaveHullDialog
import os.path
import math
from shared_nearest_neighbor_clustering import SSNClusters

try:
    _encoding = QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig)

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

        # get reference to the QGIS message bar
        self.msg_bar = self.iface.messageBar()

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
        self.iface.addPluginToVectorMenu(u"&Concave Hull", self.action)

    def unload(self):
        """
        Remove the plugin menu item and icon
        """
        self.iface.removePluginVectorMenu(u"&Concave Hull", self.action)
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
        Returns that point of *list_of_points* having minimal y-coordinate

        :param list_of_points: list of tuples
        :return: tuple (x, y)
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
        Returns the euclidian distance of the 2 given points.

        :param point1: tuple (x, y)
        :param point2: tuple (x, y)
        :return: float
        """
        return math.sqrt(math.pow(point1[0] - point2[0], 2) + math.pow(point1[1] - point2[1], 2))

    def nearest_points(self, list_of_points, point, k):
        """
        gibt eine Liste mit den Indizes der k nächsten Nachbarn aus list_of_points zum angegebenen Punkt zurück.
        Das Maß für die Nähe ist die euklidische Distanz. Intern wird k auf das Minimum zwischen dem gegebenen Wert
        für k und der Anzahl der Punkte in list_of_points gesetzt

        :param list_of_points: list of tuples
        :param point: tuple (x, y)
        :param k: integer
        :return: list of k tuples
        """
        # build a list of tuples of distances between point *point* and every point in *list_of_points*, and
        # their respective index of list *list_of_distances*
        list_of_distances = []
        for index in range(len(list_of_points)):
            list_of_distances.append((self.euclidian_distance(list_of_points[index], point), index))

        # sort distances in ascending order
        list_of_distances.sort()

        # get the k nearest neighbors of point
        nearest_list = []
        for index in range(min(k, len(list_of_points))):
            nearest_list.append((list_of_points[list_of_distances[index][1]]))
        return nearest_list

    def angle(self, from_point, to_point):
        """
        Returns the angle of the directed line segment, going from *from_point* to *to_point*, in radians. The angle is
        positive for segments with upward direction (north), otherwise negative (south). Values ranges from 0 at the
        right (east) to pi at the left side (west).

        :param from_point: tuple (x, y)
        :param to_point: tuple (x, y)
        :return: float
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
        Calculates the difference between the given angles in clockwise direction as radians.

        :param angle1: float
        :param angle2: float
        :return: float; between 0 and 2*Pi
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

    def intersect(self, line1, line2):
        """
        Returns True if the two given line segments intersect each other, and False otherwise.

        :param line1: 2-tuple of tuple (x, y)
        :param line2: 2-tuple of tuple (x, y)
        :return: boolean
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
        Return True if given point *point* is laying in the polygon described by the vertices *list_of_points*,
        otherwise False

        Based on the "Ray Casting Method" described by Joel Lawhead in this blog article:
        http://geospatialpython.com/2011/01/point-in-polygon.html

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

        return inside

    def write_wkt(self, line_string, file_name):
        """
        Writes the geometry described by line_string in Well Known Text format to file

        :param line_string: list of tuples (x, y)
        :return: None
        """
        if file_name is None:
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
        return None

    def as_wkt(self, line_string):
        """
        Returns the geometry described by line_string in Well Known Text format

        :param line_string: list of tuples (x, y)
        :return: polygon geometry as WTK
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
        Calculates a valid concave hull polygon containing all given points. The algorithm searches for that
        point in the neighborhood of k nearest neighbors which maximizes the rotation angle in clockwise direction
        without intersecting any previous line segments.

        This is an implementation of the algorithm described by Adriano Moreira and Maribel Yasmina Santos:
        CONCAVE HULL: A K-NEAREST NEIGHBOURS APPROACH FOR THE COMPUTATION OF THE REGION OCCUPIED BY A SET OF POINTS.
        GRAPP 2007 - International Conference on Computer Graphics Theory and Applications; pp 61-68.

        :param points_list: list of tuples (x, y)
        :param k: integer
        :return: list of tuples (x, y)
        """
        # return an empty list if not enough points are given
        if k > len(points_list):
            return None

        # the number of nearest neighbors k must be greater than or equal to 3
        # kk = max(k, 3)
        kk = max(k, 2)

        # delete duplicate points
        point_set = self.clean_list(points_list)

        # if point_set has less then 3 points no polygon can be created and an empty list will be returned
        if len(point_set) < 3:
            return None

        # if point_set has 3 points then these are already vertices of the hull. Append the first point to
        # close the hull polygon
        if len(point_set) == 3:
            return self.add_point(point_set, point_set[0])

        # make sure that k neighbours can be found
        kk = min(kk, len(point_set))

        # start with the point having the smallest y-coordinate (most southern point)
        first_point = self.find_min_y_point(point_set)

        # add this points as the first vertex of the hull
        hull = [first_point]

        # make the first vertex of the hull to the current point
        current_point = first_point

        # remove the point from the point_set, to prevent him being among the nearest points
        point_set = self.remove_point(point_set, first_point)
        previous_angle = math.pi

        # step counts the number of segments
        step = 2

        # as long as point_set is not empty or search is returning to the starting point
        while (current_point != first_point) or (step == 2) and (len(point_set) > 0):

            # after 3 iterations add the first point to point_set again, otherwise a hull cannot be closed
            if step == 5:
                point_set = self.add_point(point_set, first_point)

            # search the k nearest neighbors of the current point
            k_nearest_points = self.nearest_points(point_set, current_point, kk)

            # sort the candidates (neighbors) in descending order of right-hand turn. This way the algorithm progresses
            # in clockwise direction through as many points as possible
            c_points = self.sort_by_angle(k_nearest_points, current_point, previous_angle)

            its = True
            i = -1

            # search for the nearest point to which the connecting line does not intersect any existing segment
            while its is True and (i < len(c_points)-1):
                i += 1
                if c_points[i] == first_point:
                    last_point = 1
                else:
                    last_point = 0
                j = 2
                its = False

                while its is False and (j < len(hull) - last_point):
                    its = self.intersect((hull[step-2], c_points[i]), (hull[step-2-j], hull[step-1-j]))
                    j += 1

            # there is no candidate to which the connecting line does not intersect any existing segment, so the
            # for the next candidate fails. The algorithm starts again with an increased number of neighbors
            if its is True:
                return self.concave_hull(points_list, kk + 1)

            # the first point which complies with the requirements is added to the hull and gets the current point
            current_point = c_points[i]
            hull = self.add_point(hull, current_point)

            # calculate the angle between the last vertex and his precursor, that is the last segment of the hull
            # in reversed direction
            previous_angle = self.angle(hull[step - 1], hull[step - 2])

            # remove current_point from point_set
            point_set = self.remove_point(point_set, current_point)

            # increment counter
            step += 1

        all_inside = True
        i = len(point_set)-1

        # check if all points are within the created polygon
        while (all_inside is True) and (i >= 0):
            all_inside = self.point_in_polygon_q(point_set[i], hull)
            i -= 1

        # since at least one point is out of the computed polygon, try again with a higher number of neighbors
        if all_inside is False:
            return self.concave_hull(points_list, kk + 1)

        # a valid hull has been constructed
        #as_segments(hull) ## Debug
        #return [hull]
        return hull

    def enable_use_of_global_CRS(self):
        """
        Set new layers to use the project CRS.
        Code snipped taken from http://pyqgis.blogspot.co.nz/2012/10/basics-automatic-use-of-crs-for-new.html

        Example: old_behaviour = enable_use_of_global_CRS()

        :return: string
        """
        settings = QSettings()
        old_behaviour = settings.value('/Projections/defaultBehaviour')
        settings.setValue('/Projections/defaultBehaviour', 'useProject')
        return old_behaviour

    def disable_use_of_global_CRS(self, default_behaviour='prompt'):
        """
        Enables old settings again. If argument is missing then set behaviour to prompt.

        Example: disable_use_of_global_CRS(old_behaviour)

        :param default_behaviour:
        :return: None
        """
        settings = QSettings()
        settings.setValue('/Projections/defaultBehaviour', default_behaviour)
        return None

    def create_output_feature(self, geom, layer_name='ConcaveHull'):
        """
        Creates a memory layer named layer_name, default name ConcaveHull, using project CRS and
        suppressing the CRS settings dialog

        :param geom: list of polygons as a WKT string
        :param layer_name: string
        :return: boolean
        """
        if self.dlg.rb_shapefile.isChecked():
            shape_filename = self.dlg.ed_output_layer.text()
            layer_name = 'ConcaveHull'
            if shape_filename == '':
                msg = self.msg_bar.createMessage(_translate('ConcaveHull', 'No shapefile name specified', None))
                self.msg_bar.pushWidget(msg, QgsMessageBar.CRITICAL, 5)
                return False
        else:
            if self.dlg.rb_new_memory_layer.isChecked():
                layer_name = self.dlg.ed_memory_layer.text()
            else:
                layer_name = self.dlg.cb_output.currentText()

        # if the layer does not exist it has to be created
        if not QgsMapLayerRegistry.instance().mapLayersByName(layer_name):
            srs = self.iface.mapCanvas().mapRenderer().destinationCrs().authid()
            layer = QgsVectorLayer('Polygon?crs=' + str(srs), layer_name, 'memory')
            provider = layer.dataProvider()

        # if the layer already exists
        else:
            layer = QgsMapLayerRegistry.instance().mapLayersByName(layer_name)[0]
            provider = layer.dataProvider()

        # add hull geometry to data provider
        for hull in geom:
            feature = QgsFeature()
            feature.setGeometry(QgsGeometry.fromWkt(hull))
            provider.addFeatures([feature])

        # if new memory layer simply add memory layer to the map
        if self.dlg.rb_new_memory_layer.isChecked():
            QgsMapLayerRegistry.instance().addMapLayer(layer)

        # if features go to shapefile dump memory layer to shapefile
        elif self.dlg.rb_shapefile.isChecked():
            error = QgsVectorFileWriter.writeAsVectorFormat(layer, shape_filename, 'CP1250', None, 'ESRI Shapefile')
            if error != QgsVectorFileWriter.NoError:
                msg = self.msg_bar.createMessage(_translate('ConcaveHull', 'Error writing shapefile: ' + error, None))
                self.msg_bar.pushWidget(msg, QgsMessageBar.ERROR, 5)
                return False

            # add the new layer to the map
            if self.dlg.cb_add_to_map.isChecked():
                base_name = os.path.splitext(os.path.basename(str(shape_filename)))[0]
                layer_name = QgsVectorLayer(shape_filename, base_name, 'ogr')
                QgsMapLayerRegistry.instance().addMapLayer(layer_name)

        # because change of extent in provider is not propagated to the layer
        layer.updateExtents()
        layer.triggerRepaint()
        return True

    def extract_points(self, geom):
        """
        Generate list of QgsPoints from QgsGeometry *geom* ( can be point, line, or polygon )
        Code taken from fTools plugin

        :param geom: an arbitrary geometry feature
        :return: list of points
        """
        multi_geom = QgsGeometry()
        temp_geom = []
        # point geometry
        if geom.type() == 0:
            if geom.isMultipart():
                temp_geom = geom.asMultiPoint()
            else:
                temp_geom.append(geom.asPoint())
        # line geometry
        if geom.type() == 1:
            # if multipart feature explode to single part
            if geom.isMultipart():
                multi_geom = geom.asMultiPolyline()
                for i in multi_geom:
                    temp_geom.extend( i )
            else:
                temp_geom = geom.asPolyline()
        # polygon geometry
        elif geom.type() == 2:
            # if multipart feature explode to single part
            if geom.isMultipart():
                multi_geom = geom.asMultiPolygon()
                # now single part polygons
                for i in multi_geom:
                    # explode to line segments
                    for j in i:
                        temp_geom.extend( j )
            else:
                multi_geom = geom.asPolygon()
                # explode to line segments
                for i in multi_geom:
                    temp_geom.extend( i )
        return temp_geom

    def get_vector_layers_by_type(self, geom_type=None, skip_active=False):
        """
        Returns a dict of layers [name: id] in the project for the given geom_type.
        If skip_active is True the active layer is not included.
        Code taken from DigitizingTools plugin, (C) 2013 by Bernhard Stroebl

        :param geom_type: integer; geomTypes are 0: point, 1: line, 2: polygon
        :return: dict of layers with given geometry type
        """
        layer_list = {}
        for layer in self.iface.legendInterface().layers():
            if 0 == layer.type():   # vectorLayer
                if skip_active and (self.iface.mapCanvas().currentLayer().id() == layer.id()):
                    continue
                else:
                    if geom_type is not None:
                        if isinstance(geom_type,  int):
                            if layer.geometryType() == geom_type:
                                layer_list[layer.name()] = layer.id()
                        else:
                            layer_list[layer.name()] = layer.id()
        return layer_list

    def set_output_layer_combobox(self, geom_type=None, item=''):
        """
        Populates the ComboBox with all layers of the given geometry type geom_type, and sets
        currentIndex to the entry named index.

        :param geom_type: integer; geomTypes are 0: point, 1: line, 2: polygon
        :param index: string; name of the ComboBox entry to set currentIndex to
        :return: None
        """
        self.dlg.cb_output.clear()
        layer_list = self.get_vector_layers_by_type(geom_type, False)
        if len(layer_list) > 0:
            for index, aName in enumerate(layer_list):
                self.dlg.cb_output.addItem('')
                self.dlg.cb_output.setItemText(index, aName)
                if aName == item:
                    self.dlg.cb_output.setCurrentIndex(index)
        return None

    # run method that performs all the real work
    def run(self):
        # set dialog widgets
        self.dlg.ls_layers.clear()
        self.dlg.buttonBox.button(QDialogButtonBox.Ok).setDisabled(True)
        has_selected_features = False

        # check if an active layer exists
        active_layer_name = ''
        if self.iface.activeLayer() is not None:
            active_layer_name = self.iface.activeLayer().name()

        # all vector layers get added to the list
        for index, layer in enumerate(self.iface.legendInterface().layers()):
            if layer.type() == QgsMapLayer.VectorLayer:
                # if there are selected features toggle has_selected_features
                if layer.selectedFeatureCount():
                    has_selected_features = True
                self.dlg.ls_layers.addItem(layer.name())
                # select the active layer by default
                if layer.name() == active_layer_name:
                    self.dlg.ls_layers.setCurrentRow(index)

        # if at least one vector layer has selected features enable checkbutton cb_selected_only
        if has_selected_features:
            self.dlg.cb_selected_only.setEnabled(True)
            self.dlg.cb_selected_only.setChecked(True)
        else:
            self.dlg.cb_selected_only.setChecked(False)
            self.dlg.cb_selected_only.setEnabled(False)

        # initialize cb_output
        # remember the layer being selected the last time
        last_index = self.dlg.cb_output.currentText()
        # populate the combo box with the polygon layers listed in the current legend
        self.set_output_layer_combobox(2, last_index)

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
                        geom.extend(self.extract_points(feat.geometry()))
                else:
                    for feat in active_layer.getFeatures():
                        geom.extend(self.extract_points(feat.geometry()))

            num_points = len(geom)
            if num_points == 0:
                return None

            # Send WARNING to the message bar to inform about a probably long running time
            if num_points > 1000:
                msg = self.msg_bar.createMessage(u'Please be patient, processing of more then {} points may take a while'.
                                                 format(int(num_points)))
                self.msg_bar.pushWidget(msg, QgsMessageBar.WARNING, 5)

            # if more then 5000 points ask user to confirm
            if num_points > 5000:
                proceed = QMessageBox.question(None, 'Please confirm', 'Do you really want to proceed?',
                                             QMessageBox.Yes | QMessageBox.No)
                if proceed == QMessageBox.No:
                    QApplication.instance().setOverrideCursor(Qt.ArrowCursor)
                    return None

            # change cursor to inform user about ongoing processing
            QApplication.instance().setOverrideCursor(Qt.BusyCursor)

            # generate the hull geometry
            # process points with prior clustering
            hull_list = []
            if self.dlg.gb_clustering.isChecked():
                clusters = SSNClusters(geom, self.dlg.sb_neighborhood_list_size.value()).get_clusters()
                for cluster in clusters.keys():
                    the_hull = self.concave_hull(clusters[cluster], self.dlg.sb_neighbors.value())
                    if the_hull:
                        hull_list.append(self.as_wkt(the_hull))
            else:
                # process points without clustering
                the_hull = self.concave_hull(geom, self.dlg.sb_neighbors.value())
                hull_list.append(self.as_wkt(the_hull))

            # write hull geometries to output device
            success = self.create_output_feature(hull_list)

            # report result in QGIS message bar
            if success:
                msg = self.msg_bar.createMessage(_translate('ConcaveHull', '{} Concave hulls created successfully'.
                                                            format(int(len(hull_list))), None))
                self.msg_bar.pushWidget(msg, QgsMessageBar.INFO, 5)

            # clear the message bar and reset cursor
            QApplication.instance().setOverrideCursor(Qt.ArrowCursor)

        return None
