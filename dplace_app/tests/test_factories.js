describe('Testing language factories', function() {
    var mockLangFamilyFactory, mockLangFactory, $httpBackend, results;
    beforeEach(module('dplaceServices'));
    beforeEach(function() {
        inject(function($injector) {
            $httpBackend = $injector.get('$httpBackend');
            mockLangFamilyFactory = $injector.get('LanguageFamily');
            mockLangFactory = $injector.get('Language');
        });
    });
    
    it('should get languages', inject(function(LanguageFamily, Language) {
        results = {
            "count": 2,
            "results": [
            {
                "id": 77,
                "scheme": "G",
                "name": "Abkhaz-Adyge",
                "language_count": 2
            },
            {
                "id": 7,
                "scheme": "G",
                "name": "Afro-Asiatic",
                "language_count": 91
            },
            ]
        };
        $httpBackend.whenGET('/api/v1/language_families?page_size=1000')
            .respond(JSON.stringify(results));
        response = mockLangFamilyFactory.query();
        $httpBackend.flush();
        expect(response.length).toEqual(3);
        expect(response[0].name).toEqual("Select All Languages");
        expect(response[1].id).toEqual(77);
        expect(response[2].id).toEqual(7);
        expect(response[1].name).toEqual("Abkhaz-Adyge");
        expect(response[2].name).toEqual("Afro-Asiatic");
        
        results = {
            "count": 2,
            "results": [
            {
                "id": 149,
                "name": "Abkhazian",
                "glotto_code": "abkh1244",
                "iso_code": "abk",
                "family": {
                    "id": 77,
                    "scheme": "G",
                    "name": "Abkhaz-Adyge",
                    "language_count": 2
                },
                "count": 1
            },
            {
                "id": 599,
                "name": "Kabardian",
                "glotto_code": "kaba1278",
                "iso_code": "kbd",
                "family": {
                    "id": 77,
                    "scheme": "G",
                    "name": "Abkhaz-Adyge",
                    "language_count": 2
                },
                "count": 1
            }
            ]  
        };
        
        $httpBackend.whenGET('/api/v1/languages?family=77&page_size=1000')
            .respond(JSON.stringify(results));
        languages = mockLangFactory.query({family: response[1].id});
        $httpBackend.flush()
        expect(languages.length).toEqual(2);
        expect(languages[0].id).toEqual(149);
        expect(languages[1].id).toEqual(599);
    }));
});
