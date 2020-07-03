function draw(minval, pivot1, pivot2 , maxval){
    var colorScale = d3.scaleLinear()
        .range(["white", "orange", "red" ,"black"])
        .domain([minval, pivot1, pivot2 ,maxval])
    picture.style("fill", function(d) { return colorScale(d.value); });
    // update slider text
    document.getElementById("sliderText").innerHTML = `Values: ${minval}-${maxval}`;
}

$( "#slider" ).slider({
    range: true,
    min: 0,
    max: 20,
    values: [0, 20],
    slide: function( event, ui ) {
      var minval = ui.values[0];
      var maxval = ui.values[1];
      draw(minval, minval + (maxval - minval)/3, minval + 2 * (maxval - minval) / 3 ,maxval);
    }
});

