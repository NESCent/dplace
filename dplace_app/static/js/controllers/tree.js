function TreeCtrl($scope,  NewickTree, Variable, EnvironmentalVariable, CodeDescription, FindSocieties, TreesFromLanguages, getTree, GetBins) {
    $scope.setActive('tree');
    $scope.cultureVariables = Variable.query();
    $scope.environmentalVariables = EnvironmentalVariable.query();
    $scope.selected = '';
    $scope.trait = '';
    $scope.isocodes = []; 
    $scope.results = []; 
    $scope.bins = [];
    $scope.languageTrees = [];
    $scope.query = {};
    
    //basic code to download tree
    $scope.download = function() {        
        //get all the trees on the page, loop through them and trigger download
        var trees = d3.select("#trees").selectAll("svg")
            .attr("version", 1.1)
            .attr("xmlns", "http://www.w3.org/2000/svg");
        trees = trees[0];
        var selectedVar = $scope.selectedVariable ? $scope.selectedVariable.name : $scope.selectedEnvVariable.name;
        
        for (var i = 0; i < trees.length; i++) {
            var name = trees[i].parentNode.id; //name of svg file is name of tree
            var html = trees[i].parentNode.innerHTML;
            var imgsrc = 'data:image/svg+xml;base64,' + btoa(html);
            var img = '<img src="' + imgsrc + '">';
            //open("data:image/svg+xml," + encodeURIComponent(html));
            var a = d3.select("#downloadLinks").append("a")
                .attr("download", selectedVar+" "+name+".svg")
                .attr("href", imgsrc);
            a[0][0].click();
      } 
    };
    
    $scope.resetVariables = function() {
        $scope.code_ids = [];
        $scope.results = [];
        $scope.isocodes =  [];
    };
    
    $scope.varChanged = function() {
        d3.select("#trees").html('');
        $scope.query = {};
        $scope.bins = [];
        $scope.languageTrees = [];
        $scope.selected = $scope.selectedVariable.id;
        $scope.selectedEnvVariable = '';
        $scope.trait = CodeDescription.query({variable: $scope.selected });
    };
    
    $scope.envVarChanged = function() {
        d3.select("#trees").html('');
        $scope.trait = [];
        $scope.query = {};
        $scope.languageTrees = [];
        $scope.selectedVariable = '';
        $scope.selected = $scope.selectedEnvVariable.id;
        $scope.query['environmental_filters'] = [{id: $scope.selected, operator: 'all'}];
        $scope.bins = GetBins.query({query: JSON.stringify({variable_id: $scope.selected})});
       
    };

     $scope.doSearch = function() {
        $scope.searchButton.disabled = true;
        $scope.searchButton.text = 'Working...';
        $scope.resetVariables();
        $scope.trait.forEach(function(trait) {
            $scope.code_ids.push(trait.id);
        });
        if ($scope.code_ids.length > 0) $scope.query['variable_codes'] = $scope.code_ids;

        d3.select("#trees").html('');

        $scope.bins.forEach(function(bin) {
            $scope.code_ids.push(bin.code);
            $scope.trait.push({'code':bin.code, 'description': bin.min + '-' + bin.max + ' ' + $scope.selectedEnvVariable.units});
        });
        
        $scope.languageTrees = getTree.query({query:JSON.stringify($scope.query)});
        $scope.languageTrees.$promise.then(function(result) {
            for (var i = 0; i < result.isocodes.length; i++) {
                //$scope.isocodes.push(result.isocodes[i].isocode);  //needed to prune trees using JavaScript
                $scope.results.push(result.isocodes[i]);
            }
            if (result.trees) {
                for (var i = 0; i < result.trees.length; i++) {
                    $scope.constructTree(result.trees[i]);
                }
            }
            $scope.searchButton.disabled = false;
            $scope.searchButton.text = 'Search';
            
       });
    };
    
    $scope.constructTree = function(langTree) {
        var newick = Newick.parse(langTree.newickTree);
        //code below uses JavaScript to prune trees instead of ete2 - keeping just in case
       /* $scope.searchBranches(newick.branchset, newick);
        $scope.deleteParents(newick, newick.branchset);
        $scope.deleteChildrenOfRoot(newick);*/
        
        var rightAngleDiagonal = function() {
            function diagonal(diagonalPath) {
                var source = diagonalPath.source,
                    target = diagonalPath.target,
                    pathData = [source, {x: target.x, y: source.y}, target].map(function(d) { return [d.y, d.x]; });
                return "M" + pathData[0] + ' ' + pathData[1] + ' ' + pathData[2];
            }
            return diagonal;
        }
        
        var w = 700;
        var tree = d3.layout.cluster().children(function(node) { return node.branchset; });
        var nodes = tree(newick);
        
        var h = nodes.length * 9; //height depends on # of nodes
        
        tree = d3.layout.cluster()
            .size([h, w])
            .sort(function comparator(a, b) { return d3.ascending(a.length, b.length); })
            .children(function(node) { return node.branchset; })
            .separation(function separation(a, b) { return 8; });
         
        nodes = tree(newick);
        
        d3.select("#trees").append("h4")
            .text(langTree.name);
        
        var divName = langTree.name.replace(/\W/g, '') //remove any non-alphanumeric characters from the name
        
        d3.select("#trees").append("div")
            .attr("id", divName);
         
        var vis = d3.select("#"+divName).append("svg:svg")
            .attr("width", w+300)
            .attr("height", h+30)
            .append("svg:g")
            .attr("transform", "translate(40, 0)");

        var diagonal = rightAngleDiagonal();
            nodes.forEach(function(node) {
            node.rootDist = (node.parent ? node.parent.rootDist : 0) + (node.length || 0);
        });
        var rootDists = nodes.map(function(n) { return n.rootDist; });
        var yscale = d3.scale.linear()
            .domain([0, d3.max(rootDists)])
            .range([0, w]);
        nodes.forEach(function(node) {
            node.y = yscale(node.rootDist);
        });
        var links = tree.links(nodes);
        var link = vis.selectAll("path.link")
            .data(links)
            .enter().append("svg:path")
            .attr("class", "link")
            .attr("d", diagonal)
            .attr("fill", "none")
            .attr("stroke", "#ccc")
            .attr("stroke-width", "4px")
        var node = vis.selectAll("g.node")
            .data(nodes)
            .enter().append("svg:g")
            .attr("transform", function(d) { return "translate(" + d.y + ", "+ d.x + ")"; });
        node.append("svg:text")
            .attr("dx", 10)
            .attr("dy", 4)
            .attr("font-size", "14px")
            .attr("font-family", "Arial")
            .text(function(d) { return d.name; });
        $scope.results.forEach(function(code) {
            var selected = node.filter(function(d) {
                return d.name == code.isocode;
            });
            selected.append("svg:circle")
                .attr("r", 4.5)
                .attr("stroke", "#000")
                .attr("stroke-width", "0.5")
                .attr("fill", function(n) {
                    var hue = code.result * 240 / $scope.code_ids.length;
                    return 'hsl('+hue+',100%, 50%)';
                })
            });
        };
    
    //deletes a node from the tree
    $scope.deleteNode = function(branchset, toDelete) {
        indexToDelete = branchset.indexOf(toDelete);
        branchset.splice(indexToDelete, 1); 
    };
    
    //deletes parents of nodes
    $scope.deleteParents = function(newick, branchset) {
        for (var i = 0; i < branchset.length; i++) {
            if (branchset[i].branchset && branchset[i].branchset.length == 0) {
                if ($scope.getParent(newick.branchset, branchset[i])) {
                    $scope.deleteNode($scope.getParent(newick.branchset, branchset[i]).branchset, branchset[i]);
                    $scope.deleteParents(newick, newick.branchset);
                } 
            } else if (branchset[i].branchset) {
                $scope.deleteParents(newick, branchset[i].branchset);
            }
        }
    };
    
    //deletes any empty children of the root
    //this must be called last - after deleteParents
    $scope.deleteChildrenOfRoot = function(newick) {
        for (var i = 0; i < newick.branchset.length; i++) {
            if (newick.branchset[i].branchset.length == 0) {
                $scope.deleteNode(newick.branchset, newick.branchset[i]);
            }
        }
    };
    
    //returns the parent of a node
    //we don't have access to node.parent when we are pruning the tree
    $scope.getParent = function(branchset, node) { 
        for (var i = 0; i < branchset.length; i++) {
            if (branchset[i].branchset) {
                if (branchset[i].branchset.indexOf(node) != -1) {
                    return branchset[i];
                } else {
                    var result = $scope.getParent(branchset[i].branchset, node);
                    if (result) return result;
                }
            }                
        }
    };
    
    //go through branches and delete societies that don't have data
    $scope.searchBranches = function(branchset, parent) {
        for (var i = 0; i < branchset.length; i++) {
            if (branchset[i]) {
                if (branchset[i].branchset) {
                    $scope.searchBranches(branchset[i].branchset, branchset);
                } else {    
                    //if the node is not in the array, then delete it
                    //branchset[i] = a leaf node
                    if ($scope.isocodes.indexOf(branchset[i].name) == -1) {               
                        $scope.deleteNode(branchset, branchset[i]);
                        i--;
                    }
                }
            } 
        } 
    };
}