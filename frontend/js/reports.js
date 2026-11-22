(function(){
  const tablo=document.getElementById("raporTablosu"), bos=document.getElementById("raporBos");
  let veri=[];
  async function yukle(){
    try{
      const r=await fetch("/api/queries/me");
      if(r.status===401||r.status===403) return;
      if(!r.ok) throw new Error(String(r.status));
      veri=await r.json();
      document.getElementById("girisMesaji").textContent="Oturum açık. Sorgularınız aşağıda listelenir.";
      document.getElementById("csvIndir").hidden=false;
      ciz();
    }catch(e){ console.warn(e); }
  }
  function ciz(){
    const ilce=document.getElementById("ilceFiltre").value, bant=document.getElementById("bantFiltre").value,
          tarih=document.getElementById("tarihFiltre").value;
    const filtre=veri.filter(q=>(!ilce||q.ilce===ilce)&&(!bant||q.bant===bant)&&(!tarih||(q.tarih||"").startsWith(tarih)));
    tablo.hidden=filtre.length===0; bos.hidden=filtre.length>0;
    tablo.querySelector("tbody").innerHTML=filtre.map(q=>`<tr><td>${q.tarih||"—"}</td><td>${q.sonuc_id}</td>
      <td class="tabular">${q.skor??"—"}</td><td>${q.bant||"KARARSIZ"}</td>
      <td><a href="/api/report/${q.sonuc_id}.pdf">PDF</a></td>
      <td><a href="/api/query/${q.sonuc_id}.geojson">GeoJSON</a></td></tr>`).join("");
  }
  ["ilceFiltre","bantFiltre","tarihFiltre"].forEach(id=>document.getElementById(id).addEventListener("change",ciz));
  document.getElementById("csvIndir").addEventListener("click",()=>{
    const satirlar=[["tarih","sonuc_id","skor","bant"],...veri.map(q=>[q.tarih,q.sonuc_id,q.skor,q.bant])];
    const csv=satirlar.map(r=>r.map(v=>`"${String(v??"").replace(/"/g,'""')}"`).join(",")).join("\n");
    const a=document.createElement("a"); a.href=URL.createObjectURL(new Blob([csv],{type:"text/csv"}));
    a.download="yrkds-sorgularim.csv"; a.click();
  });
  yukle();
})();
