function GeographicCtrl($scope, GeographicRegion) {
    $scope.model.searchParams.regions = GeographicRegion.query();
}
