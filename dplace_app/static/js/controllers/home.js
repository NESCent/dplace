function HomeCtrl($scope, Variable, CodeDescription) {
    $scope.setActive('home');
    $scope.selectedButton= '';
    $scope.buttons = [
        {value:'geographic', name:'Geographic'},
        {value:'cultural', name:'Cultural Traits'},
        {value:'environmental', name:'Environmental'},
        {value:'language', name:'Language'}
    ];

    $scope.buttonChanged = function(selectedButton) {
        $scope.selectedButton = selectedButton;
        if(selectedButton == 'geographic') {
            $scope.activateGeographic();
        } else if(selectedButton == 'cultural') {
            $scope.activateCultural();
        } else if(selectedButton == 'environmental') {

        } else if(selectedButton == 'langauge') {

        }
    };

    // Geographic
    $scope.activateGeographic = function() {
        $scope.regions = ['America','Albania','Zimbabwe','North America'];
    };

    // Cultural Traits
    $scope.activateCultural = function() {
        $scope.traits = [{variables: Variable.query()}];
    };
    $scope.traitChanged = function(trait) {
        trait.selectedCode = undefined;
        trait.codes = CodeDescription.query({variable: trait.selectedVariableId });
    }

}