document.addEventListener("DOMContentLoaded", () => {
  const map = L.map("tourism-map").setView([20.5937, 78.9629], 5);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", { maxZoom: 19, attribution: "&copy; OpenStreetMap contributors" }).addTo(map);
  const form = document.querySelector("#destination-search");
  const input = document.querySelector("#destination");
  const status = document.querySelector("#search-status");
  const results = document.querySelector("#destination-results");
  const count = document.querySelector("#result-count");
  const markers = L.featureGroup().addTo(map);
  const setStatus = (message, isError = false) => { status.textContent = message; status.classList.toggle("is-error", isError); };
  function addMarker(place, isMain = false) {
    const marker = L.circleMarker([place.lat, place.lon], {
      radius: isMain ? 11 : 8,
      color: "#fff", weight: 3,
      fillColor: isMain ? "#d86937" : "#0b6e69",
      fillOpacity: 1
    }).addTo(markers);

    // Main place: rich popup opened immediately after fitBounds
    // Nearby: permanent tooltip so the name is always visible on the map
    if (isMain) {
      marker.bindPopup(`<strong>${place.name}</strong>${place.full_name ? `<br><span style="font-size:.8em;color:#65716f">${place.full_name}</span>` : ""}`);
    } else {
      marker.bindTooltip(place.name, {
        permanent: true,
        direction: "top",
        offset: [0, -10],
        className: "nearby-label"
      });
      // Also bind a popup for when user clicks the dot directly
      marker.bindPopup(`<strong>${place.name}</strong>`);
    }
    return marker;
  }
  function renderResults(places, placeMarkers) {
    count.textContent = `${places.length} ${places.length === 1 ? "place" : "places"}`;
    if (!places.length) { results.innerHTML = '<p class="empty-state">No nearby attractions were found.</p>'; return; }
    results.replaceChildren(...places.map((place, index) => {
      const button = document.createElement("button");
      button.type = "button"; button.className = "place-card";
      button.innerHTML = `<span class="place-number">${index + 1}</span><span><strong>${place.name}</strong><small>View on map</small></span>`;
      button.addEventListener("click", () => {
        map.flyTo([place.lat, place.lon], 15, { duration: 1.2 });
        map.once("moveend", () => placeMarkers[index].openPopup());
      });
      return button;
    }));
  }
  form.addEventListener("submit", async (event) => {
    event.preventDefault(); const destination = input.value.trim(); if (!destination) return;
    setStatus("Searching for places…"); const submit = form.querySelector("button"); submit.disabled = true;
    try {
      const response = await fetch(`/api/v1/search?destination=${encodeURIComponent(destination)}`);
      const payload = await response.json(); if (!response.ok) throw new Error(payload.error || "Unable to complete the search.");
      markers.clearLayers();
      const destinationMarker = addMarker(payload.main, true);
      const nearbyMarkers = payload.nearby.map((place) => addMarker(place));
      const bounds = markers.getBounds();
      if (bounds.isValid()) map.fitBounds(bounds.pad(0.2));
      destinationMarker.openPopup();
      renderResults(payload.nearby, nearbyMarkers);
      setStatus(`Showing ${payload.main.name} and ${payload.nearby.length} nearby attractions.`);
    } catch (error) { setStatus(error.message, true); results.innerHTML = '<p class="empty-state">Try another destination in a moment.</p>'; count.textContent = "0 places"; }
    finally { submit.disabled = false; }
  });
});
