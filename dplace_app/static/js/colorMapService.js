function ColorMapService() {

    //blue to red gradient for environmental variables
    function tempColor(index, count, min, max ) {
        hue = 240 - (((index - min) / (max - min)) * 240);
        return 'hsl('+hue+',100%, 50%)';
    }

    //normal gradient
    function mapColor(index, count) {
        hue = 240 -  (index / count)*240;
        return 'hsl(' + hue + ',100%,50%)';
    }
    
    function mapColorMonochrome(min, max, value) {
        var lum = (value-min)/(max-min) * 95;
        return 'hsl(0, 65%,'+lum+'%)'; //RED hue - can be changed
    }

    this.generateColorMap = function(results) {
        var colors = {};
        for (var i = 0; i < results.societies.length; i++) {
            var society = results.societies[i];
                for (var j = 0; j < society.environmental_values.length; j++) {
                    variable = results.environmental_variables.filter(function(env_var) {
                        return env_var.id == society.environmental_values[j].variable;
                    });
                    if (variable.length > 0) {
                        var color = tempColor(society.environmental_values[0].value, results.environmental_variables[0].range, results.code_ids[results.environmental_variables[0].id].min, results.code_ids[results.environmental_variables[0].id].max);
                        colors[society.society.id] = color;
                    }    
                }
            
            for (var j = 0; j < society.variable_coded_values.length; j++) {
                if (society.variable_coded_values[j].code_description && (society.variable_coded_values[j].code_description.description.indexOf("Missing data") != -1))
                    colors[society.society.id] = 'hsl(0, 0%, 100%)';
                else if (society.bf_cont_var) {
                    var color = mapColorMonochrome(results.code_ids[society.variable_coded_values[j].variable].min, results.code_ids[society.variable_coded_values[j].variable].max, society.variable_coded_values[j].coded_value);
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
