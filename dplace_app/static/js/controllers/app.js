function AppCtrl($scope, $location, searchModelService) {
    $scope.searchButton = {'disabled': false, 'text': 'Search'};
    $scope.model = searchModelService.getModel();
    // Root controller for app
    $scope.setActive = function(tabName) {
        $scope.searchActive = '';
        $scope.societiesActive = '';
        $scope.homeActive = '';
        $scope.aboutActive = '';
        $scope.sourceInfoActive = '';
        $scope[tabName + 'Active'] = 'active'
        if (tabName === 'home') {
            $('#homeLogo').css('visibility', 'hidden');
        } else {
            $('#homeLogo').css('visibility', 'visible');
        }
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