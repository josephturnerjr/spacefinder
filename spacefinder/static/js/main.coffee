drawMap = (locations) ->
  mapOptions = {
    mapTypeId: google.maps.MapTypeId.ROADMAP
  }
  map = new google.maps.Map(document.getElementById('listing-map'), mapOptions)
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

window.draw_listing_map = drawMap
