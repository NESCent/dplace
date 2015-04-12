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
    
    //this function is needed for the coloring of markers
    //it converts the coded_value into the bin's code
    //it also constructs var_bins, which is needed for display of legends
    //NEEDS FURTHER WORK
    $scope.assignBins = function(variable_codes) {
        var_bins = {};
        for (var i = 0; i < variable_codes.length; i++) {
            if (variable_codes[i].bf_id) {
                if (variable_codes[i].bf_id in var_bins)
                    var_bins[variable_codes[i].bf_id] = var_bins[variable_codes[i].bf_id].concat([variable_codes[i]]);
                else 
                    var_bins[variable_codes[i].bf_id] = [variable_codes[i]];
            } else if (variable_codes[i].variable in var_bins)
                var_bins[variable_codes[i].variable] = var_bins[variable_codes[i].variable].concat([variable_codes[i]]);
            else
                var_bins[variable_codes[i].variable] = [variable_codes[i]];
        }
        
        if ($scope.searchModel.results.variable_descriptions) {
            for (var i = 0; i < $scope.searchModel.results.variable_descriptions.length; i++){
                if ($scope.searchModel.results.variable_descriptions[i].data_type == 'CONTINUOUS') 
                    var_bins[$scope.searchModel.results.variable_descriptions[i].id].name = $scope.searchModel.results.variable_descriptions[i].name;
                if (var_bins[$scope.searchModel.results.variable_descriptions[i].id].name) continue;
                else var_bins[$scope.searchModel.results.variable_descriptions[i].id].name = $scope.searchModel.results.variable_descriptions[i].name;
            }
        }
        $scope.searchModel.results.code_ids = var_bins;
        
        for (var i = 0; i < $scope.searchModel.results.societies.length; i++) {
            for (var v = 0; v < $scope.searchModel.results.societies[i].variable_coded_values.length; v++) {
                variable = $scope.searchModel.results.societies[i].variable_coded_values[v].variable;
                bins = var_bins[variable];
                for (var b = 0; b < bins.length; b++) {
                    try {
                        if (parseFloat($scope.searchModel.results.societies[i].variable_coded_values[v].coded_value) < bins[b].max) {
                            $scope.searchModel.results.societies[i].variable_coded_values[v]['bf_code'] = ""+bins[b].code;
                            break;
                        }                        
                        
                    } catch (err) {
                        break;
                    }
                }
            }
        }
    }
    
    $scope.assignColors = function() {
        if ($scope.searchModel.query.variable_codes) $scope.assignBins($scope.searchModel.query.variable_codes);
        var colorMap = colorMapService.generateColorMap($scope.searchModel.getSocieties(), $scope.searchModel.query);
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