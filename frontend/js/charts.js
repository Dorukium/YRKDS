/* Chart.js radar grafigi: 5 tehlike alt puanı */
window.YRKCharts = (function () {
  let grafik = null;
  const ETIKETLER = ["ZB Zemin", "L Sıvılaşma", "S Oturma", "H Heyelan", "F Taşkın"];
  return {
    goster(kirilim) {
      const ctx = document.getElementById("radar");
      if (!ctx) return;
      if (grafik) grafik.destroy();
      const degerler = ["ZB", "L", "S", "H", "F"].map(k => kirilim[k] ?? null);
      grafik = new Chart(ctx, {
        type: "radar",
        data: {
          labels: ETIKETLER,
          datasets: [{
            label: "Alt puan (0–1)",
            data: degerler,
            spanGaps: true,
            borderColor: "#0b5c5d",
            backgroundColor: "rgba(11,92,93,.18)",
            pointBackgroundColor: "#0b5c5d",
          }],
        },
        options: {
          responsive: true,
          scales: { r: { min: 0, max: 1, ticks: { stepSize: 0.25, font: { size: 8 } },
                         pointLabels: { font: { size: 9 } } } },
          plugins: { legend: { display: false } },
        },
      });
    },
  };
})();
