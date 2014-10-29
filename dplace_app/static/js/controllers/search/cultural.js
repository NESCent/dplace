function CulturalCtrl($scope, searchModelService, Variable, CodeDescription) {
   var linkModel = function() {
        // Model/state lives in searchModelService
        $scope.traits = [searchModelService.getModel().getCulturalTraits()];

    };
    $scope.$on('searchModelReset', linkModel); // When model is reset, update our model
    linkModel();
	
    // triggered by the view when a category is changed
    $scope.categoryChanged = function(trait) {
        trait.indexVariables = Variable.query({index_categories: trait.selectedCategory.id});
        trait.nicheVariables = Variable.query({niche_categories: trait.selectedCategory.id});
		trait.codes = [];
        trait.selectedCode = "";
    };

    // triggered by the view when a trait is changed in the picker
    $scope.traitChanged = function(trait) {
        trait.selectedCode = "";
        trait.codes = CodeDescription.query({variable: trait.selectedVariable });
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
        //trait.badgeValue = trait.codes.filter(function(code) { return code.isSelected; }).length;

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
        var code_ids = [];
        traits = $scope.traits;
        traits.forEach(function(trait) {
            //the selected array contains all the codes that have been selected (even if they were then unselected)
            //we need to filter it to only search for the codes that are currently selected
            trait.selected.filter(function(code){ return code.isSelected; }).map( function(c) { code_ids.push(c.id); });
        });

        $scope.updateSearchQuery({ variable_codes: code_ids });
        $scope.searchSocieties();
    };
}
