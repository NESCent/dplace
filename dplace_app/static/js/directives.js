angular.module('dplaceMapDirective', [])
    .directive('dplaceMap', function() {
        function link(scope, element, attrs) {
            /* Temporarily Broken as OpenLayers is removed */
            element.append("<div id='mapdiv' style='width:1140px; height:480px;'></div>");
            var map = new OpenLayers.Map('mapdiv');
            var wms = new OpenLayers.Layer.WMS( "OpenLayers WMS",
                    "http://vmap0.tiles.osgeo.org/wms/vmap0", {layers: 'basic'} );
            map.addLayer(wms);
            map.zoomToMaxExtent();
            var markers = new OpenLayers.Layer.Markers("SocietyMarkers");
            map.addLayer(markers);
            scope.map = map;
            scope.mapMarkers = markers;
            var size = new OpenLayers.Size(21,25);
            var offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
            scope.icon = new OpenLayers.Icon('http://www.openlayers.org/dev/img/marker.png', size, offset);
            scope.addMarkers = function() {
                scope.mapMarkers.clearMarkers();
                if(!scope.societies) {
                    return;
                }
                scope.societies.forEach(function(societyResult) {
                    var society = societyResult.society;
                    var coordinates = society.location.coordinates;
                    // Add a marker for each point
                    var lonlat = OpenLayers.LonLat.fromArray(coordinates);
                    var marker = new OpenLayers.Marker(lonlat, scope.icon.clone());
                    marker.events.register('mouseover', marker, function(evt) {
                        var popup = new OpenLayers.Popup.FramedCloud(society.name,
                            marker.lonlat,          // lonlat
                            null,                   // size
                            society.name,           // html
                            marker.icon,            // anchor
                            false                   // closebox
                        );
                        scope.map.addPopup(popup);
                        marker.events.register('mouseout', marker, function(evt) { popup.hide(); } )
                    });
                    scope.mapMarkers.addMarker(marker);
                });
            };

            // Update markers when societies change
            scope.$watchCollection('societies', function(oldvalue, newvalue) {
                scope.map.zoomToMaxExtent();
                scope.addMarkers();
            });
        }

        return {
            restrict: 'E',
            scope: {
                societies: '='
            },
            link: link
        };
    });