import * as d3 from "d3";

// Dimensions
const margin = { top: 20, right: 30, bottom: 30, left: 40 };
const width = 1200 - margin.left - margin.right;
const height = 400 - margin.top - margin.bottom;

// Create SVG
const svg = d3.select("#chart")
    .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

// Load CSV data
Promise.all([
    d3.csv("./Data/Finnish_PISA_Reading_Results.csv"),
    d3.csv("./Data/Milestones.csv")
]).then(([data, milestones]) => {
    // Parse main data (reading results)
    const parseDate = d3.timeParse("%d.%m.%Y");
    data.forEach(d => {
        d.Date = parseDate(d.Date);
        d.Score = +d.Reading;
    });

    // Parse milestone data
    milestones.forEach(m => {
        m.Date = parseDate(m.Date);
    });

    console.log(data, milestones);

    // Scales
    const x = d3.scaleTime()
        .domain(d3.extent(data, d => d.Date))
        .range([0, width]);

    const y = d3.scaleLinear()
        .domain([470, 560])
        .range([height, 0]);

    // Axes
    svg.append("g")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(x).ticks(d3.timeYear.every(1))); // Show every year

    svg.append("g")
        .call(d3.axisLeft(y));

    // Line generator
    const line = d3.line()
        .x(d => x(d.Date))
        .y(d => y(d.Score));

    // Draw initial line
    const path = svg.append("path")
        .datum(data)
        .attr("class", "line")
        .attr("d", line)
        .style("fill", "none")
        .style("stroke", "steelblue")
        .style("stroke-width", 2)
        .attr("stroke-dasharray", function () {
            const length = this.getTotalLength();
            return `${length} ${length}`;
        })
        .attr("stroke-dashoffset", function () {
            return this.getTotalLength();
        });

    // Add circles for each data point (initially hidden)
    svg.selectAll("circle")
        .data(data)
        .enter()
        .append("circle")
        .attr("cx", d => x(d.Date))
        .attr("cy", d => y(d.Score))
        .attr("r", 3)
        .style("fill", "#E63A20")
        .style("opacity", 0);

    // Resolve overlapping flags with reduced height differences
    let previousY = -30; // Initial y-position for the first milestone
    milestones.sort((a, b) => a.Date - b.Date); // Sort milestones by date

    milestones.forEach((milestone, i) => {
        const xPosition = x(milestone.Date);
        if (i > 0) {
            // Adjust Y position to prevent overlap, but reduce differences
            const diff = Math.abs(xPosition - x(milestones[i - 1].Date));
            if (diff < 100) {
                previousY -= 20; // Reduced upward shift
            } else {
                previousY = -30; // Reset for sufficiently spaced milestones
            }
        }
        milestone.yOffset = Math.max(previousY, -height + 50); // Prevent flags from going off-screen
    });

// Add milestone flags (initially hidden)
const flags = svg.selectAll(".milestone")
    .data(milestones)
    .enter()
    .append("g")
    .attr("class", "milestone")
    .attr("transform", d => `translate(${x(d.Date)}, ${height})`) // Start off-screen
    .style("opacity", 0);

// Add lines connecting flags to x-axis (add first so they're underneath)
flags.append("line")
    .attr("x1", 0) // Adjusted to align with the right edge of the rectangle
    .attr("y1", d => d.yOffset - 7.5)
    .attr("x2", 0) // Matches x1 to keep the line straight
    .attr("y2", height) // Always reach x-axis
    .attr("stroke", "#34495e") // Line matches text box border
    .attr("stroke-width", 1);

// Add rectangles dynamically with rounded corners and updated colors
flags.append("rect")
    .attr("x", -150) // Rectangle still centered
    .attr("y", function (d) {
        const lines = wrapText(d.Description, 140, 10).length; // 140 is max width, 10 is font size
        return d.yOffset - (lines * 15); // Adjust y based on line count
    })
    .attr("width", 150)
    .attr("height", function (d) {
        const lines = wrapText(d.Description, 140, 10).length;
        return lines * 15; // Adjust height based on number of lines
    })
    .attr("rx", 10) // Rounded corners
    .attr("ry", 10) // Rounded corners
    .attr("fill", "#ecf0f1") // Matching the text box background
    .attr("stroke", "#34495e"); // Matching the text box border

// Add multiline text
flags.append("text")
    .attr("x", -135) // Adjust as needed for padding inside the rectangle
    .attr("y", function (d) {
        const lines = wrapText(d.Description, 140, 10).length;
        const offset = lines === 1 ? -15 : - (lines * 15 - 2); // Adjust for single vs. multiline
        return d.yOffset + offset;
    })
    .style("font-size", "10px")
    .style("fill", "#34495e") // Text color matching the HTML design
    .each(function (d) {
        const words = wrapText(d.Description, 140, 10);
        words.forEach((line, i) => {
            d3.select(this)
                .append("tspan")
                .attr("x", -135)
                .attr("dy", i === 0 ? "1.2em" : "1.2em") // Add spacing between lines
                .text(line);
        });
    });



    // Text Box
    const textBox = d3.select("#status");
    textBox.text("Press the spacebar to start!");

    // Precompute cumulative path lengths
    const pathLengths = data.map((d, i) => {
        if (i === 0) return 0;
        const x1 = x(data[i - 1].Date);
        const y1 = y(data[i - 1].Score);
        const x2 = x(d.Date);
        const y2 = y(d.Score);
        return Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
    });

    const cumulativeLengths = pathLengths.reduce(
        (acc, len) => [...acc, (acc[acc.length - 1] || 0) + len],
        []
    );

    // Track the current step
    let currentStep = 0;

    // Function to update the visualization incrementally
    function updateStep() {
        if (currentStep >= data.length - 1) {
            textBox.text("Animation complete!");
            return;
        }
    
        // Increment the step
        const nextStep = currentStep + 1;
    
        // Get the total path length
        const totalLength = path.node().getTotalLength();
    
        // Calculate the exact length to reveal up to the next data point
        const targetDashOffset = totalLength - cumulativeLengths[nextStep];
    
        // Animate line to the next step
        path.transition()
            .duration(1000)
            .ease(d3.easeLinear)
            .attr("stroke-dashoffset", targetDashOffset);
    
        // Show the corresponding circle (synchronized with the line animation)
        svg.selectAll("circle")
            .filter((d, i) => i === nextStep)
            .transition()
            .duration(1000)
            .style("opacity", 1);
    
        // Show and hide milestones dynamically
        milestones.forEach((milestone) => {
            const flagGroup = svg.selectAll(".milestone")
                .filter(d => d.Date.getTime() === milestone.Date.getTime());
            
            // Show the flag if the milestone date is reached
            if (milestone.Date <= data[nextStep].Date && milestone.Date > data[currentStep].Date) {
                flagGroup.transition()
                    .duration(1000)
                    .attr("transform", d => `translate(${x(d.Date)}, ${d.yOffset + height})`)
                    .style("opacity", 1);
            }
    
            // Hide the flag if it belongs to a previous step
            if (milestone.Date <= data[currentStep].Date) {
                flagGroup.transition()
                    .duration(500)
                    .style("opacity", 0);
            }
        });
    
        // Update text box
        textBox.html(`Pisa results for ${data[nextStep].Date.getFullYear()}: ${data[nextStep].Score}`);
    
        // Update the current step
        currentStep = nextStep;
    }
    

    // Event listener for spacebar
    document.addEventListener("keydown", event => {
        if (event.code === "Space") {
            event.preventDefault();
            updateStep();
        }
    });
});

