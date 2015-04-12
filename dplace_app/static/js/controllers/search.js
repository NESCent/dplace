/**
 * Controller for the search tab. pops in sub controllers for geographic/cultural/etc
 *
 * @param $scope
 * @param colorMapService
 * @param searchModelService
 * @param FindSocieties
 * @constructor
 */
function SearchCtrl($scope, colorMapService, searchModelService, FindSocieties, TreesFromLanguages) {
    $scope.setActive('search');
    $scope.searchModel = searchModelService.getModel();
    $scope.selectedButton = $scope.searchModel.selectedButton;
    $scope.buttons = [
        {value:'geographic', name:'Geographic', badgeValue:
            function() { return $scope.searchModel.getGeographicRegions().badgeValue; }
        },
        {value:'cultural', name:'Cultural Traits', badgeValue:
            function() { return $scope.searchModel.getCulturalTraits().badgeValue; }
        },
        {value:'environmental', name:'Environmental', badgeValue:
            function() { return $scope.searchModel.getEnvironmentalData().badgeValue; }
        },
        {value:'language', name:'Language', badgeValue:
            function() { return $scope.searchModel.getLanguageClassifications().badgeValue; }
        }
    ];

    $scope.buttonChanged = function(selectedButton) {
        $scope.selectedButton = selectedButton;
    };

    // All of this needs to move into model
    $scope.disableSearchButton = function () {
        $scope.searchButton.disabled = true;
        $scope.searchButton.text = 'Working...';
    };

    $scope.enableSearchButton = function () {
        $scope.searchButton.disabled = false;
        $scope.searchButton.text = 'Search';
    };
    
    //calculates the range for environmental variables
    //needed for coloring of markers
    $scope.calculateRange = function(results) {
        societies = results.societies;
        for (var i = 0; i < results.environmental_variables.length; i++) {
            var extractedValues = societies.map(function(society) { 
                for (var j = 0; j < society.environmental_values.length; j++) {
                    if (society.environmental_values[j].variable == results.environmental_variables[i].id)
                        return society.environmental_values[j].value;
                }
            });
            var min_value = Math.min.apply(null, extractedValues);
            var max_value = Math.max.apply(null, extractedValues);
            var range = max_value - min_value;
            results.environmental_variables[i]['range'] = range;
        }
    };
    
    //calculates number of codes selected for each variable and saves to coded_value
    //needed for coloring of markers
    $scope.getCodeIDs = function(results, query) {
        code_ids = {};
    
        for (var i = 0; i < query.variable_codes.length; i++) {
            for (var j = 0; j < results.variable_descriptions.length; j++) {
                if (query.variable_codes[i].variable == results.variable_descriptions[j].id) {                   
                    if (query.variable_codes[i].variable in code_ids)
                        code_ids[query.variable_codes[i].variable] += 1;
                    else
                        code_ids[query.variable_codes[i].variable] = 1;
                }
            }
        }
        for (var i = 0; i < results.societies.length; i++) {
            for (var j = 0; j < results.societies[i].variable_coded_values.length; j++) {
                results.societies[i].variable_coded_values[j]['total_codes_selected'] = code_ids[results.societies[i].variable_coded_values[j].variable];
            }
        }
    }

    
    $scope.assignColors = function() {
        results = $scope.searchModel.getResults();
        $scope.calculateRange(results);
        if ($scope.searchModel.query.variable_codes)
            $scope.getCodeIDs(results, $scope.searchModel.query);
        var colorMap = colorMapService.generateColorMap(results);
        $scope.searchModel.getSocieties().forEach(function(container) {
            container.society.style = {'background-color' : colorMap[container.society.id] };
        });
    };

    function searchForLanguageTrees() {
        var languageIDs = $scope.searchModel.getSocieties().filter(function (container) {
            return container.society.language != null;
        }).map(function (container) {
            return container.society.language.id;
        });
        $scope.searchModel.results.languageTrees = TreesFromLanguages.find({language_ids: languageIDs}, addTreesToSocieties);
    }
    
    function addTreesToSocieties() {
        $scope.searchModel.getSocieties().forEach(function (container) {
            var language = container.society.language;
            if(language != null) {
                container.society.trees = $scope.searchModel.results.languageTrees.filter(function (tree) {
                    return tree.languages.some(function (item) {
                        return angular.equals(language, item);
                    });
                });
            } else {
                container.society.trees = [];
            }
        });
    }

    // This method merges the current searchQuery object with the incoming searchQuery
    $scope.updateSearchQuery = function(searchQuery) {
        for(var propertyName in searchQuery) {
            $scope.searchModel.query[propertyName] = searchQuery[propertyName];
        }
    };

    var errorCallBack = function() {
	$scope.errors = "Invalid input.";
	$scope.enableSearchButton();
    };
	
    var searchCompletedCallback = function() {
        $scope.enableSearchButton();
        $scope.assignColors();
        searchForLanguageTrees();
        $scope.switchToResults();
    };

    $scope.searchSocieties = function() {
        $scope.disableSearchButton();
        var query = $scope.searchModel.query;
        $scope.searchModel.results = FindSocieties.find(query, searchCompletedCallback, errorCallBack);
    };

    // resets this object state and the search query.
    $scope.resetSearch = function() {
		$scope.errors = "";
		$scope.enableSearchButton();
        $scope.searchModel.reset();
        // send a notification so that the individual controllers reload their state
        $scope.$broadcast('searchModelReset');
    };

}