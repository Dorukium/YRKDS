/* V2 akışları: F1 ray/tur, F2 karşılaştırma, F3 toplu, F5 derin bağlantı,
   F7 durum/yeniden dene, F8 komut paleti. */
(function () {
  const ADIMLAR = [
    { ad: "Ara", hedef: "#araGirdi", metin: "Mahalle, koordinat veya GeoJSON ile git." },
    { ad: "Çiz", hedef: "[data-action=draw]", metin: "Poligon çiz, Enter ile bitir." },
    { ad: "Sonuç", hedef: ".sag", metin: "Skor, kanıt ve belirsizlik burada." },
    { ad: "Rapor", hedef: "a.btn[href*='/api/report/']", metin: "PDF ve GeoJSON indir." },
  ];
  let adim = 0;
  let karsilastir = false;
  let ilk = null;
  let ikinci = null;

  function veri() { return window.Alpine?.$data?.(document.getElementById("app")); }
  function aktifSonuc() { return veri()?.sonuc || null; }

  function rayCiz() {
    const ray = document.getElementById("kilavuzRay");
    if (!ray) return;
    ray.innerHTML = ADIMLAR.map((a, i) =>
      `<button class="ray-adim ${i === adim ? "aktif" : ""}" data-adim="${i}"
        aria-label="${a.ad} adımı">${i + 1}. ${a.ad}</button>`).join("");
    ray.querySelectorAll("button").forEach(b =>
      b.addEventListener("click", () => spotlight(Number(b.dataset.adim))));
  }

  function spotlight(i) {
    adim = i; rayCiz();
    const a = ADIMLAR[i], hedef = document.querySelector(a.hedef);
    const kutu = document.getElementById("turKutu");
    if (!kutu || !hedef) return;
    document.getElementById("turBaslik").textContent = `${a.ad} — ${i + 1}/4`;
    document.getElementById("turMetin").textContent = a.metin;
    kutu.hidden = false;
    hedef.scrollIntoView({ block: "center", behavior: "smooth" });
    localStorage.setItem("yrkds-tur-adim", String(i));
  }

  function turKapat() {
    const kutu = document.getElementById("turKutu");
    if (kutu) kutu.hidden = true;
    localStorage.setItem("yrkds-tur", "1");
  }

  async function derinBaglanti() {
    const q = new URLSearchParams(location.search).get("q");
    if (!q) return;
    try {
      const r = await fetch(`/api/query/${encodeURIComponent(q)}`);
      if (!r.ok) return;
      veri()?.goster(await r.json());
    } catch (e) { console.warn(e); }
  }

  function karsilastirmaKarti(a, b) {
    if (!a || !b) return "";
    const satir = (kod, ad) => {
      const x = a.tehlike_kirilimi?.[kod], y = b.tehlike_kirilimi?.[kod];
      const d = (x != null && y != null) ? (y - x) : null;
      return `<tr><td>${ad}</td><td class="tabular">${x ?? "—"}</td>
              <td class="tabular">${y ?? "—"}</td>
              <td class="tabular">${d === null ? "—" : (d > 0 ? "+" : "") + d.toFixed(2)}</td></tr>`;
    };
    const tercih = (a.skor ?? 0) <= (b.skor ?? 0)
      ? `${a.parsel_id} parselini tercih et çünkü skoru ${a.skor} ve ${b.parsel_id}'den ${((b.skor ?? 0) - (a.skor ?? 0)).toFixed(1)} puan düşük.`
      : `${b.parsel_id} parselini tercih et çünkü skoru ${b.skor} ve ${a.parsel_id}'den ${((a.skor ?? 0) - (b.skor ?? 0)).toFixed(1)} puan düşük.`;
    return `<table class="tablo"><thead><tr><th>Bileşen</th><th>A</th><th>B</th><th>Δ</th></tr></thead><tbody>
      ${satir("ZB", "Zemin")}${satir("L", "Sıvılaşma")}${satir("S", "Oturma")}
      ${satir("H", "Heyelan")}${satir("F", "Taşkın")}</tbody></table>
      <p class="kucuk"><b>${tercih}</b> Karar olasılıksaldır; zemin etüdü yerine geçmez.</p>`;
  }

  function karsilastirBaslat() {
    ilk = aktifSonuc();
    if (!ilk) return;
    karsilastir = true;
    const k = document.getElementById("karsilastirKutu");
    if (k) k.innerHTML = '<p class="kucuk">Şimdi ikinci parseli çizin; karşılaştırma burada görünecek.</p>';
  }

  window.YRK_V2 = {
    yeniSonuc(s) {
      if (karsilastir && ilk) {
        ikinci = s; karsilastir = false;
        const k = document.getElementById("karsilastirKutu");
        if (k) { k.hidden = false; k.innerHTML = karsilastirmaKarti(ilk, ikinci); }
      }
    },
    turBaslat() { spotlight(0); },
    turKapat,
  };

  async function topluYukle(file) {
    const metin = await file.text();
    let features = [];
    try {
      const j = JSON.parse(metin);
      features = j.type === "FeatureCollection" ? j.features : [j];
    } catch (e) {
      const satirlar = metin.trim().split(/\r?\n/).slice(1);
      features = satirlar.map(s => {
        const [lon, lat] = s.split(",").map(Number);
        return { type: "Feature", geometry: { type: "Point", coordinates: [lon, lat] },
                 properties: {} };
      });
    }
    const kutu = document.getElementById("topluKutu");
    kutu.innerHTML = `<p class="kucuk">${features.length} aday hesaplanıyor…</p>`;
    const sonuclar = [];
    for (const f of features.slice(0, 20)) {
      let geo = f.geometry;
      if (geo.type === "Point") {
        const [lon, lat] = geo.coordinates, d = 0.0005;
        geo = { type: "Polygon", coordinates: [[
          [lon - d, lat - d], [lon + d, lat - d], [lon + d, lat + d],
          [lon - d, lat + d], [lon - d, lat - d]]] };
      }
      try {
        const r = await fetch("/api/analyze", {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ geojson: geo }),
        });
        if (r.ok) sonuclar.push(await r.json());
      } catch (e) { /* aday atlanır */ }
    }
    sonuclar.sort((a, b) => (a.skor ?? 999) - (b.skor ?? 999));
    kutu.innerHTML = `<table class="tablo"><thead><tr><th>#</th><th>Parsel</th><th>Skor</th><th>Bant</th></tr></thead><tbody>` +
      sonuclar.map((s, i) => `<tr><td>${i + 1}</td><td>${s.parsel_id}</td>
        <td class="tabular">${s.skor ?? "—"}</td><td>${s.bant}</td></tr>`).join("") +
      '</tbody></table><button class="btn btn-outline btn-sm" id="topluCsv">CSV indir</button>';
    document.getElementById("topluCsv")?.addEventListener("click", () => {
      const csv = "parsel,skor,bant\n" + sonuclar.map(s =>
        `"${s.parsel_id}",${s.skor ?? ""},"${s.bant}"`).join("\n");
      const a = document.createElement("a");
      a.href = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
      a.download = "yrkds-adaylar.csv"; a.click();
    });
  }

  function komutPaleti() {
    const k = document.getElementById("komutPaleti");
    if (!k) return;
    k.hidden = false;
    const giris = k.querySelector("input"); giris.value = ""; giris.focus();
    const eylemler = [
      { ad: "Haritaya git", url: "/harita.html" },
      { ad: "Tur başlat", fn: () => spotlight(0) },
      { ad: "Karşılaştırma modu", fn: karsilastirBaslat },
      { ad: "Katmanları aç", fn: () => document.querySelector('[data-sekme=katmanlar]')?.click() },
      { ad: "Lejantı aç", fn: () => document.querySelector('[data-sekme=lejant]')?.click() },
      { ad: "Yöntem sayfası", url: "/yontem.html" },
    ];
    const liste = k.querySelector("ul");
    function ciz(arama = "") {
      liste.innerHTML = eylemler.filter(e => e.ad.toLocaleLowerCase("tr").includes(arama.toLocaleLowerCase("tr")))
        .map((e, i) => `<li data-i="${i}"><button>${e.ad}</button></li>`).join("");
      liste.querySelectorAll("button").forEach((b, i) => b.addEventListener("click", () => {
        const e = eylemler.filter(x => x.ad.toLocaleLowerCase("tr").includes(arama.toLocaleLowerCase("tr")))[i];
        k.hidden = true; if (e.url) location.href = e.url; else e.fn?.();
      }));
    }
    giris.oninput = () => ciz(giris.value);
    ciz();
    k.querySelector("[data-kapat]").onclick = () => { k.hidden = true; };
  }

  document.addEventListener("DOMContentLoaded", () => {
    rayCiz(); derinBaglanti();
    if (localStorage.getItem("yrkds-tur") !== "1") setTimeout(() => spotlight(0), 1300);
    document.getElementById("turKapat")?.addEventListener("click", turKapat);
    document.getElementById("karsilastirBtn")?.addEventListener("click", karsilastirBaslat);
    document.getElementById("topluDosya")?.addEventListener("change", e => {
      if (e.target.files?.[0]) topluYukle(e.target.files[0]);
    });
    document.addEventListener("keydown", e => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") { e.preventDefault(); komutPaleti(); }
    });
    // V2 sonuçlarını yakala (Alpine goster() sonrası)
    const goster = veri()?.goster;
    if (goster) {
      veri().goster = function (s) { goster.call(this, s); window.YRK_V2.yeniSonuc(s); };
    }
  });
})();
