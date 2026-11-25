// Microsoft Clarity for dayglass.io: session counts, scroll depth, rage and dead clicks, heatmaps.
// Loads only on dayglass.io itself, never for automated browsers, and never for the owner's own browsers
// (marked with ?dg_owner=1), so the owner board counts real visitors. Clarity masks anything typed into a
// field; the site has no form fields, and the page's own public text is the only text it sees.
(function () {
  try {
    var host = window.location.hostname;
    if (host !== "dayglass.io" && host !== "www.dayglass.io") return;
    if (navigator.webdriver === true) return;
    var mark = new URLSearchParams(window.location.search).get("dg_owner");
    if (mark === "1") localStorage.setItem("dg_owner", "1");
    if (mark === "0") localStorage.removeItem("dg_owner");
    if (localStorage.getItem("dg_owner") === "1") return;
  } catch (e) {
    return;
  }
  (function (c, l, a, r, i, t, y) {
    c[a] = c[a] || function () { (c[a].q = c[a].q || []).push(arguments); };
    t = l.createElement(r); t.async = 1; t.src = "https://www.clarity.ms/tag/" + i;
    y = l.getElementsByTagName(r)[0]; y.parentNode.insertBefore(t, y);
  })(window, document, "clarity", "script", "zjac22a5n1");
  window.clarity("set", "site", "dayglass");
})();
