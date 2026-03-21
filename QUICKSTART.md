# 🚀 Guida Rapida - Camera Object Detector

## 📋 Prerequisiti

- ✅ Home Assistant 2026.3.0 o superiore
- ✅ Una o più telecamere configurate in Home Assistant
- ✅ Account Moondream AI (gratuito o a pagamento)
- ✅ Connessione Internet
- ✅ Python 3.12+ (per test standalone script)

## 🎯 Installazione in 5 minuti

### Step 1: Installa l'integrazione

**Opzione A - HACS (Consigliato)**

1. Apri HACS nel tuo Home Assistant
2. Clicca su "Integrations"
3. Clicca i tre puntini in alto → "Custom repositories"
4. Aggiungi: `https://github.com/emanueleManni/camera-object-detector`
5. Categoria: "Integration"
6. Clicca "Add"
7. Cerca "Camera Object Detector" e installa
8. Riavvia Home Assistant

**Opzione B - Manuale**

1. Scarica questo repository
2. Copia `custom_components/camera_object_detector` in `<config>/custom_components/`
3. Riavvia Home Assistant

### Step 2: Ottieni l'API Key

1. Vai su https://moondream.ai/
2. Crea un account (pochi secondi)
3. Vai alla dashboard
4. Copia la tua API key

💡 **Nota**: Il piano gratuito include crediti per testare!

### Step 3: Configura l'integrazione ⚠️ OBBLIGATORIO

**⚠️ Questo step è OBBLIGATORIO** anche se vuoi usare solo l'action `detect_object` senza binary sensor!

1. Vai su **Impostazioni** → **Dispositivi e Servizi**
2. Clicca **+ Aggiungi integrazione** (in basso a destra)
3. Cerca "**Camera Object Detector**"
4. Compila il form:
   - **Telecamera**: `camera.carraio` (seleziona la tua)
   - **Servizio AI**: `Moondream AI (Cloud)`
   - **API Key**: incolla la key di Moondream
   - **Oggetto da Rilevare**: seleziona dal menu (es. `drying_rack`) o inserisci un nome custom
   - **Intervallo**: `300` secondi (5 minuti) - o `86400` (24 ore) se vuoi query rarissime
   - **💡 Disable Binary Sensor**: Attiva se vuoi SOLO l'action senza query automatiche ([dettagli](ACTION_ONLY_MODE.md))
5. Clicca **Invia**
6. ✅ Fatto!

**Risultato:**
- Se "Disable Binary Sensor" = NO: Viene creato `binary_sensor.carraio_drying_rack_detection`
- Se "Disable Binary Sensor" = SÌ: **Nessun binary sensor**, solo action disponibile (risparmio API!)
- L'action `detect_object` è **sempre** disponibile in entrambi i casi

💡 **Want Action Only?** Leggi la [guida completa "Action Only Mode"](ACTION_ONLY_MODE.md) per usare solo l'action senza query automatiche!

💡 **Oggetti supportati**: drying_rack, person, car, bicycle, dog, cat, chair, table, umbrella, bag, bottle, e molti altri!

### Step 4: Verifica che funzioni

**Opzione A - Testa il Binary Sensor**

1. Vai su **Strumenti per sviluppatori** → **Stati**
2. Cerca `binary_sensor.carraio_drying_rack_detection`
3. Dovresti vedere:
   - Stato: `on` oppure `off`
   - Attributi: `confidence`, `object_count`, `detected_objects`, `detection_object`, etc.

💡 **Tip**: Controlla `detected_objects` per vedere le coordinate bounding box e la confidenza di ogni oggetto rilevato!

**Opzione B - Testa l'Action detect_object**

1. Vai su **Strumenti per sviluppatori** → **Servizi**
2. Cerca il servizio: `camera_object_detector.detect_object`
3. Inserisci i dati:
   ```yaml
   camera_entity: camera.carraio
   detection_object: drying_rack
   ```
4. Clicca **"Chiama servizio"**
5. Guarda la risposta (Response data):
   ```yaml
   object_present: true
   object_count: 1
   confidence: 1.0
   image_time: "2024-03-21T15:30:00"
   detected_objects: [...]
   ```

✅ Se vedi la risposta, funziona perfettamente!

### Step 5: Prima automazione

**Opzione A - Usa il Binary Sensor (monitoraggio continuo)**

Ideale se vuoi monitorare costantemente lo stendino con l'intervallo configurato:

```yaml
automation:
  - alias: "Test Stendino - Binary Sensor"
    trigger:
      platform: state
      entity_id: binary_sensor.carraio_drying_rack_detection
      to: "on"
    action:
      service: notify.notify
      data:
        message: "🎉 Stendino rilevato!"
        title: "Stendino Detector"
```

**Opzione B - Usa l'Action detect_object (on-demand)**

Ideale se vuoi controllare solo quando serve (es: quando piove):

