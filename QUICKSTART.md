# 🚀 Guida Rapida - Camera Object Detector

## 📋 Prerequisiti

- ✅ Home Assistant 2024.1.0 o superiore
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

### Step 3: Configura l'integrazione

1. Vai su **Impostazioni** → **Dispositivi e Servizi**
2. Clicca **+ Aggiungi integrazione** (in basso a destra)
3. Cerca "**Camera Object Detector**"
4. Compila il form:
   - **Telecamera**: `camera.giardino` (seleziona la tua)
   - **Servizio AI**: `Moondream AI (Cloud)`
   - **API Key**: incolla la key di Moondream
   - **Oggetto da Rilevare**: seleziona dal menu (es. `Drying Rack`) o inserisci un nome custom
   - **Intervallo**: `300` secondi (5 minuti)
5. Clicca **Invia**
6. ✅ Fatto!

💡 **Oggetti supportati**: drying_rack, person, car, bicycle, dog, cat, chair, table, umbrella, bag, bottle, e molti altri!

### Step 4: Verifica che funzioni

1. Vai su **Strumenti per sviluppatori** → **Stati**
2. Cerca `binary_object_count`, `detected_objects`, `detection_object`, etc.

💡 **Tip**: Controlla `detected_objects` per vedere le coordinate bounding box e la confidenza di ogni oggetto rilevato!
3. Dovresti vedere:
   - Stato: `on` oppure `off`
   - Attributi: `confidence`, `explanation`, etc.

### Step 5: Prima automazione

Copia questo in `automations.yaml` o crea tramite UI:

```yaml
automation:
  - alias: "Test Stendino"
    trigger:
      platform: state
      entity_id: binary_sensor.stendino_presente
      to: "on"
    action:
      service: notify.persistent_notification
      data:
        message: "🎉 Stendino rilevato in giardino!"
        title: "Stendino Detector"
```

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
      condition: state
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

1. ✅ Leggi il [README completo](README.md) per esempi avanzati
2. ✅ Controlla [examples.md](examples.md) per più automazioni
3. ✅ Unisciti alla community per condividere idee!

## 💬 Supporto

- 🐛 **Bug?** Apri una [issue](https://github.com/emanueleManni/camera-object-detector/issues)
- 💡 **Idee?** Proponi una feature!
- ❤️ **Ti piace?** Lascia una stella su GitHub!
