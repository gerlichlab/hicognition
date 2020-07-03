function draw(minval, pivot1, pivot2 , maxval){
    var colorScale = d3.scaleLinear()
        .range(["white", "orange", "red" ,"black"])
        .domain([minval, pivot1, pivot2 ,maxval])
    picture.style("fill", function(d) { return colorScale(d.value); });
}

$( "#slider" ).slider({
    range: true,
    min: 0,
    max: 200,
    values: [0, 200],
    slide: function( event, ui ) {
      var minval = ui.values[0];
      var maxval = ui.values[1];
      draw(minval, (minval + maxval) / 3, 2 * (minval + maxval) / 3 ,maxval);
    }
});