// Load the second dataset for human figures visualization
d3.csv("C:/Users/roska/Desktop/Infoviz Project/Data/Mobile_usage.csv").then(percentageData => {
    // Parse the data (percentages)
    percentageData.forEach(d => {
        d.Year = +d.Year;
        d.Percentage = +d["Has in use a mobile phone with a touch screen, %"];
    });

    console.log(percentageData);

    // Generate human figures for the percentage chart
    const figuresChart = d3.select("#figures-chart");

    percentageData.forEach(d => {
        const row = figuresChart.append("div").attr("class", "row");

        // Add year label
        row.append("span").text(`${d.Year}: `).style("margin-right", "10px");

        // Total human figures
        const totalFigures = 10; // Each figure represents 10%
        const activeFigures = Math.round((d.Percentage / 100) * totalFigures);

        // Append human figures
        for (let i = 0; i < totalFigures; i++) {
            row.append("svg")
                .attr("class", "figure")
                .attr("width", 30)
                .attr("height", 60)
                .append("path")
                .attr("d", "M15 0C9 0 5 4 5 10C5 16 9 20 15 20C21 20 25 16 25 10C25 4 21 0 15 0ZM5 22C2 22 0 24 0 27L0 58C0 61 2 63 5 63L25 63C28 63 30 61 30 58L30 27C30 24 28 22 25 22L5 22Z") // SVG path for human figure
                .attr("class", i < activeFigures ? "figure active" : "figure")
                .style("fill", i < activeFigures ? "#1E90FF" : "#c3cfe2"); // Active: blue, Inactive: light blue
        }
    });
});

