angular.module('dplace', ['ngRoute', 'dplaceServices']) // Should look at ui-router instead
    .config(dplaceRouter);

function dplaceRouter($routeProvider) {
    $routeProvider
        .when('/search', {
            templateUrl: '/static/partials/search.html',
            controller: 'SearchCtrl'
        });
}
