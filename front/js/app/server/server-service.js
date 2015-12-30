/**
 * Created by george on 12/30/15.
 */
app.factory("ServerService", ["$resource", function ($resource) {
    return $resource("/servers/:id");

}]);