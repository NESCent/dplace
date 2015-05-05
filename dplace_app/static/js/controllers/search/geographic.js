function GeographicCtrl($scope, searchModelService) {
    var linkModel = function() {
        // Get a reference to the geographic regions from the model
        $scope.geographic = searchModelService.getModel().getGeographicRegions();
        $scope.$watchCollection('geographic.selectedRegions', function() {
            $scope.geographic.badgeValue = $scope.geographic.selectedRegions.length;
        });
    };
    $scope.$on('searchModelReset', linkModel); // When model is reset, update our model
    linkModel();

    $scope.removeRegion = function(region) {
        var index = $scope.geographic.selectedRegions.indexOf(region);
        $scope.geographic.selectedRegions.splice(index, 1);
    };

    // Gets the region ID from a geographic region code
    // The map uses region codes as the identifier for each region, they come from a shapefile
    // The search API uses the database id (pk) for the region, it is not present in the Map
    var regionIdFromCode = function(code) {
        var regionId = null;
        $scope.geographic.allRegions.forEach(function (region) {
            if(region.tdwg_code == code) {
                regionId = region.id;
            }
        });
        return regionId;
    };

    // annotates Database IDs onto selected regions
    var tagSelectedRegionsWithIDs = function() {
        $scope.geographic.selectedRegions.forEach(function(selectedRegion) {
            selectedRegion.id = regionIdFromCode(selectedRegion.code)
        });
    };

    $scope.doSearch = function() {
        tagSelectedRegionsWithIDs();
        var geographicRegions = $scope.geographic.selectedRegions;
        $scope.updateSearchQuery({ geographic_regions: geographicRegions });
        $scope.searchSocieties();
    };
}
