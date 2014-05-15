angular.module('dplaceFilters', [])
    .filter('formatVariableCodeValues', function() {
        return function(values) {
            return values.map( function(code_value) {
                return code_value.code_description.description;
            }).join(',');
        };
    })
    .filter('formatEnvironmentalValues', function () {
        return function(values) {
            return values.map( function(environmental_value) {
                // Should include the variable
                return environmental_value.value;
            }).join(',');
        };
    })
    .filter('formatLanguage', function () {
        return function(values) {
            return values.map( function(language) {
                return language.name;
            }).join(',');
        };
    })
    .filter('formatGeographicRegion', function () {
        return function(values) {
            return values.map( function(region) {
                return region.region_nam;
            }).join(',');
        };
    });
