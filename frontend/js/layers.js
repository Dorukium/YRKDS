/* Katman ac/kapat ve API'den GeoJSON yükleme */
window.YRKLayers = (function () {
  let harita = null;
  const katmanlar = {};
  const stiller = {
    bina: { color: "#8a6d3b", weight: 1, fillOpacity: 0.25 },
    su_yollari: { color: "#2b8cbe", weight: 2 },
    taskin: { color: "#d95f0e", weight: 1, radius: 3, fillOpacity: 0.6 },
    afete_maruz: { color: "#b30000", weight: 1, fillOpacity: 0.5 },
    deprem: { color: "#d7301f", radius: 5, fillOpacity: 0.8 },
  };

  function stile(dogrulama) {
    return { ...stiller[dogrulama] || { color: "#3388ff" } };
  }

  async function yukle(ad) {
    if (katmanlar[ad]) return katmanlar[ad];
    const r = await fetch(`/api/layers/${ad}`);
    if (!r.ok) throw new Error(`${ad}: ${r.status}`);
    const geo = await r.json();
    const katman = L.geoJSON(geo, {
      style: stile(ad),
      pointToLayer: (f, latlng) => L.circleMarker(latlng, stile(ad)),
      onEachFeature: (f, layer) => {
        if (f.properties && Object.keys(f.properties).length) {
          layer.bindTooltip(Object.entries(f.properties).map(([k, v]) => `${k}: ${v}`).join("<br>"));
        }
      },
    });
    katmanlar[ad] = katman;
    return katman;
  }

  return {
    baglan(h) { harita = h; },
    kaydet(ad, katman) { katmanlar[ad] = katman; },
    async degistir(ad, acik) {
      try {
        if (acik) {
          const k = await yukle(ad);
          if (!harita.hasLayer(k)) k.addTo(harita);
        } else if (katmanlar[ad] && harita.hasLayer(katmanlar[ad])) {
          harita.removeLayer(katmanlar[ad]);
        }
      } catch (e) {
        console.warn(e);
        const el = document.getElementById("katmanDurumu");
        if (el) el.textContent = `${ad} katmanı yüklenemedi: ${e.message}`;
      }
    },
  };
})();
