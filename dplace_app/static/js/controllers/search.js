function SearchCtrl($scope, $routeParams, LanguageClass, FindSocieties) {
    $scope.selections = [];
    $scope.families = LanguageClass.query({level: 1});

    $scope.clearLanguages = function() {
        $scope.selections = [];
        $scope.families.forEach(function (family) {
           family.subfamilies = [];
            family.selected = false;
        });
    }

    $scope.updateSelection = function(obj) {
        if(obj.selected) {
            $scope.selections.push(obj);
        } else {
            var index = $scope.selections.indexOf(obj);
            if(index > -1) {
                $scope.selections.splice(index, 1);
            }
        }
    };

    $scope.updateFamily = function(family) {
        if(family.selected) {
            family.subfamilies = LanguageClass.query({level: 2, parent: family.id});
        } else {
            family.subfamilies = [];
        }
        $scope.updateSelection(family);
    };

    $scope.updateSubfamily = function(subfamily) {
        if(subfamily.selected) {
            subfamily.subsubfamilies = LanguageClass.query({level: 3, parent: subfamily.id});
        } else {
            subfamily.subsubfamilies = [];
        }
        $scope.updateSelection(subfamily);
    };

    // This should be in another controller
    $scope.getSocieties = function(selections) {
        var ids = selections.map(function (selection) { return selection.id});
        $scope.societies = FindSocieties.find({language_class_ids: ids})
    }

}