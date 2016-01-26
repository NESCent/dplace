function LanguageCtrl($scope, searchModelService, LanguageClass, LanguageClassification) {
    var linkModel = function() {
        // Get a reference to the language classifications from the model
        $scope.languageClassifications = searchModelService.getModel().getLanguageClassifications();
    };
    $scope.$on('searchModelReset', linkModel); // When model is reset, update our model
    linkModel();

    var levels = $scope.languageClassifications.levels;

    function levelToIndex(levelObject) {
        return levelObject.level - 1;
    }
    function indexToLevel(levelIndex) {
        return levels[levelIndex];
    }

    function selectedItemAtLevel(languageFilter,levelObject) {
        return languageFilter[levelToIndex(levelObject)].selectedItem;
    }

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
        
        //make select all the default
        languageFilter.classifications.isSelected = true;
        already_selected = $scope.languageClassifications.selected.map(function(x) { return x.id; });
        languageFilter.classifications.$promise.then(function(result) {
            result.forEach(function(classification) {
                classification.isSelected = true;
                if (already_selected.indexOf(classification.id) == -1) {
                    $scope.languageClassifications.selected.push(classification);
                }
            });
            $scope.languageClassifications.badgeValue = $scope.languageClassifications.selected.filter(function(lang) { return lang.isSelected; }).length;
        });
    }

    function updateItems(languageFilter, parentObject, levelObject) {
        var index = levelToIndex(levelObject);
        languageFilter[index].items = LanguageClass.query({parent: parentObject.id, level: levelObject.level});
        languageFilter[index].selectedItem = undefined;
    }

    function clearItems(languageFilter, levelObject) {
        var index = levelToIndex(levelObject);
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

	$scope.selectAllChanged = function(languageFilter) {
		if (languageFilter.classifications.isSelected) {
			languageFilter.classifications.forEach(function(classification) {
			    classification.isSelected = true;
                if ($scope.languageClassifications.selected.indexOf(classification) == -1) {
                    $scope.languageClassifications.selected.push(classification);
                }
            });
		} else {
			languageFilter.classifications.forEach(function(classification){ 
                classification.isSelected = false; 
            });
        }
        $scope.languageClassifications.selected = $scope.languageClassifications.selected.filter(function(x) { return x.isSelected; });
        $scope.languageClassifications.badgeValue = $scope.languageClassifications.selected.length;

	};
    
    function getSelectedLanguageClassifications(languageFilter) {
        return languageFilter.classifications.filter( function (classification) {
            return classification.isSelected;
        });
    }

    $scope.getLanguageQueryFilters = function() {
        var languageQueryFilters = [];
        $scope.languageClassifications.languageFilters.forEach(function(languageFilter) {
            var selectedClassifications = getSelectedLanguageClassifications(languageFilter);
            if (selectedClassifications.length == languageFilter.classifications.length) languageFilter.classifications.isSelected = true;
            else languageFilter.classifications.isSelected = false;
            selectedClassifications.forEach(function(f) {
                if ($scope.languageClassifications.selected.indexOf(f) == -1)
                    $scope.languageClassifications.selected.push(f);
            });
	   });
        return languageQueryFilters;
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