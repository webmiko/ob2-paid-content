(function () {
  "use strict";
  var path = location.pathname;
  if (path !== "/" && path !== "") {
    return;
  }
  window.__CREAVITY_FEED_PREFETCH__ = fetch("/api/posts/", {
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  }).then(function (response) {
    if (!response.ok) {
      throw new Error(String(response.status));
    }
    return response.json();
  });
})();
