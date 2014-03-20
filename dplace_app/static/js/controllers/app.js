function AppCtrl($scope) {
    $scope.results = {'societies': []};
    // Root controller for app
    $scope.setActive = function(tabName) {
        $scope.homeActive = '';
        $scope.searchActive = '';
        $scope.societiesActive = '';
        $scope[tabName + 'Active'] = 'active'
    }
}