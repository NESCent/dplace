function SearchCtrl($scope, $routeParams, LanguageClass, EAVariable, EACodeDescription, FindSocieties) {
    $scope.languageSelections = [];
    $scope.eaVariableSelections= [];

    $scope.families = LanguageClass.query({level: 1});
    $scope.eaVariables = EAVariable.query();

    $scope.clearLanguages = function() {
        $scope.languageSelections = [];
        $scope.families.forEach(function (family) {
            family.forEach(function (subfamily) {
                subfamily.subsubfamilies = [];
                subfamily.selected = false;
            });
           family.subfamilies = [];
           family.selected = false;
        });
    }

    $scope.updateSelection = function(object, array) {
        if(object.selected) {
            array.push(object);
        } else {
            var index = array.indexOf(object);
            if(index > -1) {
                array.splice(index, 1);
            }
        }
    }

    $scope.updateLanguageSelection = function(obj) {
        $scope.updateSelection(obj, $scope.languageSelections);
    };

    $scope.updateFamily = function(family) {
        if(family.selected) {
            family.subfamilies = LanguageClass.query({level: 2, parent: family.id});
        } else {
            family.subfamilies = [];
        }
        $scope.updateLanguageSelection(family);
    };

    $scope.updateSubfamily = function(subfamily) {
        if(subfamily.selected) {
            subfamily.subsubfamilies = LanguageClass.query({level: 3, parent: subfamily.id});
        } else {
            subfamily.subsubfamilies = [];
        }
        $scope.updateLanguageSelection(subfamily);
    };

    $scope.updateSubsubfamily = function(subsubfamily) {
        $scope.updateLanguageSelection(subsubfamily);
    };

    $scope.updateEAVariableSelection = function(obj) {
        $scope.updateSelection(obj, $scope.eaVariableSelections);
    }

    $scope.updateEAVariable = function(eaVariable) {
        if(eaVariable.expanded) {
            eaVariable.codes = EACodeDescription.query({variable: eaVariable.id});
        } else {
            eaVariable.codes = [];
        }
    };

    $scope.updateCode = function(code) {
        $scope.updateEAVariableSelection(code);
    };

    $scope.getSocieties = function() {
        var mapFunction = function (selection) { return selection.id };
        var language_ids = $scope.languageSelections.map(mapFunction);
        var code_ids = $scope.eaVariableSelections.map(mapFunction);
        $scope.societies = FindSocieties.find({
            language_class_ids: language_ids,
            ea_variable_codes: code_ids
        });
    }
}