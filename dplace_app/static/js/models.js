/**
 * Objects for containing search UI state
 * Created by dan on 7/30/14.
 */

function SearchModel(VariableCategory, GeographicRegion, EnvironmentalVariable) {
    this.reset = function() {
        this.selectedButton = null;
        this.results = {}; // Populated after search is run
        this.params = {}; // state for individual controllers
        this.query = {}; // Parameters sent to the FindSocieties API
        this.results.societies = [];
        this.params.culturalTraits = new CulturalTraitModel(VariableCategory);
        this.params.geographicRegions = new GeographicRegionModel(GeographicRegion);
        this.params.environmentalData = new EnvironmentalDataModel(EnvironmentalVariable);
    };

    // getters
    this.getCulturalTraits = function() {
        return this.params.culturalTraits;
    };
    this.getGeographicRegions = function() {
        return this.params.geographicRegions;
    };
    this.getEnvironmentalData = function() {
        return this.params.environmentalData;
    };

    // Includes the search query
    this.getResults = function() {
        return this.results;
    };

    // Just the societies object
    this.getSocieties = function() {
        return this.results.societies;
    };

    this.reset();
}

// Cultural trait search
// Depends on VariableCategory for initial load. Somewhat messy, requires entire model to know about that API
function CulturalTraitModel(VariableCategory) {
    this.categories = VariableCategory.query(); // these objects get annotated with variables
    this.selectedCategory = null;
    this.selectedVariable = null;
}

function GeographicRegionModel(GeographicRegion) {
    this.selectedRegions = [];
    this.allRegions = GeographicRegion.query();
}

function EnvironmentalDataModel(EnvironmentalVariable) {
    this.variables = EnvironmentalVariable.query();
    this.selectedVariable = null;
    this.filters = [
        { operator: 'inrange', name: 'between' },
        { operator: 'lt', name: 'less than'},
        { operator: 'gt', name: 'greater than'},
        { operator: 'outrange', name: 'outside'},
    ];
    this.selectedFilter = this.filters[0];
    this.vals = [];
}