describe('Testing geographic search', function() {
    var appScope, mockAppCtrl, searchScope, geographicScope, mockSearchCtrl, mockGeographicCtrl, mockSearchModelService, mockColorMapService, mockFindSocieties;
    beforeEach(function() {
        module('dplaceServices');
        module('dplace');
    });
    
    beforeEach(inject(function($rootScope, $controller, searchModelService, colorMapService, FindSocieties, $httpBackend) {
        appScope = $rootScope.$new();

        mockSearchModelService = searchModelService;
        mockAppCtrl = $controller('AppCtrl', {$scope: appScope, searchModelService: mockSearchModelService});
        spyOn(appScope, 'setActive');

        mockColorMapService = colorMapService;
        mockFindSocieties = FindSocieties;
        searchScope = appScope.$new();
        mockSearchCtrl = $controller('SearchCtrl', {
            $scope: searchScope,
            colorMapService: mockColorMapService,
            searchModelService: mockSearchModelService,
            FindSocieties: mockFindSocieties
        });
        spyOn(searchScope, 'search').and.callThrough();
        spyOn(searchScope, 'updateSearchQuery');
        spyOn(searchScope, 'searchSocieties');

        geographicScope = searchScope.$new();
        
        mockGeographicCtrl = $controller('GeographicCtrl', {
            $scope: geographicScope,
            searchModelService: mockSearchModelService
        });
        
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
            .respond(200);

    }));
    
    it('should update badgeValue and call search', function() { 
        //test add region 
        geographicScope.geographic.selectedRegions.push(
            {
                "code": "14",
                "id": 5,
                "name": "Eastern Europe"
            }
        );
        geographicScope.$digest();
        expect(geographicScope.geographic.badgeValue).toEqual(1);
        geographicScope.geographic.selectedRegions.push(
            {
                "code": "20",
                "id": 4,
                "name": "Asia"
            }
        );
        geographicScope.$digest();
        expect(geographicScope.geographic.badgeValue).toEqual(2);
        
        //test remove region
        geographicScope.removeRegion({
                "code": "20",
                "id": 4,
                "name": "Asia"
            });
        geographicScope.$digest();
        expect(geographicScope.geographic.badgeValue).toEqual(1);
        
        geographicScope.doSearch();
        expect(searchScope.search).toHaveBeenCalled();
        searchScope.$digest();
                
        expected_searchQuery = {
            'p': [geographicScope.geographic.selectedRegions[0].id]
        };
        expect(searchScope.updateSearchQuery).toHaveBeenCalled();
        expect(searchScope.updateSearchQuery).toHaveBeenCalledWith(expected_searchQuery);
        expect(searchScope.searchSocieties).toHaveBeenCalled();
    });
});