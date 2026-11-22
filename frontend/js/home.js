/* Ana sayfa canlı istatistik ve olay akışı — API erişilemezse boş durum gösterilir. */
(function () {
  const tema = localStorage.getItem("yrkds-tema");
  if (tema) document.documentElement.dataset.theme = tema;
  document.getElementById("temaButonu")?.addEventListener("click", () => {
    const yeni = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = yeni;
    localStorage.setItem("yrkds-tema", yeni);
  });

  async function istatistik() {
    const kutu = document.getElementById("canliIstatistik");
    try {
      const [h, e] = await Promise.all([
        fetch("/api/hazirlik").then(r => r.json()),
        fetch("/api/events?limit=500").then(r => r.json()),
      ]);
      kutu.innerHTML = `
        <div class="istatistik"><span>Grid hücresi</span><b>${h.hucre.toLocaleString("tr-TR")}</b></div>
        <div class="istatistik"><span>Olay kaydı</span><b>${e.length}</b></div>
        <div class="istatistik"><span>Katman</span><b>10</b></div>
        <div class="istatistik"><span>Veri durumu</span><b class="kucuk">InSAR/SYGM yok</b></div>`;
    } catch (err) {
      kutu.innerHTML = '<div class="istatistik"><span class="muted">İstatistik yüklenemedi — API kontrol edin</span></div>';
    }
  }

  async function olaylar() {
    const list = document.getElementById("sonOlaylar");
    try {
      const r = await fetch("/api/events?limit=5");
      if (!r.ok) throw new Error(String(r.status));
      const veri = await r.json();
      list.innerHTML = veri.length
        ? veri.map(o => `<li><span class="rozet">${o.olay_turu}</span> ${o.tarih || "tarihsel"} — ${(o.etki || "").slice(0, 90)}</li>`).join("")
        : '<li class="muted">Kayıtlı olay yok.</li>';
    } catch (err) {
      list.innerHTML = '<li class="muted">Olay akışı yüklenemedi. Sayfayı yenileyin.</li>';
    }
  }
  istatistik();
  olaylar();
})();
