/**
 * Created by george on 11/30/15.
 */
app.controller('AnnounceCtrl', ['$scope', '$http','toaster','$window', function ($scope, $http,toaster,$window) {

    $scope.tabs = [true, false, false];
    $scope.tab = function(index) {
        angular.forEach($scope.tabs, function (i, v) {
            $scope.tabs[v] = false;
        });
        $scope.tabs[index] = true;
    }
}]);
