angular.module('dplace', ['ngRoute', 'dplaceServices', 'ui.bootstrap', 'dplaceFilters','dplaceDirectives']) // Should look at ui-router
    .config(dplaceRouter);

function dplaceRouter($routeProvider) {
    $routeProvider
        .when('/search', {
            templateUrl: '/static/partials/search.html',
            controller: 'SearchCtrl'
        })
        .when('/societies', {
            templateUrl: '/static/partials/societies.html',
            controller: 'SocietiesCtrl'
        })
        .otherwise({
	        redirectTo: '/search'
	});
}
