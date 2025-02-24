document.addEventListener("DOMContentLoaded", function () {
    const concButton = document.getElementById("concButton");
    const analyticsConc = document.getElementById("analyticsConc");
    const timeFrameButton = document.getElementById("timeFrameButton");
    const analyticsTimeFrame = document.getElementById("analyticsTimeFrame");
    
    concButton.addEventListener("click", function (event) {
        event.stopPropagation(); // prevents immediate closure
        analyticsConc.classList.toggle("active");
    });

    timeFrameButton.addEventListener("click", function (event) {
        event.stopPropagation(); // prevents immediate closure
        analyticsTimeFrame.classList.toggle("active");
    });
    

    // close the dropdown when clicking outside
    document.addEventListener("click", function (event) {
        if (!analyticsConc.contains(event.target)) {
            analyticsConc.classList.remove("active");
        }

        if (!analyticsTimeFrame.contains(event.target)) {
            analyticsTimeFrame.classList.remove("active");
        }
    });


    //starts with all the concs being selected

    document.querySelectorAll("#concButtonContent input[type='checkbox']").forEach(checkbox => {
        checkbox.checked = true;
      });
});
