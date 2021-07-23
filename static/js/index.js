var mymap = L.map('mapid').setView([50.1583, 12.6437], 13);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 19,
  attribution: '&copy; <a href="https://openstreetmap.org/copyright">OpenStreetMap contributors</a>'
}).addTo(mymap);

var polygon = L.polygon([
    [51.509, -0.08],
    [51.503, -0.06],
    [51.51, -0.047]
]).addTo(mymap);


function displayObjectOnMap(map, object){
  console.log(map, object)
  fetch(`https://nominatim.openstreetmap.org/search?q=${object}&format=geojson&polygon_geojson=1`)
    .then(response => {response.json().then(rJson => {
      var coords = rJson["features"][0]["geometry"]["coordinates"][0]

      var newCoords = []
      console.log(coords.length)
      for (var a=0; a < coords.length; a++){
        newCoords = newCoords.concat([[coords[a][1], coords[a][0]]])
      }

      console.log(rJson)
      console.log(newCoords)
      var polygon = L.polygon(newCoords).addTo(map)
      console.log("Added to map")
      mymap.fitBounds(polygon.getBounds());
    })
  }
  )
}