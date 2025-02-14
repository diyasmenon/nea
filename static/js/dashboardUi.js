document.addEventListener("DOMContentLoaded", function () {
    const copyAPIButton = document.getElementById("copyAPIButton");
    const APIText = document.getElementById("APIText");
    
    copyAPIButton.addEventListener("click", function () {
        navigator.clipboard.writeText(APIText.value).then(function () {
            // so user knows the api has been copied
            alert("Copied API Key to clipboard");
        }).catch(function (err) {
            console.error("Error copying text: ", err)
        });
    });
});
