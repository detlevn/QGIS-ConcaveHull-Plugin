#QGIS-ConcaveHull-Plugin

Computes a concave hull containing a set of features according to the algorithm described in detail by Adriano Moreira and Maribel Yasmina Santos (2007). Prior construction of the hull the data may optionally clustered using a Shared Nearest Neighbor Clustering algorithm after Ertoz, Steinbach & Kumar (2003).

##About this plugin

Computes a minimum area containing a set of features. The concave hull is supposed to best describe that area occupied by the given set of points. The resulting polygon geometries are stored in an existing polygon layer or new memory layer. Prior computation of the hull the given data can optionally divided into clusters.

##Using the plugin

Specify an initial number k of nearest neighbors for the algorithm to inspect. If no valid hull can be constructed the algorithm will restart with an increased number of neighbors. It proceeds until all features are enclosed by a non self-intersecting polygon.

Optionally the dataset can be clustered prior to construction of the concave hull. This plugin implements a sheared nearest neighbor algorithm. This algorithm finds clusters with at least the given number of neighbors being closer to one another than to other points. Point not being part of any clusters are considered as noise, and are not included in any cluster.

Select one or more vector layers containing points, lines, or polygons. Any mixture of geometry types is allowed, since all objects will be converted to points.

If at least one layer contains selected features you can direct the plugin to use selected features only. Note that in this case only selected features will be processed, layers without any selected feature will be ignored.

Select an output layer from the dropdown list or type in the name of a new layer. In this case a new memory layer containing the concave hull is created and added to the legend. The CRS of the new layer is being set to the project CRS.

##Examples

Included with this plugin are two test datasets with similar point distribution as describe in Moreira and Santos (2007). These are the results:

![Example 1 point distribution](/images/expl01.png)
Point distribution for example 1

![Example 1 withour clustering](/images/expl01_conch_3.png)
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

##Notes

* In general the concave hull computed by this algorithm is more concave then that computed by the alpha-shape algorithm. 

* The algorithm cannot deal with holes.

* Although you can use arbitrary input geometries, this may lead to unexpected results. This is especially true for if the input data are vertices of polygons with holes. If a hole is lying near to the polygon boundary the algorithm may include the boundary of the hole and thus leading to misinterpretation of the covered area.

* Since the algorithm increases the number k of nearest neighbors, a slightly different data distribution might lead to very different hull geometries. In the second and third example above, if all points will be used the hull geometry is more generalized than processing only the upper point cloud. Especially if you cluster the input data each cluster gets its own concave hull, and therefore can be more or less detailed than other hulls. To avoid this, you may start with a greater neighborhood k.

* When selecting a large value for k the hull geometry equals the convex hull.
 
* Processing of PostGIS-features takes a much too long running time.

##Acknowledgment

The clustering method is based on python code written by some guy named jonno (http://www.georeference.org/forum/t76320). Visited in November, 2014.

Thanks to Joel Lawhead and his book: Learning Geospatial Analysis with Python. Especially for the implementation of the ray-casting algorithm.

##Todo

* Support for Processing Toolbox

* Processing of groups of points depending on values of one or more attributes

* Optimization of code in terms of running time and readability

##Version history

* Version 1.0.0 (2015/01/07): first version

* Version 1.0.1 (2015/01/10): added UI event handlers, more user feedback, and standard file selection dialog

##Bibliography

Levent Ertoz, Michael Steinbach and Vipin Kumar (2003): Finding Clusters of Different Sizes, Shapes, and Densities in Noisy, High Dimensional Data. In Proceedings of the Second SIAM International Conference on Data Mining, San Francisco, CA, USA, May

Adriano Moreira and Maribel Yasmina Santos (2007): CONCAVE HULL: A K-NEAREST NEIGHBOURS APPROACH FOR THE COMPUTATION OF THE REGION OCCUPIED BY A SET OF POINTS. GRAPP 2007 - International Conference on Computer Graphics Theory and Applications, pp. 61-68