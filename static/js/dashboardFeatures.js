// globalises the graph to help
let dashboardConcGraph


// get the current time from the flask backend
function currentTimeFeature() {
    fetch('/currentTimeFeature')  // call the flask endpoint
        .then(response => response.json())  // parse the JSON response
        .then(data => {
            // update the content of the element with the current time
            document.getElementById('timeDashboard').innerText = data.time;
        })
        .catch(error => {
            console.error('Error fetching time:', error);
        });
}

// get the current concentrations from the flask backend
function currentConcsFeature() {
    fetch('/currentConcsFeature')  // call the flask endpoint
        .then(response => response.json())  // parse the JSON response
        .then(data => {
            // update the content of the element with the current concs
            document.getElementById('pm1.0').innerText = `PM1.0 --- ${data['PM1.0']} µg/m³`;
            document.getElementById('pm2.5').innerText = `PM2.5 --- ${data['PM2.5']} µg/m³`;
            document.getElementById('pm10.0').innerText = `PM10.0 --- ${data['PM10.0']} µg/m³`;
        })
        .catch(error => {
            console.error('Error fetching time:', error);
        });
}

// get the required data and displays it in a current conc graph
function currentConcGraphFeature() {
    fetch('/currentConcGraphFeature')
        .then(response => response.json())
        .then(data => {
            let times = data['time'];  // extract time values
            // extract concentration values
            let pm1_0 = data['PM1.0'];
            let pm2_5 = data['PM2.5'];
            let pm10_0 = data['PM10.0'];

            // if the chart doesn't exist yet, create it
            if (!dashboardConcGraph) {
                dashboardConcGraph = new Chart('dashboardConcGraph', {
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
                dashboardConcGraph.data.labels = times;
                dashboardConcGraph.data.datasets[0].data = pm1_0;
                dashboardConcGraph.data.datasets[1].data = pm2_5;
                dashboardConcGraph.data.datasets[2].data = pm10_0;
                dashboardConcGraph.update();  // update the chart with the new data
            }
        })
        .catch(error => console.error('Error fetching data:', error));
}


// fetch the current time/conc when the page loads
currentTimeFeature();
currentConcsFeature();

// trigger the chart on page load
window.onload = function() {
    currentConcGraphFeature();
};


// refresh the time every second
setInterval(currentTimeFeature, 1000);  // update time every second
setInterval(currentConcsFeature, 1000);  // update concs every second
setInterval(currentConcGraphFeature, 1000); // update graph every second
