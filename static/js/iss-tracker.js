document.addEventListener('DOMContentLoaded', function () {
    const issApiUrl = "/iss-location"; // Endpoint for ISS latitude and longitude

    const map = L.map('iss-map').setView([0, 0], 2);

    const issIcon = L.icon({
        iconUrl: '/static/images/iss-icon.png',
        iconSize: [50, 32],
        iconAnchor: [25, 16],
    });

    const marker = L.marker([0, 0], { icon: issIcon }).addTo(map);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
    }).addTo(map);

    let firstUpdate = true;

    function updateISSLocation() {
        fetch(issApiUrl)
            .then((response) => response.json())
            .then((data) => {
                const { latitude, longitude } = data;
                const latLng = [parseFloat(latitude), parseFloat(longitude)];

                // Update marker position
                marker.setLatLng(latLng);

                if (firstUpdate) {
                    map.setView(latLng, 2); // Center map initially
                    firstUpdate = false;
                } else {
                    map.panTo(latLng, { animate: true, duration: 1.5 });
                }

                // Dynamically update Latitude and Longitude
                document.getElementById('iss-latitude').innerText = latitude;
                document.getElementById('iss-longitude').innerText = longitude;

            })
            .catch((error) => {
                console.error("Error fetching ISS location:", error);
                document.getElementById('iss-latitude').innerText = "Error";
                document.getElementById('iss-longitude').innerText = "Error";
            });
    }

    // Initial ISS position update
    updateISSLocation();

    // Update ISS position every 5 seconds
    setInterval(updateISSLocation, 5000);
});
