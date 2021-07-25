var mymap = L.map('mapid').setView([50.1583, 12.6437], 13);
var tilelayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 19,
  attribution: '&copy; <a href="https://openstreetmap.org/copyright">OpenStreetMap contributors</a>'
}).addTo(mymap);

function displayObjectOnMap(map, object){
  var type = object["geometry"]["type"]


  switch (type){
    case "Polygon":
      var coords = object["geometry"]["coordinates"][0]
      break
    case "LineString":
      var coords = object["geometry"]["coordinates"]
      break
    case "Point":
      var coords = [object["geometry"]["coordinates"]]
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
  try {mymap.fitBounds(polygon.getBounds());}
  catch {}

  var addedLayers = document.getElementById("addedLayers")
  var li = document.createElement("button")
  li.innerHTML = object["properties"]["display_name"]
  li.dataset.id = polygon._leaflet_id
  li.onclick = function(){removeLayerId(mymap, this.dataset.id); this.remove()}
  addedLayers.appendChild(li)
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

/**
 * Searches for objects and return list of features
 * @param {String} object
 * @returns {JSON}
 */
async function searchObject(object){
  var rJson = await (await fetch(`https://nominatim.openstreetmap.org/search?q=${object}&format=geojson&polygon_geojson=1`)).json()
  return rJson["features"]
}

function searchFor(){
  var quary = document.getElementById("addToMap").value;
  var resultList = document.getElementById("searchResults")
  searchObject(quary).then(result => {
    for (var feature of result){
      var li = document.createElement("button")
      li.innerHTML = feature["properties"]["display_name"]
      li.dataset.feature = JSON.stringify(feature)
      li.onclick = function() {resultList.style.display = "none"; displayObjectOnMap(mymap, JSON.parse(this.dataset.feature))}
      resultList.appendChild(li)
    }
    resultList.style.removeProperty("display")
  })
}

function removeLayerId(map, id){
  map.eachLayer(function(layer){if (layer._leaflet_id == id){layer.removeFrom(map)}})
}