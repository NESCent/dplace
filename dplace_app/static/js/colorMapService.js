function ColorMapService() {
    function mapColor(index, count) {
        var hue = index * 240 / count;
        return 'hsl(' + hue + ',100%,50%)';
    }

    this.generateColorMap = function(societies, query, var_id) {
        console.log(societies);
        var colors = {};
        /*if ('environmental_filters' in query) {
            var min_value = 0, max_value = 0;
            for (var i = 0; i < societies.length; i++) {
                for (var e = 0; e < societies[i].environmental_values.length; e++) {
                    if (societies[i].environmental_values[e].variable != var_id)
                        continue;
                    else {
                        if (societies[i].environmental_values[e].value < min_value) min_value = societies[i].environmental_values[e].value;
                        else if (societies[i].environmental_values[e].value > max_value) max_value = societies[i].environmental_values[e].value;
                    
                    }
                }
                
            }
            console.log(min_value); console.log(max_value);
            var range = max_value - min_value;
            for (var i = 0; i < societies.length; i++) {
                var society = societies[i];
                var id = society.society.id;
                var value = society.environmental_values[0].value;
                var color = mapColor(value, range);
                colors[id] = color;
            }
        } else*/ if ('variable_codes' in query) {
            console.log(query);
            var numCodes = 0;
            for (var i = 0; i < query.variable_codes.length; i++) {
                if (query.variable_codes[i][0] && query.variable_codes[i][0].variable == var_id) numCodes++;
            
            }
            
            console.log(numCodes);
            
            for (var i = 0; i < societies.length; i++) {
                var society = societies[i];
                var id = society.society.id;
                for (var v = 0; v < society.variable_coded_values.length; v++) {
                    if (society.variable_coded_values[v].variable == var_id) {
                        var value = society.variable_coded_values[v].coded_value;
                        var count = query.variable_codes.length;
                        var color = mapColor(value, numCodes);
                        colors[id] = color;
                    } else {
                        continue;
                    }
                
                }
                }
            }
        
        return colors;
    };
}
