function ColorMapService() {

    //blue to red gradient for environmental variables
    function tempColor(index, min, max, name) {
    if (name == "Net Primary Production" || name == "Mean Growing Season NPP") {
        hue = 30 + (((index - min) / (max - min)) * 88);
    } else if (name == "Annual Mean Precipitation"){
        color = mapColorMonochrome(min, max, index, 252);
        return color;
    }
    else {
        hue = 240 - (((index - min) / (max - min))*240);
    }
        return 'hsl('+hue+',100%, 50%)';
    }

    //normal gradient
    function mapColor(index, count) {   
        hue = (index / count)*240;
        return 'hsl(' + hue + ',100%,50%)';
    }
    
    function mapColorMonochrome(min, max, value, color) {
        var lum = (((value-min)/(max-min))) * 78; lum = 100 - lum; 
        return 'hsl('+color+', 65%,'+lum+'%)'; 
    }

    this.generateColorMap = function(results) {
        var colors = {};
        for (var i = 0; i < results.societies.length; i++) {
            var society = results.societies[i];
            
            if (society.geographic_regions) {
                for (var j = 0; j < society.geographic_regions.length; j++) {
                    var color = mapColor(society.geographic_regions[0].tdwg_code, results.geographic_regions.length);
                    colors[society.society.id] = color;
                }
            }
            
            if (results.languages.length > 0 && society.environmental_values.length == 0 && society.variable_coded_values.length == 0) {
                    var color = mapColor(society.society.language.family.id, results.classifications.length);
                    colors[society.society.id] = color;
                
            }
            
            for (var j = 0; j < society.environmental_values.length; j++) {
                variable = results.environmental_variables.filter(function(env_var) {
                    return env_var.id == society.environmental_values[j].variable;
                });
                if (variable.length > 0) {
                    var color = tempColor(society.environmental_values[0].value,  results.environmental_variables[0].min, results.environmental_variables[0].max, results.environmental_variables[0].name);
                    colors[society.society.id] = color;
                }    
            }
            for (var j = 0; j < society.variable_coded_values.length; j++) {
                variable_description = results.variable_descriptions.filter(function(variable) {
                    return variable.variable.id == society.variable_coded_values[j].variable;
                });

                if (society.variable_coded_values[j].code_description && (society.variable_coded_values[j].code_description.description.indexOf("Missing data") != -1))
                    colors[society.society.id] = 'hsl(0, 0%, 100%)';
                else if (variable_description[0].variable.data_type.toUpperCase() == 'CONTINUOUS') {
                    var color = mapColorMonochrome(variable_description[0].variable.min, variable_description[0].variable.max, society.variable_coded_values[j].coded_value, 0);
                    colors[society.society.id] = color;
                } 
                else {
                    var color = mapColor(society.variable_coded_values[j].coded_value, variable_description[0].codes.length);
                    colors[society.society.id] = color;
                }
            }

        }
        return colors;
    };
}
