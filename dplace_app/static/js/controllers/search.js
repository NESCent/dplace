function SearchCtrl($scope, $routeParams, LanguageClass) {
    $scope.families = LanguageClass.query({level: 1});
    $scope.subfamilies = [];
    $scope.subsubfamilies = [];

    // functions to update subfamilies when family changes
    $scope.setFamily = function(familyId) {
        $scope.subsubfamilies = [];
        $scope.subfamilies = LanguageClass.query({level:2, parent: familyId});
    };

    $scope.setSubfamily= function(subFamilyId) {
        $scope.subsubfamilies = LanguageClass.query({level:3, parent: subFamilyId});
    };

}