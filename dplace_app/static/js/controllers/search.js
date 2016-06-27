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
    
    $scope.isEmpty = function(object, searchType) {
        if (searchType == 'environmental') {
            for (var i = 0; i < object.length; i++) {
                if (object[i].selectedVariable) return false;
            }
        } else {
            for (var key in object) {
                if (object[key].length > 0)
                    return false;
            }
        }
        return true;
    };
    $scope.searchCriteria = "View selected search criteria";

    $scope.showCriteria = function() {
        $("#selected-criteria").toggleClass('hidden');
        $("#search-panel").toggleClass('col-md-9', 'col-md-12');
        
        if (!$("#selected-criteria").hasClass('hidden')) $scope.searchCriteria = "Hide selected search criteria";
        else $scope.searchCriteria = "View selected search criteria";
    };
    
    $scope.checkIfSelected = function() {
        if ($scope.searchModel.getGeographicRegions().selectedRegions.length > 0) return true;
        if ($scope.searchModel.getEnvironmentalData().selectedVariables.length > 0) {
            for (var i = 0; i < $scope.searchModel.getEnvironmentalData().selectedVariables.length; i++) {
                if ($scope.searchModel.getEnvironmentalData().selectedVariables[i].selectedVariable) return true;
            }
        }
        if (!$scope.isEmpty($scope.searchModel.getCulturalTraits().selected)) return true;
        if (!$scope.isEmpty($scope.searchModel.getLanguageClassifications().selected)) return true;
        return false;
    }
    
    //removes a variable, language, or region from search parameters
    $scope.removeFromSearch = function(object, searchType) {
        var index = -1;
        switch(searchType) {
            case 'geographic':
                index = $scope.searchModel.getGeographicRegions().selectedRegions.indexOf(object);
                $scope.searchModel.getGeographicRegions().selectedRegions.splice(index, 1);
                $scope.searchModel.getGeographicRegions().badgeValue = $scope.searchModel.getGeographicRegions().selectedRegions.length;
                break;
            case 'environmental':
                index = $scope.searchModel.getEnvironmentalData().selectedVariables.indexOf(object);
                $scope.searchModel.getEnvironmentalData().selectedVariables.splice(index, 1);
                $scope.searchModel.getEnvironmentalData().badgeValue = $scope.searchModel.getEnvironmentalData().selectedVariables.length;
                break;
            case 'family':
                var langSelectedObjs = $scope.searchModel.getLanguageClassifications().selected;
                if (object in langSelectedObjs) {
                    for (var i = 0; i < langSelectedObjs[object].length; i++) {
                        langSelectedObjs[object][i].isSelected = false;
                        $scope.searchModel.getLanguageClassifications().badgeValue -= langSelectedObjs[object][i].societies.length
                    }
                    delete langSelectedObjs[object];
                    $scope.$broadcast('classificationSelectionChanged');
                }
                break;
            case 'language':
                var langSelectedObjs = $scope.searchModel.getLanguageClassifications().selected;
                if (object.family.name in langSelectedObjs) {
                    for (var i = 0; i < langSelectedObjs[object.family.name].length; i++) {
                        if (langSelectedObjs[object.family.name][i].id == object.id) {
                            langSelectedObjs[object.family.name][i].isSelected = false;
                            $scope.searchModel.getLanguageClassifications().badgeValue -= langSelectedObjs[object.family.name][i].societies.length
                            index = i;
                            break;
                        }
                    }
                    if (index > -1) {
                        langSelectedObjs[object.family.name].splice(index, 1);
                        // sync Select all checkbox in language.(html|js)
                        $scope.$broadcast('classificationSelectionChanged');
                    }
                }
                break;
            case 'culture': 
                if (object.variable in $scope.searchModel.getCulturalTraits().selected) {
                    for (var i = 0; i < $scope.searchModel.getCulturalTraits().selected[object.variable].length; i++) {
                        if (($scope.searchModel.getCulturalTraits().selected[object.variable][i].id == object.id) || ($scope.searchModel.getCulturalTraits().selected[object.variable][i].description == object.description)) {
                            $scope.searchModel.getCulturalTraits().selected[object.variable][i].isSelected = false;
                            index = i;
                            break;
                        }
                    }
                    if (index > -1) {
                        $scope.searchModel.getCulturalTraits().selected[object.variable].splice(index, 1);
                        $scope.searchModel.getCulturalTraits().selected[object.variable].allSelected = false;
                        $scope.searchModel.getCulturalTraits().badgeValue--;
                        $scope.$broadcast('variableCheck');
                    }
                
                }
            case 'variable':
                while(object.length > 0) {
                    $scope.removeFromSearch(object[0], 'culture')
                }
        }
        if (!$scope.checkIfSelected()) {
            d3.select("#selected-criteria").classed("hidden", true);
            d3.select("#search-panel").classed("col-md-12", true);
            d3.select("#search-panel").classed("col-md-9", false);
            if (!$("#selected-criteria").hasClass('hidden')) $scope.searchCriteria = "Hide selected search criteria";
            else $scope.searchCriteria = "View selected search criteria";
        }
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
            results.environmental_variables[i]['min'] = min_value.toFixed(4);
            results.environmental_variables[i]['max'] = max_value.toFixed(4);
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
            
            $scope.searchModel.results.classifications.sort(function(a,b) {
                if (a.name < b.name) return -1;
                else if (a.name > b.name) return 1;
                else return 0;
            })
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
                
                $scope.searchModel.results.variable_descriptions[i].variable['min'] = min.toFixed(2);
                $scope.searchModel.results.variable_descriptions[i].variable['max'] = max.toFixed(2);
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
    
    var searchBySocietyCallBack = function() {
        $scope.switchToSocResults($scope.model.societyQuery);
    };

        // This method merges the current searchQuery object with the incoming searchQuery
    $scope.updateSearchQuery = function(searchQuery) {
        $scope.searchModel.query = {};
        for(var propertyName in searchQuery) {
            $scope.searchModel.query[propertyName] = searchQuery[propertyName];
        }
    };
    
    $scope.searchSocieties = function() {
        $scope.disableSearchButton();
        var query = $scope.searchModel.query;
        $scope.searchModel.results = FindSocieties.find(query, searchCompletedCallback, errorCallBack);
    };
    
    $scope.searchBySociety = function() {
        var query = {'name': $scope.model.societyQuery}
        $scope.searchModel.results = FindSocieties.find(query, searchBySocietyCallBack);
    };

    $scope.search = function() {
        var i, pruned;
        searchModel = searchModelService.getModel();
        searchParams = searchModel.params;    
        searchQuery = {};
        for (var propertyName in searchParams) {
            //get selected cultural traits/codes
            if (propertyName == 'culturalTraits') {
                var codes = [];
                for (var variable in searchParams[propertyName].selected) {
                    searchParams[propertyName].selected[variable].forEach(function(code) { if (code.isSelected) codes.push(code); });
                };
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
                var classifications = [];
                for (var family in searchParams[propertyName].selected) {
                    searchParams[propertyName].selected[family].forEach(function(language) { if (language.isSelected) classifications.push(language); });
                }
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