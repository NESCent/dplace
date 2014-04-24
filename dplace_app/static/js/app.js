angular.module('dplace', ['ngRoute', 'dplaceServices', 'ui.bootstrap', 'dplaceFilters']) // Should look at ui-router
    .config(dplaceRouter);

function dplaceRouter($routeProvider) {
    $routeProvider
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
