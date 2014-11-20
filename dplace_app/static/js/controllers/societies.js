function SocietiesCtrl($scope, searchModelService, CodeDescription) {
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
            console.log($scope.legend);
        }
    };
    
    if ($scope.variables[0]) $scope.changeLegend($scope.variables[0]); //initial value of chosen variable is first variable in array
    
    $scope.generateDownloadLinks = function() {
        // queryObject is the in-memory JS object representing the chosen search options
        var queryObject = searchModelService.getModel().getQuery();
        // the CSV download endpoint is a GET URL, so we must send the query object as a string.
        var queryString = encodeURIComponent(JSON.stringify(queryObject));
        // format (csv/svg/etc) should be an argument, and change the endpoint to /api/v1/download
        $scope.csvDownloadLink = "/api/v1/csv_download?query=" + queryString;
    };
}
