function LanguageCtrl($scope, searchModelService, Language, LanguageFamily) {
    var linkModel = function() {
        // Get a reference to the language classifications from the model
        $scope.languageClassifications = searchModelService.getModel().getLanguageClassifications();
        $scope.families = [$scope.languageClassifications.allClasses];
    };
    $scope.$on('searchModelReset', linkModel); // When model is reset, update our model
    linkModel();
    
    $scope.selectionChanged = function(scheme) {
        scheme.languages = [];
        scheme.languages = Language.query({family: scheme.selectedFamily.id});
        //make select all the default
        scheme.languages.allSelected = true;
        scheme.languages.$promise.then(function(language) {
            language.isSelected = true;
            $scope.selectAllChanged(scheme);
        });
    };
    
    $scope.selectAllChanged = function(scheme) {
        if (scheme.languages.allSelected) {
            scheme.languages.forEach(function(language) {
                language.isSelected = true;
                if ($scope.languageClassifications.selected.indexOf(language) == -1) {
                    $scope.languageClassifications.selected.push(language);
                }
            });
        } else {
            scheme.languages.forEach(function(language) {
                language.isSelected = false;
            });
        }
        $scope.languageClassifications.selected = $scope.languageClassifications.selected.filter(function(x) { return x.isSelected; });
        $scope.languageClassifications.badgeValue = $scope.languageClassifications.selected.length;
    };
    
    function getSelectedLanguageClassifications(scheme) {
        return scheme.languages.filter( function (classification) {
            return classification.isSelected;
        });
    }

    $scope.getLanguageQueryFilters = function() {
        
        $scope.families.forEach(function(family) {
            var selectedClassifications = getSelectedLanguageClassifications(family);
            if (selectedClassifications.length == family.languages.length) family.languages.allSelected = true;
            else family.languages.allSelected = false;
            selectedClassifications.forEach(function(language) {
                if ($scope.languageClassifications.selected.indexOf(language) == -1) $scope.languageClassifications.selected.push(language);
            });
        });
    };

    $scope.classificationSelectionChanged = function(classification) {
        // Since the selections are stored deep in the model, this is greatly simplified by +1 / -1
        // get the currently selected languages and add them to the "selected" array
		currentSelection = $scope.getLanguageQueryFilters();
        $scope.languageClassifications.selected = $scope.languageClassifications.selected.filter(function(x) { return x.isSelected; });
        $scope.languageClassifications.badgeValue = $scope.languageClassifications.selected.length;
    };

    $scope.doSearch = function() {
        $scope.search();
    };

}