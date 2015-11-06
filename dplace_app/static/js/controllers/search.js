/**
 * Controller for the search tab. pops in sub controllers for geographic/cultural/etc
 *
 * @param $scope
 * @param colorMapService
 * @param searchModelService
 * @param FindSocieties
 * @constructor
 */
function SearchCtrl($scope, colorMapService, searchModelService, FindSocieties, LanguageClass, TreesFromLanguages) {
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
        return results;
    };
    
    //calculates number of codes selected for each variable and saves to coded_value
    //needed for coloring of markers
    $scope.getCodeIDs = function() {
        $scope.searchModel.results.code_ids = {};
        if ($scope.searchModel.query.language_classifications && !$scope.searchModel.query.variable_codes && !$scope.searchModel.query.environmental_filters) {
            $scope.searchModel.results.classifications = {};
            LanguageClass.query().$promise.then(function(result) {
                for (var i = 0; i < $scope.searchModel.results.societies.length; i++) {
                    for (var j = 0; j < $scope.searchModel.results.societies[i].languages.length; j++) {
                        language_family = $scope.searchModel.results.societies[i].languages[j].language_family.name;
                        classification = $scope.searchModel.query.language_classifications.filter(function(l) { return l.language.id == $scope.searchModel.results.societies[i].languages[j].id; });
                        if (classification.length > 0) {
                            toAdd = result.filter(function(l) { return l.id == classification[0].class_subfamily; });
                            if (toAdd[0]){
                                if (language_family in $scope.searchModel.results.classifications) {
                                    if ($scope.searchModel.results.classifications[language_family].indexOf(toAdd[0]) == -1)
                                        $scope.searchModel.results.classifications[language_family] = $scope.searchModel.results.classifications[language_family].concat(toAdd);
                                        $scope.searchModel.results.classifications['NumClassifications'] += 1;
                               } else {
                                    $scope.searchModel.results.classifications[language_family] = toAdd;
                                    $scope.searchModel.results.classifications['NumClassifications'] = 1;
                                }
                            }
                        }
                    }
                }
            });
        
        }

        if (!$scope.searchModel.query.variable_codes) return;

        for (var i = 0; i < $scope.searchModel.query.variable_codes.length; i++) {
            if ($scope.searchModel.query.variable_codes[i].bf_id) {
                if (!($scope.searchModel.query.variable_codes[i].bf_id in $scope.searchModel.results.code_ids)) {
                    $scope.searchModel.results.code_ids[$scope.searchModel.query.variable_codes[i].bf_id] = [];
                }
                if (!$scope.searchModel.results.code_ids[$scope.searchModel.query.variable_codes[i].bf_id].absolute_min) {
                    $scope.abs_min = $scope.searchModel.query.variable_codes[i].absolute_min;
                    $scope.abs_max = $scope.searchModel.query.variable_codes[i].absolute_max;
                    $scope.searchModel.results.code_ids[$scope.searchModel.query.variable_codes[i].bf_id].min = $scope.searchModel.query.variable_codes[i].absolute_min;
                    $scope.searchModel.results.code_ids[$scope.searchModel.query.variable_codes[i].bf_id].max = $scope.searchModel.query.variable_codes[i].absolute_max;
                    $scope.searchModel.results.code_ids[$scope.searchModel.query.variable_codes[i].bf_id].bf_var = true;
                }
                continue;
            }
            if ($scope.searchModel.query.variable_codes[i].variable in $scope.searchModel.results.code_ids) {
                $scope.searchModel.results.code_ids[$scope.searchModel.query.variable_codes[i].variable] = $scope.searchModel.results.code_ids[$scope.searchModel.query.variable_codes[i].variable].concat([$scope.searchModel.query.variable_codes[i]]);
            } else {
                $scope.searchModel.results.code_ids[$scope.searchModel.query.variable_codes[i].variable] = [$scope.searchModel.query.variable_codes[i]];
            }
        }
        
        for (var i = 0; i < $scope.searchModel.results.variable_descriptions.length; i++) {
            if ($scope.searchModel.results.code_ids[$scope.searchModel.results.variable_descriptions[i].id].name) continue;
            else {
                $scope.searchModel.results.code_ids[$scope.searchModel.results.variable_descriptions[i].id].name = $scope.searchModel.results.variable_descriptions[i].name;
                if (!($scope.searchModel.results.code_ids[$scope.searchModel.results.variable_descriptions[i].id].bf_var)) 
                    $scope.searchModel.results.code_ids[$scope.searchModel.results.variable_descriptions[i].id].bf_var = false;
                if ($scope.searchModel.results.variable_descriptions[i].data_type=='CONTINUOUS')
                    $scope.searchModel.results.code_ids[$scope.searchModel.results.variable_descriptions[i].id].units = $scope.searchModel.results.variable_descriptions[i].name.substring($scope.searchModel.results.variable_descriptions[i].name.indexOf('(')+1, $scope.searchModel.results.variable_descriptions[i].name.indexOf(')'));
            }
         }
    }
    $scope.assignColors = function() {
        results = $scope.searchModel.getResults();
        results = $scope.calculateRange(results);
        bf_codes = [];
        if ($scope.searchModel.query.variable_codes) {
            for (var i = 0; i < $scope.searchModel.query.variable_codes.length; i++) {
                if ($scope.searchModel.query.variable_codes[i].bf_id)
                    bf_codes.push($scope.searchModel.query.variable_codes[i].bf_id);
            }
        }
        
        //needed for coloring of markers
        for (var i = 0; i < results.societies.length; i++) {
            for (var j = 0; j < results.societies[i].variable_coded_values.length; j++) {
                if (bf_codes.indexOf(results.societies[i].variable_coded_values[j].variable) != -1)
                    results.societies[i]['bf_cont_var'] = true;
            }
        }
        var colorMap = colorMapService.generateColorMap(results);
        $scope.searchModel.getSocieties().forEach(function(container) {
            container.society.style = {'background-color' : colorMap[container.society.id] };
        });
    };

    //not used at the moment
    function searchForLanguageTrees() {
        var languageIDs = $scope.searchModel.getSocieties().filter(function (container) {
            return container.society.language != null;
        }).map(function (container) {
            return container.society.language.id;
        });
        $scope.searchModel.results.language_trees = TreesFromLanguages.find({language_ids: languageIDs}, addTreesToSocieties);
    }
    
    function addTreesToSocieties() {
        $scope.searchModel.results.language_trees.phylogenies = [];
        $scope.searchModel.results.language_trees.glotto_trees = [];
        $scope.searchModel.results.language_trees.forEach(function(tree) {
            if (tree.name.indexOf("glotto") != -1) $scope.searchModel.results.language_trees.glotto_trees.push(tree);
            else $scope.searchModel.results.language_trees.phylogenies.push(tree);
        });
        $scope.searchModel.getSocieties().forEach(function (container) {
            var language = container.society.language;
            if(language != null) {
                container.society.trees = $scope.searchModel.results.language_trees.filter(function (tree) {
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
        $scope.getCodeIDs();
        $scope.assignColors();
        addTreesToSocieties();
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