angular.module('dplaceFilters', [])
    .filter('transformG', function() {
        return function(index) {
            if (index == 0) return 'translate(0,10)'
            else {
                j = (index * 25) + 10;
                return 'translate(0,'+j+')';
            }
        }
    })    
    .filter('colorNode', function() {
        return function(value, codes) {
            var missingData = false;
            var missingDataValue;
            for (var i = 0; i < codes.length; i++) {
                if (codes[i].description && codes[i].description.indexOf("Missing data") != -1) {
                    missingData = true;
                    missingDataValue = codes[i].code;
                    break;
                }
            }
            if (missingData && value == missingDataValue) return 'hsl(0, 0%, 100%)';
            else {
               var hue = value * 240 / codes.length;
            }
            return 'hsl('+hue+',100%, 50%)';
            
        }
    })
    .filter('formatVariableCodeValues', function() {
        return function(values, variable_id) {
            return values.map( function(code_value) {   
                if (code_value.code_description && (variable_id == code_value.code_description.variable)) return code_value.code_description.description;
                else if (variable_id == code_value.variable) return code_value.coded_value;
                else return ''
            }).join('');
        };
    })
    .filter('formatValueSources', function() {
        return function(values, variable_id) {
            return values.map( function(code_value) {
                if (code_value.code_description && (variable_id == code_value.code_description.variable)) {
                    return code_value.references.map(function(reference) {
                        return reference.author + ' (' + reference.year + ')';
                    });
                }
                else if (variable_id == code_value.variable) {
                    return code_value.references.map(function(reference) {
                        return reference.author + ' (' + reference.year + ')';
                    });
                }
            }).join('')
        };
    })
    .filter('formatComment', function() {
        return function(values, variable_id) {
            str = '';
            return values.map( function(code_value) {
                if (code_value.code_description && (variable_id == code_value.code_description.variable)) {
                    if (code_value.focal_year != 'NA')
                        str = 'Focal Year: ' + code_value.focal_year;
                    if (code_value.comment) str += '\n' + code_value.comment;
                    return str;
                }
                else if (variable_id == code_value.variable) {
                    if (code_value.focal_year != 'NA') str = 'Focal Year: ' + code_value.focal_year;
                    if (code_value.comment) str += '\n' + code_value.comment;
                    return str;
                } else return ''

            }).join('')
        };
    })
    .filter('formatEnvironmentalValues', function () {
        return function(values) {
            return values.map( function(environmental_value) {
                    return environmental_value.value.toFixed(4);
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
    .filter('formatLanguageTrees', function () {
        return function(values) {
            if (angular.isArray(values)) {
                return values.map(function (language) {
                    return language.name;
                }).join("\n");
            } else {
                return '';
            }
        };
    })
    .filter('formatLanguageName', function () {
        return function(value) {
            if (value === null) {
                return '';
            } else {
                return value.name;
            }
        };
    })
    .filter('countOrBlank', function () {
        return function(value) {
            if (angular.isUndefined(value) || value.length === 0) {
                return '';
            } else {
                return value.length;
            }
        };
    })
    .filter('formatGeographicRegion', function () {
        return function(values) {
            return values.map( function(region) {
                return region.region_nam;
            }).join(',');
        };
    });
