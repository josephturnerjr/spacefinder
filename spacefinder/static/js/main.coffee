drawMap = (locations) ->
  mapOptions = {
    mapTypeId: google.maps.MapTypeId.ROADMAP
  }
  map = new google.maps.Map(document.getElementById('listing-map'), mapOptions)
  if locations.length > 0
    bounds = new google.maps.LatLngBounds()
    for location in locations
      loc = new google.maps.LatLng(location[0], location[1])
      marker = new google.maps.Marker({
          map: map,
          position: loc,
      })
      bounds.extend(loc)
    map.setCenter(bounds.getCenter())
    map.fitBounds(bounds)
  else
    map.setCenter(new google.maps.LatLng(39.303487,-76.609833))
    map.setZoom(10)

window.draw_listing_map = drawMap
