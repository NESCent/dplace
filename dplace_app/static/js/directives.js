angular.module('dplaceMapDirective', [])
    .directive('dplaceMap', function(colorMapService) {
        function link(scope, element, attrs) {
            element.append("<div id='mapdiv' style='width:1140px; height:30rem;'></div>");
            scope.localRegions = [];
            scope.checkDirty = function() {
                return !(angular.equals(scope.localRegions, scope.selectedRegions));
            };
            scope.updatesEnabled = true;
            scope.map = $('#mapdiv').vectorMap({
                map: 'tdwg-level2',
                backgroundColor: 'white',
                series: {
                    markers: [{
                        attribute: 'fill'
                    }]
                },
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
                onRegionSelected: function(e, code, isSelected, selectedRegionCodes) {
                    if(scope.updatesEnabled && attrs.selectedRegions) {
                        scope.localRegions = selectedRegionCodes.map(function(code) {
                            return {
                                code: code,
                                name: scope.map.getRegionName(code)
                            };
                        });
                        var dirty = scope.checkDirty();
                        if(dirty) {
                            scope.$apply(function() {
                                scope.selectedRegions = angular.copy(scope.localRegions);
                            });
                        }
                    }
                },
                regionsSelectable: true
            }).vectorMap('get','mapObject');

            scope.addMarkers = function() {
                scope.map.removeAllMarkers();
                if(!scope.societies) {
                    return;
                }

                // get the society IDs
                var societyIds = scope.societies.map(function(societyResult) {
                    return societyResult.society.id;
                });

                scope.societies.forEach(function(societyResult) {
                    var society = societyResult.society;
                    // Add a marker for each point
                    var marker = {latLng: society.location.coordinates.reverse(), name: society.name}
                    scope.map.addMarker(society.id, marker);
                });

                // Map IDs to colors
                var colorMap = colorMapService.generateColorMap(societyIds);
                scope.map.series.markers[0].setValues(colorMap);
            };

            if(attrs.societies) {
                // Update markers when societies change
                scope.$watchCollection('societies', function(oldvalue, newvalue) {
                    scope.addMarkers();
                });
            }

            if(attrs.selectedRegions) {
                scope.$watchCollection('selectedRegions', function(oldvalue, newvalue) {
                    var dirty = scope.checkDirty();
                    if(dirty) {
                        // update the local variable first
                        scope.localRegions = angular.copy(scope.selectedRegions);

                        // then update the UI
                        scope.updatesEnabled = false;
                        var regionCodes = scope.localRegions.map(function(region){
                            return region.code;
                        });
                        scope.map.clearSelectedRegions();
                        scope.map.setSelectedRegions(regionCodes);
                        scope.updatesEnabled = true;
                    }
                });
            }
            scope.$on('mapTabActivated', function(event, args) {
                scope.map.setSize();
            });

            scope.$on('$destroy', function() {
                scope.map.remove();

            });
        }

        return {
            restrict: 'E',
            scope: {
                societies: '=',
                region: '=',
                selectedRegions: '='
            },
            link: link
        };
    });