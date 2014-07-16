function EnvironmentalCtrl($scope, EnvironmentalVariable) {
    $scope.model.searchParams.environmentalVariables = EnvironmentalVariable.query();
    $scope.model.searchParams.environmentalFilters = [
        { operator: 'inrange', name: 'between' },
        { operator: 'lt', name: 'less than'},
        { operator: 'gt', name: 'greater than'},
        { operator: 'outrange', name: 'outside'},
    ];
    $scope.initialize = function() {
        $scope.model.searchParams.environmental = {
            selectedVariable: null,
            vals: [],
            selectedFilter: $scope.model.searchParams.environmentalFilters[0]
        };
    };
    $scope.initialize();

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
        $scope.updateSearchQuery({ environmental_filters: filters });
        $scope.searchSocieties();
    };

    $scope.resetSearch = function() {
        $scope.initialize();
        $scope.resetSearchQuery();
    };

}