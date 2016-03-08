function CulturalCtrl($scope, searchModelService, Variable, CodeDescription, ContinuousVariable, DatasetSources, getCategories) {
   var linkModel = function() {
        // Model/state lives in searchModelService
        $scope.traits = [searchModelService.getModel().getCulturalTraits()];
        $scope.traits.forEach(function(trait) {
            if (!trait.alreadySelected)
                trait.alreadySelected = []; //keeps track of traits the user has already selected
        });
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

    // triggered by the view when a trait is changed in the picker
    $scope.traitChanged = function(trait) {
        trait.selectedCode = "";
        if (trait.selectedVariable.data_type.toUpperCase() == 'CONTINUOUS') {
            trait.codes = ContinuousVariable.query({query: {bf_id: trait.selectedVariable.id}});
        } else
            trait.codes = CodeDescription.query({variable: trait.selectedVariable.id });
        trait.selected = trait.selected.filter(function(code) { return code.isSelected; });

        //make select all the default
        if (trait.alreadySelected.indexOf(trait.selectedVariable.id) == -1) {
            trait.codes.isSelected = true;
            trait.codes.$promise.then(function(result) {
                result.forEach(function(code) {
                   code.isSelected = true;
                   
                   //continuous variable codes don't have IDs
                   if (trait.selectedVariable.data_type.toUpperCase() == 'CONTINUOUS') {
                        if (trait.selected.map(function(c) { return c.variable+''+c.code; }).indexOf(code.variable+''+code.code) == -1) {
                            trait.selected.push(code);
                        }
                   
                   } else if (trait.selected.map(function(code) { return code.id; }).indexOf(code.id) == -1) {
                            trait.selected.push(code);
                   }
                });
                trait.badgeValue = trait.selected.filter(function(code) { return code.isSelected; }).length;
            });
            trait.alreadySelected.push(trait.selectedVariable.id);
        } else {
            trait.codes.$promise.then(function(result) {
                result.forEach(function(code) {
                    //continuous variable codes don't have IDs
                   if (trait.selectedVariable.data_type.toUpperCase() == 'CONTINUOUS') {
                        if (trait.selected.map(function(c) { return c.variable+''+c.code; }).indexOf(code.variable+''+code.code) != -1) {
                            code.isSelected = true;
                        }
                   } else if (trait.selected.map(function(code) { return code.id; }).indexOf(code.id) != -1) {
                        code.isSelected = true;
                   }
                });
                trait.badgeValue = trait.selected.length;
            });
        }
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
    
    function removeCode(trait, code) {
        var index = -1;
        //continuous variable codes don't have IDs
       if (trait.selectedVariable.data_type.toUpperCase() == 'CONTINUOUS') {
            for (var i = 0; i < trait.selected.length; i++) {
                if (trait.selected[i].variable == code.variable && trait.selected[i].code == code.code) {
                    index = i;
                    break;
                }
            }
       } else {
            for (var i = 0; i < trait.selected.length; i++) {
                if (trait.selected[i].id == code.id) {
                    index = i;
                    break;
                }
            }
        }
        if (index > -1) {
            trait.selected.splice(index, 1);
        }
    };

    $scope.traitCodeSelectionChanged = function(trait) {
		currentSelection = $scope.getSelectedTraitCodes();
        if (currentSelection.length == trait.codes.length) trait.codes.isSelected = true;
        else trait.codes.isSelected = false;
        trait.selected = trait.selected.filter(function(code) { return code.isSelected; });
        trait.codes.forEach(function(code) {
            if (code.isSelected) {
                //continuous variable codes don't have IDs
               if (trait.selectedVariable.data_type.toUpperCase() == 'CONTINUOUS') {
                    if (trait.selected.map(function(c) { return c.variable + ''+ c.code; }).indexOf(code.variable+''+code.code) == -1) {
                        trait.selected.push(code);
                    }
               } else {
                    if (trait.selected.map(function(code) { return code.id; }).indexOf(code.id) == -1) {
                        trait.selected.push(code);
                    }
                }   
            } else {
                removeCode(trait, code);
            }
        });
                console.log(trait.selected);

		trait.badgeValue = trait.selected.length;
	};
	
	$scope.selectAllChanged = function(trait) {
        trait.selected = trait.selected.filter(function(code) { return code.isSelected; });
		if (trait.codes.isSelected) {
			trait.codes.forEach(function(code){ 
                code.isSelected = true;
                
                //continuous variable codes don't have IDs
               if (trait.selectedVariable.data_type.toUpperCase() == 'CONTINUOUS') {
                    if (trait.selected.map(function(c) { return c.variable+''+c.code; }).indexOf(code.variable+''+code.code) == -1) {
                        trait.selected.push(code);
                    }
               
               } else {
                    if (trait.selected.map(function(code) { return code.id; }).indexOf(code.id) == -1) trait.selected.push(code);
                }
			});
		} else { 
            trait.codes.forEach(function(code){ 
                code.isSelected = false; 
                removeCode(trait, code);
            });
        }
		trait.badgeValue = trait.selected.length;
	};

    // wired to the search button. Gets the code ids, adds cultural to the query, and invokes the search
    $scope.doSearch = function() {
        $scope.search();
    };
}
