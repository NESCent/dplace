/*
 * This service wraps a singleton object that keeps track of user's
 * search UI state across controllers
 * @constructor
 */
function SearchModelService(VariableCategory, GeographicRegion, EnvironmentalCategory, LanguageFamily, DatasetSources, Language, FindSocieties, colorMapService) {
    this.model = new SearchModel(VariableCategory, GeographicRegion, EnvironmentalCategory, LanguageFamily, DatasetSources, Language);
    this.getModel = function() {
        return this.model;
    }
    
    this.updateSearchQuery = function(searchQuery) {
        this.getModel().query = {};
        for (var propertyName in searchQuery) {
            this.getModel().query[propertyName] = searchQuery[propertyName];
        }
    }
    
    this.getCodeIDs = function(results, query) {
        results.code_ids = {};
        if (query.l && !query.c && !query.e) {
            results.classifications = [];
            added = [];
            for (var i = 0; i < results.societies.length; i++) {
                if (results.societies[i].society.language) {
                    language_family = results.societies[i].society.language.family;
                    if (added.indexOf(language_family.id) == -1) {
                        results.classifications.push(language_family);
                        added.push(language_family.id);
                    }
                }
            }
            
            results.classifications.sort(function(a,b) {
                if (a.name < b.name) return -1;
                else if (a.name > b.name) return 1;
                else return 0;
            });
        }
            // console.log(results.variable_descriptions);

        for (var i = 0; i < results.variable_descriptions.length; i++) {
            if (results.variable_descriptions[i].variable.data_type.toUpperCase() == 'CONTINUOUS') {
                codes = query.c.filter(function(code) { 
                    try {
                        return parseInt(code.split('-')[0]) == results.variable_descriptions[i].variable.id; 
                    } catch(err) { 
                        return code == results.variable_descriptions[i].variable.id; 
                    }
                });
                var min;
                var max = 0;
                codes.forEach(function(c_var) {
                    if ((''+c_var).split('-').length == 1) return;
                    
                    if (!min) min = parseFloat(c_var.split('-')[1]);
                    else {
                        if (parseFloat(c_var.split('-')[1]) < min) min = parseFloat(c_var.split('-')[1]);
                    }
                    if (parseFloat(c_var.split('-')[2]) > max) max = parseFloat(c_var.split('-')[2]);
                });
                results.variable_descriptions[i].variable['min'] = min.toFixed(2);
                results.variable_descriptions[i].variable['max'] = max.toFixed(2);
                results.variable_descriptions[i].codes = codes;
            }
        }
        return results;
        
    };
    
    var calculateRange = function(results) {
        if (results.societies.length == 0) return results;

        societies = results.societies;         
        for (var i = 0; i < results.environmental_variables.length; i++) {
            extractedValues = societies.map(function(society) { 
                for (var j = 0; j < society.environmental_values.length; j++) {
                    if (society.environmental_values[j].variable == results.environmental_variables[i].id) {
                        if (society.environmental_values[j].value) return society.environmental_values[j].value;
                    }
                }
            });
            var min_value = null; var max_value = null;
           extractedValues.forEach(function(val) {
            if (!min_value) min_value = val;
            if (!max_value) max_value = val;
            
            if (val < min_value) min_value = val;
            if (val > max_value) max_value = val;
           });
           // console.log(min_value);
            var range = max_value - min_value;
            results.environmental_variables[i]['range'] = range;
            results.environmental_variables[i]['min'] = min_value.toFixed(4);
            results.environmental_variables[i]['max'] = max_value.toFixed(4);
        }
        return results;
    }
    
    this.assignColors = function(results) {
        results = calculateRange(results);
        var colorMap = colorMapService.generateColorMap(results);
        results.societies.forEach(function(container) {
            container.society.style = {'background-color': colorMap[container.society.id] };
        });
        
    }
    
    
    
}
        
        