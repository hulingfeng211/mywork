/**
 * Created by george on 9/7/15.
 */

app.filter('propsFilter', function() {
    return function(items, props) {
        var out = [];

        if (angular.isArray(items)) {
          items.forEach(function(item) {
            var itemMatches = false;

            var keys = Object.keys(props);
            for (var i = 0; i < keys.length; i++) {
              var prop = keys[i];
              var text = props[prop].toLowerCase();
              if (item[prop].toString().toLowerCase().indexOf(text) !== -1) {
                itemMatches = true;
                break;
              }
            }

            if (itemMatches) {
              out.push(item);
            }
          });
        } else {
          // Let the output be the input untouched
          out = items;
        }

        return out;
    };
});
app.controller('MenuController',["$scope","$http","toaster","$log",function($scope,$http,toaster,$timeout,$log){
   var apple_selected, tree, treedata_avm, treedata_geography;
    $scope.node={};
    $scope.my_tree_handler = function(branch) {
      var _ref;
      //$scope.output = "You selected: " + branch.label;
      //if ((_ref = branch.data) != null ? _ref.description : void 0) {
       // return $scope.output += '(' + branch.data.description + ')';
      //}
        $scope.node=branch;
    };
    $scope.my_data=[];
    $http.get('/rbac/menu').success(function(data,status,header,config){
        $scope.my_data=data;

    });


    $scope.my_tree = tree = {};
    $scope.try_async_load = function() {
      $scope.my_data = [];
      $scope.doing_async = true;
      return $timeout(function() {
        if (Math.random() < 0.5) {
          $scope.my_data = treedata_avm;
        } else {
          $scope.my_data = treedata_geography;
        }
        $scope.doing_async = false;
        return tree.expand_all();
      }, 1000);
    };
    $scope.try_delete_a_branch = function () {
        var select_node=tree.get_selected_branch();
        var p=tree.get_parent_branch(select_node);
        var tmp_children_list=[];

        angular.forEach(p.children,function(item){
            if(item.uid!=select_node.uid){
                tmp_children_list.push(item)
            }
        });
        p.children=tmp_children_list;
    };
    $scope.try_save_a_node=function(){
        //if($scope.node!=undefined){
        //    var current_node=tree.get_selected_branch();
        //    current_node=$scope.node
        //}
        //$log.info($scope.my_data);
        $http.post('/rbac/menu',$scope.my_data).success(function(data,status,header,config){
             toaster.pop('success', '确认', '保存成功');
        });

    };
    return $scope.try_adding_a_branch = function() {
      var b;
      b = tree.get_selected_branch();
      return tree.add_branch(b, {
          label: '菜单名',
        data: {
            cn: '中文名',
            en: '英文名',
            url: '链接地址',
            remark: '其他'
        }
      });
    };

}]);
app.controller('UserController', ['$scope', '$http', 'toaster', '$state', 'DTOptionsBuilder',
    function ($scope, $http, toaster, $state, DTOptionsBuilder) {
        var vm = this;
        vm.dtOptions = DTOptionsBuilder.newOptions()
            .withPaginationType('full_numbers')
            .withDisplayLength(10)
            .withLanguageSource('vendor/jquery/datatables/Chinese.json')
            //.withColReorder()
            .withColVis()
            .withTableTools('vendor/angular/angular-datatables/datatables-tabletools/swf/copy_csv_xls_pdf.swf');
        $http.get('/rbac/user').success(function(data,status,header,config){
            vm.users=data
        });
        vm.edit = function (id) {
            $state.go('app.rbac.user_edit', {user_id: id});

        };
        vm.delete = function (id) {
            $http.delete('/rbac/user/' + id).success(function (result) {

                toaster.pop('success', '确认', "删除成功");
                angular.forEach(vm.users,function(item){
                    if(item._id==id){
                        vm.users.pop(item)
                    }
                });
            });

        };


    }]);
