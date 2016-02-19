/* Tests ColorMapService, which has functions:
    tempColor(index, min, max, name)
    mapColor(index, count)
    mapColorMonochrome(min, max, value, color)
    generateColorMap(results)
    
*/

describe('Color Map Service Testing', function() {
    var mockColorService, mockResults, society, society2, society3;
    
    beforeEach(function() {
        module('dplaceServices');
    });
    
    beforeEach(inject(function(colorMapService) {
        mockColorService = colorMapService;
        mockResults = {
            'societies': [],
            'environmental_variables': [],
            'geographic_regions': [],
            'languages': [],
            'variable_descriptions': []
        }; //used to store the mock results for the test
        
        society = {
            'society': { 'id': 11264 }, 
            'environmental_values': [],
            'geographic_regions': [],
            'variable_coded_values': []
        };
        
        society2 = {
            'society': { 'id': 16 }, 
            'environmental_values': [],
            'geographic_regions': [],
            'variable_coded_values': []
        };
        
        society3 = {
            'society': { 'id': 46 }, 
            'environmental_values': [],
            'geographic_regions': [],
            'variable_coded_values': []
        };
        
    }));
    
    it('geographic region color map', function() {
        
        var geographic_region = {
            'continent': "AFRICA",
            'count': 71,
            'id': 7398,
            'level_2_re': 24,
            'region_nam': "Northeastern Africa",
            'tdwg_code': 24
        };

       society.geographic_regions.push(geographic_region);
       mockResults.geographic_regions.push(geographic_region);
        mockResults.societies.push(society);
        var map = mockColorService.generateColorMap(mockResults);
        expect(map[society.society.id]).toBe('rgb(255,0,0)');
    });
    
    it('environmental color map', function() {
        var environmental_variable = {
            'id': 317,
            'max': 29,
            'min': -17,
            'name': "Temperature",
            'range': 46
        };
        
        var environmental_value = {
            'value': 18.25,
            'variable': 317,
        };
        mockResults.environmental_variables.push(environmental_variable);
        society.environmental_values.push(environmental_value);
        mockResults.societies.push(society);
        var map = mockColorService.generateColorMap(mockResults);
        expect(map[society.society.id]).toBe('rgb(255,238,0)');
    
    });
    
    it('cultural variable map', function() {
        var variable_description = {
            'codes': [
                {'code': 'NA', 'description': 'Missing data'},
                {'code': '1', 'description': 'Absence of slavery'},
                {'code': '2', 'description': 'Incipient or nonhereditary slavery, i.e., where slave status is temporary and not transmitted to the children of slaves'},
                {'code': '3', 'description': "Slavery reported but not identified as hereditary or nonhereditary"},
                {'code': '4', 'description': "Hereditary slavery present and of at least modest social significance"},
            ],
            'variable': {
                'id': 1628,
                'data_type': 'Categorical'
            }
        };
        
        var coded_value = {
            'coded_value': '1',
            'variable': 1628,
            'code_description': variable_description.codes[1]
        };
        
        var coded_value_na = { //check missing data
            'coded_value': 'NA',
            'variable': 1628,
            'code_description': variable_description.codes[0]
        };
        
        mockResults.variable_descriptions.push(variable_description);
        society.variable_coded_values.push(coded_value);
        society2.variable_coded_values.push(coded_value_na);
        mockResults.societies.push(society);
        mockResults.societies.push(society2);
        var map = mockColorService.generateColorMap(mockResults);
        expect(map[society.society.id]).toEqual('rgb(228,26,28)');
        expect(map[society2.society.id]).toEqual('rgb(255,255,255)'); 
    });
    
    it('should use monochromatic scale for ordinal variables', function() {
        var variable_description = {
            'codes': [
                {'code': 'NA', 'description': '0-25%'},
                {'code': '1', 'description': '26-50%'},
                {'code': '2', 'description': '51-75%'},
                {'code': '3', 'description': '76-100%'}
            ],
            'variable': {
                'id': 1934,
                'data_type': 'Ordinal'
            }
        };
        
        var coded_value = {
            'coded_value': '1',
            'variable': 1934,
            'code_description': variable_description.codes[1]
        };
        
        mockResults.variable_descriptions.push(variable_description);
        society.variable_coded_values.push(coded_value);
        mockResults.societies.push(society);
        var map = mockColorService.generateColorMap(mockResults);
        //check to make sure it isn't assigning the color from colorMap
        expect(map[society.society.id]).not.toEqual('rgb(228,26,28)'); 
        expect(map[society.society.id]).toEqual('rgb(97,222,97)');
    
    });
    
    it('language family map', function() {
        var language1 = {
            'family': {
                'id': 11,
                'language_count': 11,
                'name': 'Family 1',
                'scheme': 'G'
            },
            'glotto_code': "abcd1234",
            'id': 1100,
            'iso_code': "abc",
            'name': "ABCD"
         
        };
        var language2 = {
            'family': {
                'id': 58,
                'name': 'Austronesian',
                'scheme': 'G'
            },
            'glotto_code': "efgh1234",
            'id': 1110,
            'iso_code': "efg",
            'name': "SFGH"
         
        };
        
        var language3 = {
            'family': {
                'id': 58,
                'name': 'Austronesian',
                'scheme': 'G'
            },
            'glotto_code': "lmno1234",
            'id': 1110,
            'iso_code': "lmn",
            'name': "LMNO"
         
        };

        society.society.language = language1;
        society2.society.language = language2;
        society3.society.language = language3;
        mockResults.societies.push(society);
        
        //societies 2 and 3 have the same language family
        mockResults.societies.push(society2);
        mockResults.societies.push(society3);
        mockResults.languages = mockResults.languages.concat([language1, language2, language3]);
        mockResults.classifications = [
            {
                'id': 11,
                'name': 'Family 1',
                'scheme': 'G'
            },
            {
                'id': 58,
                'name': "Austronesian",
                'scheme': 'G'
            }
        ];
        
        var map = mockColorService.generateColorMap(mockResults);
       expect(map[society.society.id]).toBe("rgb(0,0,255)");
       expect(map[society2.society.id]).toBe("rgb(0,255,0)");
       expect(map[society2.society.id]).toEqual(map[society3.society.id]);
    });
    
    it('geographic regions and languages color map', function() {
        //when searching by geographic region and language family, marker should be colored according to language family
        var geographic_region = {
            'continent': "AFRICA",
            'count': 71,
            'id': 7398,
            'level_2_re': 24,
            'region_nam': "Northeastern Africa",
            'tdwg_code': 24
        };
        var language1 = {
            'family': {
                'id': 11,
                'language_count': 11,
                'name': 'Family 1',
                'scheme': 'G'
            },
            'glotto_code': "abcd1234",
            'id': 1100,
            'iso_code': "abc",
            'name': "ABCD"
         
        };
       society.geographic_regions.push(geographic_region);
       mockResults.geographic_regions.push(geographic_region);
       society.society.language = language1;
       mockResults.languages.push(language1);
       mockResults.classifications = [
            {
                'id': 11,
                'name': 'Family 1',
                'scheme': 'G'
            },
             {
                'id': 58,
                'name': "Austronesian",
                'scheme': 'G'
            }
        ];
     mockResults.societies.push(society);
    var map = mockColorService.generateColorMap(mockResults);
    expect(map[society.society.id]).toEqual("rgb(0,0,255)")
    });
    
    it('geographic region and cultural variable', function() {
        //should color by cultural variable 
        var geographic_region = {
            'continent': "AFRICA",
            'count': 71,
            'id': 7398,
            'level_2_re': 24,
            'region_nam': "Northeastern Africa",
            'tdwg_code': 24
        };
        
        var variable_description = {
            'codes': [
                {'code': 'NA', 'description': 'Missing data'},
                {'code': '1', 'description': 'Absence of slavery'},
                {'code': '2', 'description': 'Incipient or nonhereditary slavery, i.e., where slave status is temporary and not transmitted to the children of slaves'},
                {'code': '3', 'description': "Slavery reported but not identified as hereditary or nonhereditary"},
                {'code': '4', 'description': "Hereditary slavery present and of at least modest social significance"},
            ],
            'variable': {
                'id': 1628,
                'data_type': 'Categorical'
            }
        };
        
        var coded_value = {
            'coded_value': '1',
            'variable': 1628,
            'code_description': variable_description.codes[1]
        };
        society.geographic_regions.push(geographic_region);
        mockResults.geographic_regions.push(geographic_region);
        mockResults.variable_descriptions.push(variable_description);
        society.variable_coded_values.push(coded_value);
        mockResults.societies.push(society);
        
        var map = mockColorService.generateColorMap(mockResults);
        expect(map[society.society.id]).toEqual('rgb(228,26,28)');
    
    });

});