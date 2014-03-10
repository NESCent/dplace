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
            $scope.activateEnvironmental();
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
        trait.selectedCode = null;
        trait.codes = CodeDescription.query({variable: trait.selectedVariable.id });
    };

    // Environmental Data
    $scope.activateEnvironmental = function() {
        // This should be moved to a web service
        $scope.environmentalVariables = [
          { key: 'annual_mean_temperature', name: 'Annual Mean Temperature', units:'℃'},
          { key: 'annual_temperature_variance', name: 'Annual Temperature Variance', units:'℃'},
          { key: 'temperature_constancy', name: 'Temperature Constancy'},
          { key: 'temperature_contingency', name: 'Temperature Contingency'},
          { key: 'temperature_predictability', name: 'Temperature Predictability'},
          { key: 'annual_mean_precipitation', name: 'Annual Mean Precipitation', units:'mm'},
          { key: 'annual_precipitation_variance', name: 'Annual Precipitation Variance',},
          { key: 'precipitation_constancy', name: 'Precipitation Constancy'},
          { key: 'precipitation_contingency', name: 'Precipitation Contingency'},
          { key: 'precipitation_predictability', name: 'Precipitation Predictability'},
          { key: 'mean_growing_season_duration', name: 'Mean Growing Season Duration'},
          { key: 'net_primary_productivity', name: 'Net Primary Productivity'},
          { key: 'bird_diversity', name: 'Bird Diversity'},
          { key: 'mammal_diversity', name: 'Mammal Diversity'},
          { key: 'amphibian_diversity', name: 'Amphibian Diversity'},
          { key: 'plant_diversity', name: 'Plant Diversity'},
          { key: 'elevation', name: 'Elevation'},
          { key: 'slope', name: 'Slope'}
        ];
        $scope.environmentalFilters = [
            { key: 'inrange', name: 'between' },
            { key: 'lt', name: 'less than'},
            { key: 'gt', name: 'greater than'},
            { key: 'outrange', name: 'outside'},
        ];
        $scope.environmental = {
            selectedFilter: $scope.environmentalFilters[0]
        };
    };
}