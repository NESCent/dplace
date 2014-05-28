function GeographicCtrl($scope, GeographicRegion, $http, limitToFilter, FindSocieties) {
    $scope.model.searchParams.geographic_region = undefined;
    $scope.model.searchParams.regionIds = [];
    /*
        This uses $http instead of $resource because $http
        returns a promise and not an initially empty array.
     */
    $scope.getRegions = function(regionName) {
        return $http.get("/api/v1/geographic_regions?region_nam="+regionName).then(function(response){
            return limitToFilter(response.data.results, 15);
        });
    };

    $scope.getSelectedGeographicRegions = function() {
        var regions = [];
        regions.push($scope.model.searchParams.geographic_region.id);
        return regions;
    }

    $scope.updateMap = function() {
        if($scope.model.searchParams.geographic_region) {
            var tdwgCodeString = String($scope.model.searchParams.geographic_region.tdwg_code);
            if($scope.model.searchParams.regionIds.indexOf(tdwgCodeString) == -1) {
                $scope.model.searchParams.regionIds.push(tdwgCodeString);
            }
        }
    };

    $scope.doSearch = function() {
        var geographicRegions = $scope.getSelectedGeographicRegions();
        $scope.disableSearchButton();
        $scope.model.searchResults = FindSocieties.find({ geographic_regions: geographicRegions }, function() {
            $scope.enableSearchButton();
            $scope.switchToResults();
        });
    };
}
