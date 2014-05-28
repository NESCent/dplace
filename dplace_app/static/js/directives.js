angular.module('dplaceMapDirective', [])
    .directive('dplaceMap', function() {
        function link(scope, element, attrs) {
            element.append("<div id='mapdiv' style='width:1140px; height:30rem;'></div>");
            scope.updatesEnabled = true;
            scope.map = $('#mapdiv').vectorMap({
                map: 'world_mill_en',
                backgroundColor: 'white',
                regionStyle: {
                  initial: {
                    fill: '#428bca',
                    "fill-opacity": 1,
                    stroke: '#357ebd',
                    "stroke-width": 0,
                    "stroke-opacity": 1
                  },
                  hover: {
                    "fill-opacity": 0.8
                  },
                  selected: {
                    fill: '#113'
                  },
                  selectedHover: {
                  }
                },
                onRegionOver: function(e, code) {
                    if(attrs.region) {
                        scope.$apply(function () {
                            scope.region = code;
                        });
                    }
                },
                onRegionSelected: function(e, code, isSelected, selectedRegionIds) {
                    if(attrs.selectedRegionIds && scope.updatesEnabled) {
                        scope.$apply(function() {
                            scope.selectedRegionIds = angular.copy(selectedRegionIds);
                        });
                    }
                },
                regionsSelectable: true
            }).vectorMap('get','mapObject');

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

            scope.$watchCollection('selectedRegionIds', function(oldvalue, newvalue) {
                // Then update the UI
                scope.updatesEnabled = false;
                scope.map.setSelectedRegions(angular.copy(newvalue));
                scope.updatesEnabled = true;
            });
            scope.$on('mapTabActivated', function(event, args) {
                scope.map.setSize();
            });
        }

        return {
            restrict: 'E',
            scope: {
                societies: '=',
                region: '=',
                selectedRegionIds: '='
            },
            link: link
        };
    });