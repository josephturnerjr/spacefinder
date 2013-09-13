geocoder = new google.maps.Geocoder()
codeAddress = (address) ->
  geocoder.geocode( { 'address': address}, (results, status) ->
    if status == google.maps.GeocoderStatus.OK
      drawMap(results)
    else
      alert('Geocode was not successful for the following reason: ' + status)
  )

drawMap = (locations) ->
  latlng = locations[0].geometry.location
  mapOptions = {
    zoom: 12,
    center: latlng,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  }
  map = new google.maps.Map(document.getElementById('map_canvas'), mapOptions)
  for location in locations
    marker = new google.maps.Marker({
        map: map,
        position: location.geometry.location,
    })


window.codeAddress = codeAddress
