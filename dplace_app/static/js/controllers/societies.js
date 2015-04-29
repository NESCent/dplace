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
        d3.select(".tree-legend-DL").html('');
        $scope.treeDownload();
    };
    
    $scope.treeDownload = function() {
        var tree_svg = d3.select(".phylogeny")
            .attr("version", 1.1)
            .attr("xmlns", "http://www.w3.org/2000/svg")
            .node().parentNode.innerHTML;
         tree_svg = tree_svg.substring(tree_svg.indexOf("<svg xml"));
         tree_svg = tree_svg.substring(0, tree_svg.indexOf("</svg>"));
        var imgsrc = 'data:image/svg:xml;base64,' + window.btoa(unescape(encodeURIComponent(tree_svg)));
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
