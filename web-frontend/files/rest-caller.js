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
            addAnswer(jsonResponse.response);
        }
    };
    xhttp.open("GET", "/api/query?query=" + encodeURIComponent(queryText), true);
    xhttp.send();
}

function addAnswer(text) {
    // Create answer box
    newDiv = document.createElement("div");
    newDiv.className = "answerBox";
    newDiv.textContent = text;
    
    // Add to answer list
    answerList = document.getElementById("answerList");
    answerList.insertBefore(newDiv, answerList.firstChild);
}

function setupAll() {
    // Setup ask button
    document.getElementById("askButton").onclick = doQuery;
}

window.onload = setupAll;
