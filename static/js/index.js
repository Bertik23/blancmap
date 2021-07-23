var mymap = L.map('mapid').setView([50.1583, 12.6437], 13);
var tilelayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 19,
  attribution: '&copy; <a href="https://openstreetmap.org/copyright">OpenStreetMap contributors</a>'
}).addTo(mymap);

var polygon = L.polygon([
    [51.509, -0.08],
    [51.503, -0.06],
    [51.51, -0.047]
]).addTo(mymap);


function displayObjectOnMap(map, object){
  console.log(object)
  fetch(`https://nominatim.openstreetmap.org/search?q=${object}&format=geojson&polygon_geojson=1`)
    .then(response => {response.json().then(rJson => {
      var type = rJson["features"][0]["geometry"]["type"]

      console.log(rJson)
      console.log(type)

      switch (type){
        case "Polygon":
          var coords = rJson["features"][0]["geometry"]["coordinates"][0]
          break
        case "LineString":
          var coords = rJson["features"][0]["geometry"]["coordinates"]
          break
        case "Point":
          var coords = [rJson["features"][0]["geometry"]["coordinates"]]
          break
      }
      var newCoords = []
      console.log(coords.length)
      for (var a=0; a < coords.length; a++){
        newCoords = newCoords.concat([[coords[a][1], coords[a][0]]])
      }

      console.log(newCoords)
      switch (type){
        case "Polygon":
          var polygon = L.polygon(newCoords).addTo(map)
          break
        case "LineString":
          console.log(type, "Line")
          var polygon = L.polyline(newCoords).addTo(map)
          break
        case "Point":
          console.log(type, "Pointík")
          var polygon = L.marker(newCoords[0]).addTo(map)
          break
      }
      console.log("Added to map")
      mymap.fitBounds(polygon.getBounds());
    })
  }
  )
}

function toggleTileLayer(map, overwrite=null){
  if (overwrite != null){
    if (overwrite) tilelayer.addTo(map)
    else tilelayer.removeFrom(map)
    return;
  }
  if (map.hasLayer(tilelayer)){
    tilelayer.removeFrom(map)
  } else {
    tilelayer.addTo(map)
  }
}