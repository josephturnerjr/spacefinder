(function() {
  var drawMap;

  drawMap = function(locations) {
    var bounds, loc, location, map, mapOptions, marker, _i, _len;
    mapOptions = {
      mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    map = new google.maps.Map(document.getElementById('listing-map'), mapOptions);
    if (locations.length > 0) {
      bounds = new google.maps.LatLngBounds();
      for (_i = 0, _len = locations.length; _i < _len; _i++) {
        location = locations[_i];
        loc = new google.maps.LatLng(location[0], location[1]);
        marker = new google.maps.Marker({
          map: map,
          position: loc
        });
        bounds.extend(loc);
      }
      map.setCenter(bounds.getCenter());
      return map.fitBounds(bounds);
    } else {
      map.setCenter(new google.maps.LatLng(39.303487, -76.609833));
      return map.setZoom(10);
    }
  };

  window.draw_listing_map = drawMap;

}).call(this);
