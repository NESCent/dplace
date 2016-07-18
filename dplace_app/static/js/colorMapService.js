function ColorMapService() {
    //an array of colors for coded values
    this.colorMap = [
        'NaN',
        'rgb(228,26,28)',
        'rgb(69,117,180)',
        'rgb(77,146,33)',
        'rgb(152,78,163)',
        'rgb(255,127,0)',
        'rgb(255,255,51)',
        'rgb(166,86,40)',
        'rgb(247,129,191)',
        'rgb(153,153,153)',
        'rgb(0,68,27)',
        'rgb(171,217,233)',
        'rgb(73,0,106)',
        'rgb(174,1,126)',
        'rgb(179,222,105)',
        'rgb(8,48,107)',
        'rgb(255,255,153)',
        'rgb(82,82,82)',
        'rgb(0,0,0)',
        'rgb(103,1,13)'
    ];
    // converts hsl to rgb
    function hslToRgb(h, s, l) {
        if (h < 0) h += 360;
        if (h >= 360) h = h % 360;
        var r, g, b;
        var r1, g1, b1;
        chroma = (1 - Math.abs(2*l - 1)) * s;
        
        _h = h / 60;
        
        x = chroma*(1 - Math.abs(_h % 2 - 1));
        
        if (_h >= 0 && _h < 1) {
            r1 = chroma;
            g1 = x;
            b1 = 0;
        } else if (_h >= 1 && _h < 2) {
            r1 = x;
            g1 = chroma;
            b1 = 0;
        } else if (_h >= 2 && _h < 3) {
            r1 = 0;
            g1 = chroma;
            b1 = x;
        } else if (_h >= 3 && _h < 4) {
            r1 = 0;
            g1 = x;
            b1 = chroma;
        } else if (_h >= 4 && _h < 5) {
            r1 = x;
            g1 = 0;
            b1 = chroma;
        } else if (_h >= 5 && _h < 6) {
            r1 = chroma;
            g1 = 0;
            b1 = x;
        } else if (!h) {
            r1 = 0; g1 = 0; b1 = 0;
        } 
        m = l - (0.5 * chroma);
        rgb = [Math.round((r1 + m)*255), Math.round((g1 + m)*255), Math.round((b1 + m)*255)];
        return rgb;
    }

    //blue to red gradient for environmental variables
    this.tempColor = function(index, min, max, name) {
    if (name == "Monthly Mean Net Primary Production" || name == "Mean Growing Season NPP") {
        hue = 30 + (((index - min) / (max - min)) * 88);
    } else if (name == "Monthly Mean Precipitation"){
        color = this.mapColorMonochrome(min, max, index, 252);
        return color;
    }
    else {
        hue = 240 - (((index - min) / (max - min))*240);
    }
        rgb = hslToRgb(hue, 1, 0.5);
        return 'rgb('+rgb[0]+','+rgb[1]+','+rgb[2]+')';
    }

    //normal gradient
    this.mapColor = function(index, count) {  
        hue = (index / count)*240;
        rgb = hslToRgb(hue, 1, 0.5);
        return 'rgb('+rgb[0]+','+rgb[1]+','+rgb[2]+')';
    }
    
    this.mapColorMonochrome = function(min, max, value, color) {
        var lum = (((value-min)/(max-min))) * 78; lum = 100 - lum; 
        rgb = hslToRgb(color, 0.65, lum/100);
        return 'rgb('+rgb[0]+','+rgb[1]+','+rgb[2]+')';
    }
    
    this.generateRandomHue = function(value, codes, index, count) {
        hue = (index / count) * 300;
        lum = 85 - ((value / codes) * 90)
        rgb = hslToRgb(hue, 0.65, lum/100);
        return 'rgb('+rgb[0]+','+rgb[1]+','+rgb[2]+')';
    }

    this.generateColorMap = function(results) {
        var colors = {};
        if (results.geographic_regions.length > 0) {
            results.geographic_regions.sort(function(a,b) {
                if (a.region_nam.toLowerCase() < b.region_nam.toLowerCase()) return -1;
                else if (a.region_nam.toLowerCase() > b.region_nam.toLowerCase()) return 1;
                else return 0;
            })
        }   
        for (var i = 0; i < results.societies.length; i++) {
            var society = results.societies[i];
            if (society.society.region) {
                code = results.geographic_regions.map(function(a) { return a.tdwg_code; }).indexOf(society.society.region.tdwg_code);
                if (code != -1)
                    var color = this.mapColor(code, results.geographic_regions.length);
                else
                    var color = this.mapColor(society.society.region.tdwg_code, results.geographic_regions.length);
                colors[society.society.id] = color;
            }
            
            if (results.languages.length > 0 && society.environmental_values.length == 0 && society.variable_coded_values.length == 0) {        
                code = results.classifications.map(function(a) { return a.id; }).indexOf(society.society.language.family.id);
                if (code != -1)
                    var color = this.mapColor(code, results.classifications.length);
                else
                    var color = this.mapColor(society.society.language.family.id, results.classifications.length);
                colors[society.society.id] = color;
            }
            
            for (var j = 0; j < society.environmental_values.length; j++) {
                variable = results.environmental_variables.filter(function(env_var) {
                    return env_var.id == society.environmental_values[j].variable;
                });
                if (variable.length > 0) {
                    var color = this.tempColor(society.environmental_values[j].value,  variable[0].min, variable[0].max, variable[0].name);
                    colors[society.society.id] = color;
                }    
            }
            
            for (var j = 0; j < society.variable_coded_values.length; j++) {
                variable_description = results.variable_descriptions.filter(function(variable) {
                    return variable.variable.id == society.variable_coded_values[j].variable;
                });
                
                if (variable_description[0].variable.data_type.toUpperCase() == 'ORDINAL') {
                    // there are 5 ordinal variables in the database
                    var color = this.generateRandomHue(society.variable_coded_values[j].coded_value, variable_description[0].codes.length, variable_description[0].variable.id, 5);
                    colors[society.society.id] = color;
                } else if (variable_description[0].variable.data_type.toUpperCase() == 'CONTINUOUS') {
                    var color = this.mapColorMonochrome(variable_description[0].variable.min, variable_description[0].variable.max, society.variable_coded_values[j].coded_value, 0);
                    colors[society.society.id] = color;
                } else {
                    if (society.variable_coded_values[j].coded_value == 'NA') {
                        colors[society.society.id] = 'rgb(255,255,255)';
                    } else {
                        if (variable_description[0].variable.label == "EA094") { //this variable's codes range from 11-99, for some reason
                            for (var k = 0; k < variable_description[0].codes.length; k++) {
                                if (variable_description[0].codes[k].code == society.variable_coded_values[j].coded_value) {
                                    colors[society.society.id] = this.colorMap[k+1];
                                    break;
                                }
                            }
                        } else 
                            colors[society.society.id] = this.colorMap[parseInt(society.variable_coded_values[j].coded_value)];
                    }
                }
            }

        }
        return colors;
    };
}
