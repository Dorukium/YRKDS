(function(){
  async function yukle(){
    const tur=document.getElementById("tur").value, tarih=document.getElementById("tarih").value;
    const p=new URLSearchParams({limit:"200"}); if(tur)p.set("tur",tur);
    try{
      const r=await fetch("/api/events?"+p); const veri=await r.json();
      const satirlar=veri.filter(o=>!tarih||(o.tarih||"").startsWith(tarih));
      document.getElementById("olaylar").innerHTML=satirlar.length?satirlar.map(o=>`<tr>
        <td>${o.tarih||"—"}</td><td><span class="rozet">${o.olay_turu}</span></td>
        <td>${o.mahalle||o.ilce||"—"}</td><td class="kucuk">${(o.etki||"").slice(0,100)}</td>
        <td class="kucuk">${o.kaynak_url||"—"}</td>
        <td><span class="rozet">${o.dogrulama_etiketi?"kaynaklı etiket":"kayıt"}</span></td></tr>`).join("")
        :'<tr><td colspan="6" class="muted">Filtreye uyan olay yok.</td></tr>';
    }catch(e){document.getElementById("olaylar").innerHTML='<tr><td colspan="6" class="muted">Olaylar yüklenemedi.</td></tr>';}
  }
  document.getElementById("uygula").addEventListener("click",yukle); yukle();
})();
