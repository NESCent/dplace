// Karma configuration
// Generated on Wed Jan 27 2016 22:21:49 GMT+0000 (UTC)

module.exports = function(config) {
  config.set({

    // base path that will be used to resolve all patterns (eg. files, exclude)
    basePath: '',


    // frameworks to use
    // available frameworks: https://npmjs.org/browse/keyword/karma-adapter
    frameworks: ['jasmine-jquery','jasmine'],


    // list of files / patterns to load in the browser
    files: [
        //'dplace_app/static/bower_components/jquery/src/jquery.js',
        'dplace_app/static/bower_components/angular/angular.min.js',
        'dplace_app/static/bower_components/angular-resource/angular-resource.min.js',
        'dplace_app/static/bower_components/angular-route/angular-route.min.js',
        'dplace_app/static/bower_components/angular-mocks/angular-mocks.js',
        'dplace_app/static/js/app.js',
        'dplace_app/static/js/controllers/app.js',
        'dplace_app/static/js/controllers/*.js',
        'dplace_app/static/js/models.js',
        'dplace_app/static/js/colorMapService.js',
        'dplace_app/static/js/searchModelService.js',
        'dplace_app/static/js/services.js',
        'dplace_app/static/js/filters.js',
        'dplace_app/static/js/directives.js',
        'dplace_app/static/bower_components/angular-ui-bootstrap-bower/ui-bootstrap-tpls.min.js',
        'dplace_app/static/js/controllers/search/*.js',
        'dplace_app/tests/*.js',
        
        {pattern: 'dplace_app/tests/data/*.json', watched: true, served: true, included: false}
    ],


    // list of files to exclude
    exclude: [
    ],


    // preprocess matching files before serving them to the browser
    // available preprocessors: https://npmjs.org/browse/keyword/karma-preprocessor
     preprocessors: { '*.js': ['coverage'] },

    // test results reporter to use
    // possible values: 'dots', 'progress'
    // available reporters: https://npmjs.org/browse/keyword/karma-reporter
    reporters: ['progress', 'coverage'],
    
    coverageReporter: {
        reporters: [
            {type: 'lcovonly', subdir: '.'},
        ]
    },


    // web server port
    port: 9876,


    // enable / disable colors in the output (reporters and logs)
    colors: true,


    // level of logging
    // possible values: config.LOG_DISABLE || config.LOG_ERROR || config.LOG_WARN || config.LOG_INFO || config.LOG_DEBUG
    logLevel: config.LOG_INFO,


    // enable / disable watching file and executing tests whenever any file changes
    autoWatch: true,


    // start these browsers
    // available browser launchers: https://npmjs.org/browse/keyword/karma-launcher
    browsers: ['PhantomJS'],


    // Continuous Integration mode
    // if true, Karma captures browsers, runs the tests and exits
    singleRun: true,

    // Concurrency level
    // how many browser should be started simultaneous
    concurrency: Infinity
  })
}
