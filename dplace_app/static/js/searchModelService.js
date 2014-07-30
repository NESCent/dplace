/*
 * This service wraps a singleton object that keeps track of user's
 * search UI state across controllers
 * @constructor
 */
function SearchModelService(VariableCategory, GeographicRegion, EnvironmentalVariable) {
    this.model = new SearchModel(VariableCategory, GeographicRegion, EnvironmentalVariable);
    this.getModel = function() {
        return this.model;
    }
}
