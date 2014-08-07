/*
 * This service wraps a singleton object that keeps track of user's
 * search UI state across controllers
 * @constructor
 */
function SearchModelService(VariableCategory, GeographicRegion, EnvironmentalVariable, LanguageClass) {
    this.model = new SearchModel(VariableCategory, GeographicRegion, EnvironmentalVariable, LanguageClass);
    this.getModel = function() {
        return this.model;
    }
}
