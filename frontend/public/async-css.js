(function () {
  "use strict";

  document.querySelectorAll("link[data-async-css]").forEach(function (link) {
    function apply() {
      link.media = "all";
    }

    if (link.sheet) {
      apply();
      return;
    }

    link.addEventListener("load", apply);
  });
})();
