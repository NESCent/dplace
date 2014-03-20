function EnvironmentalCtrl($scope) {
    // TODO: This should be moved to a web service and normalized
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
}