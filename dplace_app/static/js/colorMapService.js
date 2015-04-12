function ColorMapService() {
    function mapColor(index, count) {
        var hue = index * 240 / count;
        return 'hsl(' + hue + ',100%,50%)';
    }

    this.generateColorMap = function(societies, query) {
        var colors = {};
        if ('environmental_filters' in query) {
            var min_value = 0, max_value = 0;
            for (var i = 0; i < societies.length; i++) {
                if (societies[i].environmental_values[0].value < min_value) min_value = societies[i].environmental_values[0].value;
                else if (societies[i].environmental_values[0].value > max_value) max_value = societies[i].environmental_values[0].value;
            }
            var range = max_value - min_value;
            for (var i = 0; i < societies.length; i++) {
                var society = societies[i];
                var id = society.society.id;
                var value = society.environmental_values[0].value;
                var color = mapColor(value, range);
                colors[id] = color;
            }
        } else if ('variable_codes' in query) {
            for (var i = 0; i < societies.length; i++) {
                var society = societies[i];
                var id = society.society.id;
                if (society.variable_coded_values.length > 0) {
                  //  if (society.variable_coded_values[0].bf_code){  //CHECK THE USE OF [0] HERE
                    //    var value = society.variable_coded_values[0].bf_code; //NOT WORKING
                    //}
                   // else
                        var value = society.variable_coded_values[0].coded_value;
                    var count = query.variable_codes.length;
                    var color = mapColor(value, count);
                    colors[id] = color;
                    
                    if (society.variable_coded_values[0].code_description && society.variable_coded_values[0].code_description.description.indexOf("Missing data") != -1)
                        colors[id] = 'hsl(360, 100%, 100%)';
                }
            }
        }
        return colors;
    };
}
