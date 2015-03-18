function ColorMapService() {
    function mapColor(index, count) {
        var hue = index * 240 / count;
        return 'hsl(' + hue + ',100%,50%)';
    }

    this.generateColorMap = function(results, query) {
        var colors = {};
        
        for (var i = 0; i < results.societies.length; i++) {
            var society = results.societies[i];
            for (var j = 0; j < society.environmental_values.length; j++) {
                variable = results.environmental_variables.filter(function(env_var) {
                    return env_var.id == society.environmental_values[j].variable;
                });
                if (variable.length > 0) {
                    var color = mapColor(society.environmental_values[0].value, variable[0].range);
                    colors[society.society.id] = color;
                }
                    
            }
        
        }
        
        //for (var i = 0; i < societies.length; i++) {
          //  var color = mapColor(societies[i].environmental_values[0].value, 40);
            //colors[societies[i].society.id] = color;
        //}
        
        //if ('variable_codes' in query) {
          //  for (var i = 0; i < societies.length; i++) {
            //    var society = societies[i];
              //  var id = society.society.id;
                //if (society.variable_coded_values.length > 0) {
                  //  var value = society.variable_coded_values[0].coded_value;
                    //var count = query.variable_codes.length;
                    //var color = mapColor(value, count);
                    //colors[id] = color;
                //}
            //}
        //}
        return colors;
    };
}
