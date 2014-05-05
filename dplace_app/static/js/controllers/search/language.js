function LanguageCtrl($scope) {
    // TODO: Fill in an actual language
    $scope.language = {
        items: [
            { name: 'Language 1'},
            { name: 'Language 2'},
            { name: 'Language 3'}
        ],
        languageFilters: [
            { families: [{name:'a'},{name:'b'}]}
        ]
    };
}