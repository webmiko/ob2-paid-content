(function () {
  "use strict";
  var THEME_KEY = "creavity-theme";
  var COORDS_KEY = "creavity-coords";
  var DEFAULT = { lat: 55.7558, lng: 37.6174 };
  var TZ_COORDS = {
    "Europe/Kaliningrad": { lat: 54.71, lng: 20.51 },
    "Europe/Moscow": { lat: 55.76, lng: 37.62 },
    "Europe/Samara": { lat: 53.2, lng: 50.15 },
    "Asia/Yekaterinburg": { lat: 56.84, lng: 60.6 },
    "Asia/Omsk": { lat: 54.99, lng: 73.37 },
    "Asia/Krasnoyarsk": { lat: 56.01, lng: 92.87 },
    "Asia/Irkutsk": { lat: 52.29, lng: 104.28 },
    "Asia/Yakutsk": { lat: 62.03, lng: 129.73 },
    "Asia/Vladivostok": { lat: 43.12, lng: 131.89 },
    "Europe/Minsk": { lat: 53.9, lng: 27.57 },
    "Asia/Almaty": { lat: 43.24, lng: 76.95 },
    "Asia/Qyzylorda": { lat: 44.85, lng: 65.52 },
  };
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

  function coordsFromTimezone() {
    try {
      var tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
      if (TZ_COORDS[tz]) {
        return TZ_COORDS[tz];
      }
    } catch (e) {}
    var offsetHours = -new Date().getTimezoneOffset() / 60;
    return { lat: 55.75, lng: Math.max(-180, Math.min(180, offsetHours * 15)) };
  }

  function readCoords() {
    try {
      var raw = localStorage.getItem(COORDS_KEY);
      if (raw) {
        var c = JSON.parse(raw);
        if (typeof c.lat === "number" && typeof c.lng === "number") {
          var isDefault =
            c.lat === DEFAULT.lat && c.lng === DEFAULT.lng;
          if (isDefault) {
            return coordsFromTimezone();
          }
          return c;
        }
      }
    } catch (e) {}
    return coordsFromTimezone();
  }

  function clamp(v) {
    return Math.max(-1, Math.min(1, v));
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
      m + RAD * (1.9148 * Math.sin(m) + 0.02 * Math.sin(2 * m)) + RAD * 102.9372 + PI;
    var dec = Math.asin(Math.sin(l) * Math.sin(E));
    var h = RAD * -0.833;
    var w = Math.acos(
      clamp((Math.sin(h) - Math.sin(phi) * Math.sin(dec)) / (Math.cos(phi) * Math.cos(dec))),
    );
    var st = RAD * (280.16 + 0.9856474 * n) - lw;
    return {
      sunrise: fromJulian(J2000 + n + 0.0053 * Math.sin(m) - 0.0069 * Math.sin(2 * (st - w))),
      sunset: fromJulian(J2000 + n + 0.0053 * Math.sin(m) - 0.0069 * Math.sin(2 * (st + w))),
    };
  }

  function isDay(now, coords) {
    var day = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    var t = sunTimes(day, coords.lat, coords.lng);
    var ts = now.getTime();
    return ts >= t.sunrise.getTime() && ts < t.sunset.getTime();
  }

  function resolve(pref, coords) {
    if (pref === "light") {
      return "light";
    }
    if (pref === "dark") {
      return "dark";
    }
    return isDay(new Date(), coords) ? "light" : "dark";
  }

  var pref = readPref();
  var coords = readCoords();
  var theme = resolve(pref, coords);
  document.documentElement.dataset.theme = theme;
  document.documentElement.dataset.bsTheme = theme;
  document.documentElement.style.colorScheme = theme;
})();
