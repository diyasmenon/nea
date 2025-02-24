// globalises the graph to help
let analyticsHistoricalGraph
let analyticsPredictedGraph

document.addEventListener("DOMContentLoaded", function () {
    const refreshButton = document.getElementById("analyticsRefreshButton");
    
    // listening for when refresh is clicked
    refreshButton.addEventListener("click", function () {
        // calls the functions to get new data
        currentTimeFeature();
        sendData();
    });
});


// get the current time from the flask backend
function currentTimeFeature() {
    fetch('/currentTimeFeature')  // call the flask endpoint
        .then(response => response.json())  // parse the JSON response
        .then(data => {
            // update the content of the element with the current time
            document.getElementById('timeAnalytics').innerText = data.time;
        })
        .catch(error => {
            console.error('Error fetching time:', error);
        });
}

// runs whenever the status of the button is changed, to alert to get the correct data
function sendData() {
    // get selected time frame (radio button)
    let timeframe = document.querySelector('input[name="time"]:checked')?.value;

    // get selected particle sizes (checkboxes) and puts it in an array
    let sizes = [];
    document.querySelectorAll('input[name="particle"]:checked').forEach(checkbox => {
        sizes.push(checkbox.value);
    });

    // send data to Python in right format
    fetch('/analyticsFeatures', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            timeframe: timeframe,
            pm1_0: sizes.includes("pm1.0"),
            pm2_5: sizes.includes("pm2.5"),
            pm10_0: sizes.includes("pm10.0")
        })
    })
    .then(response => response.json())
    .then(data => {
            let times = data['time'];  // extract time values
            // extract concentration values
            let pm1_0 = data['PM1.0'];
            let pm2_5 = data['PM2.5'];
            let pm10_0 = data['PM10.0'];

            // if the historical chart doesn't exist yet, create it
            if (!analyticsHistoricalGraph) {
                analyticsHistoricalGraph = new Chart('analyticsHistoricalGraph', {
                    type: 'line',  // line chart type
                    data: {
                        labels: times,  // time values as labels on the x-axis
                        datasets: [
                            {
                                label: 'PM1.0',
                                data: pm1_0,
                                borderColor: '#57B0FF',
                                fill: false
                            },
                            {
                                label: 'PM2.5',
                                data: pm2_5,
                                borderColor: '#90E093',
                                fill: false
                            },
                            {
                                label: 'PM10.0',
                                data: pm10_0,
                                borderColor: '#FF9287',
                                fill: false
                           
                            }]
                    },
                    options: {
                        responsive: false, // disable responsive resizing
                        maintainAspectRatio: false, // prevent the aspect ratio from being maintained
                    }
                });
            } else {
                // update the chart data and refresh the chart
                analyticsHistoricalGraph.data.labels = times;
                analyticsHistoricalGraph.data.datasets[0].data = pm1_0;
                analyticsHistoricalGraph.data.datasets[1].data = pm2_5;
                analyticsHistoricalGraph.data.datasets[2].data = pm10_0;
                analyticsHistoricalGraph.update();  // update the chart with the new data
            }

            // if the predicted chart doesn't exist yet, create it
            if (!analyticsPredictedGraph) {
                analyticsPredictedGraph = new Chart('analyticsPredictedGraph', {
                    type: 'line',  // line chart type
                    data: {
                        labels: data['Analytics Times'].concat(data['Predicted Times']),  // time values as labels on the x-axis
                        datasets: [
                            {
                                label: 'PM1.0',
                                data: data['Analytics PM1.0'], //plots previous actual data
                                borderColor: '#57B0FF',
                                pointRadius: 0, //removes the circle of the plotted point
                                tension: 0.1, // smooths out the curve
                                fill: false
                            },
                            {
                                label: 'Predicted PM1.0',
                                data: data['Predicted PM1.0'], //plots predicted data
                                borderColor: '#4A9AE6', // different colour for prediction
                                borderDash: [5,5], // dash for prediction
                                pointRadius: 0, //removes the circle of the plotted point
                                tension: 0.1, // smooths out the curve
                                fill: false
                            },
                            {
                                label: 'PM2.5',
                                data: data['Analytics PM2.5'], //plots previous actual data
                                borderColor: '#90E093',
                                pointRadius: 0, //removes the circle of the plotted point
                                tension: 0.1, // smooths out the curve
                                fill: false
                            },
                            {
                                label: 'Predicted PM2.5',
                                data: data['Predicted PM2.5'], //plots predicted data
                                borderColor: '#7FC47F', // different colour for prediction
                                borderDash: [5,5], // dash for prediction
                                pointRadius: 0, //removes the circle of the plotted point
                                tension: 0.1, // smooths out the curve
                                fill: false
                            },
                            {
                                label: 'PM10.0',
                                data: data['Analytics PM10.0'], //plots previous actual data
                                borderColor: '#FF9287',
                                pointRadius: 0, //removes the circle of the plotted point
                                tension: 0.1, // smooths out the curve
                                fill: false
                            },
                            {
                                label: 'Predicted PM10.0',
                                data: data['Predicted PM10.0'], //plots predicted data
                                borderColor: '#E67B75', // different colour for prediction
                                borderDash: [5,5], // dash for prediction
                                pointRadius: 0, //removes the circle of the plotted point
                                tension: 0.1, // smooths out the curve
                                fill: false
                            }
                            ]
                    },
                    options: {
                        responsive: false, // disable responsive resizing
                        maintainAspectRatio: false, // prevent the aspect ratio from being maintained
                    }
                });
            } else {
                // update the historical chart data and refresh the chart
                analyticsHistoricalGraph.data.labels = times;
                analyticsHistoricalGraph.data.datasets[0].data = pm1_0;
                analyticsHistoricalGraph.data.datasets[1].data = pm2_5;
                analyticsHistoricalGraph.data.datasets[2].data = pm10_0;
                analyticsHistoricalGraph.update();  // update the chart with the new data

                // update the predicted graph (all 6 datasets)
                // times are joined so its format aligns with the format of the dataset
                analyticsPredictedGraph.data.labels = data['Analytics Times'].concat(data['Predicted Times']);
                analyticsPredictedGraph.data.datasets[0].data = data['Analytics PM1.0'];
                analyticsPredictedGraph.data.datasets[1].data = data['Predicted PM1.0'];
                analyticsPredictedGraph.data.datasets[2].data = data['Analytics PM2.5'];
                analyticsPredictedGraph.data.datasets[3].data = data['Predicted PM2.5'];
                analyticsPredictedGraph.data.datasets[4].data = data['Analytics PM10.0'];
                analyticsPredictedGraph.data.datasets[5].data = data['Predicted PM10.0'];
                analyticsPredictedGraph.update();  // update the chart with the new data

                
            }
            // update the historical trends
            document.getElementById('historicalTrendTitle').innerText = `Historical Trends for ${data['size']}`;
            document.getElementById('historicalTrend').innerText = `Overall Trend: ${data['overallTrend']}`;
            document.getElementById('historicalPeak').innerText = `Highest Peak: ${data['peakInfo']}`;
            document.getElementById('historicalAvgConc').innerText = `Average Concentration: ${data['avgConc']}`;
            
            // update the prediction trends
            document.getElementById('predictionTrendTitle').innerText = `Prediction Summary for ${data['size']}`;
            document.getElementById('predictionConfidence').innerText = `Confidence: ${data['Confidence']}`;
            document.getElementById('predictionUncertainty').innerText = `Uncertainty: ${data['Uncertainty']}`;
            document.getElementById('predictionDeviation').innerText = `Recent Deviation: ${data['Prediction Deviation']}`;
        })
        .catch(error => console.error('Error fetching data:', error));
}


// fetch the current time/historical graph data when the page loads
currentTimeFeature();
sendData();

// refresh the time every second
setInterval(currentTimeFeature, 1000);  // update time every second
setInterval(sendData, 1000);  // update historical graph every second