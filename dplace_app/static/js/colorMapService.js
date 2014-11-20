function ColorMapService() {
    function mapColor(index, count) {
        var hue = index * 240 / count;
        return 'hsl(' + hue + ',100%,50%)';
    }

    this.generateColorMap = function(societies, query, var_id) {
        var colors = {};
        if ('environmental_filters' in query) {
        //not sure if this calculation should go here
        //since we can only search for one environmental value at a time, using environmental_values[0] works fine
            var extractedValues = societies.map(function(society) { return society.environmental_values[0].value; });
            var min_value = Math.min.apply(null, extractedValues);
            var max_value = Math.max.apply(null, extractedValues);
            var range = max_value - min_value;
            for (var i = 0; i < societies.length; i++) {
                var society = societies[i];
                var id = society.society.id;
                var value = society.environmental_values[0].value; 
                var color = mapColor(value, range);
                colors[id] = color;
            }
        } 
        
        if ('variable_codes' in query) {
            var numCodes = 0;
            for (var i = 0; i < query.variable_codes.length; i++) {
                if (query.variable_codes[i].variable == var_id) numCodes++;
            }
                        
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
