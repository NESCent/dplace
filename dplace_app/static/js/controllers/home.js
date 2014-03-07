function HomeCtrl($scope, Variable) {
    $scope.setActive('home');
    $scope.searchButtons = '';

    $scope.buttonChanged = function() {
        if($scope.searchButtons == 'geographic') {
            $scope.regions = ['America','Albania','Zimbabwe','North America'];
        } else if($scope.searchButtons == 'cultural') {
            $scope.variables = Variable.query();
        } else if($scope.searchButtons == 'environmental') {

        } else if($scope.searchButtons == 'langauge') {

        }
    }
}