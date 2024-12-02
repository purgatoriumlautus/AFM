const austriaBounds = L.latLngBounds(
    L.latLng(46.5, 9.5),
    L.latLng(49.0, 17.0)
);

var map = L.map('map', {
    minZoom: 7,
    maxZoom: 13,
    maxBounds: austriaBounds,
    maxBoundsViscosity: 1.0
}).setView([47.5162, 14.5501], 7);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

var marker = L.marker([47.5162, 14.5501]).addTo(map);

function geocodeAddress(street, zipcode, country) {
    var url = `https://nominatim.openstreetmap.org/search?street=${street}&postalcode=${zipcode}&country=${country}&countrycodes=AT&format=json&limit=1`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.length > 0) {
                var lat = data[0].lat;
                var lon = data[0].lon;
                document.getElementById("location").value = `${lat},${lon}`;
                marker.setLatLng([lat, lon]);
                map.setView([lat, lon], 13);
            } else {
                alert("Location not found. Please check your input.");
            }
        })
        .catch(error => console.error("Error geocoding address:", error));
}

document.getElementById("reportForm").addEventListener("submit", function(e) {
    var street = document.getElementById("street").value;
    var zipcode = document.getElementById("zipcode").value;
    var country = "Austria";
    geocodeAddress(street, zipcode, country);
});

document.getElementById("street").addEventListener("input", updateMap);
document.getElementById("zipcode").addEventListener("input", updateMap);

function updateMap() {
    var street = document.getElementById("street").value;
    var zipcode = document.getElementById("zipcode").value;
    var country = "Austria";

    if (street && zipcode && country) {
        geocodeAddress(street, zipcode, country);
    }
}

map.on('click', function(e) {
    var lat = e.latlng.lat;
    var lon = e.latlng.lng;
    if (austriaBounds.contains([lat, lon])) {
        marker.setLatLng([lat, lon]);
        document.getElementById("location").value = `${lat},${lon}`;
    } else {
        alert("Please select a location within Austria.");
    }
});

document.getElementById("description").addEventListener("input", function() {
    var maxLength = 300;
    var currentLength = this.value.length;
    document.getElementById("charCount").textContent = `${currentLength}/${maxLength} characters`;
});

function toggleLocation() {
    const locationField = document.getElementById("location");
    const useCurrentLocation = document.getElementById("useCurrentLocation").checked;

    if (useCurrentLocation) {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;
                    if (austriaBounds.contains([lat, lon])) {
                        locationField.value = `${lat},${lon}`;
                        marker.setLatLng([lat, lon]);
                        map.setView([lat, lon], 13);
                        locationField.readOnly = true;
                    } else {
                        alert("Your current location is outside Austria.");
                    }
                },
                (error) => showError(error)
            );
        } else {
            alert("Geolocation is not supported by this browser.");
        }
    } else {
        locationField.value = "";
        locationField.readOnly = false;
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
