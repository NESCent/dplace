/* Tests ColorMapService, which has functions:
    tempColor(index, min, max, name)
    mapColor(index, count)
    mapColorMonochrome(min, max, value, color)
    generateColorMap(results)
    
*/
/*describe('SearchModelService Testing', function() {
    var mockSearchService;
    
    beforeEach(function() {
        module('ngResource');
        module('dplaceServices');
    });
    
    beforeEach(inject(function(searchModelService) {
        mockSearchService = searchModelService;
        spyOn(searchModelService, 'getModel');
    }));
    
    it('testing', function() {
        expect(mockSearchService.model).toBeDefined();
        
    });

});*/

describe('HomeController', function() {
    var appScope, homeScope, mockAppCtrl, mockHomeCtrl, mockSearchModelService;
    beforeEach(function() {
        module('dplaceServices');
        module('dplace');
    });
    
    beforeEach(inject(function($rootScope, $controller, searchModelService) {
        appScope = $rootScope.$new();
        mockSearchModelService = searchModelService;
        mockAppCtrl = $controller('AppCtrl', {$scope: appScope, searchModelService: mockSearchModelService});
        spyOn(appScope, 'setActive');
        homeScope = appScope.$new();
        mockHomeCtrl = $controller('HomeCtrl', {$scope: homeScope});
    }));
    
    it('should do this', function() {
        expect(appScope).toBeDefined(); 
    });
});

/*describe('Family', function () {
    var mockUserResource, $httpBackend, results;
    beforeEach(angular.mock.module('dplaceServices'));

    beforeEach(function () {
        angular.mock.inject(function ($injector) {
            $httpBackend = $injector.get('$httpBackend');
            mockUserResource = $injector.get('LanguageFamily');
        })
    });

    describe('getUser', function () {
        it('should call getUser with username', inject(function (LanguageFamily) {
            $httpBackend.whenGET('/api/v1/language_families?page_size=1000')
                .respond("{\"results\":[]}");
                //.respond("lang_fam.json"); //figure out how to return file contents here
                mockUserResource.query();

            $httpBackend.flush();
           // expect(result).toEqual('test');
        }));

    });
});

/*describe('Color Map Service Testing', function() {
    var mockColorService, mockResults, society;
    
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
            'languages': [],
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
        var expected_color = 'hsl(' + 24*240 + ',100%,50%)';
        expect(map[society.society.id]).toBe(expected_color);
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
        var expected_color = 'hsl('+(240-(((18.25+17)/(29+17))*240))+',100%, 50%)';
        expect(map[society.society.id]).toBe(expected_color);
    
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
        
        mockResults.variable_descriptions.push(variable_description);
        society.variable_coded_values.push(coded_value);
        mockResults.societies.push(society);
        var map = mockColorService.generateColorMap(mockResults);
        var expected_color = 'hsl('+ (1/5)*240 + ',100%,50%)';
        expect(map[society.society.id]).toBe(expected_color);
    
    });

});*/