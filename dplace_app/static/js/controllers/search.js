function SearchCtrl($scope, colorMapService) {
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

    $scope.searchCompleted = function() {
        $scope.enableSearchButton();
        $scope.assignColors();
        $scope.switchToResults();
    };
}