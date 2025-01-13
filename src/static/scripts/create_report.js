const austriaBounds = L.latLngBounds(
    L.latLng(46.5, 9.5),
    L.latLng(49.0, 17.0)
);

var map = L.map('map', {
    minZoom: 7,
    maxZoom: 16,
    maxBounds: austriaBounds,
    maxBoundsViscosity: 1.0
}).setView([47.5162, 14.5501], 7);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

var marker = L.marker([47.5162, 14.5501]).addTo(map);

function debounce(func, delay) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), delay);
    };
}

function geocodeAddress(street, zipcode, country, callback) {
    const url = `https://nominatim.openstreetmap.org/search?street=${street}&postalcode=${zipcode}&country=${country}&countrycodes=AT&format=json&limit=1`;

    fetch(url)
        .then((response) => response.json())
        .then((data) => {
            if (data.length > 0) {
                const lat = data[0].lat;
                const lon = data[0].lon;
                document.getElementById("location").value = `${lat},${lon}`;
                marker.setLatLng([lat, lon]);
                map.setView([lat, lon], 13);

                if (callback) callback();
            } else {
                alert("Location not found. Please check your input.");
            }
        })
        .catch((error) => console.error("Error geocoding address:", error));
}

const updateMap = debounce(() => {
    const street = document.getElementById("street").value;
    const zipcode = document.getElementById("zipcode").value;
    const country = "Austria";

    if (street && zipcode) {
        geocodeAddress(street, zipcode, country);
    }
}, 800);


document.getElementById("street").addEventListener("input", updateMap);
document.getElementById("zipcode").addEventListener("input", updateMap);


document.getElementById("reportForm").addEventListener("submit", function (e) {
    e.preventDefault();

    const street = document.getElementById("street").value;
    const zipcode = document.getElementById("zipcode").value;
    const country = "Austria";

    if (street && zipcode) {
        geocodeAddress(street, zipcode, country, () => {
            document.getElementById("reportForm").submit();
        });
    } else {
        alert("Please fill in both street and zipcode.");
    }
});

map.on('click', function(e) {
    var lat = e.latlng.lat;
    var lon = e.latlng.lng;

    if (austriaBounds.contains([lat, lon])) {
        marker.setLatLng([lat, lon]);
        document.getElementById("location").value = `${lat},${lon}`;

        // Reverse geocode the selected location to get street and zip code
        reverseGeocode(lat, lon);
    } else {
        alert("Please select a location within Austria.");
    }
});

function reverseGeocode(lat, lon) {
    const url = `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json`;

    fetch(url)
        .then((response) => response.json())
        .then((data) => {
            if (data && data.address) {
                const street = data.address.road || '';
                const zipcode = data.address.postcode || '';

                // Update the input fields
                document.getElementById("street").value = street;
                document.getElementById("zipcode").value = zipcode;
            } else {
                alert("Could not retrieve address information for this location.");
            }
        })
        .catch((error) => {
            console.error("Error reverse geocoding location:", error);
            alert("An error occurred while retrieving the address.");
        });
}
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

                        // Reverse geocode the user's current location to get street and zip code
                        reverseGeocode(lat, lon);

                        locationField.readOnly = true;
                    } else {
                        alert("Your current location is outside Austria.");
                    }
                },
                (error) => {
                     console.log(currentUser.location)
                    const [lat, lon] = currentUser.location.split(',').map(coord => parseFloat(coord.trim()));
                     locationField.value = `${lat},${lon}`;
                        marker.setLatLng([lat, lon]);
                        map.setView([lat, lon], 13);
                        reverseGeocode(lat, lon);

                        locationField.readOnly = true;
                }
            );
        } else {
            alert("Geolocation is not supported by this browser.");
        }
    } else {
        locationField.value = "";
        locationField.readOnly = false;
        // Reset street and zipcode fields when location use is toggled off
        document.getElementById("street").value = "";
        document.getElementById("zipcode").value = "";
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
