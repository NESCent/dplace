function LanguageCtrl($scope, LanguageClass, LanguageClassification, FindSocieties) {

    /* Prototype model for UI */
    var levels = [
        {level: 1, name: 'Family',          tag: 'family'},
        {level: 2, name: 'Subfamily',       tag: 'subfamily'},
        {level: 3, name: 'Subsubfamily',    tag: 'subsubfamily'}
    ];

    var maxLevel = levels[levels.length - 1].level

    /* Model for binding */
    var languageFilter = angular.copy(levels);
    languageFilter.forEach(function (filterLevel) {
        filterLevel.selectedItem = undefined;
    });

    /* Populate language family for first level */
    var familyLevel = 1;
    languageFilter[0].items = LanguageClass.query({level: familyLevel});

    /* Iniitial setup */
    $scope.model.searchParams.language = {
        levels: levels,
        languageFilters: [languageFilter]
    };

    function levelToIndex(levelObject) {
        return levelObject.level - 1;
    }
    function indexToLevel(levelIndex) {
        return levels[levelIndex];
    }

    function selectedItemAtLevel(languageFilter,levelObject) {
        return languageFilter[levelToIndex(levelObject)].selectedItem;
    };

    function queryParameterForLevel(levelObject) {
        return 'class_' + levelObject.tag;
    }

    function updateClassifications(languageFilter) {
        var params = {};
        levels.forEach(function (levelObject) {
            var selectedItem = selectedItemAtLevel(languageFilter, levelObject);
            if(selectedItem) {
                var param = queryParameterForLevel(levelObject);
                params[param] = selectedItem.id;
            }
        });
        if(Object.keys(params).length == 0) {
            /* Nothing selected at any level */
            languageFilter.classifications = [];
        } else {
            languageFilter.classifications = LanguageClassification.query(params);
        }
    }

    function updateItems(languageFilter, parentObject, levelObject) {
        var index = levelToIndex(levelObject)
        languageFilter[index].items = LanguageClass.query({parent: parentObject.id, level: levelObject.level});
        languageFilter[index].selectedItem = undefined;
    }

    function clearItems(languageFilter, levelObject) {
        var index = levelToIndex(levelObject)
        languageFilter[index].items = [];
        languageFilter[index].selectedItem = undefined;
    }

    $scope.selectionChanged = function(languageFilter, levelObject) {
        var changedIndex = levelToIndex(levelObject);
        var parentObject = selectedItemAtLevel(languageFilter, levelObject);
        if(changedIndex + 1 < levels.length) {
            // Update the next level
            var childLevel = indexToLevel(changedIndex + 1)
            updateItems(languageFilter, parentObject, childLevel);
        }
        if(changedIndex + 2 < levels.length) {
            var childLevel = indexToLevel(changedIndex + 2)
            clearItems(languageFilter, childLevel);
        }
        updateClassifications(languageFilter);
    };

    function getSelectedLanguageClassifications(languageFilter) {
        return languageFilter.classifications.filter( function (classification) {
            return classification.isSelected;
        });
    }

    $scope.getLanguageQueryFilters = function() {
        var languageQueryFilters = [];
        $scope.model.searchParams.language.languageFilters.forEach(function(languageFilter) {
            var selectedClassifications = getSelectedLanguageClassifications(languageFilter);
            var languageIds = selectedClassifications.map(function (classification) { return classification.language.id; });
            languageQueryFilters.push({language_ids: languageIds});
        });
        return languageQueryFilters;
    };

    $scope.doSearch = function() {
        var filters = $scope.getLanguageQueryFilters();
        $scope.disableSearchButton()
        $scope.model.searchResults = FindSocieties.find({ language_filters: filters }, function() {
            $scope.enableSearchButton();
            $scope.switchToResults();
        });
    };

}