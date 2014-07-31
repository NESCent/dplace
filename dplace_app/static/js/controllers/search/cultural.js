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
        trait.codes = CodeDescription.query({variable: trait.selectedVariable.id });
    };

    // used before searching to extract the codes from the search selection
    // Expects an array of CulturalTraitModel objects
    $scope.getSelectedTraitCodes = function(traits) {
        var allCodes = Array.prototype.concat.apply([], traits.map( function(trait) { return trait.codes; }));
        var selectedCodes = allCodes.filter( function(c) { return c.isSelected; }).map( function(c) { return c.id; })
        return selectedCodes;
    };

    $scope.traitCodeSelectionChanged = function(trait) {
        trait.badgeValue = trait.codes.filter(function(code) { return code.isSelected; }).length;
    };

    // wired to the search button. Gets the code ids, adds cultural to the query, and invokes the search
    $scope.doSearch = function() {
        var code_ids = $scope.getSelectedTraitCodes($scope.traits);
        $scope.updateSearchQuery({ variable_codes: code_ids });
        $scope.searchSocieties();
    };
}
