function ColorMapService() {
    function mapColor(index, count) {
        var hue = index * 240 / count;
        return 'hsl(' + hue + ',100%,50%)';
    }

    this.generateColorMap = function(keys) {
        var colors = {};
        for(var i=0;i<keys.length;i++) {
            var color = mapColor(i, keys.length);
            colors[keys[i]] = color;
        }
        return colors;
    };
}
