function EnvironmentalCtrl($scope, searchModelService) {
    var linkModel = function() {
        // Get a reference to the environmental search params from the model
        $scope.environmentalData = searchModelService.getModel().getEnvironmentalData();
    };
    $scope.$on('searchModelReset', linkModel); // When model is reset, update our model
    linkModel();

    var getSelectedFilters = function() {
        //environmental_vals: [{id: 1, operator: 'gt', params: [0.0]}, {id:3, operator 'inrange', params: [10.0,20.0] }
        var environmental = $scope.environmentalData;
        var filters = [{
            id: environmental.selectedVariable.id,
            operator: environmental.selectedFilter.operator,
            params: environmental.vals
        }];
        return filters;
    };

    $scope.variableChanged = function(variable) {
        if(variable != null) {
            $scope.environmentalData.badgeValue = 1;
        } else {
            $scope.environmentalData.badgeValue = 0;
        }
    };
    $scope.doSearch = function() {
		$scope.submitted = true;
        var filters = getSelectedFilters();
        $scope.updateSearchQuery({ environmental_filters: filters });
        $scope.searchSocieties();
    };
}