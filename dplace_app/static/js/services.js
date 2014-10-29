angular.module('dplaceServices', ['ngResource'])
    .config(function($httpProvider) {
        $httpProvider.defaults.xsrfCookieName = 'csrftoken';
        $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
    })
    .service('colorMapService', [ColorMapService])
    .service('searchModelService',['VariableCategory','GeographicRegion','EnvironmentalVariable','LanguageClass',SearchModelService])
    .factory('LanguageClass', function ($resource) {
        return $resource(
            '/api/v1/language_classes/:id',
            {page_size: 1000}, {
                query: {
                    method: 'GET',
                    isArray: true,
                    transformResponse: function(data, headers) {
                        return JSON.parse(data).results;
                    }
                }
            });
    })
    .factory('LanguageClassification', function ($resource) {
        return $resource(
            '/api/v1/language_classifications/:id',
            {page_size: 1000}, {
                query: {
                    method: 'GET',
                    isArray: true,
                    transformResponse: function(data, headers) {
                        return JSON.parse(data).results;
                    }
                }
            });
    })
    .factory('Variable', function ($resource) {
        return $resource(
            '/api/v1/variables/:id',
            {page_size: 1000}, {
                query: {
                    method: 'GET',
                    isArray: true,
                    transformResponse: function(data, headers) {
                        return JSON.parse(data).results;
                    }
                }
            });
    })
    .factory('VariableCategory', function ($resource) {
        return $resource(
            '/api/v1/categories/:id',
            {page_size: 1000}, {
                query: {
                    method: 'GET',
                    isArray: true,
                    transformResponse: function(data, headers) {
                        return JSON.parse(data).results;
                    }
                }
            });
    })
    .factory('CodeDescription', function ($resource) {
        return $resource(
            '/api/v1/codes/:id',
            {page_size: 1000}, {
                query: {
                    method: 'GET',
                    isArray: true,
                    transformResponse: function(data, headers) {
                        return JSON.parse(data).results;
                    }
                }
            });
    })
    .factory('EnvironmentalVariable', function ($resource) {
        return $resource(
            '/api/v1/environmental_variables/:id',
            {page_size: 1000}, {
                query: {
                    method: 'GET',
                    isArray: true,
                    transformResponse: function(data, headers) {
                        return JSON.parse(data).results;
                    }
                }
            });
    })
    .factory('FindSocieties', function($resource) {
        return $resource(
            '/api/v1/find_societies',
            {},{
                find: {
                    method: 'POST'
                }
            }
        )
    })
    .factory('GeographicRegion', function ($resource) {
        return $resource(
            '/api/v1/geographic_regions/:id',
            {page_size: 1000}, {
                query: {
                    method: 'GET',
                    isArray: true,
                    transformResponse: function(data, headers) {
                        return JSON.parse(data).results;
                    }
                }
            });
    })
    .factory('TreesFromLanguages', function($resource) {
        return $resource(
            '/api/v1/trees_from_languages',
            {},{
                find: {
                    method: 'POST',
                    isArray: true
                }
            }
        )
    })
   .factory('NewickTree', function($resource) {
        return $resource(
            '/api/v1/newick_tree/:id',
            {}, {
                query: {
                    method: 'GET',
                    isArray: false,
                    transformResponse: function(data, headers) {
                        return JSON.parse(data);
                    }
                }
            });
    })
    .factory('GetBins', function($resource) {
        return $resource(
            '/api/v1/get_bins',
            {}, {
                query: {
                    method: 'GET',
                    isArray: true
                }
            }
        )
    })
    .factory('getTree', function($resource) {
        return $resource(
            '/api/v1/get_trees',
            {}, {
                query: {
                    method: 'GET',
                    isArray: false
                }
            }
        )
    })
    ;
