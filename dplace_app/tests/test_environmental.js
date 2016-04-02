describe('Testing environmental search', function() {
    var appScope, mockAppCtrl, searchScope, envScope, mockSearchCtrl, mockEnvCtrl, mockSearchModelService, mockColorMapService, mockFindSocieties, mockEnvVar, mockEnvVal, mockMinAndMax;
    beforeEach(function() {
        module('dplaceServices');
        module('dplace');
    });
    
    beforeEach(inject(function($rootScope, $controller, searchModelService, colorMapService, FindSocieties, EnvironmentalVariable, EnvironmentalValue, MinAndMax, $httpBackend) {
        appScope = $rootScope.$new();

        mockSearchModelService = searchModelService;
        mockAppCtrl = $controller('AppCtrl', {$scope: appScope, searchModelService: mockSearchModelService});
        spyOn(appScope, 'setActive');

        mockColorMapService = colorMapService;
        mockFindSocieties = FindSocieties;
        spyOn(mockFindSocieties, 'find');
        mockEnvVal = EnvironmentalValue;
        mockEnvVar = EnvironmentalVariable;
        spyOn(mockEnvVar, 'query');
        mockMinAndMax = MinAndMax;
        
        spyOn(mockMinAndMax, 'query');
        
        searchScope = appScope.$new();
        mockSearchCtrl = $controller('SearchCtrl', {
            $scope: searchScope,
            colorMapService: mockColorMapService,
            searchModelService: mockSearchModelService,
            FindSocieties: mockFindSocieties
        });
        spyOn(searchScope, 'search').and.callThrough();
        spyOn(searchScope, 'updateSearchQuery');
        spyOn(searchScope, 'searchSocieties').and.callThrough();
        spyOn(searchScope, 'getCodeIDs');

        envScope = searchScope.$new();
        
        mockEnvCtrl = $controller('EnvironmentalCtrl', {
            $scope: envScope,
            searchModelService: mockSearchModelService,
            EnvironmentalVariable: mockEnvVar,
            EnvironmentalValue: mockEnvVal,
            MinAndMax: mockMinAndMax
        });
        spyOn(envScope, 'filterChanged');
        
        //These API calls are made in searchModelService or environmental.js
        //We just respond with 200 OK because this is testing the controller logic
        $httpBackend.whenGET('/api/v1/categories?page_size=1000')
            .respond(200);
        $httpBackend.whenGET('/api/v1/get_dataset_sources')
            .respond(200);
        $httpBackend.whenGET('/api/v1/geographic_regions?page_size=1000')
            .respond(200);
        $httpBackend.whenGET('/api/v1/environmental_categories')
            .respond(200);
        $httpBackend.whenGET('/api/v1/language_families?page_size=1000')
            .respond(200);
        $httpBackend.whenPOST('/api/v1/find_societies')
            .respond(200); //return a result here?
        $httpBackend.whenGET('/api/v1/environmental_variables?category=7&page_size=1000')
            .respond(200);
        $httpBackend.whenGET('/api/v1/min_and_max?query=%7B%22environmental_id%22:7%7D')
            .respond(JSON.stringify({
                "min": 1.111,
                "max": 500
            }));
    }));
    it('should update badgeValue and call search', function() { 
        var variable = {
            'category': 1,
            'codebook_info': '',
            'id': 7,
            'max': 500,
            'min': 1.111,
            'name': "Precipitation",
            'range': 409.999,
            'units': 'mm'
        };
        var category = {
            'id': 7,
            'name': 'Climate'
        };
        var form = {
            $valid: true,
            $dirty: false,
            $setPristine: function() {}
        };
        envScope.environmentalData.selectedVariables[0].selectedCategory = category;
        envScope.environmentalData.selectedVariables[0].EnvironmentalForm = form;
        
        //test change category and EnvironmentalVariable API call
        envScope.categoryChanged(envScope.environmentalData.selectedVariables[0]);
        expect(mockEnvVar.query).toHaveBeenCalled();
                
        //test variable changed when no variable selected
        envScope.variableChanged(envScope.environmentalData.selectedVariables[0]);
        envScope.$digest();
        expect(envScope.environmentalData.badgeValue).toEqual(0);
        expect(envScope.filterChanged).not.toHaveBeenCalled();
        
        //test variable changed with variable selected
        envScope.environmentalData.selectedVariables[0].selectedVariable = variable;
        envScope.variableChanged(envScope.environmentalData.selectedVariables[0]);
        envScope.$digest();
        expect(envScope.environmentalData.badgeValue).toEqual(1);
        expect(mockMinAndMax.query).toHaveBeenCalled();
        expect(envScope.filterChanged).toHaveBeenCalledWith(envScope.environmentalData.selectedVariables[0]);

        //test filter changed - need to figure out how to do this

        
        //test add variable
        expect(envScope.environmentalData.selectedVariables.length).toEqual(1);
        envScope.addVariable();
        envScope.$digest();
        expect(envScope.environmentalData.selectedVariables.length).toEqual(2);
        
        //test remove variable
        envScope.removeVariable(variable);
        envScope.$digest();
        expect(envScope.environmentalData.selectedVariables.length).toEqual(1);
        expect(envScope.environmentalData.selectedVariables.indexOf(variable)).toEqual(-1);
        
        //test search
        envScope.environmentalData.selectedVariables[0].selectedVariable = variable;
        envScope.environmentalData.selectedVariables[0].selectedFilter = envScope.environmentalData.filters[0];
        envScope.environmentalData.selectedVariables[0].vals = [1.0, 500];
        envScope.doSearch();
        expect(searchScope.search).toHaveBeenCalled();
        searchScope.$digest();
        
        expected_query = {
            'e': [[
                variable.id,
                envScope.environmentalData.selectedVariables[0].selectedFilter.operator,
                [1.0, 500]
            ]]
        };
        
        expect(searchScope.updateSearchQuery).toHaveBeenCalled();
        expect(searchScope.updateSearchQuery).toHaveBeenCalledWith(expected_query);
        expect(searchScope.searchSocieties).toHaveBeenCalled();
        expect(mockFindSocieties.find).toHaveBeenCalled();
       
    });
});