function AppCtrl($scope, $location) {
    $scope.model = {'searchResults': {}, 'searchParams': {}};
    $scope.searchButton = {'disabled': false, 'text': 'Search'};
    // Root controller for app
    $scope.setActive = function(tabName) {
        $scope.searchActive = '';
        $scope.societiesActive = '';
        $scope[tabName + 'Active'] = 'active'
    }
    $scope.switchToResults = function() {
        $location.path('/societies');
    }
}