function SocietiesCtrl($scope, searchModelService, LanguageClass) {
    $scope.results = searchModelService.getModel().getResults();
    console.log($scope.results);
    $scope.query = searchModelService.getModel().getQuery();
        console.log($scope.query);

    if ($scope.query.variable_codes) {
        $scope.code_ids = {};
        for (var i = 0; i < $scope.query.variable_codes.length; i++) {
            if ($scope.query.variable_codes[i].variable in $scope.code_ids) {
                $scope.code_ids[$scope.query.variable_codes[i].variable] = $scope.code_ids[$scope.query.variable_codes[i].variable].concat([$scope.query.variable_codes[i]]);
            } else {
                $scope.code_ids[$scope.query.variable_codes[i].variable] = [$scope.query.variable_codes[i]];
            }
        }
        
        if ($scope.results.variable_descriptions) {
            for (var i = 0; i < $scope.results.variable_descriptions.length; i++){
                if ($scope.code_ids[$scope.results.variable_descriptions[i].id].name) continue;
                else $scope.code_ids[$scope.results.variable_descriptions[i].id].name = $scope.results.variable_descriptions[i].name;
            
            }
        }
    }
        
    if ($scope.query.environmental_filters) {
        var extractedValues = $scope.results.societies.map(function(society) { return society.environmental_values[0].value; } );
        var min_value = Math.min.apply(null, extractedValues);
        var max_value = Math.max.apply(null, extractedValues);
        $scope.range = max_value - min_value;
    }
    
    if ($scope.query.language_classifications) {
        //get lang classifications in tree
        $scope.classifications = [];
        $scope.languageClasses = [];
        LanguageClass.query().$promise.then(function(result) {
            console.log(result);
             for (var i = 0; i < $scope.results.societies.length; i++) {
            for (var j = 0; j < $scope.results.societies[i].languages.length; j++) {
                classification = $scope.query.language_classifications.filter(function(l) { return l.language.id == $scope.results.societies[i].languages[j].id; });
                toAdd = result.filter(function(l) { return l.id == classification[0].class_subfamily; });
                if (toAdd[0] && $scope.classifications.indexOf(toAdd[0]) == -1)
                    $scope.classifications = $scope.classifications.concat(toAdd); 
            }
        }
        });
    }

    $scope.setActive('societies');

    $scope.resizeMap = function() {
        $scope.$broadcast('mapTabActivated');
    };
    
    $scope.treeSelected = function() {
        $scope.$broadcast('treeSelected', {tree: $scope.results.selectedTree});
    };

    $scope.generateDownloadLinks = function() {
        // queryObject is the in-memory JS object representing the chosen search options
        var queryObject = searchModelService.getModel().getQuery();
        // the CSV download endpoint is a GET URL, so we must send the query object as a string.
        var queryString = encodeURIComponent(JSON.stringify(queryObject));
        // format (csv/svg/etc) should be an argument, and change the endpoint to /api/v1/download
        $scope.csvDownloadLink = "/api/v1/csv_download?query=" + queryString;
    };
}
