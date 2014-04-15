function MapCtrl($scope) {
    var map = new OpenLayers.Map('mapdiv');
    var wms = new OpenLayers.Layer.WMS( "OpenLayers WMS",
            "http://vmap0.tiles.osgeo.org/wms/vmap0", {layers: 'basic'} );
    map.addLayer(wms);
    map.zoomToMaxExtent();
    var markers = new OpenLayers.Layer.Markers("SocietyMarkers");
    map.addLayer(markers);
    $scope.model.map = map;
    $scope.model.mapMarkers = markers;
    var size = new OpenLayers.Size(21,25);
    var offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
    $scope.model.icon = new OpenLayers.Icon('http://www.openlayers.org/dev/img/marker.png', size, offset);
    $scope.addMarkers = function() {
        $scope.model.mapMarkers.clearMarkers();
        if(!$scope.model.searchResults.results) {
            return;
        }
        $scope.model.searchResults.results.forEach(function(societyResult) {
            var society = societyResult.society;
            var coordinates = society.location.coordinates;
            // Add a marker for each point
            var lonlat = OpenLayers.LonLat.fromArray(coordinates);
            var marker = new OpenLayers.Marker(lonlat, $scope.model.icon.clone());
            marker.events.register('mouseover', marker, function(evt) {
                var popup = new OpenLayers.Popup.FramedCloud(society.name,
                    marker.lonlat,          // lonlat
                    null,                   // size
                    society.name,           // html
                    marker.icon,            // anchor
                    false                   // closebox
                );
                $scope.model.map.addPopup(popup);
                marker.events.register('mouseout', marker, function(evt) { popup.hide(); } )
            });
            $scope.model.mapMarkers.addMarker(marker);
        });
    };
    // Update markers when societies change
    $scope.$watchCollection('model.searchResults.results', function(oldvalue, newvalue) {
        $scope.addMarkers();
    });
}
