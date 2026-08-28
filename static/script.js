document.addEventListener("DOMContentLoaded", () => {
  const map = L.map("tourism-map", {
    zoomControl: true,
    attributionControl: false
  }).setView([20.5937, 78.9629], 5);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "&copy; OpenStreetMap contributors"
  }).addTo(map);

  const form = document.querySelector("#destination-search");
  const input = document.querySelector("#destination");
  const status = document.querySelector("#search-status");
  const results = document.querySelector("#destination-results");
  const count = document.querySelector("#result-count");
  const submitBtn = document.querySelector("#search-btn");
  const markers = L.featureGroup().addTo(map);

  const setStatus = (message, isError = false) => {
    status.textContent = message;
    status.classList.toggle("is-error", isError);
  };

  function createMainMarker(place) {
    const icon = L.divIcon({
      className: "main-pin-container",
      html: `<div class="main-destination-pin">★</div>`,
      iconSize: [36, 36],
      iconAnchor: [18, 18]
    });

    const marker = L.marker([place.lat, place.lon], { icon }).addTo(markers);
    marker.bindPopup(`
      <div style="font-family: inherit; padding: 2px;">
        <strong style="font-size: 1rem; color: #17302e;">${place.name}</strong>
        ${place.full_name ? `<div style="font-size: 0.78rem; color: #65716f; margin-top: 4px; line-height: 1.3;">${place.full_name}</div>` : ""}
      </div>
    `);
    return marker;
  }

  function createPlaceMarker(place, index) {
    const icon = L.divIcon({
      className: `place-pin-container pin-${index}`,
      html: `<div class="custom-pin" id="pin-${index}">${index + 1}</div>`,
      iconSize: [30, 30],
      iconAnchor: [15, 15]
    });

    const marker = L.marker([place.lat, place.lon], { icon }).addTo(markers);
    marker.bindPopup(`
      <div style="font-family: inherit;">
        <strong style="color: #17302e;">${place.name}</strong>
      </div>
    `);

    marker.on("click", () => {
      highlightActivePlace(index);
    });

    return marker;
  }

  function highlightActivePlace(index) {
    document.querySelectorAll(".place-card").forEach((card, i) => {
      card.classList.toggle("active", i === index);
      if (i === index) {
        card.scrollIntoView({ behavior: "smooth", block: "nearest" });
      }
    });

    document.querySelectorAll(".custom-pin").forEach((pin, i) => {
      pin.classList.toggle("is-active", i === index);
    });
  }

  function renderResults(places, placeMarkers) {
    count.textContent = `${places.length} ${places.length === 1 ? "place" : "places"}`;

    if (!places.length) {
      results.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon">🔍</div>
          <p>No nearby attractions found within this radius.</p>
        </div>
      `;
      return;
    }

    results.replaceChildren(
      ...places.map((place, index) => {
        const card = document.createElement("div");
        card.className = "place-card";
        card.innerHTML = `
          <div class="place-badge">${index + 1}</div>
          <div class="place-details">
            <span class="place-title">${place.name}</span>
            <span class="place-sub">View attraction on map</span>
          </div>
          <span class="place-arrow">→</span>
        `;

        card.addEventListener("click", () => {
          highlightActivePlace(index);
          map.flyTo([place.lat, place.lon], 15, { duration: 1.2 });
          map.once("moveend", () => placeMarkers[index].openPopup());
        });

        return card;
      })
    );
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const destination = input.value.trim();
    if (!destination) return;

    setStatus("Searching attractions...");
    submitBtn.disabled = true;

    try {
      const response = await fetch(`/api/v1/search?destination=${encodeURIComponent(destination)}`);
      const payload = await response.json();

      if (!response.ok) {
        throw new Error(payload.error || "Unable to complete search.");
      }

      markers.clearLayers();

      const mainMarker = createMainMarker(payload.main);
      const placeMarkers = (payload.nearby || []).map((p, idx) => createPlaceMarker(p, idx));

      const bounds = markers.getBounds();
      if (bounds.isValid()) {
        map.fitBounds(bounds.pad(0.18));
      }

      mainMarker.openPopup();
      renderResults(payload.nearby || [], placeMarkers);
      setStatus(`Showing ${payload.main.name} and ${(payload.nearby || []).length} nearby places.`);
    } catch (err) {
      setStatus(err.message, true);
      results.innerHTML = `<div class="empty-state"><p>Try searching another city or landmark.</p></div>`;
      count.textContent = "0 places";
    } finally {
      submitBtn.disabled = false;
    }
  });

  window.addEventListener("resize", () => {
    map.invalidateSize();
  });
});