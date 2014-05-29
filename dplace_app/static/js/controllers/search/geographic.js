function GeographicCtrl($scope, GeographicRegion, $http, limitToFilter, FindSocieties) {
    $scope.model.searchParams.selectedRegions = [];

    $scope.removeRegion = function(region) {
        $scope.model.searchParams.selectedRegions.splice($scope.model.searchParams.selectedRegions.indexOf(region));
    };

    $scope.getSelectedGeographicRegions = function() {
        return $scope.model.searchParams.selectedRegions.map(function(region) {
            return region.id;
        });
    }

    $scope.doSearch = function() {
        var geographicRegions = $scope.getSelectedGeographicRegions();
        $scope.disableSearchButton();
        $scope.model.searchResults = FindSocieties.find({ geographic_regions: geographicRegions }, function() {
            $scope.enableSearchButton();
            $scope.switchToResults();
        });
    };
}
