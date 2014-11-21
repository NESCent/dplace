function SocietiesCtrl($scope, searchModelService, CodeDescription) {
    $scope.results = searchModelService.getModel().getResults();
    $scope.query = searchModelService.getModel().getQuery();
    if ($scope.query.variable_codes) {
        $scope.code_ids = {};
        for (var i = 0; i < $scope.query.variable_codes.length; i++) {
            if ($scope.query.variable_codes[i].variable in $scope.code_ids) {
                $scope.code_ids[$scope.query.variable_codes[i].variable] = $scope.code_ids[$scope.query.variable_codes[i].variable] + 1;
            } else {
                $scope.code_ids[$scope.query.variable_codes[i].variable] = 1;
            }
        }
    }
    
    if ($scope.query.environmental_filters) {
        var extractedValues = $scope.results.societies.map(function(society) { return society.environmental_values[0].value; } );
        var min_value = Math.min.apply(null, extractedValues);
        var max_value = Math.max.apply(null, extractedValues);
        $scope.range = max_value - min_value;
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
