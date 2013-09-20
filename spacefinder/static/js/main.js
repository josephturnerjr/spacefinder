(function() {
  var drawMap;

  drawMap = function(locations) {
    var bounds, loc, location, map, mapOptions, marker, _i, _len;
    mapOptions = {
      mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    map = new google.maps.Map(document.getElementById('listing-map'), mapOptions);
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
  };

  window.draw_listing_map = drawMap;

}).call(this);
