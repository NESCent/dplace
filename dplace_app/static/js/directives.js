angular.module('languagePhylogenyDirective', [])
    .directive('languagePhylogeny', function() {
        function link(scope, element, attrs) {
            var rightAngleDiagonal = function() {
                var projection = function(d) { return [d.y, d.x]; }
                var path = function(pathData) {
                 return "M" + pathData[0] + ' ' + pathData[1] + " " + pathData[2];
                }
                function diagonal(diagonalPath, i) {
                  var source = diagonalPath.source,
                      target = diagonalPath.target,
                      midpointX = (source.x + target.x) / 2,
                      midpointY = (source.y + target.y) / 2,
                      pathData = [source, {x: target.x, y: source.y}, target];
                  pathData = pathData.map(projection);
                  return path(pathData)
                }
                diagonal.projection = function(x) {
                  if (!arguments.length) return projection;
                  projection = x;
                  return diagonal;
                };
                diagonal.path = function(x) {
                  if (!arguments.length) return path;
                  path = x;
                  return diagonal;
                };
                return diagonal;
            }
                    
            var radialRightAngleDiagonal = function() {
                return rightAngleDiagonal()
                  .path(function(pathData) {
                    var src = pathData[0],
                        mid = pathData[1],
                        dst = pathData[2],
                        radius = Math.sqrt(src[0]*src[0] + src[1]*src[1]),
                        srcAngle = coordinateToAngle(src, radius),
                        midAngle = coordinateToAngle(mid, radius),
                        clockwise = Math.abs(midAngle - srcAngle) > Math.PI ? midAngle <= srcAngle : midAngle > srcAngle,
                        rotation = 0,
                        largeArc = 0,
                        sweep = clockwise ? 0 : 1;
                    return 'M' + src + ' ' +
                      "A" + [radius,radius] + ' ' + rotation + ' ' + largeArc+','+sweep + ' ' + mid +
                      'L' + dst;
                  })
                  .projection(function(d) {
                    var r = d.y, a = (d.x - 90) / 180 * Math.PI;
                    return [r * Math.cos(a), r * Math.sin(a)];
                  })
            }
            // Convert XY and radius to angle of a circle centered at 0,0
            var coordinateToAngle = function(coord, radius) {
                var wholeAngle = 2 * Math.PI,
                    quarterAngle = wholeAngle / 4
                
                var coordQuad = coord[0] >= 0 ? (coord[1] >= 0 ? 1 : 2) : (coord[1] >= 0 ? 4 : 3),
                    coordBaseAngle = Math.abs(Math.asin(coord[1] / radius))
                
                // Since this is just based on the angle of the right triangle formed
                // by the coordinate and the origin, each quad will have different 
                // offsets
                switch (coordQuad) {
                  case 1:
                    coordAngle = quarterAngle - coordBaseAngle
                    break
                  case 2:
                    coordAngle = quarterAngle + coordBaseAngle
                    break
                  case 3:
                    coordAngle = 2*quarterAngle + quarterAngle - coordBaseAngle
                    break
                  case 4:
                    coordAngle = 3*quarterAngle + coordBaseAngle
                }
                return coordAngle
            }

            var addMarkers = function(results, variable, node, global, translate) { 
                scope.results.societies.forEach(function(society) {
                    var selected = node.filter(function(d) {
                        return d.name == society.society.iso_code;
                    });
                    if (global) selected.select("circle").remove(); 
                    var society_name = society.society.name + " (" + society.society.iso_code + ")";
                    
                    //if the marker is an environmental variable
                    if (society.environmental_values.length > 0 && society.environmental_values[0].variable == variable)  { 
                            var hover_text_value = society.environmental_values[0].value + ' ' + results.environmental_variables[0].units;
                                selected.append("svg:circle")
                                    .attr("r", function() {
                                        if (global) return 1.5;
                                        else return 4.5;
                                    })
                                    .attr("stroke", "#000")
                                    .attr("stroke-width", "0.5")
                                    .attr("transform", "translate("+translate+", 0)")
                                    .attr("fill", function(n) {
                                        value = society.environmental_values[0].value; //only 1 environmental value at a time so we can do this
                                        min = scope.results.environmental_variables[0].min;
                                        max = scope.results.environmental_variables[0].max;
                                        if (society.environmental_values[0].variable == 34 || society.environmental_values[0].variable == 36) {
                                            hue = 30 + (((value - min) / (max - min))*88)
                                        }  else if (society.environmental_values[0].variable == 27) {
                                            lum = 100 - (((value - min) / (max - min))*95);
                                            return 'hsl(252,65%,'+lum+'%)';
                                        }
                                        else {
                                            hue = 240 - (((value-min)/(max-min))*240);
                                        }
                                        return 'hsl('+hue+',100%, 50%)';
                                    })
                                    .on("mouseover", function() { 
                                                     d3.select("body").append("div")
                                                        .attr("class", "tooltip")
                                                        .html("<b>"+society_name+":</b><br>"+hover_text_value)
                                                        .style("left", (d3.event.pageX + 10)+"px")
                                                        .style("top", (d3.event.pageY + 5)+"px")
                                                        .style("opacity", .9);
                                    })
                                    .on("mouseout", function() {
                                        d3.select(".tooltip").remove();
                                    });
                            return;
                        } else if (society.variable_coded_values.length > 0) {
                        for (var i = 0; i < society.variable_coded_values.length; i++) {
                            if (society.variable_coded_values[i].variable == variable) {
                                if (society.bf_cont_var) {
                                    var hover_text_value = society.variable_coded_values[i].coded_value;
                                    if (scope.results.code_ids[society.variable_coded_values[i].variable].units) hover_text_value += ' ' + scope.results.code_ids[society.variable_coded_values[i].variable].units;
                                } else
                                    var hover_text_value = society.variable_coded_values[i].code_description.description;
                                    selected.append("svg:circle")
                                        .attr("r", function() {
                                            if (global) return 1.5;
                                            else return 4.5;
                                        })
                                        .attr("stroke", "#000")
                                        .attr("stroke-width", "0.5")
                                        .attr("transform", "translate("+translate+", 0)")
                                        .attr("fill", function(n) {
                                            if (society.variable_coded_values[i].code_description && society.variable_coded_values[i].code_description.description.indexOf("Missing data") != -1) {
                                                   return 'hsl(360, 100%, 100%)';
                                                }
                                                value = society.variable_coded_values[i].coded_value;
                                                if (society.bf_cont_var) {
                                                    min = scope.results.code_ids[society.variable_coded_values[i].variable].min;
                                                    max = scope.results.code_ids[society.variable_coded_values[i].variable].max;
                                                    var lum = (value-min)/(max-min) * 95;
                                                    return 'hsl(0, 65%,'+lum+'%)';
                                                }                                               
                                                hue = value * 240 / scope.results.code_ids[society.variable_coded_values[i].variable].length;
                                                return 'hsl('+hue+',100%, 50%)';
                                        })
                                        .on("mouseover", function() { 
                                                 d3.select("body").append("div")
                                                    .attr("class", "tooltip")
                                                    .html("<b>"+society_name+":</b><br>"+hover_text_value)
                                                    .style("left", (d3.event.pageX + 10)+"px")
                                                    .style("top", (d3.event.pageY + 5)+"px")
                                                    .style("opacity", .9);
                                        })
                                        .on("mouseout", function() {
                                            d3.select(".tooltip").remove();
                                        }); 
                                }
                            }
                        }
                });
            };
            
            var constructTree = function(langTree) {   
                d3.select("language-phylogeny").html('');
                var newick = Newick.parse(langTree.newick_string);

                if (langTree.name.indexOf("global") != -1)
                    var w = 900;
                else  var w = 700;

                if (langTree.name.indexOf("global") != -1)  {
                    var tree = d3.layout.cluster()
                    .size([360, (w/2)-100])
                    .sort(function(node) { return node.children ? node.children.length : -1; })
                    .children(function(node) { return node.branchset; })
                    .separation(function separation(a, b) { return 8; });
                }
                else {
                    var tree = d3.layout.cluster()
                        .children(function(node) { return node.branchset; });
                    var nodes = tree(newick);
                    var h = nodes.length * 9;
                    tree = d3.layout.cluster()
                        .size([h, w])
                        .sort(function comparator(a, b) { return d3.ascending(a.length, b.length); })
                        .children(function(node) { return node.branchset; })
                        .separation(function separation(a, b) { return 8; });
                }
                nodes = tree(newick);
                
                //WRITE C1, C2, E1, etc LABELS
                if (langTree.name.indexOf("global") == -1) {
                    var labels = d3.select("language-phylogeny").append("svg:svg")
                        .attr("width", w+300)
                        .attr("height", 18)
                        .attr("id", "varLabels")
                        .attr("transform", "translate(-7,0)")
                        .attr("style", "visibility:hidden;");
                    labels.append("svg:rect")
                        .attr("width", "100%")
                        .attr("height", "100%")
                        .attr("fill", "white")
                        .attr("fill-opacity", "0.8");
                    var vis = d3.select("language-phylogeny").append("svg:svg")
                        .attr("width", w+300)
                        .attr("height", h+50)
                        .attr("class", "phylogeny")
                        .append("svg:g")
                        .attr("transform", "translate(2,5)");
                    keysWritten = 1;
                    translate = 0;
                    if (scope.query.variable_codes) {
                        for (var key in scope.results.code_ids) {
                            if (scope.results.code_ids[key].length > 0 || scope.results.code_ids[key].bf_var) {
                            vis.append("svg:text")
                                .attr("dx", w+translate-9)
                                .attr("dy", 10)
                                .text("C"+keysWritten);
                            labels.append("svg:text")
                                .attr("dx", w+translate)
                                .attr("dy", 15)
                                .text("C"+keysWritten);
                            scope.results.code_ids[key].CID = "C"+keysWritten;
                            keysWritten++;
                            translate += 20;
                            }
                        }
                    }
                    
                    if (scope.query.environmental_filters) {
                        vis.append("svg:text")
                            .attr("dx", w+translate-9)
                            .attr("dy", 10)
                            .text("E1");
                         labels.append("svg:text")
                            .attr("dx", w+translate)
                            .attr("dy", 15)
                            .text("E1");
                    }
                    
                    //---------------------------------------//
                    vis = vis.append("svg:g")
                        .attr("transform", "translate(0, 15)");
                    
                } else {
                    var vis = d3.select("language-phylogeny").append("svg:svg")
                        .attr("width", w)
                        .attr("height", w)
                        .attr("pointer-events", "all")
                        .call(d3.behavior.zoom().on("zoom", redraw))
                        .attr("class", "phylogeny")
                        .append("svg:g")
                        .attr("transform", "translate(400,400)");
                }
                function redraw() {
                vis.attr("transform",
                    "translate(" + d3.event.translate + ")" + "scale(" + d3.event.scale + ")");
                }   

                if (langTree.name.indexOf("global") != -1) {
                    var diagonal = radialRightAngleDiagonal();
                } else {
                    var diagonal = rightAngleDiagonal();    
                }
                nodes.forEach(function(node) {
                    node.rootDist = (node.parent ? node.parent.rootDist : 0) + (node.length || 0);
                });
                var rootDists = nodes.map(function(n) { return (n.rootDist); });
                var yscale = d3.scale.linear()
                    .domain([0, d3.max(rootDists)])
                    .range([0, w]);

                var leafDistFromRoot = 0;
                var longest_y = 0;
               nodes.forEach(function(node) {
                    if (node.rootDist > leafDistFromRoot)
                        leafDistFromRoot = node.rootDist;
                    if (langTree.name.indexOf("global") == -1)
                        node.y = yscale(node.rootDist);
                    if (node.y > longest_y)
                        longest_y = node.y;
                });
                
                //calculate time scale
                var timeScaleYears = leafDistFromRoot * 100; //convert to years
                var pixelScale = (w / timeScaleYears) * 100;
                
                var dotted = [];
                var links = tree.links(nodes);
                var link = vis.selectAll("path.link")
                    .data(links)
                    .enter().append("svg:path")
                    .attr("class", "link")
                    .attr("d", diagonal)
                    .attr("fill", "none")
                    .attr("stroke", "#ccc")
                    .attr("stroke-width", function() {
                        if (langTree.name.indexOf("global") != -1) return "0.5px";
                        else return "3.5px";
                    });
                var node = vis.selectAll("g.node")
                    .data(nodes)
                    .enter().append("svg:g")
                    .attr("class", function(n) {
                        if (n.children) return "inner-node";
                        else return "leaf-node";
                    })
                    .attr("transform", function(d) { 
                        if ((langTree.name.indexOf("global") != -1) || (langTree.name.indexOf("glotto") != -1)) {
                           if (!d.children) {
                            if (langTree.name.indexOf("global") != -1)
                                return "rotate("+(d.x-90)+")translate("+d.y+")";
                            else if (langTree.name.indexOf("glotto") !=  -1) {
                                dotted.push({'x':d.y, 'y':d.x})
                                return "translate(" + longest_y + ", " + d.x + ")";
                            }  
                           }
                           return "translate(" + d.y + ", "+ d.x + ")";
                        }
                        else return "translate(" + d.y + ", "+ d.x + ")";
                         });
                
                if (langTree.name.indexOf("glotto") != -1) {
                    for (var d = 0; d < dotted.length; d++) {
                        if (dotted[d].x == longest_y) continue;
                        vis.append("svg:line")
                            .attr("x1", dotted[d].x+5)
                            .attr("x2", longest_y-5)
                            .attr("y1", dotted[d].y)
                            .attr("y2", dotted[d].y)
                            .attr("stroke-width", "2")
                            .attr("stroke", "#ccc")
                            .attr("stroke-dasharray", "8, 5");
                    }
                }                
                //CODE FOR MARKERS ---
                translate = 0;
                //changes markers for global tree
                if (langTree.name.indexOf("global") != -1) {
                    scope.$watch('results.chosenTVariable', function(oldValue, newvalue) {
                        chosen_var_id = scope.results.chosenTVariable.id;
                        addMarkers(scope.results, chosen_var_id, node, true, translate);
                    });
                } 
                else {
                //markers for non-global trees
                if (scope.query.variable_codes) {
                    if (langTree.name.indexOf("global") == -1) {
                        for (var key in scope.results.code_ids) {
                            if (!(scope.query.environmental_filters && key==scope.query.environmental_filters[0].id)) {
                                addMarkers(scope.results, key, node, false, translate);
                                translate += 20; 
                            }
                        }
                    }
                }
                if (scope.query.environmental_filters) {
                    addMarkers(scope.results, scope.query.environmental_filters[0].id, node, false, translate);
                }
                
                else if (scope.query.language_classifications && !scope.query.environmental_filters) {
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
                                        hue = value * 240 / scope.results.classifications['NumClassifications'];
                                        return 'hsl('+hue+',100%, 50%)';
                                    }
                                });
                                
                        }
                        
                    });
                }
                }
                console.log(scope.query);
                scope.results.societies.forEach(function(society) {
                    var selected = node.filter(function(d) {
                        return d.name == society.society.iso_code;
                    });
                    
                    //lastly, append the text
                         var text = selected.select("text");
                         if (text[0][0]) {
                            text.html(society.society.name);
                        } else {  
                            selected.append("svg:text") 
                                .attr("dx", function(n) {
                                    if (langTree.name.indexOf("global") != -1) return 5;
                                    if (scope.query.environmental_filters && scope.query.variable_codes) return translate+20;
                                    else if (scope.query.variable_codes) return translate-5;
                                    else if (scope.query.environmental_filters) return translate+10;
                                    else if (scope.query.language_classifications) return translate+10;
                                    else return translate+5;
                                })                           
                            .attr("dy", function() { if (langTree.name.indexOf("global") == -1) return 4; else return 1; })
                            .attr("font-size", function() {
                                if (langTree.name.indexOf("global") == -1) return "12px";
                                else return "3px";
                            })
                            .attr("font-family", "Arial")
                            .text(function(d) { return society.society.name; }); 
                            }
                });
                
                //Time Scale
                if (langTree.name.indexOf("glotto") == -1 && langTree.name.indexOf("global") == -1) {
                    line_svg= d3.select('language-phylogeny').append("svg:svg")
                        .attr("style", "margin-left:100px;");
                    line_svg.append("svg:line")
                        .attr("x1", "0")
                        .attr("y1", "0")
                        .attr("x2", pixelScale)
                        .attr("y2", "0")
                        .attr("style", "stroke:#ccc;stroke-width:7;");
                    line_svg.append("svg:text")
                        .attr("dy", "20")
                        .attr("dx", function() {
                            text_pos = (pixelScale - 63) / 2;
                            if (text_pos < 0) return 0;
                            else return text_pos;
                        })
                        .text("100 years");
                }
                
                phyloWidth = d3.select("language-phylogeny").select("g").node().getBBox().width;
                d3.select("#legend")
                    .attr("style", "width:"+($(window).width()-phyloWidth-100)+"px; position:absolute; right:5px; z-index:1; margin-top:10px;");
            };

            scope.$on('treeSelected', function(event, args) {
                constructTree(args.tree);
                var pos = $("#varLabels").offset();
                $(window).scroll(function() {
                    //if ($(window).scrollTop() > 100)
                       // $("#legend").stop().animate({"marginTop":($(window).scrollTop() - 100) + "px"}, "slow");
                    if ($(window).scrollTop() > (pos.top - 20) && $("#varLabels").css('position') == 'static') {
                        d3.select("#varLabels")
                            .attr('class', 'var-labels-fixed')
                            .style("visibility", "visible");
                   } else if ($(window).scrollTop() < pos.top) {
                        d3.select("#varLabels")
                            .classed('var-labels-fixed', false)
                            .style("visibility", "hidden");
                    }
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
                    markerStyle: {
                        initial: {
                            "r": 2.7,
                            "stroke-width":0.5
                        }
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
                    
                    //needed for colorMap construction - creates a results object specific to the chosen variable
                    var results = {};
                    results.societies = [];
                    results.environmental_variables = scope.results.environmental_variables;
                    results.code_ids = scope.results.code_ids;
                    scope.results.societies.forEach(function(societyResult) {
                        var society = societyResult.society;
                        // Add a marker for each point
                        var marker = {latLng: [society.location.coordinates[1], society.location.coordinates[0]], name: society.name}
                        scope.map.addMarker(society.id, marker);
                        if (scope.results.variable_descriptions.indexOf(scope.chosen) != -1) {
                            societyResult.variable_coded_values.forEach(function(coded_value) {
                                if (coded_value.variable == scope.chosen.id) {
                                    if (scope.chosen.data_type == 'CONTINUOUS') {
                                        results.societies.push({
                                            'variable_coded_values':[coded_value],
                                            'environmental_values': [],
                                            'society':society,
                                            'bf_cont_var':true,
                                        });
                                    } else {
                                        results.societies.push({
                                            'variable_coded_values':[coded_value],
                                            'environmental_values': [],
                                            'society':society,
                                        });
                                    }
                                }
                            });
                        }
                        else if (scope.results.environmental_variables.indexOf(scope.chosen) != -1) {
                            societyResult.environmental_values.forEach(function(coded_value) {
                                if (coded_value.variable == scope.chosen.id) {
                                    results.societies.push({
                                        'environmental_values': [coded_value],
                                        'variable_coded_values':[],
                                        'society':society,
                                    });
                                }
                            });
                        } 
                        else {
                            societyResult.languages.forEach(function(language) {
                                var classification = scope.query.language_classifications.filter(function(l) { return l.language.id == language.id });
                                if (classification.length > 0) {
                                    results.societies.push({
                                    'society': society,
                                        'language_family': classification[0].class_subfamily,
                                        'num_classifications': scope.results.classifications['NumClassifications'],
                                        'environmental_values': [],
                                        'variable_coded_values': [],
                                    });
                                }
                            });
                        }
                    });

                    // Map IDs to colors
                    var colorMap = colorMapService.generateColorMap(results);
                    scope.map.series.markers[0].setValues(colorMap);

                    for (var i = 0; i < societyIds.length; i++) {
                        if (societyIds[i] in colorMap) continue;
                        else scope.map.removeMarkers([societyIds[i]]);
                    }
                    
                };
                
                //constructs download link for map
                scope.mapLink = function() {                     
                        d3.select(".download-links").html('');
                        var map_svg = d3.select(".jvectormap-container").select("svg")
                            .attr("version", 1.1)
                            .attr("xmlns", "http://www.w3.org/2000/svg")
                            .attr("height", "900")
                            .node().parentNode.innerHTML;
                        map_svg = map_svg.substring(0, map_svg.indexOf("<div")); //remove zoom in/out buttons from map
                        //construct legend for download
                        var legend = d3.select(".legend-for-download");
                        var legend_svg = "";
                        if (scope.chosen) {
                            if (scope.results.environmental_variables.length > 0 && scope.chosen.id == scope.results.environmental_variables[0].id) {
                                //if the chosen map is an environmental variable
                                    legend_svg = "<g transform='translate(0,350)'>"+d3.select(".envLegend").node().innerHTML+"</g>";
                            }
                            else if (scope.results.code_ids) {
                            for (var i = 0; i < scope.results.code_ids[scope.chosen.id].length; i++) {
                                g = legend.append("svg:g")
                                    .attr("transform", function() {
                                        return 'translate(0,'+i*25+')';
                                    });
                                g.append("svg:circle")
                                    .attr("cx", "10")
                                    .attr("cy", "10")
                                    .attr("r", "4.5")
                                    .attr("stroke", "#000")
                                    .attr("stroke-width", "0.5")
                                    .attr("fill", function() {
                                        if (scope.results.code_ids[scope.chosen.id][i].description.indexOf("Missing data") != -1)
                                            return 'hsl(0, 0%, 100%)';
                                        var value = scope.results.code_ids[scope.chosen.id][i].code;
                                        var hue = value * 240 / scope.results.code_ids[scope.chosen.id].length;
                                        return 'hsl('+hue+',100%,50%)';
                                    });
                                g.append("svg:text")
                                    .attr("x", "20")
                                    .attr("y", "15")
                                    .text(scope.results.code_ids[scope.chosen.id][i].description);
                            }
                            legend_svg = "<g transform='translate(0,350)'>"+legend.node().innerHTML+"</g>";
                            }
                            var map_svg = map_svg.substring(0, map_svg.indexOf("</svg>"));
                            map_svg = map_svg.concat(legend_svg+"</svg>");
                            //generate download
                            
                            var imgsrc = 'data:image/svg+xml;base64,' + window.btoa(unescape(encodeURIComponent(map_svg)));
                            d3.select(".download-links").append("td")
                                .attr("colspan", "2")
                                .attr("style", "padding-bottom:20px")
                                .append("a")
                                .attr("class", "btn btn-info btn-dplace-download")
                                .attr("download", scope.chosen.name+" map.svg")
                                .attr("href", imgsrc)
                                .html("Download Map");
                        }
                        
                        else if (scope.results.classifications && scope.results.languages.length > 0) {
                            count = 0;
                            for (var key in scope.results.classifications) {
                                for (var i = 0; i < scope.results.classifications[key].length; i++) {
                                    g = legend.append("svg:g")
                                        .attr("transform", function() {
                                            return 'translate(0,'+ count*25 + ')';
                                        });
                                    g.append("svg:circle")
                                        .attr("cx", "10")
                                        .attr("cy", "10")
                                        .attr("r", "4.5")
                                        .attr("stroke", "#000")
                                        .attr("stroke-width", "0.5")
                                        .attr("fill", function() {
                                            var value = scope.results.classifications[key][i].id;
                                            var hue = value * 240 / scope.results.classifications['NumClassifications'];
                                            return 'hsl('+hue+',100%,50%)';
                                        });
                                    g.append("svg:text")
                                        .attr("x", "20")
                                        .attr("y", "15")
                                        .text(scope.results.classifications[key][i].name);
                                    count++;
                                }
                                
                            }
                            var legend_svg = "<g transform='translate(0,350)'>"+legend.node().innerHTML+"</g>";
                            var map_svg = map_svg.substring(0, map_svg.indexOf("</svg>"));
                            map_svg = map_svg.concat(legend_svg+"</svg>");
                            var imgsrc = 'data:image/svg+xml;base64,' + window.btoa(unescape(encodeURIComponent(map_svg)));
                            lang_family = scope.results.languages[0].language_family.name;
                            
                            d3.select(".download-links").append("td")
                                .attr("colspan", "2")
                                .attr("style", "padding-bottom:20px")
                                .append("a")
                                .attr("class", "btn btn-info btn-dplace-download")
                                .attr("download", lang_family+"map.svg")
                                .attr("href", imgsrc)
                                .html("Download Map: " + lang_family);
                        }
                };
                
                scope.mapLegend = function() {
                    if (scope.chosen.id == 34 || scope.chosen.id == 36) {
                        d3.selectAll(".envVar").attr("fill", "url(#earthy)");
                    } else if (scope.chosen.id == 27) {
                        d3.selectAll(".envVar").attr("fill", "url(#blue)");
                    }
                    
                    else {
                        d3.selectAll(".envVar").attr("fill", "url(#temp)");
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
                        scope.mapLegend();
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