//! YRKDS Rust skor motoru — app/core/scoring.py ile BİREBİR aynı formül.
//! Referans: spesifikasyon 2.1 ve 2.4. Python dosyası değişirse parity testi
//! güncellenmelidir (tek kaynak ilkesi).
use pyo3::prelude::*;

fn clamp(v: f64) -> f64 {
    v.max(0.0).min(1.0)
}

fn vs30_etkin(vs30: Option<f64>, sinif: Option<&str>) -> Option<f64> {
    if let Some(v) = vs30 {
        return Some(v);
    }
    let s = sinif?.trim().to_uppercase();
    let s = s.replace(' ', "-");
    match s.as_str() {
        "ZA" => Some(800.0),
        "ZB" => Some(560.0),
        "ZC" => Some(270.0),
        "ZD" => Some(135.0),
        "ZE" => Some(90.0),
        "ZC-ZD" => Some(200.0),
        "ZD-ZE" => Some(110.0),
        "ZB-ZC" => Some(400.0),
        _ => None,
    }
}

fn zb(vs30: Option<f64>, sinif: Option<&str>, fay_km: Option<f64>) -> Option<f64> {
    let v = vs30_etkin(vs30, sinif)?;
    let mut p = if v >= 760.0 {
        0.0
    } else if v >= 360.0 {
        0.3
    } else if v >= 180.0 {
        0.7
    } else {
        1.0
    };
    if let Some(d) = fay_km {
        p += if d < 5.0 {
            0.15
        } else if d < 15.0 {
            0.10
        } else if d < 35.0 {
            0.05
        } else {
            0.0
        };
    }
    Some(clamp(p))
}

fn l(yass: Option<f64>, kum: Option<f64>) -> Option<f64> {
    let y = yass?;
    match kum {
        Some(k) if y < 3.0 && k > 60.0 => Some(1.0),
        Some(k) if y < 5.0 && k > 40.0 => Some(0.7),
        Some(_) if y < 10.0 => Some(0.3),
        Some(_) => Some(0.0),
        None if y < 10.0 => Some(0.3),
        None => Some(0.0),
    }
}

fn s(insar: Option<f64>, karst: bool, turba: bool, yuksek_yuk: bool) -> Option<f64> {
    let h = insar?;
    let mut p = if h > 10.0 {
        1.0
    } else if h > 5.0 {
        0.6
    } else if h > 1.0 {
        0.3
    } else {
        0.0
    };
    if karst {
        p += 0.2;
    }
    if turba {
        p += 0.2;
    }
    if yuksek_yuk && karst {
        p += 0.2;
    }
    Some(clamp(p))
}

fn h(egim: Option<f64>, kaya: bool, heyelan: bool) -> Option<f64> {
    if heyelan {
        return Some(1.0);
    }
    let e = egim?;
    let mut p = if e > 30.0 {
        1.0
    } else if e > 15.0 {
        0.6
    } else if e > 5.0 {
        0.2
    } else {
        0.0
    };
    if kaya {
        p += 0.2;
    }
    Some(clamp(p))
}

fn f(
    t100: Option<bool>,
    t500: Option<bool>,
    akarsu_m: Option<f64>,
    twi: Option<f64>,
    hand_m: Option<f64>,
    gecmis: Option<i64>,
) -> Option<f64> {
    let mut p = if t100 == Some(true) {
        1.0
    } else if t500 == Some(true) {
        0.6
    } else if let (Some(d), Some(t)) = (akarsu_m, twi) {
        if d < 200.0 && t > 8.0 {
            0.7
        } else if t > 8.0 {
            0.7
        } else if t > 6.0 && (hand_m.map_or(false, |v| v < 5.0) || gecmis.unwrap_or(0) >= 2) {
            0.7
        } else if t > 5.0 {
            0.4
        } else {
            0.1
        }
    } else if let Some(t) = twi {
        if t > 8.0 {
            0.7
        } else if t > 6.0 && (hand_m.map_or(false, |v| v < 5.0) || gecmis.unwrap_or(0) >= 2) {
            0.7
        } else if t > 5.0 {
            0.4
        } else {
            0.1
        }
    } else {
        return None;
    };
    if gecmis.unwrap_or(0) >= 3 {
        p += 0.15;
    }
    Some(clamp(p))
}

fn bant(skor: f64) -> &'static str {
    if skor <= 25.0 {
        "Düşük"
    } else if skor <= 50.0 {
        "Düşük-Orta"
    } else if skor <= 70.0 {
        "Orta-Yüksek"
    } else if skor <= 85.0 {
        "Yüksek"
    } else {
        "Kritik"
    }
}

#[pyclass]
#[derive(Clone)]
pub struct SkorInput {
    #[pyo3(get, set)] pub vs30: Option<f64>,
    #[pyo3(get, set)] pub zemin_sinifi: Option<String>,
    #[pyo3(get, set)] pub yass_m: Option<f64>,
    #[pyo3(get, set)] pub kum_orani: Option<f64>,
    #[pyo3(get, set)] pub insar_hiz: Option<f64>,
    #[pyo3(get, set)] pub karst: Option<bool>,
    #[pyo3(get, set)] pub egim: Option<f64>,
    #[pyo3(get, set)] pub kaya_dusmesi: Option<bool>,
    #[pyo3(get, set)] pub heyelan_envanter: Option<bool>,
    #[pyo3(get, set)] pub taskin_100y: Option<bool>,
    #[pyo3(get, set)] pub taskin_500y: Option<bool>,
    #[pyo3(get, set)] pub akarsu_mesafe_m: Option<f64>,
    #[pyo3(get, set)] pub twi: Option<f64>,
    #[pyo3(get, set)] pub hand_m: Option<f64>,
    #[pyo3(get, set)] pub gecmis_taskin_sayisi: Option<i64>,
    #[pyo3(get, set)] pub fay_mesafe_km: Option<f64>,
    #[pyo3(get, set)] pub pga_g: Option<f64>,
    #[pyo3(get, set)] pub turba: Option<bool>,
    #[pyo3(get, set)] pub organik: Option<bool>,
    #[pyo3(get, set)] pub yuksek_bina_yuku: Option<bool>,
    #[pyo3(get, set)] pub fay_sakinim_bandi: Option<bool>,
    #[pyo3(get, set)] pub afete_maruz_bolge: Option<bool>,
    #[pyo3(get, set)] pub taskin_yapi_yasagi: Option<bool>,
    #[pyo3(get, set)] pub falez_cekme_mesafesi: Option<bool>,
}

