// Orion (app.paradigmmachines.ai) for dayglass.io: session replays with predicted gaze and friction scores.
// Same rules as clarity.js: loads only on dayglass.io itself, never for automated browsers, and never for the
// owner's own browsers (marked with ?dg_owner=1). The one exception is Orion's own agent link
// (?orion_agent=...), which Orion keeps apart from visitor numbers, so test visits can be checked.
(function (w) {
  try {
    var host = w.location.hostname;
    if (host !== "dayglass.io" && host !== "www.dayglass.io") return;
    var params = new URLSearchParams(w.location.search);
    var agent = !!params.get("orion_agent");
    if (agent) sessionStorage.setItem("dg_orion_agent", "1");
    agent = agent || sessionStorage.getItem("dg_orion_agent") === "1";
    if (!agent) {
      if (navigator.webdriver === true) return;
      var mark = params.get("dg_owner");
      if (mark === "1") localStorage.setItem("dg_owner", "1");
      if (mark === "0") localStorage.removeItem("dg_owner");
      if (localStorage.getItem("dg_owner") === "1") return;
    }
  } catch (e) {
    return;
  }
  // Orion's own snippet: a queue for identify/stop calls made before the script arrives.
  var h = (w.__orion = w.__orion || {}), o = (w.orion = w.orion || {});
  h.q = h.q || [];
  ["identify", "stop"].forEach(function (m) {
    var f = function () { h.q.push([m, [].slice.call(arguments)]); };
    f.q = 1;
    if (!o[m]) o[m] = f;
    if (!h[m]) h[m] = f;
  });
  var s = document.createElement("script");
  s.async = true;
  s.src = "https://t.paradigmmachines.ai/86vwvzk3zm3tvthbghw3.js";
  document.head.appendChild(s);
})(window);
