function SearchCtrl($scope, colorMapService, FindSocieties) {
    $scope.setActive('search');
    $scope.selectedButton = {};
    $scope.buttons = [
        {value:'geographic', name:'Geographic'},
        {value:'cultural', name:'Cultural Traits'},
        {value:'environmental', name:'Environmental'},
        {value:'language', name:'Language'}
    ];

    $scope.buttonChanged = function(selectedButton) {
        $scope.selectedButton = selectedButton;
    };

    $scope.disableSearchButton = function () {
        $scope.searchButton.disabled = true;
        $scope.searchButton.text = 'Working...';
    };

    $scope.enableSearchButton = function () {
        $scope.searchButton.disabled = false;
        $scope.searchButton.text = 'Search';
    };

    $scope.assignColors = function() {
        var colorMap = colorMapService.generateColorMap($scope.getSocietyIds());
        $scope.getResults().forEach(function(result) {
            result.society.style = {'background-color' : colorMap[result.society.id] };
        });
    };

    $scope.resetSearchQuery = function() {
        $scope.model.searchQuery = {};
    };

    $scope.updateSearchQuery = function(searchQuery) {
        for(var propertyName in searchQuery) {
            $scope.model.searchQuery[propertyName] = searchQuery[propertyName];
        }
    };

    $scope.searchSocieties = function() {
        $scope.disableSearchButton();
        $scope.model.searchResults = FindSocieties.find($scope.model.searchQuery,$scope.searchCompleted);
    };

    $scope.searchCompleted = function() {
        $scope.enableSearchButton();
        $scope.assignColors();
        $scope.switchToResults();
    };
}