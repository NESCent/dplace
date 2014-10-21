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
        //reset 'all values' to false if the variable is changed
        if ($scope.allValues.isSelected) {
            $scope.environmentalData.vals[0] = '';
            $scope.environmentalData.vals[1] = '';
            $scope.allValues.isSelected = false;
        }
    };
    
    //gets the range of environmental values if the user selects 'all values'
    $scope.allValues = function(variable) {
        if ($scope.allValues.isSelected) {
            //need to find a better way to deal with this page_size
            values = EnvironmentalValue.query({variable: variable.id, page_size:'3000'}); //get all environmental values for the selected variable
            operator = $scope.environmentalData.selectedFilter.operator;
            min_value = 0, max_value = 0;
            values.$promise.then(function (result) {
                for (var i = 0; i < result.length; i++) {
                    if (result[i].value < min_value) min_value = result[i].value;
                    else if (result[i].value > max_value) max_value = result[i].value;
                }
                if (operator == 'inrange' || operator == 'outrange') {
                    $scope.environmentalData.vals[0] = min_value;
                    $scope.environmentalData.vals[1] = max_value;
                } else if (operator == 'gt') {
                    $scope.environmentalData.vals[0] = min_value;
                } else if (operator == 'lt') {
                    $scope.environmentalData.vals[0] = max_value;
                }
            });
        }
    };
    
    $scope.doSearch = function() {
        var filters = getSelectedFilters();
        $scope.updateSearchQuery({ environmental_filters: filters });
        $scope.searchSocieties();
    };
}