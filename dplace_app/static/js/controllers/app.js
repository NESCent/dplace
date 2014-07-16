function AppCtrl($scope, $location) {

    $scope.model = {
        'searchResults': {}, // Populated after search is run
        'searchParams': {}, // Collected on clicking search button
        'searchQuery': {} // Parameters sent to the FindSocieties API
    };
    $scope.searchButton = {'disabled': false, 'text': 'Search'};
    // Root controller for app
    $scope.setActive = function(tabName) {
        $scope.searchActive = '';
        $scope.societiesActive = '';
        $scope[tabName + 'Active'] = 'active'
    };
    $scope.switchToResults = function() {
        $location.path('/societies');
    };

    $scope.getResults = function() {
        return $scope.model.searchResults.results;
    };

    $scope.getSocietyIds = function() {
        return $scope.getResults().map(function (result) {
            return result.society.id;
        });
    }
}