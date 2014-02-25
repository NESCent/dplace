angular.module('dplace', ['ngRoute', 'dplaceServices', 'ui.bootstrap']) // Should look at ui-router
    .config(dplaceRouter);

function dplaceRouter($routeProvider) {
    $routeProvider
        .when('/search', {
            templateUrl: '/static/partials/search.html',
            controller: 'SearchCtrl'
        })
        .otherwise({
	        redirectTo: '/search'
	});
}
