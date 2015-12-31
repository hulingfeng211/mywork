/**
 * Created by george on 12/30/15.
 */
app.factory("SettingsService", ["$resource", function ($resource) {
    return $resource("/settings/:id");

}]);