app.controller('UserAddController', ['$scope', '$http', 'toaster', '$state', '$stateParams', '$timeout',
    function ($scope, $http, toaster, $state, $stateParams, $timeout) {
         var user_id=$stateParams.user_id;
        $scope.user = {};

        $scope.permisons=[];
        $scope.roles=[];
        $scope.menus=[];

        //$scope.user.selected_roles = [];
        $scope.user.selected_roles = [];
        $scope.user.selected_permissons = [];
        $scope.user.selected_menus = [];

        function init_dropdown() {
            $http.get('/rbac/role').success(function (data, status, header, config) {
                $scope.roles = data;
            });

            $http.get('/rbac/permission').success(function (data, status, header, config) {
                $scope.permissons = data;
            });
            $http.get('/rbac/menu/all_leaf').success(function (data, status, header, config) {
                $scope.menus = data;
            });
        }
        if(user_id==undefined){//add new
            $scope.op='添加';
            $scope.user.password = '111111';
        }
        else{
            $scope.op='编辑';
            $http.get('/rbac/user/'+user_id).success(function(user){


                $scope.user=user;

                if(user.selected_roles==undefined||user.selected_roles.length<1){
                    $scope.user.selected_roles = [];
                }

                if(user.selected_permissons==undefined||user.selected_permissons.length<1){
                    $scope.user.selected_permissons = [];
                }
                if(user.selected_menus==undefined||user.selected_menus.length<1){
                    $scope.user.selected_menus = [];
                }

            });
        }
        init_dropdown();
        $scope.save = function () {
            $http.post('/rbac/user', $scope.user).success(function (data, status, header, config) {

                toaster.pop('success', '确认', '保存成功');
                $state.go('app.rbac.user')

            });
        };


    }]);
app.controller('RoleController', ['$scope', '$http', 'toaster', '$state', '$compile', 'DTOptionsBuilder', 'DTColumnBuilder', '$resource',
    function ($scope, $http, toaster, $state, $compile, DTOptionsBuilder, DTColumnBuilder, $resource) {

        var vm = this;
        vm.dtOptions = DTOptionsBuilder.newOptions().withPaginationType('full_numbers')
            .withLanguageSource('vendor/jquery/datatables/Chinese.json');
        $resource('/rbac/role').query().$promise.then(function (roles) {
            vm.roles = roles;
        });
        vm.edit=function(id){
            $state.go('app.rbac.role_edit',{role_id:id});

        };
        vm.delete=function(id){
            $http.delete('/rbac/role/'+id).success(function(result){

                toaster.pop('success', '确认', '删除成功');
                vm.roles.pop(vm.roles[id])
            });

        };


    }]);

app.controller('PermissionController', ['$scope', '$http', 'toaster', '$state',  'DTOptionsBuilder', '$resource',
    function ($scope, $http, toaster, $state,  DTOptionsBuilder,  $resource) {

        var vm = this;
        vm.dtOptions = DTOptionsBuilder.newOptions()
            .withPaginationType('full_numbers')
            .withDisplayLength(10)
            .withLanguageSource('vendor/jquery/datatables/Chinese.json')
            //.withColReorder()
            .withColVis()
            .withTableTools('vendor/angular/angular-datatables/datatables-tabletools/swf/copy_csv_xls_pdf.swf');

        $resource('/rbac/permission').query().$promise.then(function (permissions) {
            vm.permissions = permissions;
        });
        vm.edit=function(id){
            $state.go('app.rbac.permission_edit',{permission_id:id});

        };
        vm.delete=function(id){
            $http.delete('/rbac/permission/'+id).success(function(result){

                toaster.pop('success', '确认', "删除成功");
                vm.permissions.pop(vm.permissions[id])
            });

        };


    }]);
app.controller('PermissionAddController', ['$scope', '$http', 'toaster', '$state','$stateParams',
    function ($scope, $http, toaster, $state,$stateParams) {

        var permission_id=$stateParams.permission_id;
        $scope.permission = {};
        if(permission_id==undefined){//add new
            $scope.op='添加';
        }
        else{
            $scope.op='编辑';
            $http.get('/rbac/permission/'+permission_id).success(function(permission){
                $scope.permission=permission;

            });
        }


    $scope.save = function () {
        var message="";
        if ($scope.permission._id==undefined || $scope.permission._id==""){
            message="新增成功";
        }
        else{
            message="修改成功";
        }

        $http.post('/rbac/permission', $scope.permission).success(function (data, status, header, config) {

            toaster.pop('success', '确认', message);
            $state.go('app.rbac.permission')

        })

    };

}]);
app.controller('RoleAddController', ['$scope', '$http', 'toaster', '$state','$stateParams',
    function ($scope, $http, toaster, $state,$stateParams) {

        var role_id=$stateParams.role_id;
        $scope.role = {};
        if(role_id==undefined){//add new
            $scope.op='添加';
        }
        else{
            $scope.op='编辑';
            $http.get('/rbac/role/'+role_id).success(function(role){
                $scope.role=role;

            });
        }


    $scope.save = function () {
        var message="";
        if ($scope.role._id==undefined || $scope.role._id==""){
            message="新增成功";
        }
        else{
            message="修改成功";
        }

        $http.post('/rbac/role', $scope.role).success(function (data, status, header, config) {

            toaster.pop('success', '确认', message);
            $state.go('app.rbac.role')

        })

    };

}]);
