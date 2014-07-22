function SearchCtrl($scope, colorMapService, TreesFromLanguages) {
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

    function searchForLanguageTrees() {
        var languageIDs = $scope.model.searchResults.results.filter(function (result) {
            return result.society.language != null;
        }).map(function (result) {
            return result.society.language.id;
        });
        $scope.model.languageTrees = TreesFromLanguages.find({language_ids: languageIDs}, addTreesToSocieties);
    }
    
    function addTreesToSocieties() {
        $scope.model.searchResults.results.forEach(function (result) {
            var language = result.society.language;
            if (language != null) {
                result.society.trees = $scope.model.languageTrees.filter(function (tree) {
                    return tree.languages.some(function (item) {
                        return angular.equals(language, item);
                    });
                });
            } else {
                result.society.trees = [];
            }
        });
    }

    $scope.searchCompleted = function() {
        $scope.enableSearchButton();
        $scope.assignColors();
        searchForLanguageTrees();
        $scope.switchToResults();
    };
}