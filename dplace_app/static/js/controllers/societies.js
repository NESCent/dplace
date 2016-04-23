function SocietiesCtrl($scope, $timeout, $http, searchModelService, colorMapService) {
    $scope.results = searchModelService.getModel().getResults();
    $scope.query = searchModelService.getModel().getQuery();
    $scope.variables = [];

    $scope.buttons = [];
    if ($scope.results && $scope.results.language_trees) {
        if ($scope.results.language_trees.phylogenies.length > 0) {
            $scope.buttons.push({value:'phylogeny', name:'Phylogenies', description: "Trees derived from discrete data using phylogenetic methods (branch lengths informative)"});
        }
        if ($scope.results.language_trees.glotto_trees.length > 0) {
            $scope.buttons.push({value:'glottolog', name:'Glottolog Trees', description: "Trees derived from Glottolog language family taxonomies (branch lengths uninformative)"});
        }
        if ($scope.results.language_trees.global_tree) {
            $scope.buttons.push({value:'global', name:'Global Tree', description: "A global language supertree composed from language family taxonomies in Glottolog (branch lengths uninformative)"});
        }
    }

    $scope.tabs = [
        { title: "Table", content: "table", active: true},
        { title: "Map", content: "map", active: false},
        { title: "Tree", content: "tree", active: false},
        { title: "Download", content: "download", active: false},
    ];
        
    console.log($scope.results);
    
    $scope.csvDownloadButton = {text: 'CSV', disabled: false};

    if ($scope.results.variable_descriptions) {
        $scope.results.variable_descriptions.forEach(function(variable) {
            $scope.variables.push(variable.variable);
            variable['svgHeight'] = variable.codes.length * 27;
        });
    }
    
        
    if ($scope.query.e) {
        $scope.variables = $scope.variables.concat($scope.results.environmental_variables);
        $scope.results.environmental_variables.forEach(function(variable) {
         if (variable.name == "Monthly Mean Precipitation") variable.fill = "url(societies#blue)";
            else if (variable.name == "Net Primary Production" || variable.name == "Mean Growing Season NPP") variable.fill = "url(societies#earthy)";
            else variable.fill = "url(societies#temp)";
        });
    }
    
    $scope.setActive('societies');
    
    $scope.columnSort = { sortColumn: 'society.name', reverse: false };
        
    $scope.disableCSVButton = function () {
        $scope.csvDownloadButton.disabled = true;
        $scope.csvDownloadButton.text = 'Downloading...';
    };

    $scope.enableCSVButton = function () {
        $scope.csvDownloadButton.disabled = false;
        $scope.csvDownloadButton.text = 'CSV';
    };
    
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
        num_lines = 0;
        var gradients_svg = d3.select("#gradients-div").node().innerHTML;
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
        var legend = d3.select(".legend-for-download").append("svg:svg");
        var legend_svg = "";
        
        //cultural and environmental variables
        if ($scope.results.chosenVariable) {
            if ($scope.results.environmental_variables.length > 0 && $scope.results.environmental_variables.indexOf($scope.results.chosenVariable) != -1) {
                //if the chosen map is an environmental variable
                    legend_svg = "<g transform='translate(0,350)'>"+d3.select(".env-legend-td").node().innerHTML+"</g>";
            }
            else if ($scope.results.variable_descriptions.length > 0) {
                //cultural variables
                variable = $scope.results.variable_descriptions.filter(function(var_desc) { return var_desc.variable.id ? var_desc.variable.id == $scope.results.chosenVariable.id : var_desc.variable == $scope.results.chosenVariable.id; });
                if (variable.length > 0) {
                    if (variable[0].variable.data_type.toUpperCase() == 'CONTINUOUS') {
                        legend_svg = "<g transform='translate(20,350)'>"+d3.select(".cont-gradient-td").node().innerHTML+"</g>";
                    } else {
                
                    for (var c = 0; c < variable[0].codes.length; c++) {
                        g = legend.append("svg:g")
                            .attr("transform", function() {
                                    return 'translate(20,'+((num_lines)*25)+')';
                            });
                             g.append("svg:circle")
                            .attr("cx", "10")
                            .attr("cy", "10")
                            .attr("r", "4.5")
                            .attr("stroke", "#000")
                            .attr("stroke-width", "0.5")
                            .attr("fill", function() {
                                if (variable[0].codes[c].description.indexOf("Missing data") != -1)
                                    return 'rgb(255,255,255)';
                                var value = variable[0].codes[c].code;
                                if (variable[0].variable.data_type.toUpperCase() == 'ORDINAL') {
                                    rgb = colorMapService.generateRandomHue(value, variable[0].codes.length, variable[0].variable.id, 5);
                                    return rgb;
                                }
                                
                                rgb = colorMapService.colorMap[parseInt(value)];
                                return rgb;
                            });
                        g.append("svg:text")
                            .attr("x", "20")
                            .attr("y", "15")
                            .attr("style", "font-size: 14px;")
                            .call($scope.wrapText, variable[0].codes[c].description);
                        num_lines += 1;
                        }
                        legend_svg = "<g transform='translate(20,350)'>"+legend.node().innerHTML+"</g>";

                    }

                }

            }
            var map_svg = map_svg.substring(0, map_svg.indexOf("</svg>"));
            // concat legend and remove all relative d-place links from svg's defs urls
            map_svg = map_svg.concat(legend_svg.replace(/url\(.*?#/, 'url(#'));
            map_svg = map_svg.concat(gradients_svg +"</svg>");
            var filename = $scope.results.chosenVariable.name.replace(/[\W]+/g, "-").toLowerCase()+"-map.svg";
        }
        
        else if ($scope.results.classifications) {
            count = 0;
            
            for (var i = 0; i < $scope.results.classifications.length; i++) {
                g = legend.append("svg:g")
                    .attr("transform", function() {
                        return 'translate(0,' + count*25 + ')';
                    });
                g.append("svg:circle")
                    .attr("cx", "10")
                    .attr("cy", "10")
                    .attr("r", "4.5")
                    .attr("stroke", "#000")
                    .attr("stroke-width", "0.5")
                    .attr("fill", function() {
                        var value = $scope.results.classifications[i].id;
                        rgb = colorMapService.mapColor(value, $scope.results.classifications.length);
                        return rgb;
                    });
                g.append("svg:text")
                    .attr("x", "20")
                    .attr("y", "15")
                    .text($scope.results.classifications[i].name);
                count++;
                
            }
            var legend_svg = "<g transform='translate(0,350)'>"+legend.node().innerHTML+"</g>";
            var map_svg = map_svg.substring(0, map_svg.indexOf("</svg>"));
            map_svg = map_svg.concat(legend_svg+"</svg>");
            var filename = "language-classifications-map.svg";

        }
        
        else if ($scope.results.geographic_regions.length > 0) {
            count = 0;
            for (var i = 0; i < $scope.results.geographic_regions.length; i++) {
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
                        var value = $scope.results.geographic_regions[i].tdwg_code;
                        rgb = colorMapService.mapColor(value, $scope.results.geographic_regions.length);
                        return rgb;
                    });
                g.append("svg:text")
                    .attr("x", "20")
                    .attr("y", "15")
                    .text($scope.results.geographic_regions[i].region_nam);
                count++;
            }
            var legend_svg = "<g transform='translate(0,350)'>"+legend.node().innerHTML+"</g>";
            var map_svg = map_svg.substring(0, map_svg.indexOf("</svg>"));
            map_svg = map_svg.concat(legend_svg+"</svg>");
            var filename = "geographic-regions-map.svg";
        }
        
        map_file = new Blob([map_svg], {type: 'image/svg+xml'});
        saveAs(map_file, filename);
    }
    
    $scope.buttonChanged = function(buttonVal) {
        d3.select('language-phylogeny').html('');
        $scope.globalTree = false;
        $scope.results.selectedTree = null;
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
        if ($scope.results.selectedTree.name.indexOf("global") == -1) {
            $scope.globalTree = false;
        } else {
            $scope.globalTree = true;
        }
        
        //for environmental legend
        if ($scope.results.environmental_variables.length > 0) {
            if ($scope.results.environmental_variables[0].name == 'Net Primary Production' || $scope.results.environmental_variables[0].name == 'Mean Growing Season NPP') 
                d3.selectAll(".envVar").attr("fill", "url(societies#earthy)");
            else if ($scope.results.environmental_variables[0].name == "Annual Mean Precipitation")
                d3.selectAll(".envVar").attr("fill", "url(societies#blue)");
            else 
                d3.selectAll(".envVar").attr("fill", "url(societies#temp)");
        }
        
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
            
        //need to do this to remove the time scale
        tree_svg = tree_svg.substring(0, tree_svg.indexOf("</svg>"));
        tree_svg = tree_svg.concat("</svg>");
        var all_legends = {};
        legends_list = [];
        var gradients_svg = d3.select("#gradients-div").node().innerHTML;
        
        d3.selectAll(".legends").each( function(){
            leg = d3.select(this);
            if (leg.attr("var-id")) {
               if (leg.attr("class").indexOf("hide") == -1)
                all_legends[leg.attr("var-id")] = leg;
            }
        });
            
        for (var i = 0; i < $scope.results.variable_descriptions.length; i++) {
            id = $scope.results.variable_descriptions[i].variable.id;
            legend_id = all_legends[id];
            name = $scope.results.variable_descriptions[i].CID + '-'+ $scope.results.variable_descriptions[i].variable.name;
            svg_string = legend_id.node().innerHTML;
            svg_string = '<svg version="1.1" xmlns="http://www.w3.org/2000/svg" transform="translate(10, 10)">' + svg_string + gradients_svg + '</svg>';
            legends_list.push({'name': name.replace(/[\W]+/g, "-")+'-legend.svg', 'svg': svg_string});    
        }
        
        for (var i = 0; i < $scope.results.environmental_variables.length; i++) {
            env_svg = d3.select("#e"+$scope.results.environmental_variables[i].id).select("div").node().innerHTML;
            env_svg = '<svg version="1.1" xmlns="http://www.w3.org/2000/svg" transform="translate(10, 10)">'+env_svg.substring(0, env_svg.indexOf("</svg>")) + '</svg>' + gradients_svg + '</svg>';
            name = $scope.results.environmental_variables[i].CID + '-'+$scope.results.environmental_variables[i].name;
            legends_list.push({'name': name.replace(/[\W]+/g, "-")+'-legend.svg', 'svg': env_svg});
        }

        query = {"legends": legends_list, "tree": tree_svg, "name": $scope.results.selectedTree.name+'.svg'};
        var date = new Date();
        var filename = "dplace-tree-"+date.getFullYear()+"-"+(date.getMonth()+1)+"-"+date.getDate()+".zip"
        $http.post('/api/v1/zip_legends', query, {'responseType': 'arraybuffer'}).then(function(data) {
            file = new Blob([data.data], {type: 'application/zip'});
            saveAs(file, filename);
        });
    };
    
    //NEW CSV DOWNLOAD CODE
    //Sends a POST (rather than GET) request to the server, then constructs a Blob and uses FileSaver.js to trigger the save as dialog
    //Better because we can send more data to the server using POST request than GET request
    var file;
    $scope.download = function() {
        var date = new Date();
        var filename = "dplace-societies-"+date.toJSON().replace(/T.*$/,'')+".csv"
        if (!file) {
           $scope.disableCSVButton();
            var queryObject = searchModelService.getModel().getQuery(); 
            $http.post('/api/v1/csv_download', queryObject).then(function(data) {
                file = new Blob([data.data], {type: 'text/csv'});
                saveAs(file, filename);
                $scope.enableCSVButton();

            });
        } else {
            saveAs(file, filename);
        }
    };
}
