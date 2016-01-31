function EnvironmentalCtrl($scope, searchModelService, EnvironmentalVariable, EnvironmentalValue, MinAndMax) {
    var linkModel = function() {
        // Get a reference to the environmental search params from the model
        $scope.environmentalData = searchModelService.getModel().getEnvironmentalData();
    };
    $scope.$on('searchModelReset', linkModel); // When model is reset, update our model
    linkModel();
    
    $scope.categoryChanged = function(category) {
        $scope.environmentalData.variables = EnvironmentalVariable.query({category: category.id});    
        $scope.environmentalData.selectedVariable = '';
    };

    $scope.variableChanged = function(variable) {
        if(variable != null) {
            $scope.environmentalData.badgeValue = 1;
        } else {
            $scope.environmentalData.badgeValue = 0;
        }
        $scope.environmentalData.vals[0] = '';
        $scope.environmentalData.vals[1] = '';
        $scope.EnvironmentalForm.$setPristine();
        $scope.values = MinAndMax.query({query: {environmental_id: $scope.environmentalData.selectedVariable.id}});
        $scope.filterChanged();
    };
    
    $scope.filterChanged = function() {
        if ($scope.environmentalData.selectedFilter.operator == 'all' || $scope.environmentalData.selectedFilter.operator == 'inrange') {
            $scope.values.$promise.then(function(result) {
                $scope.environmentalData.vals[0] = result.min;
                $scope.environmentalData.vals[1] = result.max;
            });
        } else if ($scope.environmentalData.selectedFilter.operator == 'lt') {
            $scope.values.$promise.then(function(result) {
                $scope.environmentalData.vals[0] = result.max;            
            });
        }
        else if ($scope.environmentalData.selectedFilter.operator == 'gt') {
            $scope.values.$promise.then(function(result) {
                $scope.environmentalData.vals[0] = result.min;            
            });
        }
    };
    
    //gets the range of environmental values if the user selects 'all values'
    $scope.doSearch = function() {
        $scope.search();
    };
}