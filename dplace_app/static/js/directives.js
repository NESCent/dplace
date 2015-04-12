angular.module('languagePhylogenyDirective', [])
    .directive('languagePhylogeny', function() {
        function link(scope, element, attrs) {
            var constructTree = function(langTree) {
                d3.select("language-phylogeny").html('');
                var newick = Newick.parse(langTree.newick_string);
                var rightAngleDiagonal = function() {
                    function diagonal(diagonalPath) {
                        var source = diagonalPath.source,
                            target = diagonalPath.target,
                            pathData = [source, {x: target.x, y: source.y}, target].map(function(d) { return [d.y, d.x]; });
                        return "M" + pathData[0] + ' ' + pathData[1] + ' ' + pathData[2];
                    }
                    return diagonal;
                }
                
                var w = 700;
                var tree = d3.layout.cluster().children(function(node) { return node.branchset; });
                var nodes = tree(newick);
                var h = nodes.length * 9; //height depends on # of nodes
                
                tree = d3.layout.cluster()
                    .size([h, w])
                    .sort(function comparator(a, b) { return d3.ascending(a.length, b.length); })
                    .children(function(node) { return node.branchset; })
                    .separation(function separation(a, b) { return 8; });
                nodes = tree(newick);
                
                d3.select("language-phylogeny").append("h4")
                    .text(langTree.name);
                    
                var labels = d3.select("language-phylogeny").append("svg:svg")
                        .attr("width", w+300)
                        .attr("height", 15)
                        //.attr("style", "position:absolute; background-color:#fff")
                        .attr("id", "varLabels")
                        .attr("transform", "translate(-40, 0)");
                keysWritten = 1;
                translate = 20;
                if (scope.query.variable_codes) {
                    for (var key in scope.code_ids) {
                        labels.append("svg:text")
                            .attr("dx", w+15+translate)
                            .attr("dy", 15)
                            .text("C"+keysWritten);
                        scope.code_ids[key].CID = "C"+keysWritten;
                        keysWritten++;
                        translate += 20;    
                    }
                }                     
                if (scope.query.environmental_filters) {     
                        labels.append("svg:text")
                        .attr("dx", w+15+translate)
                        .attr("dy", 15)
                        .text("E1");
                }
                    
                var vis = d3.select("language-phylogeny").append("svg:svg")
                    .attr("width", w+300)
                    .attr("height", h+30)
                    .append("svg:g")
                    .attr("transform", "translate(2, 0)");
                    
                var diagonal = rightAngleDiagonal();
                
                nodes.forEach(function(node) {
                    node.rootDist = (node.parent ? node.parent.rootDist : 0) + (node.length || 0);
                });
                var rootDists = nodes.map(function(n) { return n.rootDist; });
                var yscale = d3.scale.linear()
                    .domain([0, d3.max(rootDists)])
                    .range([0, w]);
                nodes.forEach(function(node) {
                    node.y = yscale(node.rootDist);
                });
                
                var links = tree.links(nodes);
                var link = vis.selectAll("path.link")
                    .data(links)
                    .enter().append("svg:path")
                    .attr("class", "link")
                    .attr("d", diagonal)
                    .attr("fill", "none")
                    .attr("stroke", "#ccc")
                    .attr("stroke-width", "4px");
                var node = vis.selectAll("g.node")
                    .data(nodes)
                    .enter().append("svg:g")
                    .attr("transform", function(d) { return "translate(" + d.y + ", "+ d.x + ")"; });
                    
                translate = 0;
                if (scope.query.variable_codes) {
                    for (var key in scope.code_ids) {
                        scope.results.societies.forEach(function(society) {
                            var selected = node.filter(function(d) {
                                return d.name == society.society.iso_code;
                            });
                            
                            if (society.variable_coded_values.length > 0) {
                                for (var i = 0; i < society.variable_coded_values.length; i++) {
                                    if (society.variable_coded_values[i].variable == key) {
                                            var hover_text = society.variable_coded_values[i].code_description.description;
                                            selected.append("svg:circle")
                                                .attr("r", 4.5)
                                                .attr("stroke", "#000")
                                                .attr("stroke-width", "0.5")
                                                .attr("transform", "translate("+translate+", 0)")
                                                .attr("fill", function(n) {
                                                    console.log(i);
                                                    value = society.variable_coded_values[i].coded_value;
                                                    hue = value * 240 / scope.code_ids[society.variable_coded_values[i].variable].length;
                                                    return 'hsl('+hue+',100%, 50%)';
                                                })
                                                .on("mouseover", function() { //need to add text here!
                                                    translate += 20;
                                                      var g = selected.append("svg:g")
                                                  .attr("transform", "translate("+translate+", 0)");
                                                        g.select('text').remove();
                                                        g.append("svg:rect")
                                                        .attr("width", hover_text.length * 10)
                                                        .attr("height", "23")
                                                        .attr("fill", "white");
                                                        g.append("svg:text")
                                                        .attr("dy", "12")
                                                        .text(hover_text);
                                                  })
                                                  .on("mouseout", function() {
                                                      // Remove the info text on mouse out.
                                                      selected.select('g').remove();
                                                      translate -= 20;
                                                })
                                                
                                                ; 

                                    } 
                                }
                            }
                        });
                        translate += 20;
                    }
                } else if (scope.query.language_classifications && !scope.query.environmental_filters) {
                    //get lang classification
                    scope.results.societies.forEach(function(society) {
                        var selected = node.filter(function(d) {
                            return d.name == society.society.iso_code;
                        });
                        
                        for (var i = 0; i < society.languages.length; i++) {
                            var classification = scope.query.language_classifications.filter(function(l) { return l.language.id == society.languages[i].id });
                            selected.append("svg:circle")
                                .attr("r", 4.5)
                                .attr("stroke", "#000")
                                .attr("stroke-width", "0.5")
                                .attr("fill", function(n) {
                                    if (classification.length > 0) {
                                        value = classification[0].class_subfamily;
                                        hue = value * 240 / scope.classifications.length;
                                        return 'hsl('+hue+',100%, 50%)';
                                    }
                                });
                            
                            
                        }
                        
                    });
                }
                
                scope.results.societies.forEach(function(society) {
                    var selected = node.filter(function(d) {
                        return d.name == society.society.iso_code;
                    });
                    //append the circles
                    if (society.environmental_values.length > 0) {
                        selected.append("svg:circle")
                            .attr("r", 4.5)
                            .attr("stroke", "#000")
                            .attr("stroke-width", "0.5")
                            .attr("transform", "translate("+translate+", 0)")
                            .attr("fill", function(n) {
                                value = society.environmental_values[0].value; //only 1 environmental value at a time so we can do this
                                hue = value * 240 / scope.range;
                                return 'hsl('+hue+',100%, 50%)';
                            });
                    } 
                    
                    //lastly, append the text
                        selected.append("svg:text") 
                            .attr("dx", function(n) {
                                if (scope.query.environmental_filters && scope.query.variable_codes) return translate+20;
                                else if (scope.query.environmental_filters) return translate+10;
                                else if (scope.query.language_classifications) return translate+10;
                                else return translate;
                            })                           
                            .attr("dy", 4)
                            .attr("font-size", "14px")
                            .attr("font-family", "Arial")
                            .text(function(d) { return d.name; });  
                });
                
                phyloWidth = d3.select("g").node().getBBox().width;
                d3.select("#legend")
                    .attr("style", "width:"+($(window).width()-phyloWidth-100)+"px; position:absolute; right:5px; z-index:1; margin-top:10px;");
            };

            scope.$on('treeSelected', function(event, args) {
                constructTree(args.tree);
                var pos = $("#varLabels").offset();
                $(window).scroll(function() {
                    if ($(window).scrollTop() > 100)
                        $("#legend").stop().animate({"marginTop":($(window).scrollTop() - 100) + "px"}, "slow");
                    if ($(window).scrollTop() > (pos.top - 20) && $("#varLabels").css('position') == 'static') 
                        d3.select("#varLabels").attr('class', 'var-labels-fixed');
                    else if ($(window).scrollTop() < pos.top)
                        d3.select("#varLabels").classed('var-labels-fixed', false);
                });
            });
        }

        return {
            restrict: 'E',
            link: link
        };
    });
    
