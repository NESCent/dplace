/**
 * Controller for the search tab. pops in sub controllers for geographic/cultural/etc
 *
 * @param $scope
 * @param colorMapService
 * @param searchModelService
 * @param FindSocieties
 * @constructor
 */
function SearchCtrl($scope, $window, $location, colorMapService, searchModelService, FindSocieties) {
    $scope.setActive('search');
    $scope.searchModel = searchModelService.getModel();
    $scope.searchBySocietyButton = {text: 'Search', disabled: false};
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
        $scope.searchBySocietyButton = {text: 'Working...', disabled: true};

    };

    $scope.enableSearchButton = function () {
        $scope.searchButton.disabled = false;
        $scope.searchButton.text = 'Search';
        $scope.searchBySocietyButton = {text: 'Search', disabled: false};

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

    var errorCallBack = function() {
        $scope.errors = "Invalid input.";
        $scope.enableSearchButton();
    };
	
    var searchCompletedCallback = function() {
        $scope.enableSearchButton();
        $scope.searchModel.results = searchModelService.getCodeIDs($scope.searchModel.results, $scope.searchModel.query);
        searchModelService.assignColors($scope.searchModel.results);
        $scope.searchModel.results.searched = true;
        $scope.switchToResults();
    };
    
    var searchBySocietyCallBack = function() {
        $scope.enableSearchButton();
        $scope.searchModel.results.searchedByName = true;
        if ($scope.searchModel.results.societies.length == 1) 
            $window.location.href = '/society/'+$scope.searchModel.results.societies[0].society.ext_id;
        else 
            $scope.switchToResults();
    };

    $scope.searchSocieties = function() {
        $scope.disableSearchButton();
        var query = $scope.searchModel.query;
        $scope.searchModel.results = FindSocieties.find(query, searchCompletedCallback, errorCallBack);
    };
    
    $scope.searchBySociety = function() {
        $scope.disableSearchButton();
        $scope.searchModel.query = {'name': $scope.model.societyQuery}
        $scope.searchModel.results = FindSocieties.find($scope.searchModel.query, searchBySocietyCallBack);
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
                        pruned = codes[i].variable;
                        if ('id' in codes[i]) {
                            pruned += '-' + codes[i].id;
                        }
                        if ('min' in codes[i]) {
                            pruned += '-' + codes[i].min;
                        }
                        if ('max' in codes[i]) {
                            pruned += '-' + codes[i].max;
                        }
                        searchQuery['c'].push(pruned.toString());
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
        searchModelService.updateSearchQuery(searchQuery);
        // console.log(searchQuery);
        $scope.searchSocieties();

    };

    // resets this object state and the search query.
    $scope.resetSearch = function() {
        $scope.errors = "";
        $scope.enableSearchButton();
        $scope.searchModel.reset();
        // send a notification so that the individual controllers reload their state
        $scope.$broadcast('searchModelReset');

        // hide selected search criteria div if shown
        if (!$("#selected-criteria").hasClass('hidden')) {
            $("#selected-criteria").addClass('hidden');
            $scope.searchCriteria = "View selected search criteria";
            $("#search-panel").toggleClass('col-md-9', 'col-md-12');
        }
    };

}