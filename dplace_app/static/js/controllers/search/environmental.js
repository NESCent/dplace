function EnvironmentalCtrl($scope, EnvironmentalVariable, FindSocieties) {
    $scope.model.searchParams.environmentalVariables = EnvironmentalVariable.query();
    $scope.model.searchParams.environmentalFilters = [
        { operator: 'inrange', name: 'between' },
        { operator: 'lt', name: 'less than'},
        { operator: 'gt', name: 'greater than'},
        { operator: 'outrange', name: 'outside'},
    ];
    $scope.model.searchParams.environmental = {
        selectedVariable: null,
        vals: [],
        selectedFilter: $scope.model.searchParams.environmentalFilters[0]
    };

    $scope.getSelectedFilters = function() {
        //environmental_vals: [{id: 1, operator: 'gt', params: [0.0]}, {id:3, operator 'inrange', params: [10.0,20.0] }
        var environmental = $scope.model.searchParams.environmental;
        var filters = [{
            id: environmental.selectedVariable.id,
            operator: environmental.selectedFilter.operator,
            params: environmental.vals
        }];
        return filters;
    };

    $scope.doSearch = function() {
        var filters = $scope.getSelectedFilters();
        $scope.disableSearchButton()
        $scope.model.searchResults = FindSocieties.find({ environmental_filters: filters}, $scope.searchCompleted );
    };

}