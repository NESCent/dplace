function SocietiesCtrl($scope, searchModelService, CodeDescription) {
    $scope.results = searchModelService.getModel().getResults();
    if ($scope.results.variable_descriptions && $scope.results.variable_descriptions.length > 0) {
        $scope.code_ids = {};
        for (var i = 0; i < $scope.results.variable_descriptions.length; i++) {
            results = CodeDescription.query({variable: $scope.results.variable_descriptions[i].id});
            $scope.code_ids[$scope.results.variable_descriptions[i].id] = results;

        }
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
