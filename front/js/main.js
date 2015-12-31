'use strict';

/* Controllers */

angular.module('app')
    .controller('AppCtrl', ['$scope', '$translate', '$localStorage', '$window', 'subject', "$http", '$state','$rootScope','SettingsService',
        function ($scope, $translate, $localStorage, $window, subject, $http, $state,$rootScope,SettingsService) {
            // add 'ie' classes to html
            var isIE = !!navigator.userAgent.match(/MSIE/i);
            isIE && angular.element($window.document.body).addClass('ie');
            isSmartDevice($window) && angular.element($window.document.body).addClass('smart');
            var userId=subject.getPrincipal().email;
            var settings=SettingsService.query({"create_user":userId});
            if(!angular.isDefined(settings)){
                settings={
                    themeID: 1,
                    navbarHeaderColor: 'bg-black',
                    navbarCollapseColor: 'bg-white-only',
                    asideColor: 'bg-black',
                    headerFixed: true,
                    asideFixed: false,
                    asideFolded: false,
                    asideDock: false,
                    container: false
                };
            }
            // config
            $scope.app = {
                name: '我的工作',
                version: '1.3.3',
                // for chart colors
                color: {
                    primary: '#7266ba',
                    info: '#23b7e5',
                    success: '#27c24c',
                    warning: '#fad733',
                    danger: '#f05050',
                    light: '#e8eff0',
                    dark: '#3a3f51',
                    black: '#1c2b36'
                },
                settings: settings
            };

            // save settings to local storage
            if (angular.isDefined($localStorage.settings)) {
                $scope.app.settings = $localStorage.settings;
            } else {
                $localStorage.settings = $scope.app.settings;
            }
            $scope.$watch('app.settings', function () {
                if ($scope.app.settings.asideDock && $scope.app.settings.asideFixed) {
                    // aside dock and fixed must set the header fixed.
                    $scope.app.settings.headerFixed = true;
                }
                // save to local storage
                $localStorage.settings = $scope.app.settings;

                //update setting data to server
                SettingsService.save({"settings":$scope.app.settings,"_id":userId});

            }, true);

            // angular translate
            $scope.lang = {isopen: false};

            //默认支持英语与简体中文
            $scope.langs = {en: 'English', cn: '简体中文'};

            //多语言支持
            //$scope.langs = {en:'English', de_DE:'German', it_IT:'Italian',cn:'中文'};
            $scope.selectLang = $scope.langs[$translate.proposedLanguage()] || "English";

            $scope.setLang = function (langKey, $event) {
                // set the current lang
                $scope.selectLang = $scope.langs[langKey];
                // You can change the language during runtime
                $translate.use(langKey);
                $scope.lang.isopen = !$scope.lang.isopen;
            };

            function isSmartDevice($window) {
                // Adapted from http://www.detectmobilebrowsers.com
                var ua = $window['navigator']['userAgent'] || $window['navigator']['vendor'] || $window['opera'];
                // Checks for iOs, Android, Blackberry, Opera Mini, and Windows mobile devices
                return (/iPhone|iPod|iPad|Silk|Android|BlackBerry|Opera Mini|IEMobile/).test(ua);
            }

            //用户登出
            $rootScope.logout = function () {
                subject.logout();
                $http.get('/auth/logout').success(function (data) {
                    console.log(data);
                    $state.go('access.signin');
                });
            };

        }]);
