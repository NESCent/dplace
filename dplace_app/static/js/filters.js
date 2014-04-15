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
    .filter('formatLanguageClassifications', function () {
        return function(values) {
            return values.map( function(classification) {
                return classification.name;
            }).join(',');
        };
    });
