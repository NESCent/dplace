angular.module('dplaceDirectives', [])
  .directive('languagePicker', function() {
    return {
        restrict: 'E',
        scope: {
            language: '='
        },
        template: '<span ng-click="toggleShowChildren(language)"' +
            'ng-class="{\'triangle-down\' : language.isShowingChildren, ' +
            '\'triangle-right\' : !language.isShowingChildren }" >' +
            '{{ language.name }}' +
            '</span>'
    };
  });

