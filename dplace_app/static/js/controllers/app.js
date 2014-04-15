function AppCtrl($scope) {
    $scope.model = {'searchResults': {}};
    $scope.searchButton = {'disabled': false, 'text': 'Search'};
    // Root controller for app
    $scope.setActive = function(tabName) {
        $scope.homeActive = '';
        $scope.searchActive = '';
        $scope.societiesActive = '';
        $scope[tabName + 'Active'] = 'active'
    }
}