```yaml
automation:
  - alias: "Promemoria Stendino"
    trigger:
      # Quando inizia a piovere
      - platform: numeric_state
        entity_id: sensor.gw1100a_rain_rate  # Sensore pioggia
        above: 0.1
      # Oppure alle 20:00
      - platform: time
        at: "20:00:00"
    action:
      # Rileva stendino on-demand (chiama API solo quando necessario)
      - service: camera_object_detector.detect_object
        data:
          camera_entity: camera.carraio
          detection_object: "drying_rack"
        response_variable: detection
      
      # Solo se rilevato
      - condition: template
        value_template: "{{ detection.object_present }}"
      
      # Notifica
      - service: notify.notify
        data:
          title: "⚠️ Ritira lo stendino!"
          message: "Lo stendino è ancora fuori!"
```

**💡 Vantaggio dell'Action**: Chiama l'API solo quando serve, risparmiando costi!

## 🎨 Aggiungi una Card

Lovelace UI → Aggiungi card → Tipo: Entities

```yaml
type: entities
title: 🏡 Controllo Giardino
entities:
  - entity: binary_sensor.stendino_presente
    name: Stendino
    secondary_info: last-changed
```

## 📱 Notifiche Mobile

Sul tuo telefono!

```yaml
automation:
  - alias: "Stendino + Pioggia"
    trigger:
      platform: state
      entity_id: weather.home
      to: "rainy"
    condition:
    ⚠️ Errore: "No AI service specified"

➡️ **Causa**: Non hai configurato l'integrazione tramite UI (Step 3)

➡️ **Soluzione**: Vai in **Impostazioni** → **Dispositivi e Servizi** → **+ Aggiungi Integrazione** → Cerca "Camera Object Detector" e configura

➡️ **Dettagli completi**: Leggi [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md)

###   condition: state
      entity_id: binary_sensor.stendino_presente
      state: "on"
    action:
      service: notify.mobile_app_<il_tuo_telefono>
      data:
        title: "⚠️ Attenzione!"
        message: "Lo stendino è fuori e sta per piovere!"
```

**Sostituisci** `mobile_app_<il_tuo_telefono>` con il tuo dispositivo (es. `mobile_app_iphone_di_mario`)

## 🔧 Configurazione Avanzata

### Modifica le impostazioni

1. **Impostazioni** → **Dispositivi e Servizi**
2. Trova "Camera Object Detector"
3. Clicca **Configura**
4. Modifica intervallo, API key, etc.

### Intervalli consigliati

- ⚡ **Tempo reale**: 60 secondi (alto consumo API)
- ✅ **Normale**: 300 secondi (5 minuti) - **consigliato**
- 💰 **Economico**: 900 secondi (15 minuti)
- 🌙 **Notte**: 1800 secondi (30 minuti)

### Costi stimati

Con 300 secondi (5 min):
- Richieste/giorno: ~288
- Richieste/mese: ~8.640

Verifica i prezzi su https://moondream.ai/pricing

## ❓ Problemi Comuni

### "Camera not found"

➡️ Verifica che la telecamera sia configurata: vai su **Impostazioni** → **Dispositivi** e cerca la tua camera.

### "API key required"

➡️ Hai selezionato "Moondream AI" ma non hai inserito l'API key. Inseriscila o seleziona "Local" (non ancora implementato).

### Sensore sempre "unavailable"

➡️ Controlla i log: **Impostazioni** → **Sistema** → **Log**. Cerca errori con "stendino".

### Rilevamenti imprecisi

➡️ Verifica:

- Oggetto ben visibile nell'inquadratura
- Nome oggetto corretto (in inglese)
- Prova con nomi più specifici (es. "folding drying rack" invece di "rack")

### Test prima dell'installazione

➡️ Usa lo script standalone:

```bash
# Installa dipendenze
pip install moondream pillow

# Test con immagine (sostituisci YOUR_API_KEY con la tua chiave da https://moondream.ai/)
python tests/test_moondream_standalone.py foto.jpg YOUR_API_KEY drying_rack
```

- Telecamera ben posizionata
- Stendino ben visibile nell'inquadratura

## 🎓 Prossimi Passi

1. ✅ **Modalità Action Only?** Leggi **[ACTION_ONLY_MODE.md](ACTION_ONLY_MODE.md)** per disabilitare il binary sensor e risparmiare sui costi
2. ✅ Leggi la **[Guida Action Completa](ACTION_GUIDE.md)** per usare `detect_object` nelle automazioni
3. ✅ Vedi **[Esempi di Automazioni](automation_example.yaml)** per casi d'uso avanzati
4. ✅ Se hai problemi, leggi **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)**
5. ✅ Leggi il [README completo](README.md) per dettagli tecnici
6. ✅ Controlla [examples.md](examples.md) per più automazioni
7. ✅ Unisciti alla community per condividere idee!

## 📚 Documentazione

## 💬 Supporto

- 🐛 **Bug?** Apri una [issue](https://github.com/emanueleManni/camera-object-detector/issues)
- 💡 **Idee?** Proponi una feature!
- ❤️ **Ti piace?** Lascia una stella su GitHub!
