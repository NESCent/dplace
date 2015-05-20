function SocietiesCtrl($scope, searchModelService, LanguageClass, ZipTest) {
    $scope.results = searchModelService.getModel().getResults();
    $scope.query = searchModelService.getModel().getQuery();
    console.log($scope.query);
    console.log($scope.results);
    $scope.variables = [];
    $scope.buttons = [
        {value:'phylogeny', name:'Phylogenies'},
        {value:'glottolog', name:'Glottolog Trees'},
    ];
    
    if ($scope.results.variable_descriptions) {
        $scope.variables = $scope.variables.concat($scope.results.variable_descriptions);
    }
        
    if ($scope.query.environmental_filters) {
        $scope.variables = $scope.variables.concat($scope.results.environmental_variables);
        $scope.results.code_ids[$scope.results.environmental_variables[0].id] = [];
        var extractedValues = $scope.results.societies.map(function(society) { return society.environmental_values[0].value; } );
        var min_value = Math.min.apply(null, extractedValues);
        var max_value = Math.max.apply(null, extractedValues);
        $scope.range = max_value - min_value;
    }
    for (var key in $scope.results.code_ids) {
        $scope.results.code_ids[key]['svgSize'] = $scope.results.code_ids[key].length * 27;
    }
    
    $scope.setActive('societies');

    $scope.resizeMap = function() {
        $scope.$broadcast('mapTabActivated');
    };
    
    $scope.buttonChanged = function(buttonVal) {
        d3.select('language-phylogeny').html('');
        if (buttonVal.indexOf('phylogeny') != -1) {
            $scope.trees = $scope.results.language_trees.phylogenies;
        } else {
            $scope.trees = $scope.results.language_trees.glotto_trees;
        }
    };
    
    $scope.treeSelected = function() {
        $scope.$broadcast('treeSelected', {tree: $scope.results.selectedTree});
        d3.select(".tree-download").html('');
        $scope.treeDownload();
    };

    $scope.treeDownload = function() {
        var tree_svg = d3.select(".phylogeny")
            .attr("version", 1.1)
            .attr("xmlns", "http://www.w3.org/2000/svg")
            .node().parentNode.innerHTML;
         tree_svg = tree_svg.substring(tree_svg.indexOf("<svg xml"));
         tree_svg = tree_svg.substring(0, tree_svg.indexOf("</svg>"));
         tree_svg = tree_svg.concat("</svg>");
         var legends = [];
         var all_legends = [];

        legends = legends.concat(d3.selectAll('.bffalse'));
        if ($scope.results.classifications) {
            legends = legends.concat(d3.selectAll('.tree-legend-langs'));
        }
        for (var key in $scope.results.code_ids){
            if ($scope.results.code_ids[key].bf_var)
                all_legends.push(d3.select('.bf-cont-gradient').node());
        }
        
        html_legends = [legends.length];
        
        for (var i = 0; i < legends.length; i++) {
            for (var j = 0; j < legends[i].length; j++) {
                all_legends.push(legends[i][j]);
            }
        }

        count = 0;
        for (var key in $scope.results.code_ids) {
            all_legends[count].name = $scope.results.code_ids[key].name;
            count++;
        }
        
        legends = [];
        for (var i = 0; i < all_legends.length; i++) {
            legend = all_legends[i].innerHTML;
            html_legends[i] = legend;
            if (all_legends[i].name)
                svg_string = '<g transform="translate(5, 20)"><text>'+all_legends[i].name+'</text><g transform="translate(0,20)">'+legend+"</g></g>";
            else                
                svg_string = '<g transform="translate(5, 20)">'+legend+"</g>";
            svg_string = '<svg version="1.1" xmlns="http://www.w3.org/2000/svg">'+svg_string+'</svg>';
            if (all_legends[i].name)
                legends.push({'name': all_legends[i].name, 'svg':svg_string});
            else
                legends.push({'name': 'Legend', 'svg':svg_string});

        }
        query = {"legends": legends, "tree":tree_svg};
        d3.select(".tree-download").append("a")
            .attr("class", "btn btn-info btn-dplace-download")
            .attr("download", "legend.svg")
            .attr("href", "/api/v1/zip_legends?query="+encodeURIComponent(JSON.stringify(query)))
            .html("Download this phylogeny");
    };
    
    $scope.changeMap = function(chosenVariable) {
        chosenVariableId = chosenVariable.id;
        d3.select(".legend-for-download").html('');
    }

    $scope.generateDownloadLinks = function() {
        // queryObject is the in-memory JS object representing the chosen search options
        var queryObject = searchModelService.getModel().getQuery();
        // the CSV download endpoint is a GET URL, so we must send the query object as a string.
        var queryString = encodeURIComponent(JSON.stringify(queryObject));
        // format (csv/svg/etc) should be an argument, and change the endpoint to /api/v1/download
        $scope.csvDownloadLink = "/api/v1/csv_download?query=" + queryString;
    };
}