angular.module('dplaceMapDirective', [])
    .directive('dplaceMap', function(colorMapService) {
        function link(scope, element, attrs) {
            // jVectorMap requires an ID for the element
            // If not present, default to 'mapDiv'
            var mapDivId = scope.mapDivId || 'mapDiv';
            // Not possible to assign default values to bound attributes, so check
            element.append("<div id='" + mapDivId + "' style='width:900px; height:30rem;'></div>");
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
                        fill: '#C0C6C6',
                        "fill-opacity": 1,
                        "stroke": '#357ebd',
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
                    if(!scope.results) {
                        return;
                    }

                    // get the society IDs
                    var societyIds = scope.results.societies.map(function(societyResult) {
                        return societyResult.society.id;
                    });

                    scope.results.societies.forEach(function(societyResult) {
                        var society = societyResult.society;
                        // Add a marker for each point
                        var marker = {latLng: [society.location.coordinates[1], society.location.coordinates[0]], name: society.name}
                        scope.map.addMarker(society.id, marker);
                    });

                    // Map IDs to colors
                    var colorMap = colorMapService.generateColorMap(scope.results);
                    scope.map.series.markers[0].setValues(colorMap);

                    for (var i = 0; i < societyIds.length; i++) {
                        if (societyIds[i] in colorMap) continue;
                        else scope.map.removeMarkers([societyIds[i]]);
                    }
                    
                };
                
                //constructs download link for map
                scope.mapLink = function() {                     
                    if (!scope.chosen.download_link_generated) {
                        var map_svg = d3.select(".jvectormap-container").select("svg")
                            .attr("version", 1.1)
                            .attr("xmlns", "http://www.w3.org/2000/svg")
                            .node().parentNode.innerHTML;
                        map_svg = map_svg.substring(0, map_svg.indexOf("<div")); //remove zoom in/out buttons from map
                        var imgsrc = 'data:image/svg+xml;base64,' + window.btoa(unescape(encodeURIComponent(map_svg)));
                        d3.select(".download-links").append("li").append("a")
                            .attr("class", "btn btn-info btn-dplace-download")
                            .attr("download", scope.chosen.name+"map.svg")
                            .attr("href", imgsrc)
                            .html("Download Map: " + scope.chosen.name);
                        scope.chosen.download_link_generated = true;
                    }
                };

                if(attrs.results) {
                    // Update markers when societies change
                    scope.$watchCollection('results', function(oldvalue, newvalue) {
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
                results: '=',
                region: '=',
                selectedRegions: '=',
                mapDivId: '@',
                visible: '=',
                query: '=',
                chosen: '=',
            },
            link: link
        };
    });