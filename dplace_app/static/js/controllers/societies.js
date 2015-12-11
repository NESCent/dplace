function SocietiesCtrl($scope, searchModelService, LanguageClass, ZipTest) {
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
        //$scope.results.code_ids[$scope.results.environmental_variables[0].id] = [];
    }
    
    for (var key in $scope.results.code_ids) {
        $scope.results.code_ids[key]['svgSize'] = $scope.results.code_ids[key].length * 27;
    }
    $scope.setActive('societies');

    $scope.resizeMap = function() {
        $scope.$broadcast('mapTabActivated');
    };
    
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
            if ($scope.results.environmental_variables[0].id == 34 || $scope.results.environmental_variables[0].id == 36) 
                d3.selectAll(".envVar").attr("fill", "url(#earthy)");
            else if ($scope.results.environmental_variables[0].id == 27)
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
        
        if ($scope.results.classifications) {
            item = d3.select('.tree-legend-langs');
            svg_string = '<svg version="1.1" xmlns="http://www.w3.org/2000/svg">' + item.node().innerHTML + '</svg>';
            legends.push({'name': 'Language Classifications', 'svg': svg_string});
        } else {
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
                    legends.push({'name': name+'-legend.svg', 'svg': svg_string});    
            }
        }
        
        query = {"legends": legends, "tree": tree_svg, "name": $scope.results.selectedTree.name+'.svg'};
        d3.select(".tree-download").append("a")
            .attr("class", "btn btn-info btn-dplace-download")
            .attr("download", "legend.svg")
            .attr("href", "/api/v1/zip_legends?query="+encodeURIComponent(JSON.stringify(query)))
            .html("Download this phylogeny");
    };
    
    $scope.changeMap = function(chosenVariable) {
        chosenVariableId = chosenVariable.id;
        d3.select(".legend-for-download").html('');
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
