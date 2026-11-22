/* D4 — TR/EN arayüz. Eksik anahtarlar TR'ye düşer (dürüst geri dönüş). */
(function () {
  const DIL = localStorage.getItem('yrkds-dil') || 'tr';
  let sozluk = {};

  function uygula() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const anahtar = el.dataset.i18n;
      if (sozluk[anahtar]) el.textContent = sozluk[anahtar];
    });
    document.documentElement.lang = DIL;
    const sec = document.getElementById('dilSec');
    if (sec) sec.value = DIL;
  }

  async function baslat() {
    try {
      const tr = await fetch('/locales/tr.json').then(r => r.json());
      if (DIL === 'tr') sozluk = tr;
      else {
        const en = await fetch('/locales/en.json').then(r => r.json());
        sozluk = Object.assign({}, tr, en);
      }
    } catch (e) { console.warn('i18n yüklenemedi', e); }
    uygula();
  }

  document.addEventListener('DOMContentLoaded', () => {
    baslat();
    document.getElementById('dilSec')?.addEventListener('change', e => {
      localStorage.setItem('yrkds-dil', e.target.value);
      location.reload();
    });
  });
})();
