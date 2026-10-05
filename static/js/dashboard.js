// Get the inspection button from the HTML page.
const inspectButton = document.getElementById("inspectButton");

// Run this function when the button is clicked.
inspectButton.addEventListener("click", async function () {

    // Send an HTTP GET request to the Flask /inspect route.
    const response = await fetch("/inspect");

    // Convert the JSON response into a JavaScript object.
    const data = await response.json();

    // Display numerical inspection results.
    document.getElementById("meanBrightness").textContent =
        data.mean_brightness;

    document.getElementById("brightnessStd").textContent =
        data.standard_deviation;

    document.getElementById("minBrightness").textContent =
        data.min_brightness;

    document.getElementById("maxBrightness").textContent =
        data.max_brightness;

    document.getElementById("uniformityScore").textContent =
        data.uniformity_score;

    // Get the inspection status element.
    const statusElement =
        document.getElementById("inspectionStatus");

    // Display PASS or FAIL.
    statusElement.textContent =
        data.inspection_status;

    // Change the status color.
    if (data.inspection_status === "PASS") {
        statusElement.style.color = "green";
    } else {
        statusElement.style.color = "red";
    }

    // Refresh the history table after the new inspection is saved.
    await loadHistory();
});

// Load inspection history from the database.
async function loadHistory() {

    // Request all saved inspection records from Flask.
    const response = await fetch("/history");

    // Convert the JSON response into a JavaScript array.
    const inspections = await response.json();

    // Find the table body in index.html.
    const tableBody =
        document.getElementById("historyTableBody");

    // Remove existing rows.
    tableBody.innerHTML = "";


    // Create one table row for each inspection.
    inspections.forEach(function (inspection) {

        // Create a new HTML table row.
        const row = document.createElement("tr");

        // Add inspection data to the row.
        row.innerHTML = `
            <td>${inspection.id}</td>
            <td>${inspection.mean_brightness}</td>
            <td>${inspection.standard_deviation}</td>
            <td>${inspection.min_brightness}</td>
            <td>${inspection.max_brightness}</td>
            <td>${inspection.uniformity_score}</td>
            <td>${inspection.inspection_status}</td>
        `;

        // Add the row to the history table.
        tableBody.appendChild(row);
    });
}


// Load inspection history when the dashboard first opens.
loadHistory();