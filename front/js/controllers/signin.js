'use strict';

/* Controllers */
  // signin controller
app.controller('SigninFormController', ['$scope', '$http', '$state','subject', 'usernamePasswordToken',
    function ($scope, $http, $state, subject,usernamePasswordToken) {

        $scope.user = {};
        $scope.authError = null;
        $scope.token = usernamePasswordToken;
        if(subject.authenticated){
            $state.go('app.dashboard-v1');
        }
        $scope.myInterval = 5000;
        var slides = $scope.slides = [];
        $scope.addSlide = function () {
            slides.push({
                image: 'img/c' + slides.length + '.jpg',
                text: ['Carousel text #0', 'Carousel text #1', 'Carousel text #2', 'Carousel text #3'][slides.length % 4]
            });
        };
        for (var i = 0; i < 4; i++) {
            $scope.addSlide();
        }

        $scope.login = function() {
            $scope.authError = null;

            // Try to login
            /**$http.post('/auth/login', {email: $scope.user.email, password: $scope.user.password})
            .then(function(response) {
                if ( !response.data.user ) {
                    $scope.authError = 'Email or Password not right';
                }else{
                    $state.go('app.dashboard-v1');
                }
                }, function(x) {
                    $scope.authError = 'Server Error';
             });*/
            $scope.token.rememberMe=true;
            $scope.token.username=$scope.token.email;

            subject.login($scope.token).then(function (data) {
                console.log(data);
                if(!data.info||!data.info.authc.principal){
                    $scope.authError = data;
                }else{
                    $scope.user=data.info.authc.principal;
                    $state.go('app.dashboard-v1');
                }
            }, function (error) {
                console.log(error);
                $scope.authError = 'Server Error';
            });
    };
  }])
;