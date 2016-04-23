function CulturalCtrl($scope, searchModelService, Variable, CodeDescription, ContinuousVariable, DatasetSources, getCategories) {
   var linkModel = function() {
        // Model/state lives in searchModelService
        $scope.traits = [searchModelService.getModel().getCulturalTraits()];
        $scope.errors = "";
        numVars();
    };
    
    
    $scope.$on('searchModelReset', linkModel); // When model is reset, update our model
    linkModel();
        
    //triggered by the view when a source is changed
    $scope.sourceChanged = function(trait) {
        trait.source_categories = [];
        trait.source_categories = getCategories.query({query: {source: trait.selectedSource.id}});
    };

    // triggered by the view when a category is changed
    $scope.categoryChanged = function(trait) {
        trait.indexVariables = Variable.query({index_categories: trait.selectedCategory.id, source: trait.selectedSource.id});
		trait.codes = [];
        trait.selectedCode = "";
    };
    
    function numVars() {
        $scope.count = 0;
        $scope.traits.forEach(function(trait) {
            trait.badgeValue = 0;
            for (var variable in trait.selected) {
                if (trait.selected[variable].length > 0) $scope.count++;
                trait.badgeValue += trait.selected[variable].length;
            }
        });
        if ($scope.count < 5) $scope.errors = "";
    };
    
    $scope.$on('variableCheck', numVars);
    
    // triggered by the view when a trait is changed in the picker
    $scope.traitChanged = function(trait) {
        trait.selectedCode = "";
        if (trait.selectedVariable.data_type.toUpperCase() == 'CONTINUOUS') {
            trait.codes = ContinuousVariable.query({query: {bf_id: trait.selectedVariable.id}});
        } else
            trait.codes = CodeDescription.query({variable: trait.selectedVariable.id });
        
        //make select all the default
        if (trait.selectedVariable.id in trait.selected) {
            trait.codes.$promise.then(function(result) { 
                result.forEach(function(code) {
                    if (trait.selectedVariable.data_type.toUpperCase() == 'CONTINUOUS'){
                        if (trait.selected[trait.selectedVariable.id].map(function(c) { return c.variable+''+c.code; }).indexOf(code.variable+''+code.code) != -1) {
                            code.isSelected = true;
                        }
                    } else if (trait.selected[trait.selectedVariable.id].map(function(c) { return c.id; }).indexOf(code.id) != -1)
                        code.isSelected = true;
                });
                numVars();
            });
        } else {
            trait.codes.$promise.then(function(result) {
                result.forEach(function(code) {
                    code.isSelected = true;
                    if (trait.selectedVariable.data_type.toUpperCase() == 'CONTINUOUS') code.short_description = code.description;
                    if (code.variable in trait.selected) {
                        if (trait.selectedVariable.data_type.toUpperCase() == 'CONTINUOUS') {
                            if (trait.selected[code.variable].map(function(c) { return c.variable+''+c.code; }).indexOf(code.variable+''+code.code) == -1) {
                                trait.selected[code.variable].push(code);
                            }
                        } else if (trait.selected[code.variable].map(function(c) { return c.id; }).indexOf(code.id) == -1) {
                            trait.selected[code.variable].push(code);
                        }
                    } else {
                        trait.selected[code.variable] = [code];
                        trait.selected[code.variable].variable_name = trait.selectedVariable.label + ' - ' + trait.selectedVariable.name;
                    }
                });
                trait.selected[trait.selectedVariable.id].allSelected = true;
                numVars();
            });
        }
    };
    
    $scope.traitCodeSelectionChanged = function(trait, code) {
        if (code.isSelected) {
            if (code.variable in trait.selected) {
                if (trait.selectedVariable.data_type.toUpperCase() == 'CONTINUOUS') {
                    code.short_description = code.description;
                    if (trait.selected[code.variable].map(function(c) { return c.variable+''+c.code; }).indexOf(code.variable+''+code.code) == -1) 
                        trait.selected[code.variable].push(code);
                } else if (trait.selected[code.variable].map(function(c) { return c.id; }).indexOf(code.id) == -1) 
                    trait.selected[code.variable].push(code);
            } else 
                trait.selected[code.variable] = [code];
                trait.selected[code.variable].variable_name = trait.selectedVariable.label + ' - ' + trait.selectedVariable.name;
        } else {
            $scope.removeFromSearch(code, 'culture');
        }
        if (trait.selected[code.variable].length == trait.codes.length) trait.selected[code.variable].allSelected = true;
        else trait.selected[code.variable].allSelected = false;
        numVars();
    };

    // used before searching to extract the codes from the search selection
    // Expects an array of CulturalTraitModel objects
	// this only gets the selected codes for the currently selected cultural trait
    $scope.getSelectedTraitCodes = function() {
		traits = $scope.traits;
		var allCodes = Array.prototype.concat.apply([], traits.map( function(trait) { 
			return trait.codes; 
		}));
		return allCodes.filter( function(c) { return c.isSelected; });
    };
	
	$scope.selectAllChanged = function(trait) {
        if (trait.selectedVariable.id in trait.selected) {
            if (trait.selected[trait.selectedVariable.id].allSelected) { // all selected
                trait.codes.forEach(function(code) {
                    code.isSelected = true;
                    if (trait.selectedVariable.data_type.toUpperCase() == 'CONTINUOUS') {
                        code.short_description = code.description;
                        if (trait.selected[trait.selectedVariable.id].map(function(c) { return c.variable+''+c.code; }).indexOf(code.variable+''+code.code) == -1) {
                            trait.selected[trait.selectedVariable.id].push(code);
                        }
                    } else {
                        if(trait.selected[trait.selectedVariable.id].map(function(c) { return c.id; }).indexOf(code.id) == -1) 
                            trait.selected[trait.selectedVariable.id].push(code);
                    }
                });
            } else { // deselect all
                trait.codes.forEach(function(code) {
                    code.isSelected = false;
                    $scope.removeFromSearch(code, 'culture');
                });
            }
        }
        numVars();
	};

    // wired to the search button. Gets the code ids, adds cultural to the query, and invokes the search
    $scope.doSearch = function() {
        if ($scope.count > 4) {
            $scope.errors = "Error, search is limited to 4 variables";
            return;
        }
        $scope.search();
    };
}
