function ColorMapService() {

    //blue to red gradient for environmental variables
    function tempColor(index, min, max, id ) {
    if (id == 34 || id == 36) {
        hue = 30 + (((index - min) / (max - min)) * 88);
    } else if (id == 27){
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
        var lum = (((value-min)/(max-min))) * 78;
        lum = 100 - lum;
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
                
            for (var j = 0; j < society.environmental_values.length; j++) {
                variable = results.environmental_variables.filter(function(env_var) {
                    return env_var.id == society.environmental_values[j].variable;
                });
                if (variable.length > 0) {
                    var color = tempColor(society.environmental_values[0].value,  results.environmental_variables[0].min, results.environmental_variables[0].max, results.environmental_variables[0].id);
                    colors[society.society.id] = color;
                }    
            }
            
            for (var j = 0; j < society.variable_coded_values.length; j++) {
                if (society.variable_coded_values[j].code_description && (society.variable_coded_values[j].code_description.description.indexOf("Missing data") != -1))
                    colors[society.society.id] = 'hsl(0, 0%, 100%)';
                else if (society.bf_cont_var) {
                    var color = mapColorMonochrome(results.code_ids[society.variable_coded_values[j].variable].min, results.code_ids[society.variable_coded_values[j].variable].max, society.variable_coded_values[j].coded_value, 0);
                    colors[society.society.id] = color;
                } else {
                    var color = mapColor(society.variable_coded_values[j].coded_value, results.code_ids[society.variable_coded_values[j].variable].length);
                    colors[society.society.id] = color;
                }
            }
            
            if (society.language_family) {
                var color = mapColor(society.language_family, society.num_classifications);
                colors[society.society.id] = color;
            }
        }
        return colors;
    };
}
