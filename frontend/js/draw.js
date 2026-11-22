/* Leaflet.Draw ile parsel çizimi -> POST /api/analyze */
window.YRKDraw = (function () {
  let harita = null;
  let ui = null;
  let cizilen = null;
  let sonGeo = null;

  function renk(skor) {
    if (skor === null) return "#777";
    if (skor <= 25) return "#2e9e5b";
    if (skor <= 50) return "#8fbf3f";
    if (skor <= 70) return "#e0a21b";
    if (skor <= 85) return "#e06a1b";
    return "#c62929";
  }

  async function analizEt(layer) {
    ui.durumMetin = "HESAPLANIYOR";
    try {
      const geojson = layer.toGeoJSON();
      sonGeo = geojson;
      const r = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          geojson,
          senaryo: document.getElementById("senaryoSec")?.value || "bugun",
        }),
      });
      if (!r.ok) throw new Error(`API hatası ${r.status}`);
      const sonuc = await r.json();
      layer.setStyle({ color: renk(sonuc.skor), fillColor: renk(sonuc.skor), fillOpacity: 0.4 });
      ui.goster(sonuc);
      ui.durumMetin = "ANALİZ TAMAM";
    } catch (e) {
      ui.durumMetin = "HATA: " + e.message;
      console.error(e);
    }
  }

  function alanEtiketi(layer) {
    const el = document.getElementById("olcumEtiket");
    if (!el) return;
    try {
      const latlngs = layer.getLatLngs()[0];
      const xs = latlngs.map(p => p.lng), ys = latlngs.map(p => p.lat);
      const minx = Math.min(...xs), maxx = Math.max(...xs),
            miny = Math.min(...ys), maxy = Math.max(...ys);
      const latOrt = (miny + maxy) / 2;
      const alan = (maxx - minx) * 111320 * Math.cos(latOrt * Math.PI / 180)
                 * (maxy - miny) * 110574;
      el.textContent = `Alan ≈ ${(alan / 10000).toFixed(2)} ha`;
    } catch (e) {
      el.textContent = "";
    }
  }

  return {
    sonGeojson() { return sonGeo; },
    temizle() {
      if (cizilen && harita) {
        harita.eachLayer(l => { if (l.hasLayer && l.hasLayer(cizilen)) l.removeLayer(cizilen); });
        cizilen = null;
      }
      ui.sonuc = null;
      window.YRKUX?.sonucYok?.();
      const el = document.getElementById("olcumEtiket");
      if (el) el.textContent = "";
    },
    /* Haritadaki grid hucresine tiklaninca kucuk bir parsel olusturup analiz eder */
    analizGeojson(geojson) {
      const layer = L.geoJSON(geojson);
      analizEt(layer);
    },
    baglan(h, arayuz) {
      harita = h; ui = arayuz;
      const katman = new L.FeatureGroup().addTo(h);
      h.addControl(new L.Control.Draw({
        edit: { featureGroup: katman, remove: true },
        draw: {
          polygon: { allowIntersection: false, shapeOptions: { color: "#0b5c5d" } },
          rectangle: { shapeOptions: { color: "#0b5c5d" } },
          circle: false, circlemarker: false, marker: false, polyline: false,
        },
      }));
      h.on("draw:created", e => {
        if (cizilen) katman.removeLayer(cizilen);
        cizilen = e.layer;
        katman.addLayer(cizilen);
        alanEtiketi(cizilen);
        window.YRKUX?.cizimAta?.(cizilen);
        analizEt(cizilen);
      });
      h.on("draw:edited", () => { if (cizilen) analizEt(cizilen); });
      document.getElementById("geojsonIndir")?.addEventListener("click", () => {
        const geo = cizilen ? cizilen.toGeoJSON() : { type: "FeatureCollection", features: [] };
        const a = document.createElement("a");
        a.href = URL.createObjectURL(new Blob([JSON.stringify(geo)], { type: "application/geo+json" }));
        a.download = "yrkds-sorgu.geojson"; a.click();
      });
    },
  };
})();
