function GeographicCtrl($scope, GeographicRegion) {
    $scope.initialize = function() {
        $scope.model.searchParams.selectedRegions = [];
    };
    $scope.initialize();

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
    };

    $scope.getSelectedGeographicRegions = function() {
        var regionsWithoutIds = $scope.model.searchParams.selectedRegions;
        var regionIds = regionsWithoutIds.map(function(region) {
            return $scope.regionIdFromCode(Number(region.code));
        });
        return regionIds;
    };

    $scope.doSearch = function() {
        var geographicRegions = $scope.getSelectedGeographicRegions();
        $scope.updateSearchQuery({ geographic_regions: geographicRegions });
        $scope.searchSocieties();
    };

    $scope.resetSearch = function() {
        $scope.initialize();
        $scope.resetSearchQuery();
    };

}
