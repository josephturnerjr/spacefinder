geocoder = new google.maps.Geocoder()
g_locations = null
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
  bounds = new google.maps.LatLngBounds()
  loc_list = $('#location-list')
  loc_list.removeAttr('disabled')
  for location in locations
    marker = new google.maps.Marker({
        map: map,
        position: location.geometry.location,
    })
    bounds.extend(location.geometry.location)
    ((location)->
      google.maps.event.addListener(marker, 'click', () ->
        alert location.formatted_address
      )
    )(location)
    loc_list.html('').append("<option value='#{location.formatted_address}'>#{location.formatted_address}</option>")
  g_locations = locations
  loc_list.change((e)->
    update_hidden()
  )
  update_hidden()
  $('#step2').removeAttr('disabled')
  map.setCenter(bounds.getCenter())
  map.fitBounds(bounds)

update_hidden = () ->
  selected = $('#location-list').val()
  for location in g_locations
    if location.formatted_address == selected
      $('#latitude').val(location.geometry.location.lat())
      $('#longitude').val(location.geometry.location.lng())
      return


window.codeAddress = codeAddress
