console.log(reports);
    var map = L.map('map').setView([47.5, 13.5], 7);

    // OpenStreetMap as a base map
    var basemap = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

   var waterlevels = L.tileLayer.wms("https://gis.lfrz.gv.at/wmsgw/?key=460276c6b17d485ea29604196d48fb5a&service=WMS&version=1.3.0&request=GetLegendGraphic&format=image%2Fpng&width=20&height=20&layer=pegelaktuell", {
        layers: 'pegelaktuell',
        format: 'image/png',
        transparent: true,
    }).addTo(map);
function getDistance(lat1, lon1, lat2, lon2) {
    const R = 6371;
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c; // Distance in km
}

function showReports(userLat, userLng, radius) {
    const markers = L.markerClusterGroup();
    reports.forEach(function(report) {
        if (report.location) {
            const coords = report.location.split(',');
            const lat = parseFloat(coords[0]);
            const lng = parseFloat(coords[1]);
            const distance = getDistance(userLat, userLng, lat, lng);
            if (distance <= radius) {
                const marker = L.marker([lat, lng]);
                marker.bindPopup(`
                    <strong>Description:</strong> ${report.description}<br>
                    <strong>Location:</strong> ${lat}, ${lng}
                `);
                markers.addLayer(marker);
            }
        }
    });

    map.addLayer(markers);
}

function getUserLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const userLat = position.coords.latitude;
                const userLng = position.coords.longitude;
                const radius = 20;
                showReports(userLat, userLng, radius);
            },
            (error) => showError(error)
        );
    } else {
        alert("Geolocation is not supported by this browser.");
    }
}

function showError(error) {
    switch (error.code) {
        case error.PERMISSION_DENIED:
            alert("Permission denied. Please enable location access or enter your location manually.");
            break;
        case error.POSITION_UNAVAILABLE:
            alert("Location information is unavailable.");
            break;
        case error.TIMEOUT:
            alert("The request to get user location timed out.");
            break;
        case error.UNKNOWN_ERROR:
            alert("An unknown error occurred.");
            break;
    }
}

window.onload = function() {
    getUserLocation();
};

    // Legend
    var legend = L.control({ position: 'bottomright' });
    legend.onAdd = function (map) {
        var div = L.DomUtil.create('div', 'info legend');
        div.style.backgroundColor = 'white';
        div.style.padding = '20px';
        div.innerHTML = `
            <strong>Legend</strong><br>
            <img src="https://gis.lfrz.gv.at/wmsgw/?key=460276c6b17d485ea29604196d48fb5a&service=WMS&version=1.3.0&request=GetLegendGraphic&format=image%2Fpng&width=10&height=30&layer=pegelaktuell" alt="Legend" />
            <span>Water levels</span><br>
            <img src="static/marker-icon.png" alt="Report Icon" width="13" height="20">
            <span>Flood report</span>
        `;
        return div;
    };
    legend.addTo(map);

    // Layer control
    var baseMaps = {
        "OpenStreetMap": basemap,
    };

    var overlayMaps = {
        "Flood Reports": markers,
        "Water Levels": waterlevels
    };

    L.control.layers(baseMaps, overlayMaps).addTo(map);