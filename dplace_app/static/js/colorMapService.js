function ColorMapService() {
    function mapColor(index, count) {
        var hue = index * 240 / count;
        return 'hsl(' + hue + ',100%,50%)';
    }

    this.generateColorMap = function(societies, query) {
        var colors = {};
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
        return colors;
    
    };
    
    
    /*this.generateColorMap = function(keys) {
        var colors = {};
        for(var i=0;i<keys.length;i++) {
            var color = mapColor(i, keys.length);
            colors[keys[i]] = color;
        }
        return colors;
    };*/
}
