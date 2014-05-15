function SocietiesCtrl($scope, $routeParams) {
    $scope.setActive('societies');
    $scope.resizeMap = function() {
        $scope.$broadcast('mapTabActivated');
    }
}