#[pymethods]
impl SkorInput {
    #[new]
    #[pyo3(signature = (
        vs30=None, zemin_sinifi=None, yass_m=None, kum_orani=None, insar_hiz=None,
        karst=None, egim=None, kaya_dusmesi=None, heyelan_envanter=None,
        taskin_100y=None, taskin_500y=None, akarsu_mesafe_m=None, twi=None, hand_m=None,
        gecmis_taskin_sayisi=None, fay_mesafe_km=None, pga_g=None, turba=None,
        organik=None, yuksek_bina_yuku=None, fay_sakinim_bandi=None,
        afete_maruz_bolge=None, taskin_yapi_yasagi=None, falez_cekme_mesafesi=None
    ))]
    #[allow(clippy::too_many_arguments)]
    fn new(
        vs30: Option<f64>,
        zemin_sinifi: Option<String>,
        yass_m: Option<f64>,
        kum_orani: Option<f64>,
        insar_hiz: Option<f64>,
        karst: Option<bool>,
        egim: Option<f64>,
        kaya_dusmesi: Option<bool>,
        heyelan_envanter: Option<bool>,
        taskin_100y: Option<bool>,
        taskin_500y: Option<bool>,
        akarsu_mesafe_m: Option<f64>,
        twi: Option<f64>,
        hand_m: Option<f64>,
        gecmis_taskin_sayisi: Option<i64>,
        fay_mesafe_km: Option<f64>,
        pga_g: Option<f64>,
        turba: Option<bool>,
        organik: Option<bool>,
        yuksek_bina_yuku: Option<bool>,
        fay_sakinim_bandi: Option<bool>,
        afete_maruz_bolge: Option<bool>,
        taskin_yapi_yasagi: Option<bool>,
        falez_cekme_mesafesi: Option<bool>,
    ) -> Self {
        Self {
            vs30, zemin_sinifi, yass_m, kum_orani, insar_hiz, karst, egim,
            kaya_dusmesi, heyelan_envanter, taskin_100y, taskin_500y,
            akarsu_mesafe_m, twi, hand_m, gecmis_taskin_sayisi, fay_mesafe_km, pga_g,
            turba, organik, yuksek_bina_yuku, fay_sakinim_bandi,
            afete_maruz_bolge, taskin_yapi_yasagi, falez_cekme_mesafesi,
        }
    }
}

/// (skor, bant, veto, [(kod, alt_puan), ...]) döndürür.
#[pyfunction]
fn skor_hesapla(
    input: &SkorInput,
) -> (Option<f64>, String, bool, Vec<(String, Option<f64>)>) {
    let alt: Vec<(String, Option<f64>)> = vec![
        ("ZB".into(), zb(input.vs30, input.zemin_sinifi.as_deref(), input.fay_mesafe_km)),
        ("L".into(), l(input.yass_m, input.kum_orani)),
        ("S".into(), s(
            input.insar_hiz,
            input.karst.unwrap_or(false),
            input.turba.unwrap_or(false) || input.organik.unwrap_or(false),
            input.yuksek_bina_yuku.unwrap_or(false),
        )),
        ("H".into(), h(
            input.egim,
            input.kaya_dusmesi.unwrap_or(false),
            input.heyelan_envanter.unwrap_or(false),
        )),
        ("F".into(), f(
            input.taskin_100y,
            input.taskin_500y,
            input.akarsu_mesafe_m,
            input.twi,
            input.hand_m,
            input.gecmis_taskin_sayisi,
        )),
    ];

    let weights = [0.25_f64, 0.20, 0.25, 0.15, 0.15];
    let mut toplam = 0.0;
    let mut agirlik = 0.0;
    for (i, (_, v)) in alt.iter().enumerate() {
        if let Some(p) = v {
            toplam += weights[i] * p;
            agirlik += weights[i];
        }
    }
    let skor = if agirlik > 0.0 {
        // Python round() banker's rounding kullanir; birebir parity icin
        // rust tarafinda da round_ties_even (half-to-even) uygulanir.
        Some(((100.0 * toplam / agirlik) * 10.0).round_ties_even() / 10.0)
    } else {
        None
    };

    let veto = input.fay_sakinim_bandi == Some(true)
        || input.afete_maruz_bolge == Some(true)
        || input.taskin_yapi_yasagi == Some(true)
        || input.falez_cekme_mesafesi == Some(true);

    let bant = skor.map(bant).unwrap_or("KARARSIZ").to_string();
    (skor, bant, veto, alt)
}

#[pymodule]
fn skor_motoru(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<SkorInput>()?;
    m.add_function(wrap_pyfunction!(skor_hesapla, m)?)?;
    Ok(())
}
