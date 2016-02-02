function EnvironmentalCtrl($scope, searchModelService, EnvironmentalVariable, EnvironmentalValue, MinAndMax) {
    var linkModel = function() {
        // Get a reference to the environmental search params from the model
        $scope.environmentalData = searchModelService.getModel().getEnvironmentalData();
        $scope.environmentalData.selectedVariables = [{'vals': ['', ''], 'selectedFilter': $scope.environmentalData.selectedFilter}];
    };
    $scope.$on('searchModelReset', linkModel); // When model is reset, update our model
    linkModel();
    
    $scope.categoryChanged = function(category) {
        $scope.environmentalData.variables = EnvironmentalVariable.query({category: category.id});    
    };
    
    $scope.addVariable = function() {
        $scope.environmentalData.selectedVariables.push({'vals': ['', ''], 'selectedFilter': $scope.environmentalData.selectedFilter});
    };

    $scope.variableChanged = function(variable) {
        if(variable.selectedVariable != null) {
            $scope.environmentalData.badgeValue += 1;
        } else {
            if ($scope.environmentalData.badgeValue != 0) 
            $scope.environmentalData.badgeValue -= 1;
        }

        variable.EnvironmentalForm.$setPristine();
        $scope.values = MinAndMax.query({query: {environmental_id: variable.selectedVariable.id}});
        $scope.filterChanged(variable);
    };
    
    $scope.filterChanged = function(variable) {
        if (variable.EnvironmentalForm.$dirty && variable.selectedFilter.operator != 'all') return;
        selected_variable = $scope.environmentalData.selectedVariables.filter(function(env_var) {
            return env_var.selectedVariable.id == variable.selectedVariable.id;
        });
        if (selected_variable.length == 1) {
            MinAndMax.query({query: {environmental_id: variable.selectedVariable.id}}).$promise.then(function(result) {
                selected_variable[0].vals[0] = result.min;
                selected_variable[0].vals[1] = result.max;
            });
        }
        
    };
    
    //gets the range of environmental values if the user selects 'all values'
    $scope.doSearch = function() {
        console.log($scope.environmentalData);
        $scope.search();
    };
}