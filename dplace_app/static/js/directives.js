angular.module('dplaceMapDirective', [])
    .directive('dplaceMap', function() {
        function link(scope, element, attrs) {
            element.append("<div id='mapdiv' style='width:1140px; height:480px;'></div>");
            scope.map = $('#mapdiv').vectorMap({map: 'world_mill_en'}).vectorMap('get','mapObject');
            scope.addMarkers = function() {
                scope.map.removeAllMarkers();
                if(!scope.societies) {
                    return;
                }
                scope.societies.forEach(function(societyResult) {
                    var society = societyResult.society;
                    // Add a marker for each point
                    var marker = {latLng: society.location.coordinates.reverse(), name: society.name}
                    scope.map.addMarker(society.id, marker);
                });
            };

            // Update markers when societies change
            scope.$watchCollection('societies', function(oldvalue, newvalue) {
                scope.addMarkers();
            });

            scope.$on('mapTabActivated', function(event, args) {
                scope.map.setSize();
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