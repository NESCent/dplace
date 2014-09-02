function CulturalCtrl($scope, searchModelService, Variable, CodeDescription) {
	var selected = []; //keeps track of selected codes
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
		selectedCodes = allCodes.filter( function(c) { return c.isSelected; }).map( function(c) { return c.id; });
        return selectedCodes;
    };

    $scope.traitCodeSelectionChanged = function(trait) {
        //trait.badgeValue = trait.codes.filter(function(code) { return code.isSelected; }).length;
		 currentSelection = $scope.getSelectedTraitCodes();
		currentSelection.forEach(function(code) {
			if (selected.indexOf(code) == -1) { 
			//if selected trait code is not already in the array of selected codes, add it to the array
				selected.push(code);
			}
		});
		trait.badgeValue = selected.length; //update badge value
	};
	
	$scope.selectAllChanged = function(trait) { //this doesn't work
		angular.forEach(trait.codes, function(code){ code.isSelected = true; });
	};

    // wired to the search button. Gets the code ids, adds cultural to the query, and invokes the search
    $scope.doSearch = function() {
        //var code_ids = $scope.getSelectedTraitCodes();
        $scope.updateSearchQuery({ variable_codes: selected });
        $scope.searchSocieties();
    };
}
