function AppCtrl($scope, $location, $http, searchModelService) {
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
        var queryObject = $scope.model.getQuery();
        for (var key in queryObject) {
            if (key == 'c') {
                queryString = "["
                for (var v = 0; v < queryObject[key].length; v++) {
                    if (queryObject[key][v].id)
                        queryString += queryObject[key][v].variable + '-' + queryObject[key][v].id;
                    else {
                        queryString += queryObject[key][v].variable + '-' + queryObject[key][v].min + '-' + queryObject[key][v].max;
                    }
                    if (v < queryObject[key].length-1)
                        queryString += ',';
                }
                queryString += "]"
                $location.search(key, queryString);
            } else {
                $location.search(key, JSON.stringify(queryObject[key]));
            }
        }
    };
    
    $scope.switchToSocResults = function(name) {
        $location.path('/societies/search/'+name);
    };

    $scope.getSocietyIds = function() {
        return $scope.model.getSocieties().map(function (container) {
            return container.society.id;
        });
    };
}