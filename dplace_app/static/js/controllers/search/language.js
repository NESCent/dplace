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
                    if (!(language.family.name in $scope.languageClassifications.selected)) {
                        $scope.languageClassifications.selected[language.family.name] = [];
                    }
                    if ($scope.languageClassifications.selected[language.family.name].map(function(lang) { return lang.id; }).indexOf(language.id) != -1) {
                        language.isSelected = true;
                    }
                });
            });
        }
    };

    function badgeValue() {
        var total = 0;
        for (var key in $scope.languageClassifications.selected) {
            for (var i = 0; i < $scope.languageClassifications.selected[key].length; i++) {
                total += $scope.languageClassifications.selected[key][i].societies.length;
            }
        }
        $scope.languageClassifications.badgeValue = total;
    };
        
    $scope.selectAllChanged = function(scheme) {
        if (scheme.languages.allSelected) {
            scheme.languages.forEach(function(language) {
                language.isSelected = true;
                if (!(language.family.name in $scope.languageClassifications.selected)) {
                        $scope.languageClassifications.selected[language.family.name] = [];
                    }
                if ($scope.languageClassifications.selected[language.family.name].map(function(lang) { return lang.id; }).indexOf(language.id) == -1) {
                    $scope.languageClassifications.selected[language.family.name].push(language);
                }
            });
        } else {
            scheme.languages.forEach(function(language) {
                language.isSelected = false;
                $scope.removeFromSearch(language, 'language');
            });
        }
        badgeValue();

    };
    
    function getSelectedLanguageClassifications(scheme) {
        return scheme.languages.filter( function (classification) {
            return classification.isSelected;
        });
    };

    var classificationSelectionChangedFunc = $scope.classificationSelectionChanged = function() {
        $scope.families.forEach(function(family) {
            var selectedClassifications = getSelectedLanguageClassifications(family);
            if (selectedClassifications.length == family.languages.length) family.languages.allSelected = true;
            else family.languages.allSelected = false;
            family.languages.forEach(function(language) {
                if (language.isSelected) {
                    if (!(language.family.name in $scope.languageClassifications.selected)) {
                        $scope.languageClassifications.selected[language.family.name] = [];
                    }
                    if ($scope.languageClassifications.selected[language.family.name].map(function(lang) { return lang.id; }).indexOf(language.id) == -1) {
                        $scope.languageClassifications.selected[language.family.name].push(language);
                        badgeValue();
                    }
                } else {
                    if (!(language.family.name in $scope.languageClassifications.selected)) {
                        return;
                    }
                    if ($scope.languageClassifications.selected[language.family.name].map(function(lang) { return lang.id; }).indexOf(language.id) != -1) {
                       $scope.removeFromSearch(language, 'language');
                    }
                }
            });
        });
    };

    // classificationSelectionChanged is broadcasted if user remove language criterion
    // from the show search criteria panel - mainly to sync 'Select all' checkbox
    $scope.$on('classificationSelectionChanged', classificationSelectionChangedFunc);

    $scope.doSearch = function() {
        $scope.search();
    };

}