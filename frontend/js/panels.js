/* Alpine.js store: sonuc paneli ve genel durum */
document.addEventListener("alpine:init", () => {
  Alpine.data("yrkds", () => ({
    sonuc: null,
    durumMetin: "HARİTA YÜKLENİYOR",
    baslat() {
      window.YRKMap.baslat(this);
    },
    goster(sonuc) {
      this.sonuc = sonuc;
      window.YRKUX?.sonucVar?.();
      // x-if ile panel bir sonraki tick'te render edilir; canvas o zaman var.
      this.$nextTick(() => window.YRKCharts.goster(sonuc.tehlike_kirilimi));
    },
    kapat() {
      this.sonuc = null;
      window.YRKUX?.sonucYok?.();
    },
    bantSinifi(bant) {
      return bant || "KARARSIZ";
    },
  }));
});
