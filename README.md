# QGIS-ConcaveHull-Plugin

Computes a concave hull containing a set of features according to the algorithm described in detail by Adriano Moreira 
and Maribel Yasmina Santos (2007). Prior construction of the hull the data may optionally clustered using a 
Shared Nearest Neighbor Clustering algorithm after Ertoz, Steinbach & Kumar (2003).

## About this plugin

Computes a minimum area containing a set of features. The concave hull is supposed to best describe that area 
occupied by the given set of points. The resulting polygon geometries are stored in an existing polygon layer 
or new memory layer. Prior computation of the hull the given data can optionally be divided into clusters.

## Using the plugin

### Generating concave hulls
Specify an initial number k of nearest neighbors for the algorithm to inspect. If no valid hull can be constructed 
the algorithm will restart with an increased number of neighbors. It proceeds until all features are enclosed by 
a non self-intersecting polygon.

Select one or more vector layers containing points, lines, or polygons. Any mixture of geometry types is allowed, 
since all objects will be converted to points. The active map layer will be selected by default.

If at least one layer contains selected features you can direct the plugin to use selected features only. 
Note that in this case only selected features will be processed, layers without any selected feature will be ignored.

Hull polygons get the attributes Id (of hull) and Count. Count receives the number of points falling inside this polygon.

The concave hull algorithm can build a single concave hull polygon as well as many hulls based on an attribute. 
This works like a group by clause. In this case the field grouping is based on will be added to the hulls. The
specified field of the first selected layer will be the template for the new field. Grouping requires the 
specification of a field for all selected layers.  

Output can go to a new memory layer, an existing map layer, or a new shape file. Type in the name of the new memory layer. 
In this case a new memory layer containing the concave hull is created and added to the legend. 
The CRS of the new layer is being set to the project CRS. If you select an output layer from the dropdown list 
all created polygon features will be appended to this layer. If you select output to shapefile browse to the directory 
where the shapefile should be saved, and type in the filename. An existing shapefile will be overwritten.  

### Clustering input points

The dataset can be clustered optionally based on location prior construction of the concave hull. 
This plugin implements a Sheared Nearest Neighbor Algorithm. The algorithm finds clusters with at least the 
given number of neighbors being closer to one another than to other points. Points not being part of any cluster 
are considered as noise, and are not included in any cluster. These points optionally go to a separate layer 
for inspection and fine tuning of algorithm parameters.

Optionally only clustered input points can be output to a layer without creating hulls. Use this function for
debugging purposes or for further processing with other QGIS tools. In this case the result layer will have fields
Id (for the cluster), Count (points in cluster), and the group by attribute value (if any selected).

### Creating polygon geometry from input points interactively

The plugin functionality can be used for creating polygons too. Select points from one or many layers, open the dialog,
select the appropriate layers, mark using selected objects, unmark grouping, select an existing layer for the
output, and press the Apply button. Any created polygon will be written to the specified layer. The plugin will respond
to any changes to the layer legend and selections while it is opened. You can select points from any layer, 
mixtures are allowed, and create polygons one by one. Finally press Cancel button to close the dialog. 

## Examples

Included with this plugin are two test datasets with similar point distribution as describe in Moreira and Santos (2007). 
These are the results:

![Example 1 point distribution](/images/expl01.png)
Point distribution for example 1

![Example 1 without clustering](/images/expl01_conch_3.png)
Concave hull without clustering, starting with k=3

![Example 1 subset of points, k=3](/images/expl01_conch_3_a.png)
Concave hull for a subset of points, starting with k=3

![Example 1 subset of points, k=10](/images/expl01_conch_10_a.png)
Concave hull for the same subset of points, starting with k=10

![Example 1 with clustering](/images/expl01_clust_5_3.png)
First clustered (5 neighbors), then concave hull with k=3

![Example 2 point distribution](/images/expl02.png)
Point distribution for example 2

![Example 2](/images/expl02_clust_5_5.png)
First clustered (5 neighbors), then concave hull with k=5

![Example 3](/images/expl03_clust_field_conch.png)
First clustered by location and field (categories represented by point color), then concave hull based on clusterId

## Notes

* In general the concave hull computed by this algorithm is more concave then that computed by the alpha-shape algorithm. 

* The algorithm cannot deal with holes.

* Although you can use arbitrary input geometries, this may lead to unexpected results. 
This is especially true for if the input data are vertices of polygons with holes. 
If a hole is lying near to the polygon boundary the algorithm may include the boundary of the hole 
and thus leading to misinterpretation of the covered area.

* If segment lengths of input polygons and lines are very different you may consider to add 
additional vertices (densify), otherwise the algorithm may pass over these segments leading to _eroded_ boundaries. 

* Since the algorithm increases the number k of nearest neighbors, a slightly different data distribution 
might lead to very different hull geometries. In the second and third example above, if all points will 
be used the hull geometry is more generalized than processing only the upper point cloud. 
Especially if you cluster the input data each cluster gets its own concave hull, and therefore can be 
more or less detailed than other hulls. To avoid this, you may start with a greater neighborhood k.

* When selecting a large value for k the hull geometry equals the convex hull.

* Construction of concave hulls based on points grouped by an attribute may lead to overlapping polygons, 
since these groups are processed independently. Overlapping concave hulls may be an indicator for 
interspersed distribution of variables.

* If output of clustered points only is selected, then the plugin returns the same result as the former 
SNNCluster processing algorithm.

## Acknowledgment

The clustering method is based on python code written by some guy named jonno 
(http://www.georeference.org/forum/t76320). Visited in November, 2014.

Thanks to Joel Lawhead and his book: Learning Geospatial Analysis with Python. Especially for the 
implementation of the ray-casting algorithm.

## Version history

* Version 2.0.0 (2019/01/03): first version for QGIS 3.4
  - one to many layers can contribute to the point set
  - grouping based on attributes is now supported in the GUI version
  - new Apply function allows interactive processing and makes it an powerful edit tool for creating polygons 
  from given points
  - noise points will be written to a layer for inspection
  - only clustered input points can be output to a layer without creating hulls
  - plugin is now displays more messages to let the user know what is going on
  - several minor issues are fixed
  - algorithms for processing framework are not provided any more, because the KNN algorithm is already shipped with QGIS

* Version 1.0.2 (2015/02/10): added algorithms to processing framework, standard attributes, grouping based on fields

* Version 1.0.1 (2015/01/10): added UI event handlers, more user feedback, and standard file selection dialog

* Version 1.0.0 (2015/01/07): first version

## Future developments

* User-defined distance function
* Support for 3-d points
* Prepare Cluster Algorithm for new processing framework

## Bibliography

Levent Ertoz, Michael Steinbach and Vipin Kumar (2003): Finding Clusters of Different Sizes, Shapes, and Densities in Noisy, High Dimensional Data. In Proceedings of the Second SIAM International Conference on Data Mining, San Francisco, CA, USA, May

Adriano Moreira and Maribel Yasmina Santos (2007): CONCAVE HULL: A K-NEAREST NEIGHBOURS APPROACH FOR THE COMPUTATION OF THE REGION OCCUPIED BY A SET OF POINTS. GRAPP 2007 - International Conference on Computer Graphics Theory and Applications, pp. 61-68
