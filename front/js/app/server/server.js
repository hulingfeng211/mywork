/**
 * Created by george on 12/9/15.
 */

app.controller('ServerListCtrl', ['$scope', '$http', 'toaster', '$window', 'subject', '$log', 'ServerService', '$state',
    function ($scope, $http, $toaster, $window, subject, $log, ServerService, $state) {

        function get_server_list() {
            var seconds = new Date() / 1000;
            $scope.servers = ServerService.query({
                create_user: subject.getPrincipal().email,
                _v: seconds.toString()
            });
            //var url = '/servers?create_user='+subject.getPrincipal().email+'&_v='+seconds.toString();// + '?net=' + $scope.current_tab.name;

        }

        $scope.on_server_selected = function (server) {

            $state.go('app.server.detail', {"serverId": server._id})

        };
        get_server_list();
        if (angular.isDefined($scope.servers) && $scope.servers.length > 0) {
            $state.go('app.server.detail', {"serverId": $scope.server[0]._id})
        }


    }]);

app.controller('ServerNewCtrl', ['$scope', '$http', 'toaster', '$window', 'subject', '$log', 'ServerService',
    function ($scope, $http, $toaster, $window, subject, $log, ServerService) {

        //TODO
        $scope.oses = [
            "Centos 6.5 X86_64",
            "Centos 6.5 X86",
            "Windows 2008 R2 X64",
            "Windows 2003",
            "Windows 7",
            "Windows 2012"

        ];
        $scope.server={
            name: '',
            ipaddr: '',
            admin_name: '',
            admin_pwd: '',
            os: 'Windows 2008 R2 X64',
            owner: subject.getPrincipal().name,
            net: '内网',
            desc: '',
            _id: ''
        };
        $scope.save_server = function () {
            ServerService.save($scope.server);
            $state.go('app.server.list');
        }

    }]);

app.controller('ServerDetailCtrl', ['$scope', '$stateParams', 'toaster', '$state', 'subject', '$log', 'ServerService',
    function ($scope, $stateParams, $toaster, $state, subject, $log, ServerService) {

        //TODO
        var serverId = $stateParams.serverId;
        $scope.oses = [
            "Centos 6.5 X86_64",
            "Centos 6.5 X86",
            "Windows 2008 R2 X64",
            "Windows 2003",
            "Windows 7",
            "Windows 2012"

        ];
        $scope.save_server = function () {
            ServerService.save($scope.server);
            $state.go('app.server.list');

        };
        $scope.server = ServerService.get({"id": serverId});


    }]);

app.controller('ServerCtrl', ['$scope', '$http', 'toaster', '$window', 'subject','$log',
    function ($scope, $http, toaster, $window, subject,$log) {

        $scope.tabs = [
            {'name': '内网', 'active': true},
            {'name': '外网', 'active': false}

        ];
        $scope.oses=[
            "Centos 6.5 X86_64",
            "Centos 6.5 X86",
            "Windows 2008 R2 X64",
            "Windows 2003",
            "Windows 7",
            "Windows 2012"

        ];
        var empty_server = {
            name: '',
            ipaddr: '',
            admin_name: '',
            admin_pwd: '',
            os: 'Windows 2008 R2 X64',
            owner: subject.getPrincipal().name,
            net: '内网',
            desc: '',
            _id: ''
        };
        $log.debug(subject.getPrincipal());
        $scope.server = empty_server;

        $scope.current_tab = $scope.tabs[0];
        $scope.get_server_list=function(){
            get_servers();
        };

        function get_servers() {
            var seconds=new Date()/1000;
            var url = '/servers?create_user='+subject.getPrincipal().email+'&_v='+seconds.toString();// + '?net=' + $scope.current_tab.name;
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
                $scope.server=empty_server;
                get_servers()
            });

        }


    }]);