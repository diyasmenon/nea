// get the current time from the flask backend
function getCurrentTime() {
    fetch('/currentTimeFeature')  // call the flask endpoint
        .then(response => response.json())  // Parse the JSON response
        .then(data => {
            // update the content of the element with the current time
            document.getElementById('timeDashboard').innerText = data.time;
        })
        .catch(error => {
            console.error('Error fetching time:', error);
        });
}

// Fetch the current time when the page loads
getCurrentTime();

// refresh the time every second
setInterval(getCurrentTime, 1000);  // Update time every second
