function LanguageCtrl($scope, searchModelService, LanguageClass, LanguageClassification) {
	var linkModel = function() {
        // Get a reference to the language classifications from the model
        $scope.languageClassifications = searchModelService.getModel().getLanguageClassifications();
		selected = [];
	};
    $scope.$on('searchModelReset', linkModel); // When model is reset, update our model
    linkModel();

    var levels = $scope.languageClassifications.levels;
	var selected = [];

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
		if (languageFilter.classifications.id.isSelected) {	
			languageFilter.classifications.forEach(function(classification) {
			classification.isSelected = true; 
			selected.push(classification);
			$scope.languageClassifications.badgeValue++;
			
			});
	
		} else {
			angular.forEach(languageFilter.classifications, function(classification){classification.isSelected = false; $scope.languageClassifications.badgeValue--;});
		}
		//alert(languageFilter.classifications.id);
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
            var languageIds = selectedClassifications.map(function (classification) { return classification.language.id; });
            //languageQueryFilters.push({language_ids: languageIds});
			selectedClassifications.forEach(function(f) {
				selected.push(f);
			});
	   });
        return languageQueryFilters;
    };
	
    $scope.classificationSelectionChanged = function(classification) {
        // Since the selections are stored deep in the model, this is greatly simplified by +1 / -1
        // get the currently selected languages and add them to the "selected" array
		currentSelection = $scope.getLanguageQueryFilters();
		currentSelection.forEach(function(c) {
			if (selected.indexOf(c) == -1) {
				selected.push(c);
			}
		});

        if(classification.isSelected) {
            $scope.languageClassifications.badgeValue++;
        } else {
            $scope.languageClassifications.badgeValue--;
        }
    };

    $scope.doSearch = function() {
	//the selected array contains all languages that were selected (even if they were then unselected)
	//so we filter the selected array so we only search for currently selected languages
		var filters = selected.filter(function(classification) { return classification.isSelected; }).map(function(c) { return {language_ids:[c.language.id]}; });
	  // var filters = $scope.getLanguageQueryFilters();
        $scope.updateSearchQuery({ language_filters: filters });
        $scope.searchSocieties();
    };

}