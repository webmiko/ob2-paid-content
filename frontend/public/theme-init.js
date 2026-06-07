(function () {
  "use strict";

  var THEME_KEY = "creavity-theme";
  var COORDS_KEY = "creavity-coords";
  var DEFAULT = { lat: 55.7558, lng: 37.6174 };
  var PI = Math.PI;
  var RAD = PI / 180;
  var DAY_MS = 86400000;
  var J1970 = 2440588;
  var J2000 = 2451545;
  var E = RAD * 23.4397;

  function readPref() {
    var v = localStorage.getItem(THEME_KEY);
    return v === "light" || v === "dark" || v === "auto" ? v : "auto";
  }

  function readCoords() {
    try {
      var raw = localStorage.getItem(COORDS_KEY);
      if (!raw) return DEFAULT;
      var c = JSON.parse(raw);
      if (typeof c.lat === "number" && typeof c.lng === "number") return c;
    } catch (e) {}
    return DEFAULT;
  }

  function toJulian(d) {
    return d.valueOf() / DAY_MS - 0.5 + J1970;
  }

  function fromJulian(j) {
    return new Date((j + 0.5 - J1970) * DAY_MS);
  }

  function sunTimes(date, lat, lng) {
    var lw = RAD * -lng;
    var phi = RAD * lat;
    var d = toJulian(date) - J2000;
    var n = Math.round(d - 0.0009 - lw / (2 * PI));
    var m = RAD * (357.5291 + 0.98560028 * n);
    var l =
      m +
      RAD * (1.9148 * Math.sin(m) + 0.02 * Math.sin(2 * m)) +
      RAD * 102.9372 +
      PI;
    var dec = Math.asin(Math.sin(l) * Math.sin(E));
    var h = RAD * -0.833;
    var w = Math.acos(
      (Math.sin(h) - Math.sin(phi) * Math.sin(dec)) / (Math.cos(phi) * Math.cos(dec)),
    );
    var st = RAD * (280.16 + 0.9856474 * n) - lw;
    var riseJ =
      J2000 + n + 0.0053 * Math.sin(m) - 0.0069 * Math.sin(2 * (st - w));
    var setJ =
      J2000 + n + 0.0053 * Math.sin(m) - 0.0069 * Math.sin(2 * (st + w));
    return { sunrise: fromJulian(riseJ), sunset: fromJulian(setJ) };
  }

  function isDay(now, coords) {
    var day = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    var t = sunTimes(day, coords.lat, coords.lng);
    var ts = now.getTime();
    return ts >= t.sunrise.getTime() && ts < t.sunset.getTime();
  }

  function resolve(pref, coords) {
    if (pref === "light") return "light";
    if (pref === "dark") return "dark";
    return isDay(new Date(), coords) ? "light" : "dark";
  }

  var pref = readPref();
  var coords = readCoords();
  var theme = resolve(pref, coords);
  document.documentElement.dataset.theme = theme;
  document.documentElement.dataset.bsTheme = theme;
  document.documentElement.style.colorScheme = theme;
})();
