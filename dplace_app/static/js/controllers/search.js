/**
 * Controller for the search tab. pops in sub controllers for geographic/cultural/etc
 *
 * @param $scope
 * @param colorMapService
 * @param searchModelService
 * @param FindSocieties
 * @constructor
 */
function SearchCtrl($scope, colorMapService, searchModelService, FindSocieties) {
    $scope.setActive('search');
    $scope.searchModel = searchModelService.getModel();
    $scope.selectedButton = $scope.searchModel.selectedButton;
    var rP = 'radioPlaces';
    var rL = 'radioLanguage';
    var rC = 'radioCulture';
    var rE = 'radioEnv';
    // preserve active button style if any
    if($scope.selectedButton) {
        switch($scope.selectedButton.radioClass) {
        case 'radioPlaces':
            rP += ' active';
            break;
        case 'radioLanguage':
            rL += ' active';
            break;
        case 'radioCulture':
            rC += ' active';
            break;
        case 'radioEnv':
            rE += ' active';
            break;
        }
    }
    $scope.buttons = [
        {radioClass: rP, value:'geographic', name:'PLACES', badgeValue:
            function() { return $scope.searchModel.getGeographicRegions().badgeValue; }
        },
        {radioClass: rL, value:'language', name:'LANGUAGE', badgeValue:
            function() { return $scope.searchModel.getLanguageClassifications().badgeValue; }
        },
        {radioClass: rC, value:'cultural', name:'CULTURE', badgeValue:
            function() { return $scope.searchModel.getCulturalTraits().badgeValue; }
        },
        {radioClass: rE, value:'environmental', name:'ENVIRONMENT', badgeValue:
            function() { return $scope.searchModel.getEnvironmentalData().badgeValue; }
        }
    ];

    $scope.buttonChanged = function(selectedButton) {
        $scope.selectedButton = selectedButton;
        $scope.searchModel.selectedButton = selectedButton;
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
            extractedValues = societies.map(function(society) { 
                for (var j = 0; j < society.environmental_values.length; j++) {
                    if (society.environmental_values[j].variable == results.environmental_variables[i].id) {
                        if (society.environmental_values[j].value) return society.environmental_values[j].value;
                    }
                }
            });
            var min_value = null; var max_value = null;
           extractedValues.forEach(function(val) {
            if (!min_value) min_value = val;
            if (!max_value) max_value = val;
            
            if (val < min_value) min_value = val;
            if (val > max_value) max_value = val;
           });
            var range = max_value - min_value;
            results.environmental_variables[i]['range'] = range;
            results.environmental_variables[i]['min'] = Math.round(min_value*10000)/10000;
            results.environmental_variables[i]['max'] = Math.round(max_value*10000)/10000;
        }
        return results;
    };
    
    //calculates number of codes selected for each variable and saves to coded_value
    //needed for coloring of markers
    $scope.getCodeIDs = function() {
        $scope.searchModel.results.code_ids = {};
        if ($scope.searchModel.query.l && !$scope.searchModel.query.c && !$scope.searchModel.query.e) {
            $scope.searchModel.results.classifications = [];
            added = [];
            for (var i = 0; i < $scope.searchModel.results.societies.length; i++) {
                for (var s = 0; s < $scope.searchModel.results.societies[i].languages.length; s++) {
                    language_family = $scope.searchModel.results.societies[i].languages[s].family;
                    if (added.indexOf(language_family.id) == -1) { 
                        $scope.searchModel.results.classifications.push(language_family);       
                        added.push(language_family.id);
                    }
                }
            }
        }

        for (var i = 0; i < $scope.searchModel.results.variable_descriptions.length; i++) {
            if ($scope.searchModel.results.variable_descriptions[i].variable.data_type.toUpperCase() == 'CONTINUOUS') {
                codes = $scope.searchModel.query.c.filter(function(code) { return code.variable == $scope.searchModel.results.variable_descriptions[i].variable.id; });
                var min;
                var max = 0;
                
                codes.forEach(function(c_var) {
                    if (!min) {
                        min = c_var.min;
                    } else {
                        if (c_var.min < min) min = c_var.min;
                    }
                    if (c_var.max > max) max = c_var.max;
                });
                
                $scope.searchModel.results.variable_descriptions[i].variable['min'] = min;
                $scope.searchModel.results.variable_descriptions[i].variable['max'] = max;
                $scope.searchModel.results.variable_descriptions[i].variable['units'] = $scope.searchModel.results.variable_descriptions[i].variable.name.substring($scope.searchModel.results.variable_descriptions[i].variable.name.indexOf('(')+1, $scope.searchModel.results.variable_descriptions[i].variable.name.indexOf(')'));
                $scope.searchModel.results.variable_descriptions[i].codes = codes;
            }                    
            
        }
    }
    
    $scope.assignColors = function() {
        results = $scope.searchModel.getResults();
        results = $scope.calculateRange(results);
        var colorMap = colorMapService.generateColorMap(results);
        $scope.searchModel.getSocieties().forEach(function(container) {
            container.society.style = {'background-color' : colorMap[container.society.id] };
        });
    };
    
    function addTreesToSocieties() {
        $scope.searchModel.results.language_trees.phylogenies = [];
        $scope.searchModel.results.language_trees.glotto_trees = [];
        $scope.searchModel.results.language_trees.forEach(function(tree) {
            if (tree.name.indexOf("global") != -1) $scope.searchModel.results.language_trees.global_tree = tree;
            else if (tree.name.indexOf("glotto") != -1) {
                $scope.searchModel.results.language_trees.glotto_trees.push(tree);
            }
            else {
                $scope.searchModel.results.language_trees.phylogenies.push(tree);
            }
        $scope.searchModel.results.language_trees.glotto_trees.sort(function(a, b) { return a.name > b.name; });
        $scope.searchModel.results.language_trees.phylogenies.sort(function(a, b) { return a.name > b.name; });
        });
        $scope.searchModel.getSocieties().forEach(function (container) {
            var language = container.society.name;
            if(language != null) {
                container.society.trees = $scope.searchModel.results.language_trees.filter(function (tree) {
                    return tree.taxa.some(function (item) {
                        return item.societies.some(function(label) {
                            return angular.equals(label.society.name, language);
                        });
                    });
                });
            } else {
                container.society.trees = [];
            }
        });
    }


    var errorCallBack = function() {
	$scope.errors = "Invalid input.";
	$scope.enableSearchButton();
    };
	
    var searchCompletedCallback = function() {
        $scope.enableSearchButton();
        $scope.getCodeIDs();
        $scope.assignColors();
        addTreesToSocieties();
        $scope.searchModel.results.searched = true;
        $scope.switchToResults();
    };

        // This method merges the current searchQuery object with the incoming searchQuery
    $scope.updateSearchQuery = function(searchQuery) {
        $scope.searchModel.query = {};
        for(var propertyName in searchQuery) {
            $scope.searchModel.query[propertyName] = searchQuery[propertyName];
        }
        console.log($scope.searchModel.query);
    };
    
    $scope.searchSocieties = function() {
        $scope.disableSearchButton();
        var query = $scope.searchModel.query;
        $scope.searchModel.results = FindSocieties.find(query, searchCompletedCallback, errorCallBack);
    };

    $scope.search = function() {
        var i, pruned;
        searchModel = searchModelService.getModel();
        searchParams = searchModel.params;    
        searchQuery = {};
        for (var propertyName in searchParams) {
            //get selected cultural traits/codes
            if (propertyName == 'culturalTraits') {
                var codes = searchParams[propertyName].selected.filter(function(code){ return code.isSelected; });
                if (codes.length > 0) {
                    searchQuery['c'] = [];
                    for (i = 0; i < codes.length; i++) {
                        pruned = {variable: codes[i].variable};
                        if ('id' in codes[i]) {
                            pruned['id'] = codes[i].id;
                        }
                        if ('min' in codes[i]) {
                            pruned['min'] = codes[i].min;
                        }
                        if ('max' in codes[i]) {
                            pruned['max'] = codes[i].max;
                        }
                        searchQuery['c'].push(pruned);
                    }
                }
            }
            //get selected regions
            if (propertyName == 'geographicRegions') {
                var selectedRegions = searchParams[propertyName].selectedRegions;  
                selectedRegions.forEach(function (selectedRegion) {
                    searchParams[propertyName].allRegions.forEach(function(region) {
                        if (region.tdwg_code == selectedRegion.code)
                            selectedRegion.id = region.id;
                    });
                });
                if (selectedRegions.length > 0) {
                    searchQuery['p'] = [];
                    for (i = 0; i < selectedRegions.length; i++) {
                        searchQuery['p'].push(selectedRegions[i].id);
                    }
                }
            }
            //get selected environmental variable and search parameters
            if (propertyName == 'environmentalData') {
                searchParams[propertyName].selectedVariables.forEach(function(variable) {
                    if (variable.selectedVariable) {
                        filters = [
                            variable.selectedVariable.id,
                            variable.selectedFilter.operator,
                            variable.vals
                        ];
                        if ('e' in searchQuery) {
                            searchQuery['e'].push(filters);
                        } else {
                            searchQuery['e'] = [filters];
                        }
                    }
                });
            }
            
            //get selected languages
            if (propertyName == 'languageClassifications') { 
                var classifications = searchParams[propertyName].selected.filter(function(classification){ return classification.isSelected; });
                if (classifications.length > 0) {
                    searchQuery['l'] = [];
                    for (i = 0; i < classifications.length; i++) {
                        searchQuery['l'].push(classifications[i].id);
                    }
                }
           }
        }
        $scope.updateSearchQuery(searchQuery);
        $scope.searchSocieties();
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