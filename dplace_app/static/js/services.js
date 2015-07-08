angular.module('dplaceServices', ['ngResource'])
    .config(function($httpProvider) {
        $httpProvider.defaults.xsrfCookieName = 'csrftoken';
        $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
    })
    .service('colorMapService', [ColorMapService])
    .service('searchModelService',['VariableCategory','GeographicRegion','EnvironmentalCategory', 'LanguageClass',SearchModelService])
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
    .factory('Source', function ($resource) {
        return $resource (
            '/api/v1/sources/:id',
            {page_size: 1000}, {
                query: {
                    method: 'GET',
                    isArray: true,
                    transformResponse: function(data, headers) {
                        return JSON.parse(data).results;
                    }
                }
            }
        )
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
                        if (!JSON.parse(data).results) {
                            return [JSON.parse(data)];
                        }                            
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
            '/api/v1/codes/?variable=:variable',
            {page_size: 1000}, {
                query: {
                    method: 'GET',
                    isArray: true,
                    transformResponse: function(data, headers) {
                        if (!JSON.parse(data).results) {
                            return [JSON.parse(data)];
                        }
                        
                        return JSON.parse(data).results;
                    }
                }
            });
    })
    .factory('EnvironmentalValue', function($resource) {
        return $resource(
            '/api/v1/environmental_values/:id',
            {}, {
                query: {
                    method: 'GET',
                    isArray: true,
                    transformResponse: function(data, headers) {
                        return JSON.parse(data).results;
                    }
                }
            }
        )
    })
    .factory('MinAndMax', function($resource) {
        return $resource(
            '/api/v1/min_and_max',
            {}, {
                query: {
                    method: 'GET',
                    isArray:false
                }
            }
        )
    })
    .factory('getCategories', function($resource) {
        return $resource(
            '/api/v1/get_categories',
            {}, {
                query: {
                    method: 'GET',
                    isArray:true
                }
            }
        )
    })
    .factory('BfContinuousVariable', function($resource) {
        return $resource(
            '/api/v1/bf_cont_variable',
            {}, {
                query: {
                    method: 'GET',
                    isArray:true,
                    transformResponse: function(data, headers) {
                        return JSON.parse(data);
                    }
                }
            }
        )
    })
    .factory('EnvironmentalCategory', function($resource) {
        return $resource(
            '/api/v1/environmental_categories/:id',
            {}, {
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
    .factory('ZipTest', function($resource) {
        return $resource(
            '/api/v1/zip_legends',
            {}, {
                 
                query: {
                    method: 'GET',
                    isArray:false,
                }
            }
        )
    })
    //not used at the moment
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
    ;
