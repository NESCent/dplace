angular.module('dplaceMapDirective', [])
    .directive('dplaceMap', function(colorMapService) {
        function link(scope, element, attrs) {
            // jVectorMap requires an ID for the element
            // If not present, default to 'mapDiv'
            var mapDivId = scope.mapDivId || 'mapDiv';
            // Not possible to assign default values to bound attributes, so check
            element.append("<div id='" + mapDivId + "' style='width:1140px; height:30rem;'></div>");
            scope.localRegions = [];
            scope.checkDirty = function() {
                return !(angular.equals(scope.localRegions, scope.selectedRegions));
            };
            scope.updatesEnabled = true;
            var hideMap = function(scope) {
                if(angular.isDefined(scope.map)) {
                    scope.map.remove();
                    scope.map = undefined;
                }
            };

            var showMap = function(scope) {
                scope.map = $('#' + mapDivId).vectorMap({
                    map: 'tdwg-level2_mill_en',
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
                    if(!scope.societies || (!scope.chosen && !scope.query.language_classifications)) {
                        return;
                    }

                    // get the society IDs
                    var societyIds = scope.societies.map(function(societyResult) {
                        return societyResult.society.id;
                    });
                                        
                    scope.societies.forEach(function(societyResult) {
                        var society = societyResult.society;
                        // Add a marker for each point
                        var marker = {latLng: society.location.coordinates, name: society.name}
                        scope.map.addMarker(society.id, marker);
                    });

                    // Map IDs to colors
                    if (scope.query.language_classifications && !scope.chosen) { //scope.chosen undefined for geographic and language searches
                        var colorMap = colorMapService.generateColorMap(scope.societies, scope.query, -1);
                    } else {
                        var colorMap = colorMapService.generateColorMap(scope.societies, scope.query, scope.chosen.id);
                    }
                    scope.map.series.markers[0].setValues(colorMap);

                    for (var i = 0; i < societyIds.length; i++) {
                        if (societyIds[i] in colorMap) continue;
                        else scope.map.removeMarkers([societyIds[i]]);
                    }
                    
                };
                
                //this function gets the svg code and passes it to societies.js for download
                //we can't access the map's svg code in societies.js (the map needs to be active)
                //so this is a solution (?) maybe there's a better way to do this in the future
                scope.mapLink = function() { 
                    var map_svg = d3.select(".jvectormap-container").select("svg")
                        .attr("version", 1.1)
                        .attr("xmlns", "http://www.w3.org/2000/svg")
                        .node().parentNode.innerHTML;
                    map_svg = map_svg.substring(0, map_svg.indexOf("<div")); //remove zoom in/out buttons from map
                    scope.link()(map_svg);
                };

                if(attrs.societies) {
                    // Update markers when societies change
                    scope.$watchCollection('societies', function(oldvalue, newvalue) {
                        scope.societies.forEach(function(societyResult) {
                            var society = societyResult.society;
                            society.location.coordinates = society.location.coordinates.reverse();
                        });
                        scope.addMarkers();
                    });
                }
                if (attrs.chosen) {
                    scope.$watchCollection('chosen', function(oldvalue, newvalue) {
                        scope.addMarkers(); 
                        scope.mapLink();
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
                scope.$on('$destroy', function() {
                    hideMap(scope);
                });
                                
                scope.map.updateSize();
                
            };

            // Handle visibility toggle
            // This is necessary for results page where element is in the DOM but not visible.
            var initiallyVisible = false;
            // If we have a bound variable to toggle visibility, watch for changes to it
            if(attrs.visible) {
                // 'visible' attribute was bound in the tag
                // use the scope value and watch for changes
                initiallyVisible = scope.visible;
                scope.$watch('visible', function(oldValue, newValue) {
                    if(scope.visible) {
                        showMap(scope);
                    } else {
                        hideMap(scope);
                    }
                });
            } else {
               // tag does not bind a 'visible' attribute, default to true
                initiallyVisible = true;
            }

            if(initiallyVisible) {
                showMap(scope);
            }
        }

        return {
            restrict: 'E',
            scope: {
                societies: '=',
                region: '=',
                selectedRegions: '=',
                mapDivId: '@',
                visible: '=',
                query: '=',
                chosen: '=',
                link: '&',
            },
            link: link
        };
    });