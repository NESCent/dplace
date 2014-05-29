function GeographicCtrl($scope, GeographicRegion, $http, limitToFilter, FindSocieties) {
    $scope.model.searchParams.selectedRegions = [];
    $scope.model.geographic_regions = GeographicRegion.query();
    $scope.removeRegion = function(region) {
        var index = $scope.model.searchParams.selectedRegions.indexOf(region)
        $scope.model.searchParams.selectedRegions.splice(index, 1);
    };

    $scope.regionIdFromCode = function(code) {
        var regionId;
        $scope.model.geographic_regions.forEach(function (region) {
            if(region.tdwg_code == code) {
                regionId = region.id;
            }
        });
        return regionId;
    }

    $scope.getSelectedGeographicRegions = function() {
        var regionsWithoutIds = $scope.model.searchParams.selectedRegions;
        var regionIds = regionsWithoutIds.map(function(region) {
            return $scope.regionIdFromCode(Number(region.code));
        });
        return regionIds;
    }

    $scope.doSearch = function() {
        $scope.disableSearchButton();
        var geographicRegions = $scope.getSelectedGeographicRegions();
        $scope.model.searchResults = FindSocieties.find({ geographic_regions: geographicRegions }, function() {
            $scope.enableSearchButton();
            $scope.switchToResults();
        });
    };
}
