/* Harita UX: tur, kısayollar, arama, sekmeler, tema, dışa aktarma, boş durum. */
(function () {
  const ADIMLAR = [
    { baslik: "1/4 — Ara", metin: "Mahalle, koordinat veya GeoJSON yapıştırıp Git'e basın." },
    { baslik: "2/4 — Katmanlar", metin: "Sol panelden katmanları açıp kapatın." },
    { baslik: "3/4 — Çizim", metin: "✎ aracıyla parsel çizin; Enter ile bitirin." },
    { baslik: "4/4 — Sonuç", metin: "Skor, kanıtlar ve PDF raporu sağ panelde." },
  ];
  let turAdim = 0;
  let cizim = null;

  function turGoster() {
    const kutu = document.getElementById("turKutu");
    if (!kutu) return;
    const a = ADIMLAR[turAdim];
    document.getElementById("turBaslik").textContent = a.baslik;
    document.getElementById("turMetin").textContent = a.metin;
    kutu.hidden = false;
  }
  function turKapat() {
    const kutu = document.getElementById("turKutu");
    if (kutu) kutu.hidden = true;
    localStorage.setItem("yrkds-tur", "1");
  }
  function turBaslat() { turAdim = 0; turGoster(); }

  function tema() {
    const yeni = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = yeni;
    localStorage.setItem("yrkds-tema", yeni);
  }

  function sekmeAc(ad) {
    document.querySelectorAll("[data-sekme]").forEach(b =>
      b.setAttribute("aria-selected", String(b.dataset.sekme === ad)));
    document.querySelectorAll("[data-panel]").forEach(p => { p.hidden = p.dataset.panel !== ad; });
  }

  async function ara(girdi) {
    const sonuc = document.getElementById("araSonuc");
    const metin = girdi.trim();
    if (!metin) return;
    if (metin.startsWith("{")) {
      try {
        const geo = JSON.parse(metin);
        window.YRKDraw.analizGeojson(geo);
        sonuc.textContent = "GeoJSON analize gönderildi.";
        return;
      } catch (e) { sonuc.textContent = "GeoJSON ayrıştırılamadı."; return; }
    }
    const koord = metin.match(/^\s*(-?\d+(?:\.\d+)?)\s*[, ]\s*(-?\d+(?:\.\d+)?)\s*$/);
    if (koord) {
      const lat = parseFloat(koord[1]), lon = parseFloat(koord[2]);
      window.YRKMap?.merkezle?.(lat, lon);
      sonuc.textContent = `${lat}, ${lon} koordinatına gidildi.`;
      return;
    }
    sonuc.textContent = "Arama yerel dizinde aranıyor…";
    try {
      const r = await fetch(`/api/events?limit=200`);
      const olaylar = await r.json();
      const eslesme = olaylar.find(o => (o.mahalle || "").toLocaleLowerCase("tr").includes(metin.toLocaleLowerCase("tr")));
      if (eslesme && eslesme.lat && eslesme.lon) {
        window.YRKMap?.merkezle?.(eslesme.lat, eslesme.lon);
        sonuc.textContent = `${eslesme.mahalle} bulundu.`;
      } else {
        sonuc.textContent = "Yerel kayıtta bulunamadı. Nominatim dış arama erişimi bu sürümde yok (ADR).";
      }
    } catch (e) { sonuc.textContent = "Arama servisi yanıt vermedi."; }
  }

  function disaAktar() {
    const geo = cizim ? cizim.toGeoJSON() : { type: "FeatureCollection", features: [] };
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([JSON.stringify(geo)], { type: "application/geo+json" }));
    a.download = "yrkds-parsel.geojson"; a.click();
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("temaButonu")?.addEventListener("click", tema);
    document.querySelectorAll("[data-sekme]").forEach(b =>
      b.addEventListener("click", () => sekmeAc(b.dataset.sekme)));
    document.getElementById("araForm")?.addEventListener("submit", e => {
      e.preventDefault(); ara(document.getElementById("araGirdi").value);
    });
    // Tur v2.js tarafından yönetilir; ikinci zamanlayıcı/kapatma dinleyicisi yok.

    document.querySelectorAll(".arac-cubugu button").forEach(btn => btn.addEventListener("click", () => {
      const a = btn.dataset.action;
      if (a === "zoom-in") window.YRKMap?.zoom?.(1);
      if (a === "zoom-out") window.YRKMap?.zoom?.(-1);
      if (a === "draw") document.querySelector(".leaflet-draw-draw-polygon")?.click();
      if (a === "layers") sekmeAc("katmanlar");
      if (a === "legend") sekmeAc("lejant");
      if (a === "export") disaAktar();
      if (a === "clear") window.YRKDraw?.temizle?.();
      if (a === "fullscreen") document.documentElement.requestFullscreen?.();
    }));
    document.addEventListener("keydown", e => {
      if (["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement?.tagName)) return;
      const k = e.key.toLowerCase();
      if (k === "d") document.querySelector(".leaflet-draw-draw-polygon")?.click();
      if (k === "l") sekmeAc("katmanlar");
      if (k === "g") sekmeAc("lejant");
      if (k === "e") disaAktar();
      if (k === "f") document.documentElement.requestFullscreen?.();
      if (k === "escape") turKapat();
    });
  });

  window.YRKUX = {
    turBaslat, turKapat,
    sonucVar() { const b = document.getElementById("bosDurum"); if (b) b.hidden = true; },
    sonucYok() { const b = document.getElementById("bosDurum"); if (b) b.hidden = false; },
    cizimAta(l) { cizim = l; },
  };
})();
