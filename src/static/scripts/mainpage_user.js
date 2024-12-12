console.log(reports);
    var map = L.map('map').setView([47.5, 13.5], 7);

    // OpenStreetMap as a base map
    var basemap = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);
    proj4.defs("EPSG:3416", "+proj=lcc +lat_0=47.5 +lon_0=13.3333333333333 +lat_1=49 +lat_2=46 +x_0=400000 +y_0=400000 +datum=ETRS89 +units=m +no_defs");


function convertToLatLng(utmX, utmY, zone) {
    const [lng, lat] = proj4("EPSG:3416", "WGS84", [utmX, utmY]);
    return { lat, lng };
}
function getWaterLevelColor(gesamtcode) {
  const gesamtcodeString = String(gesamtcode);
  const firstDigit = gesamtcodeString.charAt(0);

  if (!firstDigit || isNaN(firstDigit)) {
    return "#808080";
  }

  const firstDigitNum = parseInt(firstDigit, 10);

  switch (firstDigitNum) {
    case 1: return "#66ccff";
    case 2: return "#0066ff";
    case 3: return "#0000cc";
    case 4: return "#ff6600";
    case 5: return "#cc0000";
    case 6: return "#660033";
    case 9: return "#808080";
    default: return "#808080";
  }
}
var waterlevels = L.markerClusterGroup()
async function getData() {
  const url = "https://gis.lfrz.gv.at/wmsgw/?key=a64a0c9c9a692ed7041482cb6f03a40a&request=GetFeature&service=WFS&version=2.0.0&outputFormat=json&typeNames=inspire:pegelaktuell";

  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Response status: ${response.status}`);
    }

    const json = await response.json();
    console.log("Fetched GeoJSON data:", json);

    const features = json.features;
    if (!features || features.length === 0) {
      console.warn("No features found in the GeoJSON data.");
      return;
    }

    features.forEach(function (report) {
      if (report.geometry && report.geometry.type === "Point") {
        const coordinates = report.geometry.coordinates;
        if (coordinates && coordinates.length === 2) {
          const { lat, lng } = convertToLatLng(coordinates[0], coordinates[1]);
          if (report.properties.land == "") {
             const marker = L.marker([lat, lng], {
              icon: L.divIcon({
                className: 'water-level-icon',
                html: `<div style="background-color: ${getWaterLevelColor(report.properties.gesamtcode)}; padding: 5px; border-radius: 50%; width: 20px; height: 20px; border: black solid 1px"></div>`
              })
            });
              const waterLevel = report.properties.wertw_cm || 'No data';
              const messstelle = report.properties.messstelle || 'No Name';
              const zeitpunkt = report.properties.zeitpunkt || 'No time data';
              const popupContent = `
            <strong>Measurement Station:</strong> ${messstelle}<br>
            <strong>Time of Last Measurement:</strong> ${zeitpunkt}<br>
            <strong>Water Level (cm):</strong> ${waterLevel}<br>
          `;
              marker.bindPopup(popupContent);
              waterlevels.addLayer(marker);
          }
        }
      } else {
        console.warn("Feature does not contain point geometry:", report);
      }
    });

  } catch (error) {
    console.error("Error fetching or processing data:", error.message);
  }
  map.addLayer(waterlevels);
}
getData();
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
var markers = L.markerClusterGroup();
function showReports(userLat, userLng, radius) {
    markers.clearLayers();
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
            <div style="display: flex; align-items: center; padding: 2px">
            <div style="width: 20px; border: black solid 1px;height: 20px; background-color: #66ccff; border-radius: 50%; margin-right: 5px;"></div>
            <span>Low water</span>
        </div>
        <div style="display: flex; align-items: center;padding: 2px">
            <div style="width: 20px; border: black solid 1px;height: 20px; background-color: #0066ff; border-radius: 50%; margin-right: 5px;"></div>
            <span>Medium water</span>
        </div>
        <div style="display: flex; align-items: center;padding: 2px">
            <div style="width: 20px; border: black solid 1px;height: 20px; background-color: #0000cc; border-radius: 50%; margin-right: 5px;"></div>
            <span>Increased flow</span>
        </div>
        <div style="display: flex; align-items: center;padding: 2px">
            <div style="width: 20px; border: black solid 1px;height: 20px; background-color: #ff6600; border-radius: 50%; margin-right: 5px;"></div>
            <span>Flood level 1</span>
        </div>
        <div style="display: flex; align-items: center;padding: 2px">
            <div style="width: 20px;border: black solid 1px; height: 20px; background-color: #cc0000; border-radius: 50%; margin-right: 5px;"></div>
            <span>Flood level 2</span>
        </div>
        <div style="display: flex; align-items: center;padding: 2px">
            <div style="width: 20px; border: black solid 1px;height: 20px; background-color: #660033; border-radius: 50%; margin-right: 5px;"></div>
            <span>Flood level 3</span>
        </div>
        <div style="display: flex; align-items: center;padding: 2px">
            <div style="width: 20px; border: black solid 1px;height: 20px; background-color: #808080; border-radius: 50%; margin-right: 5px;"></div>
            <span>No data</span>
        </div>
             <div style="display: flex; align-items: center;padding: 2px">
              <img src="https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png" alt="Red Icon" width="20" height="30" style="margin-right: 5px;">
            <span>Flood report</span>
            <div>
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