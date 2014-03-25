function EnvironmentalCtrl($scope, EnvironmentalVariable) {
    $scope.environmentalVariables = EnvironmentalVariable.query();
    $scope.environmentalFilters = [
        { key: 'inrange', name: 'between' },
        { key: 'lt', name: 'less than'},
        { key: 'gt', name: 'greater than'},
        { key: 'outrange', name: 'outside'},
    ];
    $scope.environmental = {
        selectedFilter: $scope.environmentalFilters[0]
    };
}