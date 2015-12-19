/**
 * Created by george on 12/16/15.
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
app.controller('TaskCtrl', ['$scope', 'ProjectService', 'LabelService',
    function ($scope, ProjectService, LabelService) {

        $scope.projects = ProjectService.query();

        $scope.labels = LabelService.query();
        $scope.add_project = function () {
            var project = {
                name: $scope.newProject.name,
                filter: angular.lowercase($scope.newProject.name),
                color: '#ccc'
            };
            $scope.projects.push(project);
            ProjectService.save(project);
            $scope.newProject.name = '';
        };
        $scope.delete_project = function (project) {
            ProjectService.delete({id: project._id});
            //todo

        };
        $scope.addLabel = function () {
            var newLabel = {
                name: $scope.newLabel.name,
                filter: angular.lowercase($scope.newLabel.name),
                color: '#ccc'
            };
            $scope.labels.push(newLabel);
            LabelService.save(newLabel);
            $scope.newLabel.name = '';
        };

        $scope.labelClass = function (label) {
            return {
                'b-l-info': angular.lowercase(label) === 'angular',
                'b-l-primary': angular.lowercase(label) === 'bootstrap',
                'b-l-warning': angular.lowercase(label) === 'client',
                'b-l-success': angular.lowercase(label) === 'work'
            };
        };

    }]);

app.controller('TaskListCtrl', ['$scope', '$stateParams', 'TaskService',
    function ($scope, $stateParams, TaskService) {
        $scope.project = $stateParams.project;
        $scope.label = $stateParams.label;

        function query_tasks() {


            //var expression = {q: '{"project":'+$scope.project+'",labels":{"$all":["' + $scope.label + '"]}}'};
            var expression={};

            if(angular.isDefined($scope.project)){
                expression['project']=$scope.project;
            }
            if(angular.isDefined($scope.label)){
                expression['labels']={"$all":[$scope.label]}
            }
            var q={q:JSON.stringify(expression).toString()};
            $scope.tasks=TaskService.query(q);


            /**
            if (angular.isDefined($scope.label)) {
                $scope.tasks = TaskService.query(expression);
                return;
            }
            if (angular.isDefined($scope.project)) {
                $scope.tasks = TaskService.query({project: $scope.project});
                return;
            }
             */

        }
        query_tasks();
        $scope.refresh_task=query_tasks;


        $scope.delete_task=function(task){
            TaskService.delete({"id": task._id});
            var eIndex = $scope.tasks.indexOf(task);
            if(eIndex>-1){
                $scope.tasks.splice(eIndex,1);

            }
        }

    }]);


app.controller('TaskDetailCtrl', ['$scope', 'TaskService', '$stateParams', function ($scope, TaskService, $stateParams) {

    $scope.task=TaskService.get({"id":($stateParams.taskId)});

}]);

app.controller('TaskNewCtrl', ['$scope', 'ProjectService', 'LabelService', 'TaskService','$state','$filter',
    function ($scope, ProjectService, LabelService, TaskService,$state,$filter) {


        var empty_task = {
            name: '',
            project: '',
            labels: [],
            complete: false,
            start:$filter('date')(new Date(),'short'),
            end: $filter('date')(new Date(),'short'),
            comment: '',
            status: ''
        };
        $scope.task = empty_task;
        $scope.dateOptions = {
            formatYear: 'yyyy',
            startingDay: 1,
            class: 'datepicker'
        };
        $scope.format = 'yyyy-MM-dd';
        $scope.start = new Date();
        $scope.end = new Date();

        $scope.open_start = function ($event) {
            $event.preventDefault();
            $event.stopPropagation();

            $scope.start_opened = true;
        };
        $scope.open_end = function ($event) {
            $event.preventDefault();
            $event.stopPropagation();

            $scope.end_opened = true;
        };

        $scope.today = function () {
            if ($scope.start_opened) {
                $scope.dt_start = new Date();
            }
            if ($scope.end_opened) {
                $scope.dt_end = new Date();
            }
            $scope.dt = new Date();
        };
        $scope.today();

        $scope.clear = function () {
            if ($scope.start_opened) {
                $scope.task.start = null;
            }
            if ($scope.end_opened) {
                $scope.task.end = null;
            }
        };
        $scope.save_task = function () {
            TaskService.save($scope.task);
            $scope.task = empty_task;
            $state.go('app.task.list');

        };
        $scope.lables = LabelService.query();
        $scope.projects =ProjectService.query({'_v':new Date()/1000});

    }]);

angular.module('app').directive('labelColor', function () {
    return function (scope, $el, attrs) {
        $el.css({'color': attrs.color});
    }
});