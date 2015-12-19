/**
 * Created by george on 12/16/15.
 */
app.factory('mails', ['$http', function ($http) {
  var path = 'js/app/mail/mails.json';
  var mails = $http.get(path).then(function (resp) {
    return resp.data.mails;
  });

  var factory = {};
  factory.all = function () {
    return mails;
  };
  factory.get = function (id) {
    return mails.then(function(mails){
      for (var i = 0; i < mails.length; i++) {
        if (mails[i].id == id) return mails[i];
      }
      return null;
    })
  };
  return factory;
}]);
app.factory("TaskService", ["$resource", function ($resource) {
    return $resource("/tasks/:id");

}]);
app.factory("ProjectService", ["$resource", function ($resource) {
    return $resource("/projects/:id");

}]);
app.factory("LabelService", ["$resource", function ($resource) {
    return $resource("/labels/:id");

}]);