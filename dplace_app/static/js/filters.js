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
    .filter('formatVariables', function() {
        return function(selected, selectedVariable) {
            return selected.filter(function(code) { return code.variable == selectedVariable ;});
        };
    })
    .filter('colorNode', ['colorMapService', function(colorMapService) {
        return function(value, codes) {
            if (codes.societies) {
                if (codes.classifications) {
                    rgb = colorMapService.mapColor(value, codes.classifications.length);
                    return rgb;
                }
                if (codes.geographic_regions.length > 0) {
                    rgb = colorMapService.mapColor(value, codes.geographic_regions.length);
                    return rgb;
                } 
            }
            
            if (codes.type == 'environmental') {
                min = Math.min.apply(null,codes.codes.map(function(c) { return c.id; }));
                max = Math.max.apply(null,codes.codes.map(function(c) { return c.id; }));
                rgb = colorMapService.tempColor(value, min, max, '');
                return rgb;
            }
            
        
            var missingData = false;
            var missingDataValue;
            for (var i = 0; i < codes.codes.length; i++) {
                if (codes.codes[i].description && codes.codes[i].description.indexOf("Missing data") != -1) {
                    missingData = true;
                    missingDataValue = codes.codes[i].code;
                    break;
                }
            }
            if (missingData && value == missingDataValue) return 'rgb(255, 255, 255)';
            else {
                if (codes.variable.data_type.toUpperCase() == 'ORDINAL') {
                    rgb = colorMapService.generateRandomHue(value, codes.codes.length,codes.variable.id,5);
                } else {
                    if (codes.variable.label == "EA094") {
                        for (var k = 0; k < codes.codes.length; k++) {
                            if (codes.codes[k].code == value) {
                                rgb = colorMapService.colorMap[k+1];
                                break;
                            }
                            
                        }
                    } else 
                        rgb = colorMapService.colorMap[parseInt(value)];
                }
                return rgb;
            }
        }
    }])
    .filter('numValues', function() {
        return function(values, variable_id) {
            return values.filter(function(code_value) {
                if (code_value.code_description && (variable_id == code_value.code_description.variable)) return code_value;
                else if (variable_id == code_value.variable) return code_value;
            }).length - 1;
        };
    })
    .filter('formatVariableCodeValues', function() {
        return function(values, variable_id) {
            codes = values.filter( function(code_value) {   
               if (code_value.code_description && (variable_id.id == code_value.code_description.variable)) return code_value;
                else if (variable_id.id == code_value.variable) return code_value;
            });
            return [codes[0]];
        };
    })
    .filter('formatValue', function() {
        return function(value) {
            if (!value) return '';
            if (value.code_description) return value.code_description.description;
            else return value.coded_value;
        };
    })
    .filter('formatEnvironmentalValues', function () {
        return function(values, variable_id) {
            codes = values.filter( function(environmental_value) {
                if (environmental_value.variable == variable_id) {
                    // TODO why is called this filter twice?
                    // First environmental_value.value is a float un-toFixed(4)
                    // then as string whereby the value is already toFixed(4)
                    try{
                        environmental_value.coded_value_float = environmental_value.coded_value_float.toFixed(4)
                    }catch(e){}
                    return environmental_value;
                }
            });
            return [codes[0]];
        };
    })
    .filter('formatValueSources', function() {
        return function(value) {
            if (!value) return '';
            return value.references.map(function(reference) {
                return reference.author + ' (' + reference.year + ')';
            }).join('; ');
        };
    })
    .filter('formatComment', function() {
        return function(code_value) {
            if (!code_value) return '';
            str = '';
            if (code_value.focal_year != 'NA') str = 'Focal Year: ' + code_value.focal_year;
            if (code_value.comment) str += '\n' + code_value.comment;
            return str;
        };
    })
    .filter('formatLanguage', function () {
        return function(language) {
            if (language == null){
                return '';
            } else {
                return language.family.name;
            }
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
        return function(region) {
            if (region == null) {
                return '';
            } else {
                return region.region_nam;
            }
        };
    });
