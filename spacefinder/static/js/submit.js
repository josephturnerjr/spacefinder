(function() {
  var codeAddress, drawMap, g_locations, geocoder, update_hidden;

  geocoder = new google.maps.Geocoder();

  g_locations = null;

  codeAddress = function(address) {
    return geocoder.geocode({
      'address': address
    }, function(results, status) {
      if (status === google.maps.GeocoderStatus.OK) {
        return drawMap(results);
      } else {
        return alert('Geocode was not successful for the following reason: ' + status);
      }
    });
  };

  drawMap = function(locations) {
    var bounds, latlng, loc_list, location, map, mapOptions, marker, _fn, _i, _len;
    latlng = locations[0].geometry.location;
    mapOptions = {
      zoom: 12,
      center: latlng,
      mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    map = new google.maps.Map(document.getElementById('map_canvas'), mapOptions);
    bounds = new google.maps.LatLngBounds();
    loc_list = $('#location-list');
    loc_list.removeAttr('disabled').html('');
    _fn = function(location) {
      return google.maps.event.addListener(marker, 'click', function() {
        return alert(location.formatted_address);
      });
    };
    for (_i = 0, _len = locations.length; _i < _len; _i++) {
      location = locations[_i];
      marker = new google.maps.Marker({
        map: map,
        position: location.geometry.location
      });
      bounds.extend(location.geometry.location);
      _fn(location);
      loc_list.append("<option value='" + location.formatted_address + "'>" + location.formatted_address + "</option>");
    }
    g_locations = locations;
    loc_list.change(function(e) {
      return update_hidden();
    });
    update_hidden();
    $('#step2').removeAttr('disabled');
    map.setCenter(bounds.getCenter());
    return map.fitBounds(bounds);
  };

  update_hidden = function() {
    var location, selected, _i, _len;
    selected = $('#location-list').val();
    for (_i = 0, _len = g_locations.length; _i < _len; _i++) {
      location = g_locations[_i];
      if (location.formatted_address === selected) {
        $('#latitude').val(location.geometry.location.lat());
        $('#longitude').val(location.geometry.location.lng());
        return;
      }
    }
  };

  window.codeAddress = codeAddress;

}).call(this);
