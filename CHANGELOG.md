## CHANGELOG

### Version 2.0.0 (2019/01/03): 
* First version for QGIS 3.4
* UI: grouping based on attributes is now supported (Issue #4)
* UI: Added Apply function, allows interactive processing and makes it an powerful edit tool for creating polygons 
  from given points
* SNNCluster: noise points will be written to a layer for inspection
* SNNCluster: only clustered input points can be output to a layer without creating hulls
* UI: plugin is now displays more messages to let the user know what is going on (Issue #9)
* ConcaveHull: Several minor issues are fixed
* PROC: algorithms for processing framework are not provided any more, because the KNN algorithm is already shipped with QGIS

### Version 1.0.2

* ConcaveHull: Added attributes id, count, and group by field to output
* SNNCluster: Added attribute clusterId and group by field to output
* PROC: Added support for group by fields clause
* PROC: Added algorithms to processing environment (Issue #3) 
* ConcaveHull: Fixed coordinate precision issue 
* UI: Replaced icon with SVG version

### Version 1.0.1 (2015/01/10)

* UI: Added support for English and German language
* UI: Added event handlers for controls to ensure meaningful settings (Issue #1)
* UI: Added standard output file selector (Issue #2) 
* UI: Added status information for the user

### Version 1.0.0 (2015/01/07)

* First version
