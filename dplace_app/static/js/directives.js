angular.module('languagePhylogenyDirective', [])
    .directive('languagePhylogeny', function(colorMapService) {
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

            var addMarkers = function(langTree, results, variable, node, global, translate) { 
                scope.results.societies.forEach(function(society) {
                    var selected = node.filter(function(d) {
                        return (d.name == society.society.name);
                    });
                    if (global) selected.select("circle").remove(); 
                    var society_name = society.society.name;
                    if (society.society.language) society_name += " (" + society.society.language.glotto_code + ")"; //formerly isocode
                    
                    if (!variable) {
                        if (!global) return;
                        if (scope.query.l) {
                            for (var i = 0; i < society.languages.length; i++) {

                                selected.append("svg:circle")
                                    .attr("r", 1.5)
                                    .attr("stroke", "#000")
                                    .attr("stroke-width", "0.5")
                                    .attr("fill", function(n) {
                                        value = society.languages[i].family.id;
                                        rgb = colorMapService.mapColor(value, results.classifications.length);
                                        return rgb;
                                        
                                    })
                                    .on("mouseover", function() {
                                         d3.select("body").append("div")
                                            .attr("class", "tree-tooltip")
                                            .html("<b>"+society_name+"</b>")
                                            .style("z-index", 1000)
                                            .style("max-width", "250px")
                                            .style("left", (d3.event.pageX + 10)+"px")
                                            .style("top", (d3.event.pageY + 5)+"px");
                                    })
                                    .on("mouseout", function() {
                                        d3.select(".tree-tooltip").remove();
                                    });
                                
                            }
                        
                        } else if (scope.query.p) {
                            for (var i = 0; i < society.geographic_regions.length; i++) {
                                selected.append("svg:circle")
                                    .attr("r", 1.5)
                                    .attr("stroke", "#000")
                                    .attr("stroke-width", "0.5")
                                    .attr("fill", function(n) {
                                        value = society.geographic_regions[i].tdwg_code;
                                        rgb = colorMapService.mapColor(value, results.geographic_regions.length);
                                        return rgb;
                                    })
                                    .on("mouseover", function() {
                                         d3.select("body").append("div")
                                            .attr("class", "tree-tooltip")
                                            .html("<b>"+society_name+"</b>")
                                            .style("z-index", 1000)
                                            .style("max-width", "250px")
                                            .style("left", (d3.event.pageX + 10)+"px")
                                            .style("top", (d3.event.pageY + 5)+"px");
                                    })
                                    .on("mouseout", function() {
                                        d3.select(".tree-tooltip").remove();
                                    });
                            }
                        }
                    
                    }
                    
                    //if the marker is an environmental variable      
                    if (society.environmental_values.length > 0) {
                        for (var i = 0; i < society.environmental_values.length; i++) {
                            if (society.environmental_values[i].variable == variable.id) {
                                var hover_text_value = society.environmental_values[i].value + ' ' + variable.units;
                                selected.append("svg:circle")
                                    .attr("r", function() {
                                        if (global) return 1.5;
                                       else return 4.5;
                                    })
                                    .attr("stroke", "#000")
                                    .attr("stroke-width", "0.5")
                                    .attr("transform", "translate("+translate+",0)")
                                    .attr("fill", function(n) {
                                        rgb = colorMapService.tempColor(society.environmental_values[i].value, variable.min, variable.max, variable.name);
                                        return rgb;
                                    })
                                    .on("mouseover", function() {
                                         d3.select("body").append("div")
                                            .attr("class", "tree-tooltip")
                                            .html("<b>"+society_name+":</b><br>"+hover_text_value)
                                            .style("z-index", 1000)
                                            .style("max-width", "250px")
                                            .style("left", (d3.event.pageX + 10)+"px")
                                            .style("top", (d3.event.pageY + 5)+"px");
                                    })
                                    .on("mouseout", function() {
                                        d3.select(".tree-tooltip").remove();
                                    });
                            } 
                        }
                    
                    } 
                    if (society.variable_coded_values.length > 0 && variable.variable) {
                        for (var i = 0; i < society.variable_coded_values.length; i++) {
                            if (society.variable_coded_values[i].variable == variable.variable.id) {
                                if (variable.variable.data_type.toUpperCase() == 'CONTINUOUS') {
                                    var hover_text_value = society.variable_coded_values[i].coded_value;
                                    if (variable.variable.units) hover_text_value += ' ' + variable.variable.units;
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
                                                   return 'rgb(255, 255, 255)';
                                                }
                                                value = society.variable_coded_values[i].coded_value;     
                                                 if (variable.variable.data_type.toUpperCase() == 'CONTINUOUS') {
                                                    var min = variable.variable.min;
                                                    var max = variable.variable.max;
                                                    rgb = colorMapService.mapColorMonochrome(min, max, value, 0);
                                                    return rgb;
                                                } 
                                                if (variable.variable.data_type.toUpperCase() == 'ORDINAL') {
                                                    rgb = colorMapService.generateRandomHue(value, variable.codes.length, variable.variable.id, 5);
                                                    return rgb;
                                                }
                                                
                                                rgb = colorMapService.colorMap[parseInt(value)];
                                                return  rgb;
                                        })
                                        .on("mouseover", function() {
                                             d3.select("body").append("div")
                                                .attr("class", "tree-tooltip")
                                                .html("<b>"+society_name+":</b><br>"+hover_text_value)
                                                .style("z-index", 1000)
                                                .style("max-width", "250px")
                                                .style("left", (d3.event.pageX + 10)+"px")
                                                .style("top", (d3.event.pageY + 5)+"px");
                                        })
                                        .on("mouseout", function() {
                                            d3.select(".tree-tooltip").remove();
                                        }); 
                                }
                            }
                        }
                });
            };
            
            var addLogo = function(height) {
                $.get("/static/images/D-PLACE_VLogo_RGB.svg", function(data) {
                    var svg_data = data.childNodes;
                    d3.select(".phylogeny").append("svg:g")
                        .attr("transform", "scale(0.5) translate(500,0)")
                        .attr("style", "opacity: 0.35;")
                        .attr("id", "tree-logo");
                    document.getElementById("tree-logo").innerHTML = svg_data[1].innerHTML;
                });
            };
                        
            var constructTree = function(langTree) {   
                d3.select("language-phylogeny").html('');
                var newick = Newick.parse(langTree.newick_string);
                if (langTree.name.indexOf("global") != -1) var w = 900;
                else  var w = 500;
                if (langTree.name.indexOf("global") != -1)  {
                    var tree = d3.layout.cluster()
                    .size([360, (w/2)-100])
                    .sort(function(node) { return node.children ? node.children.length : -1; })
                    .children(function(node) { return node.branchset; })
                    .separation(function separation(a, b) { return 8; });
                } else {
                    var tree = d3.layout.cluster()
                        .children(function(node) { return node.branchset; });
                    var nodes = tree(newick);
                    var h = nodes.length * 8;
                    tree = d3.layout.cluster()
                        .size([h, w])
                        .sort(function comparator(a, b) { return d3.ascending(a.length, b.length); })
                        .children(function(node) { return node.branchset; })
                        .separation(function separation(a, b) { return 8; });
                }
                nodes = tree(newick);
                
                //WRITE C1, C2, E1, etc LABELS
                if (langTree.name.indexOf("global") == -1) {
                    /*var labels = d3.select("language-phylogeny").append("svg:svg")
                        .attr("width", w+300)
                        .attr("height", 18)
                        .attr("id", "varLabels")
                        .attr("transform", "translate(-7,0)")
                        .attr("style", "visibility:hidden;");
                    labels.append("svg:rect")
                        .attr("width", "100%")
                        .attr("height", "100%")
                        .attr("fill", "white")
                        .attr("fill-opacity", "0.8");*/
                    var vis = d3.select("language-phylogeny").append("svg:svg")
                        .attr("width", w+200)
                        .attr("height", h+150)
                        .attr("class", "phylogeny")
                        .append("svg:g")
                        .attr("transform", "translate(2,5)");
                    keysWritten = 1;
                    translate = 0;
                    if (scope.query.c) {
                        for (var r = 0; r < scope.results.variable_descriptions.length; r++) {
                            vis.append("svg:text")
                                .attr("dx", w+translate-9)
                                .attr("dy", 10)
                                .text("C"+keysWritten);
                            /*labels.append("svg:text")
                                .attr("dx", w+translate)
                                .attr("dy", 15)
                                .text("C"+keysWritten);*/
                            scope.results.variable_descriptions[r].CID = "C"+keysWritten;
                            keysWritten++;
                            translate += 20;
                        }                 
                       
                    }
                    
                    if (scope.query.e) {
                        keysWritten = 1;
                        for (var r = 0; r < scope.results.environmental_variables.length; r++) {
                            vis.append("svg:text")
                                .attr("dx", w+translate-9)
                                .attr("dy", 10)
                                .text("E"+keysWritten);
                             /*labels.append("svg:text")
                                .attr("dx", w+translate)
                                .attr("dy", 15)
                                .text("E"+keysWritten);*/
                                scope.results.environmental_variables[r].CID = "E"+keysWritten;
                                keysWritten++;
                                translate += 20;
                        }
                    }
                    
                    //---------------------------------------//
                    vis = vis.append("svg:g")
                        .attr("transform", "translate(0, 15)");
                    
                } else {
                    var vis = d3.select("language-phylogeny").append("svg:svg")
                        .attr("width", w)
                        .attr("height", w)
                        .attr("pointer-events", "all")
                        .call(d3.behavior.zoom().on("zoom", redraw).translate([w/2,w/2]))
                        .attr("class", "phylogeny")
                        .append("svg:g")
                        .attr("transform", "translate("+w/2+","+w/2+")");
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
                
                taxa = {}
                include = scope.results.societies.map(function(s) { return s.society.ext_id; });
                for (var i = 0; i < langTree.taxa.length; i++) {
                   for (var t = 0; t < langTree.taxa[i].societies.length; t++) {
                        if (include.indexOf(langTree.taxa[i].societies[t].society.ext_id) != -1) {
                            if (langTree.taxa[i].label in taxa)
                                continue; 
                            taxa[langTree.taxa[i].label] = langTree.taxa[i].societies[t];
                        }
                    }
                }
                nodes.forEach(function(node) {
                    node.rootDist = (node.parent ? node.parent.rootDist : 0) + (node.length || 0);
                    if (node.name in taxa) {
                        node.name = taxa[node.name].society.name;
                    }
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
                        //if ((langTree.name.indexOf("global") != -1) || (langTree.name.indexOf("glotto") != -1)) {
                           if (!d.children) {
                            if (langTree.name.indexOf("global") != -1)
                                return "rotate("+(d.x-90)+")translate("+d.y+")";
                            else {//if (langTree.name.indexOf("glotto") !=  -1) {
                                dotted.push({'x':d.y, 'y':d.x})
                                return "translate(" + longest_y + ", " + d.x + ")";
                            }  
                           }
                           return "translate(" + d.y + ", "+ d.x + ")";
                        //}
                        //else return "translate(" + d.y + ", "+ d.x + ")";
                         });
                
                //if (langTree.name.indexOf("glotto") != -1) {
                    for (var d = 0; d < dotted.length; d++) {
                        if (dotted[d].x >= longest_y-4) continue;
                        vis.append("svg:line")
                            .attr("x1", dotted[d].x)
                            .attr("x2", longest_y-5)
                            .attr("y1", dotted[d].y)
                            .attr("y2", dotted[d].y)
                            .attr("stroke-width", "3.5px")
                            .attr("stroke", "#ccc")
                    }
                //}                
                //CODE FOR MARKERS ---
                translate = 0;
                //changes markers for global tree
                if (langTree.name.indexOf("global") != -1) {
                    if ((scope.query.l || scope.query.p) && !scope.query.e && !scope.query.c) {
                            addMarkers(langTree, scope.results, null, node, true, translate);
                    }

                    scope.$watch('results.chosenTVariable', function(oldValue, newvalue) {
                    if (scope.results.chosenTVariable) {
                            chosen_var_id = scope.results.variable_descriptions.filter(function(variable) { return variable.variable.id == scope.results.chosenTVariable.id });
                            if (chosen_var_id.length > 0)
                                addMarkers(langTree, scope.results, chosen_var_id[0], node, true, translate);
                            else {
                                d3.select(".envVar").attr("fill", function() {
                                    if (scope.results.chosenTVariable.name == "Monthly Mean Precipitation") {console.log("blue"); return "url(societies#blue)";}
                                    else if (scope.results.chosenTVariable.name == "Net Primary Production" || scope.results.chosenTVariable.name == "Mean Growing Season NPP") return "url(societies#earthy)";
                                    else return "url(societies#temp)";
                                });
                                addMarkers(langTree, scope.results,scope.results.chosenTVariable, node, true, translate);
                            }
                        } 
                    });
                } 
                else {
                //markers for non-global trees
                    if (scope.query.c) {
                        for (var r = 0; r < scope.results.variable_descriptions.length; r++) { 
                            addMarkers(langTree, scope.results, scope.results.variable_descriptions[r], node, false, translate);
                            translate += 20;
                        }
                    }
                    if (scope.query.e) {
                        for (var r = 0; r < scope.results.environmental_variables.length; r++) {
                            if (!d3.select("#e"+scope.results.environmental_variables[r].id).select("svg")[0][0]) {
                                legend = d3.select("#e"+scope.results.environmental_variables[r].id).append("svg:svg")
                                    .attr("height", "50")
                                    .attr("width", "400")
                                    .attr("class", "envLegend");
                                legend.append("svg:rect")
                                    .attr("height", "30")
                                    .attr("width", "250")
                                    .attr("x", "20")
                                    .attr("fill", function() {
                                    if (scope.results.environmental_variables[r].name == "Net Primary Production" || scope.results.environmental_variables[r].name == "Mean Growing Season NPP") 
                                       return "url(societies#earthy)";
                                   else if (scope.results.environmental_variables[r].name == "Monthly Mean Precipitation") 
                                        return "url(societies#blue)";
                                    else return "url(societies#temp)";
                                    });
                                legend.append("svg:text")
                                    .attr("x", "0")
                                    .attr("y", "45")
                                    .text(scope.results.environmental_variables[r].min + ' ' + scope.results.environmental_variables[r].units);
                                legend.append("svg:text")
                                    .attr("x", "250")
                                    .attr("y", "45")
                                    .text(scope.results.environmental_variables[r].max + ' ' + scope.results.environmental_variables[r].units);
                            }
                            addMarkers(langTree, scope.results, scope.results.environmental_variables[r], node, false, translate);
                            translate += 20;
                        }
                    }
                    
                    if (scope.query.l && !scope.query.e && !scope.query.c) {
                        addMarkers(langTree, scope.results, null, node, false, translate);
                    }
                }
                                
                scope.results.societies.forEach(function(society) {
                    var selected = node.filter(function(d) {
                        return d.name == society.society.name;
                    });
                    //lastly, append the text
                         var text = selected.select("text");
                         if (text[0][0]) {
                            text.html(society.society.name);
                        } else {  
                            selected.append("svg:text") 
                                .attr("dx", function(n) {
                                    if (langTree.name.indexOf("global") != -1) return 5;
                                    if (scope.query.e && scope.query.c) return translate+20;
                                    else if (scope.query.c) return translate-5;
                                    else if (scope.query.e) return translate+10;
                                    else if (scope.query.l) return translate+10;
                                    else return translate+5;
                                })                           
                            .attr("dy", function() { if (langTree.name.indexOf("global") == -1) return 4; else return 1; })
                            .attr("font-size", function() {
                                if (langTree.name.indexOf("global") == -1) return "12px";
                                else return "3px";
                            })
                            .attr("font-family", "Arial")
                            .text(function(d) { 
                                return society.society.name; 
                            }); 
                            }
                });
                d3.selectAll(".inner-node").select("circle").remove();
                d3.selectAll(".inner-node").select("text").remove();
                
                //Time Scale
                if (langTree.name.indexOf("glotto") == -1 && langTree.name.indexOf("global") == -1) {
                    line_svg= d3.select('language-phylogeny').append("svg:svg")
                        .attr("style", "margin-left:100px; margin-top:-100px;");
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
                
                if (langTree.name.indexOf("global") == -1) addLogo(h/2);   
            };

            scope.$on('treeSelected', function(event, args) {
                constructTree(args.tree);
             
                $(window).scroll(function() {
                    if($(".phylogeny").height() > $("#legend").height()) {
                        
                        if ($(window).scrollTop() > $(".navbar").height()+250) {
                            if (args.tree.name.indexOf("global") == -1) {
                                if (document.getElementsByClassName("in").length > 0) {
                                    bottom = document.getElementsByClassName("in")[0].getBoundingClientRect().top;
                                    margTop = document.getElementById("legend").getBoundingClientRect().top;
                                    difference = bottom - margTop;
                                    $("#legend").stop().animate({"marginTop": ($(window).scrollTop() - 290 - difference) + "px"}, "slow");
                                } else { 
                                    $("#legend").stop().animate({"marginTop":($(window).scrollTop() - 350) + "px"}, "slow");
                                }
                                        
                            } else
                                $("#legend").stop().animate({"marginTop": ($(window).scrollTop() - 300) + "px"}, "slow");
                            
                        } else {
                            $("#legend").stop().animate({"marginTop": "0px"}, "slow");
                        }
                    }
                        
                    /*if ($(window).scrollTop() > $(".navbar").height()+250) {
                        d3.select("#varLabels")
                            .attr('class', 'var-labels-fixed')
                            .style("visibility", "visible");
                   } else {
                        d3.select("#varLabels")
                            .classed('var-labels-fixed', false)
                            .style("visibility", "hidden");
                    }*/
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
            element.append("<div id='" + mapDivId + "' style='width:800px; height:30rem;'></div>");
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
                    onMarkerClick: function(e, code) {
                        window.open("/society/"+scope.map.series.markers[0].elements[code].config.weburl);
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
                    
                $.get("/static/images/D-PLACE_VLogo_RGB.svg", function(data) {
                    var svg_data = data.childNodes;
                    d3.selectAll(".jvectormap-container svg g").insert("svg:g")
                        .attr("transform", "scale(0.35) translate(30, 800)")
                        .attr("style", "opacity: 0.35;")
                    .attr("id", "map-logo");
                    document.getElementById("map-logo").innerHTML = svg_data[1].innerHTML;
                });

                
                scope.addMarkers = function() {
                    if (!scope.map) {
                        return;
                    }
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
                    results.geographic_regions = scope.results.geographic_regions;
                    results.languages = scope.results.languages;
                    results.variable_descriptions = scope.results.variable_descriptions;
                    scope.results.societies.forEach(function(societyResult) {
                        var society = societyResult.society;
                        // Add a marker for each point
                        var marker = {latLng: [society.location.coordinates[1], society.location.coordinates[0]], name: society.name, weburl: society.ext_id}
                        
                         if (!scope.chosen) {   
                            results = scope.results;
                        } else {
                            variable = scope.results.variable_descriptions.filter(function(var_code) {
                                return var_code.variable == scope.chosen;
                            });
                        
                            if (variable.length > 0) {
                                societyResult.variable_coded_values.forEach(function(coded_value) {
                                    if (coded_value.variable == scope.chosen.id) {
                                        if (coded_value.code_description && coded_value.code_description.description.indexOf("Missing data") != -1) {
                                            return;
                                        }
                                        if (scope.chosen.data_type.toUpperCase() == 'CONTINUOUS') {
                                            results.societies.push({
                                                'variable_coded_values':[coded_value],
                                                'environmental_values': [],
                                                'society':society,
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
                        }
                        scope.map.addMarker(society.id, marker); 
                    });

                    // Map IDs to colors
                    var colorMap = colorMapService.generateColorMap(results);
                    scope.map.series.markers[0].setValues(colorMap);

                    for (var i = 0; i < societyIds.length; i++) {
                        if (societyIds[i] in colorMap) continue;
                        else scope.map.removeMarkers([societyIds[i]]);
                    }
                };

                scope.mapLegend = function() {
                    if (!scope.chosen) return;
                    if (scope.chosen.name == "Net Primary Production" || scope.chosen.name == "Mean Growing Season NPP") {
                        d3.selectAll(".envVar").attr("fill", "url(societies#earthy)");
                    } else if (scope.chosen.name == "Monthly Mean Precipitation") {
                        d3.selectAll(".envVar").attr("fill", "url(societies#blue)");
                    }
                    else {
                        d3.selectAll(".envVar").attr("fill", "url(societies#temp)");
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
