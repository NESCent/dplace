function EnvironmentalCtrl($scope, EnvironmentalVariable, FindSocieties) {
    $scope.environmentalVariables = EnvironmentalVariable.query();
    $scope.environmentalFilters = [
        { operator: 'inrange', name: 'between' },
        { operator: 'lt', name: 'less than'},
        { operator: 'gt', name: 'greater than'},
        { operator: 'outrange', name: 'outside'},
    ];
    $scope.environmental = {
        selectedVariable: null,
        vals: [],
        selectedFilter: $scope.environmentalFilters[0]
    };

    $scope.getSelectedFilters = function() {
        //environmental_vals: [{id: 1, operator: 'gt', params: [0.0]}, {id:3, operator 'inrange', params: [10.0,20.0] }
        var environmental = $scope.environmental;
        var filters = [{
            id: environmental.selectedVariable.id,
            operator: environmental.selectedFilter.operator,
            params: environmental.vals
        }];
        return filters;
    };

    $scope.doSearch = function() {
        var filters = $scope.getSelectedFilters();
        $scope.results.societies = FindSocieties.find({ environmental_filters: filters});
        // TODO: Activate the societies link
    };

}