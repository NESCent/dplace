/*
 * This service wraps a singleton object that keeps track of user's
 * search UI state across controllers
 * @constructor
 */
function SearchModelService(VariableCategory, GeographicRegion, EnvironmentalCategory, LanguageClass, DatasetSources) {
    this.model = new SearchModel(VariableCategory, GeographicRegion, EnvironmentalCategory, LanguageClass, DatasetSources);
    this.getModel = function() {
        return this.model;
    }
    
}
