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
                    var value = society.variable_coded_values[0].coded_value;
                    var count = query.variable_codes.length;
                    var color = mapColor(value, count);
                    colors[id] = color;
                }
            }
        }
        return colors;
    };
}
