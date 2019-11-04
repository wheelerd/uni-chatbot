function doQuery() {
    // Get question
    queryText = document.getElementById("inputBox").value;
    
    // Do REST request
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            // Parse response
            jsonResponse = JSON.parse(xhttp.responseText);
            
            // Add to answer list
            addAnswer(jsonResponse.response, jsonResponse.image);
        }
    };
    xhttp.open("GET", "/api/query?query=" + encodeURIComponent(queryText), true);
    xhttp.send();
}

function processTextKey(event) {
    console.log(event);
    if(event.key === "Enter")
        doQuery();
}

function getMetrics() {
    // Do REST request
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            // Parse response
            jsonResponse = JSON.parse(xhttp.responseText);
            
            // Update API call counter
            metricsText = document.getElementById("metricsText");
            count = jsonResponse.apiCalls;
            if(count == 0)
                metricsText.textContent = "This bot has not been asked a question yet. Be the first!";
            else if(count == 1)
                metricsText.textContent = "This bot has been asked a single question before!";
            else
                metricsText.textContent = "This bot has been asked a question " + count + " times before!";
        }
    };
    xhttp.open("GET", "/api/getStats", true);
    xhttp.send();
}

function addAnswer(text, imageBase64) {
    // Create answer box
    newDiv = document.createElement("div");
    newDiv.className = "answerBox";
    newDiv.textContent = text;
    
    if(imageBase64 !== null) {
        newBreak = document.createElement("br");
        newDiv.appendChild(newBreak);
        newImg = document.createElement("img");
        newImg.setAttribute('src', 'data:image/png;base64,' + imageBase64);
        newDiv.appendChild(newImg);
    }
    
    // Add to answer list
    answerList = document.getElementById("answerList");
    answerList.insertBefore(newDiv, answerList.firstChild);
    
    // Update metrics
    getMetrics();
}

function setupAll() {
    // Setup ask button
    document.getElementById("askButton").onclick = doQuery;
    
    // Setup input text box
    document.getElementById("inputBox").addEventListener("keydown", processTextKey);
    
    // Setup metrics timer and call first time
    setInterval(getMetrics, 20000); // Auto-update every 20 seconds
    getMetrics();
}

window.onload = setupAll;
