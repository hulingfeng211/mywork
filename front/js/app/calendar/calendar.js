/**
 * calendarDemoApp - 0.1.3
 */

app.controller('FullcalendarCtrl', ['$scope', '$http', '$log', function ($scope, $http, $log) {

    var date = new Date();
    var d = date.getDate();
    var m = date.getMonth();
    var y = date.getFullYear();

    /* event source that pulls from google.com */
    /*$scope.eventSource = {
            url: "http://www.google.com/calendar/feeds/usa__en%40holiday.calendar.google.com/public/basic",
            className: 'gcal-event',           // an option!
            currentTimezone: 'America/Chicago' // an option!
     };*

    /* event source that contains custom events on the scope */
    $scope.events = [];
    /** [{
        title: 'All Day Event',
        start: new Date(y, m, 1),
        className: ['b-l b-2x b-info'],
        location: 'Shanghai ',
        info: '测试'
    }];*/
    $scope.eventSources=[];
    $scope.events=[];

    /**
     [
      {title:'All Day Event', start: new Date(y, m, 1), className: ['b-l b-2x b-info'], location:'New York', info:'This a all day event that will start from 9:00 am to 9:00 pm, have fun!'},
      {title:'Dance class', start: new Date(y, m, 3), end: new Date(y, m, 4, 9, 30), allDay: false, className: ['b-l b-2x b-danger'], location:'London', info:'Two days dance training class.'},
      {title:'Game racing', start: new Date(y, m, 6, 16, 0), className: ['b-l b-2x b-info'], location:'Hongkong', info:'The most big racing of this year.'},
      {title:'Soccer', start: new Date(y, m, 8, 15, 0), className: ['b-l b-2x b-info'], location:'Rio', info:'Do not forget to watch.'},
      {title:'Family', start: new Date(y, m, 9, 19, 30), end: new Date(y, m, 9, 20, 30), className: ['b-l b-2x b-success'], info:'Family party'},
      {title:'Long Event', start: new Date(y, m, d - 5), end: new Date(y, m, d - 2), className: ['bg-success bg'], location:'HD City', info:'It is a long long event'},
      {title:'Play game', start: new Date(y, m, d - 1, 16, 0), className: ['b-l b-2x b-info'], location:'Tokyo', info:'Tokyo Game Racing'},
      {title:'Birthday Party', start: new Date(y, m, d + 1, 19, 0), end: new Date(y, m, d + 1, 22, 30), allDay: false, className: ['b-l b-2x b-primary'], location:'New York', info:'Party all day'},
      {title:'Repeating Event', start: new Date(y, m, d + 4, 16, 0), alDay: false, className: ['b-l b-2x b-warning'], location:'Home Town', info:'Repeat every day'},      
      {title:'Click for Google', start: new Date(y, m, 28), end: new Date(y, m, 29), url: 'http://google.com/', className: ['b-l b-2x b-primary']},
      {title:'Feed cat', start: new Date(y, m+1, 6, 18, 0), className: ['b-l b-2x b-info']}
    ];*/
    function load_events() {
        var dt=new Date()/1000;
        var url='/events?_v='+dt.toString();
        $http.get(url).then(function (res) {

            //$scope.events=[];
           // while($scope.events.pop()){
//
          //  }
            angular.forEach(res.data, function (v) {
                $scope.events.push(v);
            });
            //$scope.eventSources = [$scope.events];
            // $scope.eventSources = [res.data];
            if(angular.isArray(res.data))
                $scope.events = res.data;
        });
    }
    //load_events();

    function save_event(e) {

        var data = {
            title: e.title,
            start: e.start,
            className: e.className,
            location: e.location,
            info: e.info,
            _id: angular.isNumber(e._id) ? "" : e._id
        };
        var url = '/events';
        $log.debug(data);
        $http.post(url, data).then(function () {
            //do nothing.
        });
    }


    /* alert on dayClick */
    $scope.precision = 400;
    $scope.lastClickTime = 0;

    $scope.alertOnEventClick = function( date, jsEvent, view ){
      var time = new Date().getTime();
      if(time - $scope.lastClickTime <= $scope.precision){
          $scope.events.push({
              _id:"",
            title: 'New Event',
            start: date,
            className: ['b-l b-2x b-info']
          });
      }
      $scope.lastClickTime = time;
    };
    /* alert on Drop */
    $scope.alertOnDrop = function(event, delta, revertFunc, jsEvent, ui, view){
        if(!is_local_event(event))
            save_event(event);
       $scope.alertMessage = ('Event Droped to make dayDelta ' + delta);
    };
    $scope.get_event_list=function(){
        load_events();

    };
    //
    function is_local_event(event){
        return angular.isNumber(event._id);
    }
    /* alert on Resize */
    $scope.alertOnResize = function(event, delta, revertFunc, jsEvent, ui, view){
        if(!is_local_event(event))
            save_event(event);
       $scope.alertMessage = ('Event Resized to make dayDelta ' + delta);
    };

    $scope.overlay = $('.fc-overlay');
    $scope.alertOnMouseOver = function( event, jsEvent, view ){
      $scope.event = event;
      $scope.overlay.removeClass('left right').find('.arrow').removeClass('left right top pull-up');
      var wrap = $(jsEvent.target).closest('.fc-event');
      var cal = wrap.closest('.calendar');
      var left = wrap.offset().left - cal.offset().left;
      var right = cal.width() - (wrap.offset().left - cal.offset().left + wrap.width());
      if( right > $scope.overlay.width() ) { 
        $scope.overlay.addClass('left').find('.arrow').addClass('left pull-up')
      }else if ( left > $scope.overlay.width() ) {
        $scope.overlay.addClass('right').find('.arrow').addClass('right pull-up');
      }else{
        $scope.overlay.find('.arrow').addClass('top');
      }
      (wrap.find('.fc-overlay').length == 0) && wrap.append( $scope.overlay );
    };

    /* config object */
    $scope.uiConfig = {
      calendar:{
        height: 450,
        editable: true,
        header:{
          left: 'prev',
          center: 'title',
          right: 'next'
        },
        dayClick: $scope.alertOnEventClick,
        eventDrop: $scope.alertOnDrop,
        eventResize: $scope.alertOnResize,
        eventMouseover: $scope.alertOnMouseOver
      }
    };
    
    /* add custom event*/
    $scope.addEvent = function() {
      $scope.events.push({
          _id:"",
        title: 'New Event',
        start: new Date(y, m, d),
        className: ['b-l b-2x b-info']
      });
    };

    /* save event */

    $scope.save=function(e){
        save_event(e);
    };
    /* remove event */
    $scope.remove = function (e) {
        //delete from db
        if (angular.isNumber(e._id)) {

            $scope.events.splice($scope.events.indexOf(e), 1);
        }
        else {
            var url = '/events/' + e._id;
            $http.delete(url).then(function () {
                $scope.events.splice($scope.events.indexOf(e), 1);
            });
        }

    };

    /* Change View */
    $scope.changeView = function(view, calendar) {
      $('.calendar').fullCalendar('changeView', view);
    };

    $scope.today = function(calendar) {
      $('.calendar').fullCalendar('today');
    };

    /* event sources array*/
    $scope.eventSources = [$scope.events];

    /**
     $scope.$watchCollection('events', function (newValue) {
        angular.forEach(newValue, function (event) {

            save_event(event)
        })

    });*/
}]);
/* EOF */