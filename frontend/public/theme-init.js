(function () {
  "use strict";
  var THEME_KEY = "creavity-theme";
  var DARK_MEDIA = "(prefers-color-scheme: dark)";

  function readPref() {
    var v = localStorage.getItem(THEME_KEY);
    return v === "light" || v === "dark" || v === "auto" ? v : "auto";
  }

  function systemTheme() {
    if (typeof window.matchMedia !== "function") {
      return "light";
    }
    return window.matchMedia(DARK_MEDIA).matches ? "dark" : "light";
  }

  function resolve(pref) {
    if (pref === "light") {
      return "light";
    }
    if (pref === "dark") {
      return "dark";
    }
    return systemTheme();
  }

  var theme = resolve(readPref());
  document.documentElement.dataset.theme = theme;
  document.documentElement.dataset.bsTheme = theme;
  document.documentElement.style.colorScheme = theme;
})();
