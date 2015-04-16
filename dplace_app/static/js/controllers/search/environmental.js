function EnvironmentalCtrl($scope, searchModelService, EnvironmentalVariable, EnvironmentalValue, MinAndMax) {
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
    
    $scope.categoryChanged = function(category) {
        $scope.environmentalData.variables = EnvironmentalVariable.query({category: category.id});    
    };

    $scope.variableChanged = function(variable) {
        if(variable != null) {
            $scope.environmentalData.badgeValue = 1;
        } else {
            $scope.environmentalData.badgeValue = 0;
        }
        $scope.environmentalData.vals[0] = '';
        $scope.environmentalData.vals[1] = '';
        
        if ($scope.environmentalData.selectedFilter.operator == 'all') {
            values = MinAndMax.query({query: {environmental_id: $scope.environmentalData.selectedVariable.id}});
            values.$promise.then(function(result) {
                $scope.environmentalData.vals[0] = result.min;
                $scope.environmentalData.vals[1] = result.max;
            });
        }
    };
    
    $scope.filterChanged = function() {
        if ($scope.environmentalData.selectedFilter.operator != 'all') return;
        else {
            values = MinAndMax.query({query: {environmental_id: $scope.environmentalData.selectedVariable.id}});
            values.$promise.then(function(result) {
                $scope.environmentalData.vals[0] = result.min;
                $scope.environmentalData.vals[1] = result.max;
            });
        }
    };
    
    //gets the range of environmental values if the user selects 'all values'
    $scope.doSearch = function() {
        var filters = getSelectedFilters();
        $scope.updateSearchQuery({ environmental_filters: filters });
        $scope.searchSocieties();

    };
}