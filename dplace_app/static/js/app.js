angular.module('dplace', ['ngRoute', 'dplaceServices', 'ui.bootstrap']) // Should look at ui-router
    .config(dplaceRouter);

function dplaceRouter($routeProvider) {
    $routeProvider
        .when('/search', {
            templateUrl: '/static/partials/search.html',
            controller: 'SearchCtrl'
        })
        .when('/home', {
            templateUrl: '/static/partials/home.html',
            controller: 'HomeCtrl'
        })
        .when('/societies', {
            templateUrl: '/static/partials/societies.html',
            controller: 'SocietiesCtrl'
        })
        .otherwise({
	        redirectTo: '/home'
	});
}
