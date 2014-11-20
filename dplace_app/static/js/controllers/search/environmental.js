function EnvironmentalCtrl($scope, searchModelService, EnvironmentalValue) {
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
        $scope.environmentalData.vals[0] = '';
        $scope.environmentalData.vals[1] = '';
        
        if ($scope.environmentalData.selectedFilter.operator == 'all') {
            values = EnvironmentalValue.query({variable: $scope.environmentalData.selectedVariable.id});
            min_value = 0, max_value = 0;
            values.$promise.then(function(result) {
                for (var i = 0; i < result.length; i++) {
                    if (result[i].value < min_value) min_value = result[i].value;
                    else if (result[i].value > max_value) max_value = result[i].value;
                }
            $scope.environmentalData.vals[0] = min_value;
            $scope.environmentalData.vals[1] = max_value;
            });
        }
    };
    
    $scope.filterChanged = function() {
        if ($scope.environmentalData.selectedFilter.operator != 'all') {
            return;
        } else {
            // Place the min/max values into the text fields as placeholders.
            EnvironmentalValue.query({variable: $scope.environmentalData.selectedVariable.id}, function(results) {
                var extractedValues = results.map(function(o) { return o.value; });
                $scope.environmentalData.vals[0] = Math.min.apply(null, extractedValues);
                $scope.environmentalData.vals[1] = Math.max.apply(null, extractedValues);
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