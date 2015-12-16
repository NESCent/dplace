function SocietiesCtrl($scope, $timeout, searchModelService, LanguageClass, ZipTest) {
    $scope.results = searchModelService.getModel().getResults();
    $scope.query = searchModelService.getModel().getQuery();
    $scope.variables = [];
    $scope.buttons = [
        {value:'phylogeny', name:'Phylogenies', description: "Trees derived from discrete data using phylogenetic methods (branch lengths informative)"},
        {value:'glottolog', name:'Glottolog Trees', description: "Trees derived Glotolog language family taxonomies (branch lengths uninformative)"},
        {value:'global', name:'Global Tree', description: "A global language supertree composed from language family taxonomies in Glottolog (branch lengths uninformative)"},
    ];
    
    $scope.tabs = [
        { title: "Table", content: "table", active: true},
        { title: "Map", content: "map", active: false},
        { title: "Tree", content: "tree", active: false},
        { title: "Download", content: "download", active: false},
    ];
        
    console.log($scope.results);
    if ($scope.results.variable_descriptions) {
        $scope.variables = $scope.variables.concat($scope.results.variable_descriptions);
    }
        
    if ($scope.query.environmental_filters) {
        $scope.variables = $scope.variables.concat($scope.results.environmental_variables);
    }
    
    for (var key in $scope.results.code_ids) {
        $scope.results.code_ids[key]['svgSize'] = $scope.results.code_ids[key].length * 27;
    }
    
    $scope.setActive('societies');
    
    var num_lines = 0;              
    $scope.wrapText = function(text, string) {
        text.each(function() {
            var text = d3.select(this),
            words = string.split(/\s+/).reverse(),
            word,
            line = [],
            lineNumber = 0,
            lineHeight = 0.1,
            x = text.attr("x"),
            y = 0,
            dy = 1,
            tspan = text.text(null)
                .append("svg:tspan")
                .attr("x", x)
                .attr("y", y)
                .attr("dy", dy + "em");
            while (word = words.pop()) {
                line.push(word);
                tspan.text(line.join(" "));
                if (tspan.node().getComputedTextLength() > 800) {
                    y += 20;
                    line.pop();
                    tspan.text(line.join(" "));
                    line = [word];
                    tspan = text.append("svg:tspan")
                        .attr("x", "20")
                        .attr("y", y)
                        .attr("dy", ++lineNumber * lineHeight + dy + "em")
                        .text(word);
                    num_lines += 1;
                }
            }
        });
        
    };
    
    $scope.constructMapDownload = function() {
        d3.select(".legend-for-download").html('');
        d3.select(".download-links").html('');
        num_lines = 0;
        var gradients_svg = d3.select("#gradients").node().innerHTML;
        map_svg = d3.select(".jvectormap-container").select("svg")
                        .attr("version", 1.1)
                        .attr("xmlns", "http://www.w3.org/2000/svg")
                        .attr("height", function() {
                            if ($scope.results.chosenVariable && $scope.results.environmental_variables.length > 0 && $scope.results.chosenVariable == $scope.results.environmental_variables[0]) return "500";
                            else return "1500";
                        })
                        .node().parentNode.innerHTML;
        map_svg = map_svg.substring(0, map_svg.indexOf("<div")); //remove zoom in/out buttons from map
        
        //construct legend for download
        var legend = d3.select(".legend-for-download");
        var legend_svg = "";
        
        //cultural and environmental variables
        if ($scope.results.chosenVariable) {
            if ($scope.results.environmental_variables.length > 0 && $scope.results.chosenVariable == $scope.results.environmental_variables[0]) {
                //if the chosen map is an environmental variable
                    legend_svg = "<g transform='translate(0,350)'>"+d3.select(".envLegend").node().innerHTML+"</g>";
            }
            else if ($scope.results.code_ids) {
                //cultural variables
                for (var i = 0; i < $scope.results.code_ids[$scope.results.chosenVariable.id].length; i++) {
                    g = legend.append("svg:g")
                        .attr("transform", function() {
                                return 'translate(0,'+((num_lines)*25)+')';
                        });
                    g.append("svg:circle")
                        .attr("cx", "10")
                        .attr("cy", "10")
                        .attr("r", "4.5")
                        .attr("stroke", "#000")
                        .attr("stroke-width", "0.5")
                        .attr("fill", function() {
                            if ($scope.results.code_ids[$scope.results.chosenVariable.id][i].description.indexOf("Missing data") != -1)
                                return 'hsl(0, 0%, 100%)';
                            var value = $scope.results.code_ids[$scope.results.chosenVariable.id][i].code;
                            var hue = value * 240 / $scope.results.code_ids[$scope.results.chosenVariable.id].length;
                            return 'hsl('+hue+',100%,50%)';
                        });
                    g.append("svg:text")
                        .attr("x", "20")
                        .attr("y", "15")
                        .attr("style", "font-size: 14px;")
                        .call($scope.wrapText, $scope.results.code_ids[$scope.results.chosenVariable.id][i].description);
                    num_lines += 1;
                }

                legend_svg = "<g transform='translate(0,350)'>"+legend.node().innerHTML+"</g>";
            }
            var map_svg = map_svg.substring(0, map_svg.indexOf("</svg>"));
            map_svg = map_svg.concat(legend_svg);
            map_svg = map_svg.concat(gradients_svg +"</svg>");
            //generate download
            var imgsrc = 'data:image/svg+xml;base64,' + window.btoa(unescape(encodeURIComponent(map_svg)));
            d3.select(".download-links").append("td")
                .attr("colspan", "2")
                .attr("style", "padding-bottom:20px")
                .append("a")
                .attr("class", "btn btn-info btn-dplace-download")
                .attr("download", $scope.results.chosenVariable.name.replace(" ", "-").toLowerCase()+"-map.svg")
                .attr("href", imgsrc)
                .html("Download Map");
        }
        
        else if ($scope.results.classifications && $scope.results.languages.length > 0) {
            count = 0;
            for (var key in $scope.results.classifications) {
                for (var i = 0; i < $scope.results.classifications[key].length; i++) {
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
                            var value = $scope.results.classifications[key][i].id;
                            var hue = value * 240 / $scope.results.classifications['NumClassifications'];
                            return 'hsl('+hue+',100%,50%)';
                        });
                    g.append("svg:text")
                        .attr("x", "20")
                        .attr("y", "15")
                        .text($scope.results.classifications[key][i].name);
                    count++;
                }
                
            }
            var legend_svg = "<g transform='translate(0,350)'>"+legend.node().innerHTML+"</g>";
            var map_svg = map_svg.substring(0, map_svg.indexOf("</svg>"));
            map_svg = map_svg.concat(legend_svg+"</svg>");
            var imgsrc = 'data:image/svg+xml;base64,' + window.btoa(unescape(encodeURIComponent(map_svg)));
            lang_family = $scope.results.languages[0].language_family.name;
            
            d3.select(".download-links").append("td")
                .attr("colspan", "2")
                .attr("style", "padding-bottom:20px")
                .append("a")
                .attr("class", "btn btn-info btn-dplace-download")
                .attr("download", lang_family+"map.svg")
                .attr("href", imgsrc)
                .html("Download Map");
        }
    }
    
    $scope.tabChanged = function() {
        if ($scope.tabs[1].active) {
            $scope.constructMapDownload();
        }
    }
    
    $scope.buttonChanged = function(buttonVal) {
        d3.select('language-phylogeny').html('');
        $scope.globalTree = false;
        if (buttonVal.indexOf("global") != -1) {
            $scope.globalTree = true;
            $scope.results.selectedTree = $scope.results.language_trees.global_tree;
            $scope.treeSelected();
        }
        if (buttonVal.indexOf('phylogeny') != -1) {
            $scope.trees = $scope.results.language_trees.phylogenies;
        } else {
            $scope.trees = $scope.results.language_trees.glotto_trees;
        }
    };
    
    $scope.treeSelected = function() {
        $scope.$broadcast('treeSelected', {tree: $scope.results.selectedTree});
        d3.select(".tree-download").html('');
        if ($scope.results.selectedTree.name.indexOf("global") == -1) {
            $scope.globalTree = false;
            $scope.treeDownload();
        } else {
            $scope.globalTree = true;
        }
        
        //for environmental legend
        if ($scope.results.environmental_variables.length > 0) {
            if ($scope.results.environmental_variables[0].name == 'Net Primary Production' || $scope.results.environmental_variables[0].name == 'Mean Growing Season NPP') 
                d3.selectAll(".envVar").attr("fill", "url(#earthy)");
            else if ($scope.results.environmental_variables[0].name == "Annual Mean Precipitation")
                d3.selectAll(".envVar").attr("fill", "url(#blue)");
            else 
                d3.selectAll(".envVar").attr("fill", "url(#temp)");
        }
        
    };
    
    $scope.showOrHide = function(chosenVarId, id) {
        if (!$scope.globalTree) return false;
        
        if (chosenVarId == id) return false;
        else return true;
    };
    
    $scope.legendArrow = function(code) {
        if (code.hidden) code.hidden = false;
        else code.hidden = true;
    };
    
    $scope.clicked = function(trees) {
        if (trees.length == 1) {
            tree_to_display = trees[0].name;
        } else {
            var i = 0;
            while (trees[i].name.indexOf("global") != -1) {
                i++;
            }
            tree_to_display = trees[i].name;
        }
        
        if (tree_to_display.indexOf("global") != -1) {
            $scope.results.selectedButton = $scope.buttons[2];
        }
       else if (tree_to_display.indexOf("glotto") == -1) 
            $scope.results.selectedButton = $scope.buttons[0];
        else 
            $scope.results.selectedButton = $scope.buttons[1];
            
        $scope.buttonChanged($scope.results.selectedButton.value);
        tree = $scope.trees.filter(function(t) {
            return t.name == tree_to_display;
        });

        if (tree.length > 0) {
            $scope.results.selectedTree = tree[0];
            $scope.treeSelected();
        }
        $scope.tabs[2].active = true;
    }
    
    $scope.treeDownload = function() {
        var tree_svg = d3.select(".phylogeny")
            .attr("version", 1.1)
            .attr("xmlns", "http://www.w3.org/2000/svg")
            .node().parentNode.innerHTML;
         tree_svg = tree_svg.substring(tree_svg.indexOf("<svg xml"));
         tree_svg = tree_svg.substring(0, tree_svg.indexOf("</svg>"));
         tree_svg = tree_svg.concat("</svg>");
         var all_legends = {};
        legends = [];

        d3.selectAll(".legends").each( function(){
                item = d3.select(this);
                if (item.attr("var-id")) {
                   if (item.attr("class").indexOf("hide") == -1)
                    all_legends[item.attr("var-id")] = item;
                }
            });
            
        for (var key in $scope.results.code_ids) {
                item = all_legends[key];
                name = $scope.results.code_ids[key].name;
                svg_string = item.node().innerHTML;
                svg_string = '<svg version="1.1" xmlns="http://www.w3.org/2000/svg">' + svg_string + '</svg>';
                legends.push({'name': name.replace(/[\W]+/g, "-")+'-legend.svg', 'svg': svg_string});    
        }
        
        
        query = {"legends": legends, "tree": tree_svg, "name": $scope.results.selectedTree.name+'.svg'};
        d3.select(".tree-download").append("a")
            .attr("class", "btn btn-info btn-dplace-download")
            .attr("download", "legend.svg")
            .attr("href", "/api/v1/zip_legends?query="+encodeURIComponent(JSON.stringify(query)))
            .html("Download this phylogeny");
    };
    
    $scope.showComments = function(society, variable_id) {
        for (var i = 0; i < society.variable_coded_values.length; i++) {
            if (society.variable_coded_values[i].variable == variable_id) {
                if ((society.variable_coded_values[i].focal_year.length > 0 && society.variable_coded_values[i].focal_year != 'NA') || society.variable_coded_values[i].comment.length > 0)
                    return true
                else    
                    return false
            }
        }
    };
    
    $scope.showSource = function(society, variable_id) {
        for (var i = 0; i < society.variable_coded_values.length; i++) {
            if (society.variable_coded_values[i].variable == variable_id) {
                if (society.variable_coded_values[i].references.length > 0)
                    return true;
                else return false;
            }
        }
        return false;
    };

    
    $scope.changeMap = function(chosenVariable) {
        $timeout(function() { $scope.constructMapDownload(); });

    }

    $scope.generateDownloadLinks = function() {
        // queryObject is the in-memory JS object representing the chosen search options
        var queryObject = searchModelService.getModel().getQuery();
        // the CSV download endpoint is a GET URL, so we must send the query object as a string.
        var queryString = encodeURIComponent(JSON.stringify(queryObject));
        // format (csv/svg/etc) should be an argument, and change the endpoint to /api/v1/download
        $scope.csvDownloadLink = "/api/v1/csv_download?query=" + queryString;
    };
    
    $scope.generateDownloadLinks();
    
}
