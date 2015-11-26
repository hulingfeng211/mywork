// config

var app =
    angular.module('app')
        .config(
        ['$controllerProvider', '$compileProvider', '$filterProvider', '$provide',
            function ($controllerProvider, $compileProvider, $filterProvider, $provide) {

                // lazy controller, directive and service
                app.controller = $controllerProvider.register;
                app.directive = $compileProvider.directive;
                app.filter = $filterProvider.register;
                app.factory = $provide.factory;
                app.service = $provide.service;
                app.constant = $provide.constant;
                app.value = $provide.value;
            }
        ])
        .config(['$translateProvider', function ($translateProvider) {
            // Register a loader for the static files
            // So, the module will search missing translation tables under the specified urls.
            // Those urls are [prefix][langKey][suffix].
            $translateProvider.useStaticFilesLoader({
                prefix: 'l10n/',
                suffix: '.json'
            });
            // Tell the module what language to use by default
            $translateProvider.preferredLanguage('cn');
            // Tell the module to store the language in the local storage
            $translateProvider.useLocalStorage();
        }])
        .config(['paginationConfig', function (paginationConfig) {
            paginationConfig.firstText = '第一页';
            paginationConfig.previousText = '向前';
            paginationConfig.nextText = '向后';
            paginationConfig.lastText = '最后一页';


        }]);

angular.module('app').factory('redirectInterceptor', ['$rootScope','$q', function ($rootScope,$q) {
   return {
            'response': function (response) {
                if (response.status === 401) {
                    console.log("Response 401");
                    $rootScope.logout();
                    return ;
                }
                return response || $q.when(response);
            },
            'responseError': function (rejection) {
                if (rejection.status === 401) {
                    console.log("Response Error 401");
                    $rootScope.logout();
                    return ;
                }
                return $q.reject(rejection);
            }
        };
}]);
angular.module('app').config(['$httpProvider', function ($httpProvider) {
    $httpProvider.interceptors.push('redirectInterceptor');
}]);
