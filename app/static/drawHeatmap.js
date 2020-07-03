// Add heatmap
// set the dimensions and margins of the graph

var widthElement = document.getElementById("heatmap").offsetWidth;
var heightElement = document.getElementById("heatmap").offsetHeight;

var margin = {top: 30, right: 30, bottom: 30, left: 30},
  width = widthElement - margin.left - margin.right,
  height = heightElement - margin.top - margin.bottom;

// append the svg object to the body of the page
var svg = d3.select("#heatmap")
.append("svg")
  .attr("width", width + margin.left + margin.right)
  .attr("height", height + margin.top + margin.bottom)
.append("g")
  .attr("transform",
        "translate(" + margin.left + "," + margin.top + ")");

// Labels of row and columns

var myGroups = new Array(90);
var myVars = new Array(90);

for (let dummy = 0; dummy < 90; dummy++){
  myGroups[dummy] = String(dummy);
  myVars[dummy] = String(90 - dummy);
}

// Build X scales and axis:
var x = d3.scaleBand()
  .range([ 0, width ])
  .domain(myGroups)
  .padding(0.01);
svg.append("g")
  .attr("transform", "translate(0," + height + ")")
  .call(d3.axisBottom(x))

// Build y scales and axis:
var y = d3.scaleBand()
  .range([ height, 0 ])
  .domain(myVars)
  .padding(0.01);
svg.append("g")
  .call(d3.axisLeft(y));

// Build color scale
var myColor = d3.scaleLinear()
  .range(["white", "orange", "red" ,"black"])
  .domain([0, 6.6, 13.2 , 20])


// declare variable so that it is available to the slider adjustment logic
var picture

//Read the data


d3.csv("http://localhost:5000/static/pileup_test.csv", function(data){
      console.log(data)
      // create a tooltip
      var tooltip = d3.select("#heatmap")
      .append("div")
      .style("opacity", 0)
      .attr("class", "tooltip")
      .style("background-color", "white")
      .style("border", "solid")
      .style("border-width", "2px")
      .style("border-radius", "5px")
      .style("padding", "5px")

      // Three function that change the tooltip when user hover / move / leave a cell
      var mouseover = function(d) {
      tooltip.style("opacity", 1)
      }
      var mousemove = function(d) {
      tooltip
          .html("The exact value of<br>this cell is: " + d.value)
          .style("left", (d3.mouse(document.body)[0]) + "px")
          .style("top", (d3.mouse(document.body)[1]) + "px");
      }
      var mouseleave = function(d) {
      tooltip.style("opacity", 0)
      }

      // add the squares
      picture = svg.selectAll()
                  .data(data, function(d) {return d.variable+':'+d.group;})
                  .enter()
                  .append("rect")
                      .attr("x", function(d) { return x(d.group) })
                      .attr("y", function(d) { return y(d.variable) })
                      .attr("width", x.bandwidth() )
                      .attr("height", y.bandwidth() )
                      .style("fill", function(d) { return myColor(d.value)} )
                  .on("mouseover", mouseover)
                  .on("mousemove", mousemove)
                  .on("mouseleave", mouseleave)
    });
// update slider text

document.getElementById("sliderText").innerHTML = `Values: 0-20`;