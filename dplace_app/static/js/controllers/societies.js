function SocietiesCtrl($scope, $location, $timeout, $http, searchModelService, colorMapService, TreesFromSocieties, FindSocieties) {

    $scope.appendQueryString();
    
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            if (    cookie.substring(0, 10) === ('csrftoken=')) {
                cookieValue = decodeURIComponent(cookie.substring(10));
                break;
             }
        }
    }
    $scope.cookieValue = cookieValue;
    
    $scope.results = searchModelService.getModel().getResults();
    $scope.query = searchModelService.getModel().getQuery();
    $scope.searchModel = searchModelService.getModel();
    $scope.csvDownloadButton = {text: 'CSV', disabled: false};
    $scope.globalTree = false;
    $scope.variables = [];
    $scope.buttons = [];
    $scope.setActive('societies');
    $scope.columnSort = { sortColumn: 'society.name', reverse: false };
    
    $scope.tabs = [
        { title: "Table", content: "table", active: true},
        { title: "Map", content: "map", active: false},
        { title: "Tree", content: "tree", active: false},
        { title: "Download", content: "download", active: false},
    ];

    
    var forLegends = function() {
        if ($scope.results.variable_descriptions) {
            $scope.results.variable_descriptions.forEach(function(variable) {
                if (variable.variable.data_type.toUpperCase() == 'CONTINUOUS') {
                    variable.variable.fill = "/"+window.location.href.split('/').pop()+"#grad1";
                }
                $scope.variables.push(variable.variable);
                variable['svgHeight'] = variable.codes.length * 27;
                
            });
        }
            
        if ($scope.query.e) {
            $scope.variables = $scope.variables.concat($scope.results.environmental_variables);
            $scope.results.environmental_variables.forEach(function(variable) {
             if (variable.name == "Annual Mean Precipitation") variable.fill = "/"+window.location.href.split('/').pop()+"#blue";
                else if (variable.name == "Monthly Mean Net Primary Production" || variable.name == "Mean Growing Season NPP") variable.fill = "/"+window.location.href.split('/').pop()+"#earthy";
                else variable.fill = "/"+window.location.href.split('/').pop()+"#temp";
            });
        }
        if ($scope.variables.length > 0) {
            $scope.results.chosenVariable = $scope.variables[0];
        }

    }
    
    
    var searchCompletedCallback = function() {
        $scope.results = searchModelService.getCodeIDs($scope.searchModel.results, $scope.searchModel.query);
        $scope.query = $scope.searchModel.query;
        searchModelService.assignColors($scope.results);
        $scope.searchModel.results.searched = true;
        forLegends();
    };
    
    if (!$scope.searchModel.results.searched && !$scope.searchModel.results.searchedByName) {
        var queryObject = $location.search();
        var by_name = false;
        for (var key in queryObject) {
            if (key == 'name') {
                 by_name = true;
            } else {
                queryObject[key] = JSON.parse(queryObject[key]);

            }
            
        }
        if (!by_name) {
            searchModelService.updateSearchQuery(queryObject);
            $scope.searchModel.results = FindSocieties.find(queryObject, searchCompletedCallback);
        } else {
            $scope.results = FindSocieties.find(queryObject);
            $scope.searchModel.results.searchedByName = true;
        }
        
    } else {
        forLegends();

    }

       
    var treeButtons = function() {
        if ($scope.results.language_trees && $scope.results.language_trees.length > 0) {
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
    }
    
    var sortTrees = function() {
        $scope.results.language_trees.phylogenies = [];
        $scope.results.language_trees.glotto_trees = [];
        $scope.results.language_trees.forEach(function(tree) {
            if (tree.name.indexOf("global") != -1) $scope.results.language_trees.global_tree = tree;
            else if (tree.name.indexOf("glotto") != -1) {
                $scope.results.language_trees.glotto_trees.push(tree);
            }
            else {
                $scope.results.language_trees.phylogenies.push(tree);
            }
        $scope.results.language_trees.glotto_trees.sort(function(a, b) { return a.name > b.name; });
        $scope.results.language_trees.phylogenies.sort(function(a, b) { return a.name > b.name; });
        });
        treeButtons();
    }
    
    $scope.addTrees = function() {
        if ($scope.results.language_trees && $scope.results.language_trees.length > 0) return;
        if ($scope.tabs[2].active) {
            list = $scope.results.societies.map(function(s) { return s.society.id});
            society_ids = {'s': list};
            $scope.results.language_trees = TreesFromSocieties.find(society_ids, sortTrees);
    }
    }

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
        $scope.results.selectedTree = null;
        if (buttonVal.indexOf("global") != -1) {
            $scope.globalTree = true;
            $scope.results.selectedTree = $scope.results.language_trees.global_tree;
            $scope.results.chosenTVariable = $scope.variables[0];
            $scope.treeSelected();
        } else if (buttonVal.indexOf('phylogeny') != -1) {
            $scope.globalTree = false;
            $scope.trees = $scope.results.language_trees.phylogenies;
        } else {
            $scope.globalTree = false;
            $scope.trees = $scope.results.language_trees.glotto_trees;
        }
    };
    
    $scope.treeDownload = function() {
        try {
        var tree_svg = d3.select(".phylogeny")
            .attr("version", 1.1)
            .attr("xmlns", "http://www.w3.org/2000/svg")
            .node().parentNode.innerHTML;
        }
        catch(e){
            return;
        }
        var all_legends = {};
        legends_list = [];
        var gradients_svg = d3.select("#gradients-div").node().innerHTML;
        
        d3.selectAll(".legends").each( function(){
            leg = d3.select(this);
            if (leg.attr("var-id") && leg.attr("class").indexOf("hide") == -1) {
               if ($scope.globalTree) {
                   if ($scope.results.chosenTVariable.var_id) {
                       if (leg.attr("var-id") == $scope.results.chosenTVariable.var_id) 
                        all_legends[leg.attr("var-id")] = leg;
                    
                   } else if (parseInt(leg.attr("var-id")) == $scope.results.chosenTVariable.id) {
                       all_legends[leg.attr("var-id")] = leg;
                   }
               } else 
                    all_legends[leg.attr("var-id")] = leg;
            }
        });
                    
        for (var i = 0; i < $scope.results.variable_descriptions.length; i++) {
            id = $scope.results.variable_descriptions[i].variable.id;
            name = ''
            if (!all_legends[id]) continue;
            legend_id = all_legends[id];
            if ($scope.results.variable_descriptions[i].CID) name += $scope.results.variable_descriptions[i].CID + '-';
            name += $scope.results.variable_descriptions[i].variable.name;
            svg_string = legend_id.node().innerHTML;
            svg_string = svg_string.replace(/url\(.*?#/, 'url(#');
            svg_string = '<svg version="1.1" xmlns="http://www.w3.org/2000/svg" transform="translate(10, 10)">' + svg_string + gradients_svg + '</svg>';
            legends_list.push({'name': name.replace(/[\W]+/g, "-")+'-legend.svg', 'svg': svg_string});    
        }
                
        for (var i = 0; i < $scope.results.environmental_variables.length; i++) {
            id = $scope.results.environmental_variables[i].var_id;
            name = ''
            if (!all_legends[id]) continue;
            legend_id = all_legends[id];
            if ($scope.results.environmental_variables[i].CID) name += $scope.results.environmenal_variables[i].CID;
            name += $scope.results.environmental_variables[i].name;
            svg_string = legend_id.node().innerHTML;
            svg_string = svg_string.replace(/url\(.*?#/, 'url(#');
            svg_string = '<svg version="1.1" xmlns="http://www.w3.org/2000/svg" transform="translate(10, 10)">'+svg_string + gradients_svg + '</svg>';
            legends_list.push({'name': name.replace(/[\W]+/g, "-")+'-legend.svg', 'svg': svg_string});
        }

        $scope.toSendquery = {'l': legends_list, 't': [tree_svg], 'n': [$scope.results.selectedTree.name+'.svg']};
         $scope.toSendquery = JSON.stringify($scope.toSendquery);
        
    };
    
    
    $scope.treeSelected = function() {
        $scope.$broadcast('treeSelected', {tree: $scope.results.selectedTree});
        if ($scope.results.selectedTree.name.indexOf("global") == -1) {
            $scope.globalTree = false;
        } else {
            $scope.globalTree = true;
        }
        
        $scope.treeDownload();
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
    
    $scope.nexusDownload = function() {
        var filename = $scope.results.selectedTree.name+"-d-place.NEXUS";
        string = "#NEXUS\nBEGIN TREES;\nTREE " + $scope.results.selectedTree.name+" = " + $scope.results.selectedTree.newick_string+"\nEND;"
        
        nexus_file = new Blob([string], {type: 'text/nexus'});
        saveAs(nexus_file, filename);
    }
    
    
    $scope.disableCSVButton = function () {
        $scope.csvDownloadButton.disabled = true;
        $scope.csvDownloadButton.text = 'Downloading...';
    };

    $scope.enableCSVButton = function () {
        $scope.csvDownloadButton.disabled = false;
        $scope.csvDownloadButton.text = 'CSV';
    };
    
    var file;
    $scope.download = function() {
        var date = new Date();
        var filename = "dplace-societies-"+date.toJSON().replace(/T.*$/,'')+".csv"
        if (!file) {
            $scope.disableCSVButton();
            // queryObject is the in-memory JS object representing the chosen search options
            var queryObject = searchModelService.getModel().getQuery();
            // the CSV download endpoint is a GET URL, so we must send the query object as a string.
            var queryString = encodeURIComponent(JSON.stringify(queryObject));
            // format (csv/svg/etc) should be an argument, and change the endpoint to /api/v1/download
            var csvDownloadLink = "/api/v1/csv_download?query=" + queryString;
            $http.get(csvDownloadLink).then(function(data) {
               file = new Blob([data.data], {type: 'text/csv'});
                saveAs(file, filename);
                $scope.enableCSVButton(); 
            });
        } else {
            var filename = "dplace-societies-"+date.toJSON().replace(/T.*$/,'')+".csv"
            saveAs(file, filename);
        }    
    };

}
