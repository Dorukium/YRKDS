/* Leaflet harita kurulumu ve grid temsil katmanı */
window.YRKMap = (function () {
  let harita = null;
  let ui = null;
  let gridKatmani = null;

  /* Sürekli risk rampası — sert eşiklerle her şeyi kırmızı boyamak yanıltıcıdır. */
  function riskRengi(f) {
    const p = (f && f.properties) || {};
    const sinir = (v, ust) => Math.max(0, Math.min(1, (v ?? 0) / ust));
    const risk = 0.35 * sinir(p.twi, 12) + 0.25 * sinir(p.egim, 30)
      + 0.25 * (1 - sinir(p.vs30 ?? 800, 800)) + 0.15 * sinir(p.kum, 80);
    // Viridis esintili, renk körlüğü güvenli sıralı palet (kırmızı-yeşil ikilisi yok)
    if (risk < 0.25) return "#440154";
    if (risk < 0.45) return "#3b528b";
    if (risk < 0.60) return "#21918c";
    if (risk < 0.75) return "#5ec962";
    return "#fde725";
  }

  async function gridYukle() {
    // F6: sunucu tarafı PNG tile — istemcide canvas dairesi yok.
    gridKatmani = L.tileLayer("/tiles/{z}/{x}/{y}.png", {
      maxZoom: 16, maxNativeZoom: 13, opacity: 0.9, attribution: "YRKDS risk ızgarası",
    });
    gridKatmani.addTo(harita);
    window.YRKLayers.kaydet("grid", gridKatmani);

    harita.on("click", async ev => {
      try {
        const r = await fetch(`/api/cell?lon=${ev.latlng.lng}&lat=${ev.latlng.lat}`);
        if (!r.ok) return;
        const c = await r.json();
        const d = 0.00011;
        const kart = L.popup().setLatLng(ev.latlng).setContent(`
          <div class="kucuk"><b>${c.ilce || "—"}</b><br>
          Eğim ${Number(c.egim || 0).toFixed(1)}° · TWI ${Number(c.twi || 0).toFixed(1)}<br>
          Vs30 ${c.vs30 || "yok"} · Kum ${c.kum ? Number(c.kum).toFixed(0) + "%" : "yok"}<br>
          Kıyı &lt;2m: ${c.kiyi_2m ? "evet" : "hayır"}<br>
          Yasal kısıt: Bilinmiyor — veri yok<br>
          <button class="btn btn-dark btn-sm" id="tamAnaliz">Tam analiz</button></div>`);
        kart.openOn(harita);
        document.getElementById("tamAnaliz")?.addEventListener("click", () => {
          const parsel = {
            type: "Polygon", coordinates: [[
              [ev.latlng.lng - d, ev.latlng.lat - d], [ev.latlng.lng + d, ev.latlng.lat - d],
              [ev.latlng.lng + d, ev.latlng.lat + d], [ev.latlng.lng - d, ev.latlng.lat + d],
              [ev.latlng.lng - d, ev.latlng.lat - d],
            ]],
          };
          window.YRKDraw.analizGeojson(parsel);
        });
      } catch (e) { console.warn(e); }
    });
  }

  async function olaylariYukle() {
    const r = await fetch("/api/events?tur=deprem&limit=300");
    if (!r.ok) return;
    const olaylar = await r.json();
    const cluster = L.markerClusterGroup();
    olaylar.forEach(o => {
      if (o.lat === null || o.lon === null) return;
      const m = L.circleMarker([o.lat, o.lon], { radius: 5, color: "#d7301f", fillOpacity: 0.8 });
      m.bindPopup(`<b>${o.tarih || 'tarihsel'}</b><br>${o.etki || ''}<br><small>${o.kaynak_url || ''}</small>`);
      cluster.addLayer(m);
    });
    cluster.addTo(harita);
    window.YRKLayers.kaydet("deprem", cluster);
  }

  return {
    merkezle(lat, lon) {
      if (harita) harita.setView([lat, lon], 15);
    },
    zoom(yon) {
      if (harita) harita.setZoom(harita.getZoom() + yon);
    },
    baslat(arayuz) {
      ui = arayuz;
      harita = L.map("harita", { zoomControl: false }).setView([36.90, 30.73], 11);
      const osm = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19, attribution: "© OpenStreetMap contributors",
      });
      const esri = L.tileLayer(
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        { attribution: "Tiles © Esri", maxZoom: 19 },
      );
      const topo = L.tileLayer("https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png", {
        maxZoom: 17, attribution: "© OpenTopoMap (CC-BY-SA)",
      });
      osm.addTo(harita);
      L.control.layers({ "Sokak (OSM)": osm, "Uydu (Esri)": esri, "Arazi (OpenTopoMap)": topo }, null,
        { position: "topright" }).addTo(harita);
      harita.on("mousemove", ev => {
        const el = document.getElementById("koordinat");
        if (el) el.textContent = `${ev.latlng.lat.toFixed(4)}°K, ${ev.latlng.lng.toFixed(4)}°D`;
      });

      window.YRKLayers.baglan(harita);
      window.YRKDraw.baglan(harita, arayuz);

      document.querySelectorAll("[data-katman]").forEach(el => {
        el.addEventListener("change", () => window.YRKLayers.degistir(el.dataset.katman, el.checked));
      });

      (async () => {
        try {
          await gridYukle();
          const cb = document.querySelector('[data-katman="grid"]');
          if (cb) { cb.dataset.yuklu = "1"; }
          await olaylariYukle();
          const durumEl = document.getElementById("katmanDurumu");
          if (durumEl) durumEl.textContent = "25 m grid yüklendi (~20 bin örnek). "
            + "InSAR/SYGM/TDTH ve yasal VETO katmanları veri setinde yok; "
            + "guven ve karar buna göre düşürülür.";
          ui.durumMetin = "HAZIR";
        } catch (e) {
          ui.durumMetin = "VERİ YÜKLENEMEDİ";
          console.error(e);
        }
      })();
    },
  };
})();
