var mymap = L.map('mapid').setView([50.1583, 12.6437], 13);
var tilelayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 19,
  attribution: '&copy; <a href="https://openstreetmap.org/copyright">OpenStreetMap contributors</a>'
}).addTo(mymap);
var printer = L.easyPrint({
	title: 'Save map',
	position: 'topleft',
	sizeModes: ["Current", 'A4Portrait', 'A4Landscape'],
  filename: 'myMap',
  exportOnly: true,
}).addTo(mymap);

function displayObjectOnMap(map, object){
  object["properties"]["color"] = object["properties"]["color"] || "#3399ff"
  var type = object["geometry"]["type"]
  var bbox = object["bbox"]

  var polygon = drawGeoJson(mymap, object)
  console.log("Added to map")
  mymap.fitBounds([[bbox[1], bbox[0]], [bbox[3], bbox[2]]]);


  var addedLayers = document.getElementById("addedLayers")
  var li = document.createElement("li")
  var span = document.createElement("span")
  var delButton = document.createElement("button")
  var colorPicker = document.createElement("input")
  for (a of [li, delButton, colorPicker, span]){
    a.dataset.id = polygon._leaflet_id;
    a.dataset.geoJSON = JSON.stringify(object)
  }
  span.classList.add("layerControls")
  colorPicker.type = "color"
  colorPicker.value = object["properties"]["color"]
  colorPicker.onchange = function (){
    getLayerId(mymap, this.dataset.id).setStyle({"color": this.value});
    removeObjectFromBackend(this.dataset.id);
    o = JSON.parse(this.dataset.geoJSON)
    o["properties"]["color"] = this.value
    addObjectToBackend(this.dataset.id, o)
  }
  colorPicker.classList.add("form-control", "form-control-color")
  li.innerHTML = object["properties"]["display_name"]
  li.classList.add("list-group-item", "bg-light-dark", "border-secondary", "text-white")
  delButton.innerHTML = '<i class="bi bi-trash"></i>'
  delButton.onclick = function(){
    removeLayerId(mymap, this.dataset.id);
    this.parentNode.parentNode.remove();
    removeObjectFromBackend(this.dataset.id)
  }
  delButton.classList.add("btn", "btn-delete", "btn-secondary")
  span.appendChild(colorPicker)
  span.appendChild(delButton)
  li.appendChild(span)
  addedLayers.appendChild(li)
  roundEdges(document.getElementById("addedLayers"))
  addObjectToBackend(polygon._leaflet_id, object)
}

function drawGeoJson(map, geoJson){
  var out = L.geoJSON(
    geoJson,
    {
      style: function(feature){
        return {color: feature.properties.color}
      }
    }
  )
  out.addTo(map)
  return out
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
  resultList.innerHTML = ""
  searchObject(quary).then(result => {
    for (var feature of result){
      var li = document.createElement("li")
      var button = document.createElement("button")
      li.innerHTML = feature["properties"]["display_name"]
      li.classList.add("list-group-item", "bg-light-dark", "border-secondary", "text-white")
      button.innerHTML = '<i class="bi bi-plus-lg"></i>'
      button.dataset.feature = JSON.stringify(feature)
      button.onclick = function() {
        displayObjectOnMap(mymap, JSON.parse(this.dataset.feature))
      }
      button.classList.add("btn", "btn-add", "btn-secondary", "layersControl")
      li.appendChild(button)
      resultList.appendChild(li)
    }
    resultList.style.removeProperty("display")
    roundEdges(document.getElementById("searchResults"))
  })
}

function removeLayerId(map, id){
  map.eachLayer(function(layer){if (layer._leaflet_id == id){layer.removeFrom(map)}})
}

/**
 * Get the layer with id.
 * @param {L.Map} map 
 * @param {Number} id 
 * @returns {L.Layer}
 */
function getLayerId(map, id){
  var layer;
  map.eachLayer(function(l){if (l._leaflet_id == id){console.log("Jeah"); layer = l}})
  return layer;
}

function roundEdges(element){
  for (var li of element.children){
    li.classList.remove("rounded-top", "rounded-bottom")
  }
  element.children[0].classList.add("rounded-top")
  element.children[element.children.length-1].classList.add("rounded-bottom")
}

function addObjectToBackend(id, object){
  fetch(`/api/updateCurrentMap`, 
    {
      method: "POST",
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({"id": id, "object": object})
    }
  )
}

function removeObjectFromBackend(id){
  fetch(`/api/updateCurrentMap?id=${id}`, 
    {
      method: "DELETE",
      headers: {
        'Content-Type': 'application/json'
      }
    }
  )
}

async function getMapFromBackend(name, userId){
  var url = `/api/getMap?name=${name}`
  if (userId){
    url += `&userId=${userId}`
  }
  return await (await fetch(url)).json()
}

function loadLastMap(){
  const urlParams = new URLSearchParams(window.location.search);
  const mapName = urlParams.get('map');
  const uid = urlParams.get("userId")

  console.log(mapName, uid)
  if (mapName == null){
    loadMap("Current")
  }
  else {
    console.log(mapName, uid)
    loadMap(mapName, uid)
  }
}

function loadMap(name, uid){
  clearMap()
  getMapFromBackend(name, uid).then(objects => {
    removeObjectFromBackend("all")
    for (var i in objects["data"]){
      displayObjectOnMap(mymap, objects["data"][i])
    }
  })
}

function clearMap(){
  for (var i of document.getElementById("addedLayers").getElementsByClassName("btn-delete")){
    i.click()
  }
}

function saveMap(){
  var name = prompt("Enter name of map");
  if (name != null){
    getMapFromBackend("Current").then(response => {
    fetch(`/api/saveMap`, 
      {
        method: "POST",
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({"name": name, "map": response["data"]})
      }
    )
  }
  )
}
}

function deleteMap(name){
  fetch(`/api/deleteMap?name=${name}`,
    {
      method: "DELETE",
      headers: {
        'Content-Type': 'application/json'
      }
    }
  )
}

loadLastMap()