/**
 * Created by george on 12/9/15.
 */
app.controller('ServerCtrl', ['$scope', '$http', 'toaster', '$window', 'subject',
    function ($scope, $http, toaster, $window, subject) {

        $scope.tabs = [
            {'name': '内网', 'active': true},
            {'name': '外网', 'active': false}

        ];
        var empty_server = {
            name: '',
            ipaddr: '',
            admin_name: '',
            admin_pwd: '',
            os: '',
            owner: subject.getPrincipal().name,
            net: '内网',
            desc: '',
            _id: ''
        };
        $scope.server = empty_server;

        $scope.current_tab = $scope.tabs[0];

        function get_servers() {
            var url = '/servers?create_user='+subject.getPrincipal().email;// + '?net=' + $scope.current_tab.name;
            $http.get(url).then(function (res) {
                $scope.servers = res.data;

                if ($scope.servers.length > 0)
                    $scope.server = $scope.servers[0];
            });

        }

        function initialize() {
            get_servers();
        }

        initialize();
        $scope.delete_server = function (server) {
            var url = '/servers/' + server._id;
            $http.delete(url).then(function (res) {
                toaster.pop('success', 'Waring', '删除成功');
                var eIndex = $scope.servers.indexOf($scope.server);
                if (eIndex > -1) {
                    $scope.servers.splice(eIndex, 1);
                    if ($scope.servers.length > 0) {
                        $scope.server = $scope.servers[0];
                        $scope.on_server_selected($scope.server);
                        //$scope.circulation.selected=true;
                    }
                }
            });
        };

        $scope.on_server_selected = function (server) {
            /**var url='/servers/'+server._id;
             $http.get(url).then(function(res){

            });*/
            $scope.server = server;

        };
        $scope.tab_change = function (tab) {
            angular.forEach($scope.tabs, function (i, v) {
                $scope.tabs[v].active = false;
            });
            tab.active = true;
            $scope.current_tab = tab;
            get_servers();
        };

        $scope.add_server = function () {
            $scope.server={};
            $scope.server = empty_server;

        };


        $scope.save_server = function () {
            var url = '/servers';
            $http.post(url, $scope.server).then(function () {
                toaster.pop('success', '确认', '保存成功');
                get_servers()
            });

        }


    }]);