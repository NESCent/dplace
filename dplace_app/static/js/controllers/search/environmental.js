function EnvironmentalCtrl($scope, searchModelService, EnvironmentalVariable, EnvironmentalValue, MinAndMax, CodeDescription) {
    var linkModel = function() {
        // Get a reference to the environmental search params from the model
        $scope.environmentalData = searchModelService.getModel().getEnvironmentalData();
        if ($scope.environmentalData.selectedVariables.length == 0) {
            $scope.environmentalData.selectedVariables.push({'vals': ['', ''], 'selectedFilter': $scope.environmentalData.selectedFilter, 'variables': []});
        }
            
    };
    $scope.$on('searchModelReset', linkModel); // When model is reset, update our model
    linkModel();
    
    $scope.categoryChanged = function(variable) {
        variable.variables = EnvironmentalVariable.query({index_categories: [variable.selectedCategory.id]});
    };
    
    $scope.addVariable = function() {
        $scope.environmentalData.selectedVariables.push({'vals': ['', ''], 'selectedFilter': $scope.environmentalData.selectedFilter, 'variables': []});
    };
    
    $scope.variableChanged = function(variable) {
        if(variable.selectedVariable != null) {
            if (variable.selectedVariable.data_type == 'Categorical') variable.selectedVariable.selected = [];
            variable.selectedVariable.codes = CodeDescription.query({variable: variable.selectedVariable.id });
            $scope.environmentalData.badgeValue = $scope.environmentalData.selectedVariables.map(function(e) { return e.selectedVariable != null; }).length;
            variable.EnvironmentalForm.$setPristine();
            $scope.values = MinAndMax.query({query: {environmental_id: variable.selectedVariable.id}});
            $scope.filterChanged(variable);
        }
    };
    
    $scope.codeSelected = function(variable, code) {
        if (code.isSelected) {
            if (variable.selected.map(function(v) { return v.id; }).indexOf(code.id) == -1) {
                variable.selected.push(code);
            }
        } else {
            variable.selected.splice(variable.selected.indexOf(code), 1);
        }
        if (variable.selected.length == variable.codes.length) variable.allSelected = true;
        else variable.allSelected = false;

    }
    
    $scope.selectAll = function(variable) {
        if (variable.allSelected) {
            variable.codes.forEach(function(c) {
                c.isSelected = true;
                if (variable.selected.map(function(v) { return v.id; }).indexOf(c.id) == -1) variable.selected.push(c);
            });
        } else {
            variable.codes.forEach(function(c) {
               c.isSelected = false;
               variable.selected.splice(variable.selected.indexOf(c), 1);
            });
        }
    };
    
    $scope.filterChanged = function(variable) {
        if (variable.EnvironmentalForm.$dirty && variable.selectedFilter.operator != 'all') return;
            selected_variable = $scope.environmentalData.selectedVariables.filter(function(env_var) {
            return env_var.selectedVariable == variable.selectedVariable;
        });
        if (selected_variable.length == 1) {
            $scope.values.$promise.then(function(result) {
                selected_variable[0].vals[0] = result.min;
                selected_variable[0].vals[1] = result.max;
            });
        }
        
    };
    
    //gets the range of environmental values if the user selects 'all values'
    $scope.doSearch = function() {
        $scope.search();
    };
}