function AppCtrl($scope, $location, searchModelService) {
    $scope.searchButton = {'disabled': false, 'text': 'Search'};
    $scope.model = searchModelService.getModel();
    // Root controller for app
    $scope.setActive = function(tabName) {
        $scope.searchActive = '';
        $scope.societiesActive = '';
        $scope.aboutActive = '';
        $scope[tabName + 'Active'] = 'active'
    };

    $scope.switchToResults = function() {
        $location.path('/societies');
    };

    $scope.getSocietyIds = function() {
        return $scope.model.getSocieties().map(function (container) {
            return container.society.id;
        });
    };
}