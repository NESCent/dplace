function SocietiesCtrl($scope, searchModelService, LanguageClass) {
    $scope.results = searchModelService.getModel().getResults();
    $scope.query = searchModelService.getModel().getQuery();
    $scope.variables = [];
    console.log($scope.results);
    if ($scope.results.variable_descriptions) {
        $scope.variables = $scope.variables.concat($scope.results.variable_descriptions);
    }
        
    if ($scope.query.environmental_filters) {
        $scope.variables = $scope.variables.concat($scope.results.environmental_variables);
        $scope.results.code_ids[$scope.results.environmental_variables[0].id] = [];
        var extractedValues = $scope.results.societies.map(function(society) { return society.environmental_values[0].value; } );
        var min_value = Math.min.apply(null, extractedValues);
        var max_value = Math.max.apply(null, extractedValues);
        $scope.range = max_value - min_value;
    }

    /*if ($scope.query.language_classifications && !$scope.query.variable_codes && !$scope.query.environmental_filters) {
        //get lang classifications in tree
        $scope.results.classifications = [];
        $scope.languageClasses = [];
        LanguageClass.query().$promise.then(function(result) {
            for (var i = 0; i < $scope.results.societies.length; i++) {
                for (var j = 0; j < $scope.results.societies[i].languages.length; j++) {
                    classification = $scope.query.language_classifications.filter(function(l) { return l.language.id == $scope.results.societies[i].languages[j].id; });
                    if (classification.length > 0) {
                        toAdd = result.filter(function(l) { return l.id == classification[0].class_subfamily; });
                        if (toAdd[0] && $scope.results.classifications.indexOf(toAdd[0]) == -1)
                            $scope.results.classifications = $scope.results.classifications.concat(toAdd); 
                    }
                }
            }
        });
        $scope.results.chosenVariable = -1;
    }*/

    $scope.setActive('societies');

    $scope.resizeMap = function() {
        $scope.$broadcast('mapTabActivated');
    };
    
    $scope.treeSelected = function() {
        $scope.$broadcast('treeSelected', {tree: $scope.results.selectedTree});
        $scope.treeDownload();
    };
    
    $scope.treeDownload = function() {
        var legend = d3.select(".tree-legend-DL")
            .append("svg:g")
            .attr("transform", function() {
                return 'translate(0,0)';
            });
        var prev_codes = 0;
        var final_transform = 0;
        for (var key in $scope.results.code_ids) {
            container_g = legend.append("svg:g")
                .attr("transform", function () {
                    translate = (prev_codes * 25) + 25;
                    return 'translate(0,'+translate+')';
                });
            container_g.append("svg:text")
                .text($scope.results.code_ids[key].name)
        
            for (var i = 0; i < $scope.results.code_ids[key].length; i++) {
            g = container_g.append("svg:g")
                .attr("transform", function() {
                    if (i == 0) 
                        return 'translate(0,10)';
                    else {
                        j = (i*25)+10;
                        final_transform = j;
                        return 'translate(0,'+j+')';
                    }
                });
            var fill = function() {
                var value = $scope.results.code_ids[key][i].code;
                    var hue = value * 240 / $scope.results.code_ids[key].length;
                    return 'hsl('+hue+',100%,50%)';
            }              
            g.append("svg:circle")
                .attr("cx", "10")
                .attr("cy", "10")
                .attr("r", "4.5")
                .attr("stroke", "#000")
                .attr("stroke-width", "0.5")
                .attr("fill", function() {
                    var value = $scope.results.code_ids[key][i].code;
                    var hue = value * 240 / $scope.results.code_ids[key].length;
                    return 'hsl('+hue+',100%,50%)';
                });
            g.append("svg:text")
                .attr("x", "20")
                .attr("y", "15")
                .text($scope.results.code_ids[key][i].description);
            }        
            prev_codes = $scope.results.code_ids[key].length;
        }
        d3_height = d3.select(".phylogeny").style("height");
        d3_height = parseInt(d3_height);
        
        d3.select(".tree-download").html('');
        var tree_svg = d3.select(".phylogeny")
            .attr("version", 1.1)
            .attr("xmlns", "http://www.w3.org/2000/svg")
            .node().parentNode.innerHTML;
        tree_svg = tree_svg.substring(tree_svg.indexOf("<svg xml"));
        
        //this changes the height of the svg for the download, so it includes the legend
        var code_count = 0;
        for (var key in $scope.results.code_ids) {
            code_count = code_count + $scope.results.code_ids[key].length;
        }
        append_height = tree_svg.substring(0, tree_svg.indexOf("height="));
        digits = d3_height.toString().length;
        d3_height += (code_count * 50);
        append_height = append_height.concat("height="+'"'+d3_height+'"');
        to_append = tree_svg.substring(tree_svg.indexOf("height=")+9+digits);
        append_height = append_height.concat(to_append);
                
        //this changes the position of the phylogeny to make room for the legend
        change_transform = append_height.substring(0, append_height.indexOf("transform="));
        change_transform = change_transform.concat('transform="translate' + '(0,' + (final_transform+50));
        transform_length = append_height.substring(append_height.indexOf("transform="), append_height.indexOf(")"));
        to_append = append_height.substring(append_height.indexOf("transform=")+transform_length.length);
        change_transform = change_transform.concat(to_append);
        
       //add legend to download
       var tree_legend = d3.select(".tree-legend-DL").node().innerHTML;
       console.log(change_transform);
       add_legend = change_transform.substring(0, change_transform.indexOf(">"));
       add_legend = add_legend.concat(">" + tree_legend);
       add_legend = add_legend.concat(change_transform.substring(change_transform.indexOf(">")+1));

       var imgsrc = 'data:image/svg+xml;base64,' + window.btoa(unescape(encodeURIComponent(add_legend)));
        d3.select(".tree-download").append("a")
            .attr("class", "btn btn-info btn-dplace-download")
            .attr("download", "tree.svg")
            .attr("href", imgsrc)
            .html("Download Phylogeny");
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
}
