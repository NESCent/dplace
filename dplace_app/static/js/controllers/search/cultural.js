function CulturalCtrl($scope, Variable, VariableCategory, CodeDescription) {
    $scope.initialize = function() {
        $scope.model.searchParams.traits = [{
            categories: VariableCategory.query(),
            variables: [],
            selectedCategory: null,
            selectedVariable: null
        }];
    };
    $scope.initialize();

    $scope.categoryChanged = function(trait) {
        trait.indexVariables = Variable.query({index_categories: trait.selectedCategory.id});
        trait.nicheVariables = Variable.query({niche_categories: trait.selectedCategory.id});
        trait.codes = [];
        trait.selectedCode = "";
    };

    $scope.traitChanged = function(trait) {
        trait.selectedCode = "";
        trait.codes = CodeDescription.query({variable: trait.selectedVariable.id });
    };

    $scope.getSelectedTraitCodes = function() {
        var allCodes = Array.prototype.concat.apply([], $scope.model.searchParams.traits.map( function(trait) { return trait.codes; }));
        var selectedCodes = allCodes.filter( function(c) { return c.isSelected; }).map( function(c) { return c.id; })
        console.log(selectedCodes);
        return selectedCodes;
    };

    // Search for societies matching this
    $scope.doSearch = function() {
        var code_ids = $scope.getSelectedTraitCodes()
        $scope.updateSearchQuery({ variable_codes: code_ids });
        $scope.searchSocieties();
    };

    $scope.resetSearch = function() {
        $scope.initialize();
        $scope.resetSearchQuery();
    };

}
