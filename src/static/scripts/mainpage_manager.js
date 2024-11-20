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

   var markers = L.markerClusterGroup();

    // Add markers for reports
    reports.forEach(function (report) {
        if (report.location) {
            var coords = report.location.split(',');
            var lat = parseFloat(coords[0]);
            var lng = parseFloat(coords[1]);

            if (!isNaN(lat) && !isNaN(lng)) {
                var marker = L.marker([lat, lng]);
                marker.bindPopup(`
                    <strong>Description:</strong> ${report.description}<br>
                    <strong>Location:</strong> ${lat}, ${lng}
                `);
                markers.addLayer(marker);
            }
        }
    });

    map.addLayer(markers);

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