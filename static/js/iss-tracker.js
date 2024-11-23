document.addEventListener('DOMContentLoaded', function () {
    const issApiUrl = "/iss-location"; // Endpoint for ISS latitude and longitude
    const geocodingApiUrl = "https://api.opencagedata.com/geocode/v1/json";
    const geocodingApiKey = window.opencageApiKey;

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
                console.log("ISS Coordinates:", { latitude, longitude });

                const latLng = [parseFloat(latitude), parseFloat(longitude)];
                marker.setLatLng(latLng);

                // Smoothly move the map to the new position
                if (firstUpdate) {
                    map.setView(latLng, 2);
                    firstUpdate = false;
                } else {
                    map.flyTo(latLng, 2, { animate: true, duration: 1.5 });
                }

                document.getElementById('iss-latitude').innerText = latitude;
                document.getElementById('iss-longitude').innerText = longitude;

                const geocodeUrl = `${geocodingApiUrl}?q=${latitude}+${longitude}&key=${geocodingApiKey}`;
                fetch(geocodeUrl)
                    .then((response) => response.json())
                    .then((geoData) => {
                        const components = geoData.results[0]?.components || {};
                        const country = components.country || "Int'l Waters";
                        const region = components.state || components.region || "Unknown";

                        document.getElementById('iss-region').innerText = region;
                        document.getElementById('iss-country').innerText = country;
                    })
                    .catch((error) => {
                        console.error("Error fetching geocoding data:", error);
                        document.getElementById('iss-region').innerText = "Unable to fetch region";
                        document.getElementById('iss-country').innerText = "Unable to fetch country";
                    });
            })
            .catch((error) => {
                console.error("Error fetching ISS location:", error);
                document.getElementById('iss-latitude').innerText = "Error";
                document.getElementById('iss-longitude').innerText = "Error";
                document.getElementById('iss-region').innerText = "Error";
                document.getElementById('iss-country').innerText = "Error";
            });
    }

    updateISSLocation();
    setInterval(updateISSLocation, 30000); // Poll every 30 seconds
});
