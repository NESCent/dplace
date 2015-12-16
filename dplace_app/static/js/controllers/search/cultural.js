function CulturalCtrl($scope, searchModelService, Variable, CodeDescription, ContinuousVariable, DatasetSources, getCategories) {
   var linkModel = function() {
        // Model/state lives in searchModelService
        $scope.traits = [searchModelService.getModel().getCulturalTraits()];
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
        if (trait.selectedVariable.data_type == 'Continuous') {
            trait.codes = ContinuousVariable.query({query: {bf_id: trait.selectedVariable.id}});
        } else
            trait.codes = CodeDescription.query({variable: trait.selectedVariable.id });
    };

    // used before searching to extract the codes from the search selection
    // Expects an array of CulturalTraitModel objects
	// this only gets the selected codes for the currently selected cultural trait
    $scope.getSelectedTraitCodes = function() {
		traits = $scope.traits;
		var allCodes = Array.prototype.concat.apply([], traits.map( function(trait) { 
			return trait.codes; 
		}));
		selectedCodes = allCodes.filter( function(c) { return c.isSelected; }).map( function(c) { return c; });
	   return selectedCodes;
    };

    $scope.traitCodeSelectionChanged = function(trait) {
		currentSelection = $scope.getSelectedTraitCodes();
		currentSelection.forEach(function(code) {
			if (trait.selected.indexOf(code) == -1) {
			//if selected trait code is not already in the array of selected codes, add it to the array
				trait.selected.push(code);
			}
		});
		trait.badgeValue = trait.selected.filter(function(code) { return code.isSelected; }).length;
	};
	
	$scope.selectAllChanged = function(trait) {
		if (trait.codes.isSelected) {
			trait.codes.forEach(function(code){ code.isSelected = true;
			if (trait.selected.indexOf(code) == -1) {
				trait.selected.push(code);
			}
			});
		} else { trait.codes.forEach(function(code){ code.isSelected = false; });}

		trait.badgeValue = trait.selected.filter(function(code) { return code.isSelected; }).length;

	};

    // wired to the search button. Gets the code ids, adds cultural to the query, and invokes the search
    $scope.doSearch = function() {
        $scope.search();
    };
}
