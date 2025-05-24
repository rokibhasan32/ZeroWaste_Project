document.getElementById("uploadForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const fileInput = document.getElementById("fileInput");
    if (fileInput.files.length === 0) return alert("Please select a file.");

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    try {
        const response = await fetch("/analyze", {
            method: "POST",
            body: formData
        });

        if (!response.ok) throw new Error("Failed to analyze image.");

        const data = await response.json();

        document.getElementById("wasteType").textContent = data.waste_type;
        document.getElementById("confidence").textContent = data.confidence;
        document.getElementById("amount").textContent = data.amount;
        document.getElementById("lat").textContent = data.lat;
        document.getElementById("lon").textContent = data.lon;
        document.getElementById("timestamp").textContent = data.timestamp;

        document.getElementById("results").classList.remove("hidden");

    } catch (err) {
        alert("Error: " + err.message);
    }
});
