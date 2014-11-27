function SocietiesCtrl($scope, searchModelService) {
    $scope.results = searchModelService.getModel().getResults();
    $scope.query = searchModelService.getModel().getQuery();
    $scope.setActive('societies');
    $scope.variables = [];
    
    if ($scope.results.variable_descriptions) {
        $scope.variables = $scope.variables.concat($scope.results.variable_descriptions);
    }
        
    if ($scope.results.environmental_variables) {
        $scope.variables = $scope.variables.concat($scope.results.environmental_variables);
    }
    
    $scope.changeLegend = function(chosenVariable) {
        chosenVariableId = chosenVariable.id;
        if ($scope.query.variable_codes) {
            $scope.legend = $scope.query.variable_codes.filter(function(code) { if (code.variable == chosenVariableId) return code; });
        } else if ($scope.query.language_classifications) {
            $scope.classifications = {};
            $scope.legend = [];
            for (var i = 0; i < $scope.results.societies.length; i++) {
                for (var j = 0; j < $scope.results.societies[i].languages.length; j++) {
                    toAdd = $scope.query.language_classifications.filter(function(l) { return l.language.id == $scope.results.societies[i].languages[j].id; });
                    if (toAdd[0] && !(toAdd[0].class_subfamily in $scope.classifications)) {
                        $scope.classifications[toAdd[0].class_subfamily] = toAdd[0].ethnologue_classification.split(',')[1];
                    }
                }
            }
            
            for (var key in $scope.classifications) {
                $scope.legend.push({'code': key, 'description': $scope.classifications[key]});
            }
        }
    };
    
    if ($scope.variables[0]) $scope.changeLegend($scope.variables[0]); //initial value of chosen variable is first variable in array
    else $scope.changeLegend(-1);
    $scope.generateDownloadLinks = function() {
        // queryObject is the in-memory JS object representing the chosen search options
        var queryObject = searchModelService.getModel().getQuery();
        // the CSV download endpoint is a GET URL, so we must send the query object as a string.
        var queryString = encodeURIComponent(JSON.stringify(queryObject));
        // format (csv/svg/etc) should be an argument, and change the endpoint to /api/v1/download
        $scope.csvDownloadLink = "/api/v1/csv_download?query=" + queryString;
    };
}
