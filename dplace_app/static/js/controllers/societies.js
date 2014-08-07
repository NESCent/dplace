function SocietiesCtrl($scope, searchModelService) {
    $scope.results = searchModelService.getModel().getResults();
    $scope.setActive('societies');
    $scope.resizeMap = function() {
        $scope.$broadcast('mapTabActivated');
    };

    $scope.generateDownloadLinks = function() {
        $scope.csvDownloadLink = "#";
    };
}
