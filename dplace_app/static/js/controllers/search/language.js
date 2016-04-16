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
        
        if (!scheme.selectedFamily.alreadySelected) {
            //make select all the default
            scheme.languages.allSelected = true;
            scheme.languages.$promise.then(function(language) {
                language.isSelected = true;
                $scope.selectAllChanged(scheme);
            });
            scheme.selectedFamily.alreadySelected = true;
        } else {
            scheme.languages.$promise.then(function(result) {
                result.forEach(function(language) {
                    if ($scope.languageClassifications.selected.map(function(lang) { return lang.id; }).indexOf(language.id) != -1) {
                        language.isSelected = true;
                    }
                });
            });
        }
    };
    
    $scope.selectAllChanged = function(scheme) {
        if (scheme.languages.allSelected) {
            scheme.languages.forEach(function(language) {
                language.isSelected = true;
                if ($scope.languageClassifications.selected.map(function(lang) { return lang.id; }).indexOf(language) == -1) {
                    $scope.languageClassifications.selected.push(language);
                    $scope.languageClassifications.badgeValue += language.societies.length;
                }
            });
        } else {
            scheme.languages.forEach(function(language) {
                language.isSelected = false;
                $scope.removeFromSearch(language, 'language');
                
            });
        }
    };
    
    function getSelectedLanguageClassifications(scheme) {
        return scheme.languages.filter( function (classification) {
            return classification.isSelected;
        });
    };

    $scope.classificationSelectionChanged = function() {
        $scope.families.forEach(function(family) {
            var selectedClassifications = getSelectedLanguageClassifications(family);
            if (selectedClassifications.length == family.languages.length) family.languages.allSelected = true;
            else family.languages.allSelected = false;
            family.languages.forEach(function(language) {
                if (language.isSelected) {
                    if ($scope.languageClassifications.selected.map(function(lang) { return lang.id; }).indexOf(language.id) == -1) {
                        $scope.languageClassifications.selected.push(language);
                        $scope.languageClassifications.badgeValue += language.societies.length;
                    }
                } else {
                    if ($scope.languageClassifications.selected.map(function(lang) { return lang.id; }).indexOf(language.id) != -1) {
                       $scope.removeFromSearch(language, 'language');
                       
                    }
                }
            });
        });
    };

    $scope.doSearch = function() {
        $scope.search();
    };

}