angular.module('dplaceServices', ['ngResource'])
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
    .factory('FindSocieties', function($resource) {
        return $resource(
            '/api/v1/find_societies',
            {},{
                find: {
                    method: 'GET',
                    isArray: true
                }
            }
        )
    });