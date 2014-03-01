function SearchCtrl($scope, $routeParams, LanguageClass, EAVariable, EACodeDescription, FindSocieties) {
    $scope.languageSelections = [];
    $scope.eaVariableSelections = [];

    $scope.families = LanguageClass.query({level: 1});
    $scope.eaVariables = EAVariable.query();

    $scope.clearAll = function() {
        $scope.clearLanguageSelections();
        $scope.clearEaVariableSelections();
    };

    $scope.clearLanguageSelections = function() {
        $scope.families.forEach(function (family) {
            family.isSelected = false;
            $scope.updateFamilySelected(family);
        });
        $scope.languageSelections = [];
    };

    $scope.clearEaVariableSelections = function () {
        $scope.eaVariables.forEach(function (eaVariable) {
            if(eaVariable.codes) {
                eaVariable.codes.forEach(function (code) {
                    code.isSelected = false;
                });
            }
        });
        $scope.eaVariableSelections = [];
    }
    // Families can be collapsed and can be selected
    // Changing collapse should load subfamilies if not present, and check them by default
    // changing selected should just update selections.
    // unchecking a selection should clear out its
    // clearing subfamilies should find selections first and clear them

    $scope.toggleShowChildren = function(family) {
        family.isShowingChildren = !family.isShowingChildren;
        if(family.isShowingChildren && family.children == undefined) {
            // load subfamilies
            family.children = LanguageClass.query({
                level: family.level + 1,
                parent: family.id
            }, function() {
                family.children.forEach( function(child) {
                    child.isSelected = family.isSelected;
                });
            });
        }
    };

    // When checking or unchecking a checkbox, cascade the changes to the children if they have been loaded
    $scope.updateFamilySelected = function(family, parent, grandparent) {
        if(family.children) {
            family.children.forEach(function(child) {
                child.isSelected = family.isSelected;
                // Recurse!
                $scope.updateFamilySelected(child);
            });
        }
        if(parent) {
            $scope.unselectIfIncomplete(parent);
            if(grandparent) {
                $scope.unselectIfIncomplete(grandparent);
            }
        }
    };

    // EA Methods

    $scope.toggleShowEACodes = function(eaVariable) {
        eaVariable.isShowingCodes = !eaVariable.isShowingCodes;
        if(eaVariable.isShowingCodes && eaVariable.codes == undefined) {
            // load EA Variable codes
            eaVariable.codes =  EACodeDescription.query({variable: eaVariable.id});
        }
    };

    $scope.updateCodeSelected = function(code) {
        if(code.isSelected) {
            $scope.eaVariableSelections.push(code);
        } else {
            $scope.eaVariableSelections.splice($scope.eaVariableSelections.indexOf(code));
        }
    }

    // start at the root
    $scope.unselectIfIncomplete = function(family) {
        if(family.children) {
            var numberOfChildren = family.children.length;
            var numberOfSelectedChildren = family.children.map(function(child) {
                if(child.isSelected) {
                    return 1;
                } else {
                    return 0;
                }
            }).reduce(function(previous,current) {
                    return previous + current;
            });
            if(numberOfSelectedChildren != numberOfChildren) {
                // not all selected
                family.isSelected = false;
            }
        }
    };

    $scope.updateSelection = function(object, array) {
        if(object.isSelected) {
            array.push(object);
        }
        if(object.children) {
            object.children.forEach( function(child) {
                $scope.updateSelection(child, array);
            });
        }
    };

    // Clears out the language selections and re-populates it based on current state
    $scope.updateFamilySelections = function() {
        // get all the selected families
        $scope.languageSelections = [];
        $scope.families.forEach(function (family) {
            $scope.updateSelection(family, $scope.languageSelections);
        });
    };

    $scope.updateEaCodeSelections = function() {
        $scope.eaVariableSelections = [];
        $scope.eaVariables.forEach(function(eaVariable) {
            if(eaVariable.codes) {
                eaVariable.codes.forEach(function(code) {
                    $scope.updateSelection(code, $scope.eaVariableSelections);
                });
            }
        });
    }

    $scope.getSocieties = function() {
        // refresh the languageSelections array
        $scope.updateFamilySelections();
        $scope.updateEaCodeSelections();
        var mapFunction = function (selection) { return selection.id };
        var language_ids = $scope.languageSelections.map(mapFunction);
        var code_ids = $scope.eaVariableSelections.map(mapFunction);
        $scope.societies = FindSocieties.find({
            language_class_ids: language_ids,
            ea_variable_codes: code_ids
        });
    };
}