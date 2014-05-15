function GeographicCtrl($scope, GeographicRegion, $http, limitToFilter) {
    /*
        This uses $http instead of $resource because $http
        returns a promise and not an initially empty array.
     */
    $scope.getRegions = function(regionName) {
        return $http.get("/api/v1/geographic_regions?region_nam="+regionName).then(function(response){
            return limitToFilter(response.data.results, 15);
        });
    };
}