/**
 * Breaks a string into multiple lines for a given width.
 * @param {string} text The input text to wrap.
 * @param {number} maxWidth The maximum width for a line.
 * @param {number} fontSize The font size in pixels.
 * @returns {string[]} An array of lines of text.
 */
function wrapText(text, maxWidth, fontSize) {
    const words = text.split(" ");
    const lines = [];
    let line = "";

    const canvas = document.createElement("canvas");
    const context = canvas.getContext("2d");
    context.font = `${fontSize}px sans-serif`;

    words.forEach((word) => {
        const testLine = line + word + " ";
        const testWidth = context.measureText(testLine).width;
        if (testWidth > maxWidth && line.length > 0) {
            lines.push(line.trim());
            line = word + " ";
        } else {
            line = testLine;
        }
    });

    if (line.length > 0) {
        lines.push(line.trim());
    }

    return lines;
}


document.addEventListener("keydown", event => {
    if (event.code === "Space") {
        event.preventDefault();
        updateStep();
    }
});


d3.csv("./Data/Mobile_usage.csv").then(percentageData => {
    percentageData.forEach(d => {
        d.Year = +d.Year;
        d.Percentage = +d["Has in use a mobile phone with a touch screen, %"];
    });

    createBarChart(percentageData);
});


function createBarChart(data) {
    // Dimensions and Margins
    const barMargin = { top: 40, right: 30, bottom: 40, left: 60 };
    const barWidth = 800 - barMargin.left - barMargin.right;
    const barHeight = 400 - barMargin.top - barMargin.bottom;

    // Create SVG for Bar Chart
    const barSvg = d3.select("#figures-chart")
        .append("svg")
        .attr("width", barWidth + barMargin.left + barMargin.right)
        .attr("height", barHeight + barMargin.top + barMargin.bottom);

    // Add Title
    barSvg.append("text")
        .attr("x", (barWidth + barMargin.left + barMargin.right) / 2) // Center the title
        .attr("y", barMargin.top / 2) // Position above the chart
        .attr("text-anchor", "middle") // Center align the text
        .style("font-size", "16px") // Font size for title
        .style("font-weight", "bold") // Bold text
        .style("fill", "#34495e") // Title color
        .text("Percentage of smartphone users aged 16-24."); // Title text

    const chartGroup = barSvg.append("g")
        .attr("transform", `translate(${barMargin.left},${barMargin.top})`);

    // Scales
    const xBar = d3.scaleBand()
        .domain(data.map(d => d.Year))
        .range([0, barWidth])
        .padding(0.2);

    const yBar = d3.scaleLinear()
        .domain([0, 100]) // Percentage scale from 0% to 100%
        .range([barHeight, 0]);

    // Axes
    chartGroup.append("g")
        .attr("transform", `translate(0,${barHeight})`)
        .call(d3.axisBottom(xBar).tickFormat(d3.format("d"))); // Format years as integers

    chartGroup.append("g")
        .call(d3.axisLeft(yBar).ticks(10).tickFormat(d => `${d}%`)); // Format ticks as percentages

    // Bars
    chartGroup.selectAll(".bar")
        .data(data)
        .enter()
        .append("rect")
        .attr("class", "bar")
        .attr("x", d => xBar(d.Year))
        .attr("y", d => yBar(d.Percentage))
        .attr("width", xBar.bandwidth())
        .attr("height", d => barHeight - yBar(d.Percentage))
        .attr("fill", "#1E90FF")
        .attr("rx", 4) // Rounded corners for bars
        .attr("ry", 4);

    // Add percentage labels above each bar
    chartGroup.selectAll(".label")
        .data(data)
        .enter()
        .append("text")
        .attr("class", "label")
        .attr("x", d => xBar(d.Year) + xBar.bandwidth() / 2)
        .attr("y", d => yBar(d.Percentage) - 5)
        .attr("text-anchor", "middle")
        .style("font-size", "10px")
        .style("fill", "#34495e")
        .text(d => `${d.Percentage}%`);
}
