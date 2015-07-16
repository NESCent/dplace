angular.module('dplace', ['ngRoute', 'dplaceServices', 'ui.bootstrap', 'dplaceFilters', 'dplaceMapDirective', 'languagePhylogenyDirective']) // Should look at ui-router
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
        .when('/home', {
            templateUrl: '/static/partials/home.html',
            controller: 'HomeCtrl'
        })
        .when('/about', {
            templateUrl: '/static/partials/about.html',
            controller: 'AboutCtrl'
        })
        .when('/source_info', {
            templateUrl:'/static/partials/source_info.html',
            controller:'SourceInfoCtrl'
        })
        .otherwise({
	        redirectTo: '/home'
	});
}
