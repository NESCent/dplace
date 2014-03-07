function AppCtrl($scope) {
    // Root controller for app
    $scope.setActive = function(tabName) {
        $scope.homeActive = '';
        $scope.searchActive = '';
        $scope[tabName + 'Active'] = 'active'
    }
}