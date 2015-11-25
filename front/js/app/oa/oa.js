app.controller('OACtrl', ['$scope', '$http','toaster','$window', function ($scope, $http,toaster,$window) {

    $scope.statuses = [
        {"name":"未开封","color":"primary",'value':0},
        {"name":"未确认","color":"warning",'value':1},
        {"name":"已确认","color":"success",'value':2}
    ];
    $scope.status=$scope.statuses[1];

    var page_per=8;//每页显示8条记录
    $scope.circulations=[];
    $scope.showMore=true;
    $scope.comment='';

    function get_cirulations(i_status,lastDate) {

        var url = '/circulations?status=' + i_status.toString();
        if(lastDate!=null||lastDate!=''){
            url=url+'&last='+lastDate;
        }
        $http.get(url).then(function (resp) {

            //$scope.circulations = resp.data;
            if (resp==null||resp.data == null || resp.data[0] == undefined){
                $scope.showMore=false;
                return;
            }
            $scope.showMore=true;
            // 初始化UI元素
            angular.forEach(resp.data,function(item){
                item.color=$scope.colors[i_status];
                $scope.circulations.push(item);
            });
            var circulations_length=$scope.circulations.length;
            $scope.lastCirculation=$scope.circulations[circulations_length-1];

            /**angular.forEach($scope.circulations,function(item){
                item.color=$scope.colors[i_status];
            });*/

            $scope.circulation=$scope.circulations[0];
            $scope.circulations[0].selected=true;
            get_criculation_detail($scope.circulation);
            get_reciver_list();
            get_comments_list();
        });
    }


    get_cirulations(1,'');
    $scope.show_more_click=function(){
        if($scope.lastCirculation!=null){
            get_cirulations($scope.status.value,$scope.lastCirculation.CDate);
        }
        else{
            $scope.showMore=false;
        }
    };
    $scope.status_click = function (status) {
        $scope.status=status;
        $scope.circulations=[];//clear list
        get_cirulations(status.value,'');

    };
    $scope.colors = ['primary',  'warning', 'success'];


    $scope.deleteNote = function (note) {
        $scope.notes.splice($scope.notes.indexOf(note), 1);
        if (note.selected) {
            $scope.note = $scope.notes[0];
            $scope.notes.length && ($scope.notes[0].selected = true);
        }
    };

    $scope.selectCirculation = function (circulation) {
        angular.forEach($scope.circulations, function (circulation) {
            circulation.selected = false;
        });
        $scope.circulation = circulation;
        $scope.circulation.selected = true;
        get_criculation_detail($scope.circulation);
    };
    $scope.view_online_file = function (fileInfo) {
        var url = '/circulation/attachfile';
        var data = {
            fileName: fileInfo.FileName,
            filePath: fileInfo.FilePath
        };
        toaster.pop('wait','浏览附件','正在打开附件，请稍后...',90000000);
        $http.post(url, data).then(function (res) {
            toaster.clear();
            $window.open(res.data, '_blank');
        },function(res){
            //$window.alert('在线浏览失败');
            toaster.clear();
            toaster.pop('warning','浏览附件','浏览附件失败，请联系管理员');
        });

    };
    $scope.add_comment=function(){
        var url='/circulation/comments/'+$scope.circulationDetail.MsgserId;
        var data ={'comment':$scope.comment};
        $http.post(url,data).then(function(res){
            toaster.pop('success','评论','评论成功');
            $scope.comment='';
            get_comments_list();
        });

    };
    $scope.comment_tab_selected= function () {
        toaster.pop('success','评论','selected');
        $scope.comment='';


    };
    function get_criculation_detail(circulation){
         $http.get('/circulations/' + circulation.MsgserId).then(function (resp) {

            $scope.circulationDetail = resp.data;
            // set default
            get_reciver_list();
            get_comments_list();

        });
    }
    function change_reciver_page(newValue) {
        $scope.current_page_reciver = [];
        angular.forEach($scope.recivers, function (reciver, i) {
            if (i >= page_per * (newValue - 1) && i < page_per * newValue) {
                $scope.current_page_reciver.push(reciver);
            }
        });
    }

    //获取传阅人列表
    function get_reciver_list() {
        var reciver_user_url = "/circulation/" + $scope.circulation.MsgserId + "/user";
        $http.get(reciver_user_url).then(function (res) {
            $scope.recivers = res.data;
            $scope.current_page_no = 1;
            $scope.totalItems = $scope.recivers.length;
            $scope.maxSize = page_per;
            $scope.numPages = Math.floor($scope.totalItems / page_per);
            //change_reciver_page(1);
            $scope.$watch('current_page_no', function (newValue, oldValue) {
                //if(newValue==oldValue)
                //    return;
                change_reciver_page(newValue);
                //$scope.$apply();
            },true);

        });
    }

    //获取讨论列表
    function get_comments_list(){
        url='/circulation/comments/'+$scope.circulation.MsgserId;
        $http.get(url).then(function(res){
            $scope.comments=res.data;

        });
    }



}]);