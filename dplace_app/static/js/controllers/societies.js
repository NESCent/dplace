function SocietiesCtrl($scope, searchModelService, CodeDescription) {
    $scope.results = searchModelService.getModel().getResults();
    if ($scope.results.variable_descriptions && $scope.results.variable_descriptions.length > 0) {
        $scope.code_ids = {};
        for (var i = 0; i < $scope.results.variable_descriptions.length; i++) {
            results = CodeDescription.query({variable: $scope.results.variable_descriptions[i].id});
            $scope.code_ids[$scope.results.variable_descriptions[i].id] = results;
        }
    }
    
    if ($scope.results.environmental_variables && $scope.results.environmental_variables.length > 0) {
        var min_value = 0, max_value = 0;
        
        for (var i = 0; i < $scope.results.societies.length; i++) {
            if ($scope.results.societies[i].environmental_values[0].value < min_value) min_value = $scope.results.societies[i].environmental_values[0].value;
            else if ($scope.results.societies[i].environmental_values[0].value > max_value) max_value = $scope.results.societies[i].environmental_values[0].value;
        }
        $scope.range = max_value - min_value;
    
    }

    $scope.query = searchModelService.getModel().getQuery();
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
