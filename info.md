# Camera Object Detector

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Rilevamento automatico di oggetti usando AI per Home Assistant.

## Caratteristiche

✅ **Rilevamento automatico** di oggetti tramite AI  
📷 **Telecamere integrate** - usa le tue telecamere esistenti  
🤖 **Moondream AI** - analisi cloud potente e precisa  
🔄 **Aggiornamento configurabile** - da 30 secondi a 1 ora  
📊 **Attributi dettagliati** - confidence, spiegazione, timestamp  
🎨 **Icone personalizzate** - feedback visivo chiaro  

## Installazione Rapida

1. Installa tramite HACS o manualmente
2. Ottieni API key da [moondream.ai](https://moondream.ai/)
3. Configura tramite UI: Impostazioni → Dispositivi e Servizi → Aggiungi integrazione
4. Seleziona la tua telecamera
5. Inserisci l'API key
6. Enjoy! 🎉

## Casi d'uso

- 🌧️ **Notifica prima della pioggia** se lo stendino è fuori
- 🌅 **Promemoria al tramonto** per ritirare il bucato
- 🌙 **Alert notturno** se dimenticato fuori
- 📊 **Statistiche** su quanto spesso dimentichi lo stendino

## Esempi di Automazione

### Avviso pioggia
```yaml
automation:
  - alias: "Avviso stendino prima della pioggia"
    trigger:
      platform: state
      entity_id: weather.home
      to: "rainy"
    condition:
      condition: state
      entity_id: binary_sensor.stendino_presente
      state: "on"
    action:
      service: notify.mobile_app
      data:
        message: "Lo stendino è fuori e sta per piovere!"
```

### Promemoria sera
```yaml
automation:
  - alias: "Promemoria stendino al tramonto"
    trigger:
      platform: sun
      event: sunset
      offset: "-00:30:00"
    condition:
      condition: state
      entity_id: binary_sensor.stendino_presente
      state: "on"
    action:
      service: notify.mobile_app
      data:
        message: "Ritira lo stendino dal giardino!"
```

## Documentazione

Per documentazione completa, esempi e troubleshooting, visita il [README completo](https://github.com/yourusername/camera-object-detector).

## Supporto

Hai trovato un bug o hai una feature request? [Apri una issue](https://github.com/yourusername/camera-object-detector/issues)!

## Contribuire

Contributi benvenuti! Pull requests sono apprezzate.

---

Made with ❤️ for the Home Assistant community
