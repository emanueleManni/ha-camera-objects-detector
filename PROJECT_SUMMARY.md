# Camera Object Detector - Riepilogo Progetto

## 📁 Struttura Progetto

```
Trova stendino/
├── custom_components/
│   └── camera_object_detector/          # ← Integrazione Home Assistant
│       ├── __init__.py             # Inizializzazione
│       ├── manifest.json           # Metadata integrazione
│       ├── const.py                # Costanti
│       ├── config_flow.py          # Configurazione UI
│       ├── binary_sensor.py        # Sensore di rilevamento
│       ├── ai_client.py            # Client API Moondream
│       ├── strings.json            # Traduzioni base
│       └── translations/           # Traduzioni localizzate
│           ├── en.json
│           └── it.json
│
├── README.md                       # Documentazione completa
├── QUICKSTART.md                   # Guida rapida installazione
├── examples.md                     # Esempi automazioni
├── TESTING.md                      # Guida test
├── CHANGELOG.md                    # Storia versioni
├── LICENSE                         # Licenza MIT
│
├── tests/                          # Script di test
│   └── test_moondream_standalone.py  # Script test API
├── verify_installation.py          # Script verifica
├── requirements-dev.txt            # Dipendenze sviluppo
├── hacs.json                       # Configurazione HACS
├── info.md                         # Info HACS
└── .gitignore                      # File da ignorare
```

## Funzionalità Implementate

### Integrazione Base

- [x] Custom integration per Home Assistant
- [x] Configurazione tramite UI (no YAML)
- [x] Manifest con dipendenze
- [x] Costanti centralizzate

### Rilevamento AI

- [x] Integrazione Moondream AI SDK
- [x] Object detection con bounding box
- [x] Configurazione oggetto da rilevare (dropdown + custom)
- [x] Esecuzione sincrona nel thread executor
- [x] Gestione errori robusta
- [x] Placeholder per AI locale (futuro)

### Sensore

- [x] Binary sensor (on/off basato su object_count)
- [x] Attributi: object_count, detected_objects, detection_object, request_id, timestamp
- [x] Bounding box coordinate per ogni oggetto rilevato
- [x] Confidenza per oggetto individuale
- [x] Icone personalizzate (hanger on/off)
- [x] Device class: occupancy
- [x] Update coordinator per polling

### Configurazione

- [x] Config flow completo
- [x] Validazione input (camera, API key)
- [x] Selettore oggetto con dropdown (drying_rack, person, car, etc.)
- [x] Supporto per nome oggetto personalizzato
- [x] Options flow per modifiche
- [x] Unique ID per evitare duplicati
- [x] Scan interval configurabile (30s - 1h)

### Localizzazione

- [x] Traduzioni italiano
- [x] Traduzioni inglese
- [x] Strings.json base

### Documentazione

- [x] README completo con esempi
- [x] Quick start guide
- [x] Esempi automazioni dettagliati
- [x] Guida testing
- [x] Changelog strutturato
- [x] Licenza MIT

### Strumenti

- [x] Script test standalone Moondream
- [x] Script verifica installazione
- [x] Requirements per sviluppo
- [x] Configurazione HACS

## 🚀 Come Usare

### Installazione Rapida

1. **Copia l'integrazione**

   ```bash
   cp -r custom_components/camera_object_detector <home-assistant-config>/custom_components/
   ```

2. **Riavvia Home Assistant**

3. **Configura**
   - Impostazioni → Dispositivi e Servizi
   - Aggiungi integrazione "Camera Object Detector"
   - Seleziona telecamera
   - Inserisci API key Moondream
   - Imposta intervallo scansione

### Test API (Prima di Installare)

```bash
# Installa dipendenze minime
pip install moondream pillow

# Test con tua immagine (sostituisci YOUR_API_KEY con la tua chiave)
python tests/test_moondream_standalone.py foto_giardino.jpg YOUR_API_KEY drying_rack

# Test con oggetto diverso
python tests/test_moondream_standalone.py foto.jpg YOUR_API_KEY person
```

### Verifica Installazione

```bash
python verify_installation.py
```

## Approccio Object Detection

L'integrazione utilizza il metodo **`model.detect(image, object_name)`** dell'SDK Moondream per rilevare oggetti specifici nelle immagini.

### Come Funziona

1. **Caricamento immagine**: Viene scaricata dalla telecamera configurata
2. **Inizializzazione modello**: `model = md.vl(api_key=api_key)`
3. **Detection**: `result = model.detect(image, detection_object)`
4. **Parsing risultato**: Estrae lista oggetti con bounding box e confidenza

### Formato Risposta

```json
{
  "objects": [
    {
      "confidence": 0.95,
      "x": 450,
      "y": 320,
      "width": 150,
      "height": 200
    }
  ],
  "request_id": "req_123abc"
}
```

### Oggetti Supportati

L'integrazione include un menu a tendina con oggetti comuni:

- `drying_rack` - stendibiancheria
- `person` - persona
- `car` - automobile
- `bicycle` - bicicletta
- `dog`, `cat` - animali domestici
- `chair`, `table` - mobili
- `umbrella`, `bag`, `bottle` - oggetti vari

È possibile inserire qualsiasi nome di oggetto in inglese come valore personalizzato.

### Vantaggi rispetto VQA

✅ **Più accurato**: Detection diretta invece di analisi testuale  
✅ **Più veloce**: Meno elaborazione richiesta  
✅ **Coordinate**: Fornisce posizione esatta con bounding box  
✅ **Estendibile**: Funziona con qualsiasi oggetto  

## 💡 Esempi Automazioni

### 1. Alert Pioggia + Stendino Fuori

```yaml
automation:
  - alias: "Stendino e pioggia"
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
        message: "⚠️ Lo stendino è fuori e sta per piovere!"
```

### 2. Promemoria Serale

```yaml
automation:
  - alias: "Ritira stendino"
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
        message: "🌅 Ricorda di ritirare lo stendino!"
```

## 📊 Stato Sensore

**Entity ID**: `binary_sensor.stendino_presente`

**Stati**:

- `on` = Stendino rilevato
- `off` = Stendino non presente
- `unavailable` = Errore comunicazione

**Attributi**:

```yaml
object_count: 2               # Numero oggetti rilevati
detected_objects:             # Lista oggetti con dettagli
  - confidence: 0.95
    x: 450
    y: 320
    width: 150
    height: 200
  - confidence: 0.87
    x: 650
    y: 310
    width: 140
    height: 195
detection_object: "drying_rack"  # Oggetto cercato
request_id: "req_123abc"      # ID richiesta Moondream
last_image_time: "2026-..."   # Timestamp UTC
ai_service: "moondream"       # Servizio utilizzato
camera_entity: "camera...."   # Camera usata
```

## Personalizzazione

### Cambiare Oggetto da Rilevare

1. Vai su **Impostazioni** → **Dispositivi e Servizi**
2. Trova "Camera Object Detector"
3. Clicca **Configura**
4. Seleziona nuovo oggetto dal menu o inserisci custom

### Aggiungere Oggetti al Menu

Modifica [const.py](custom_components/camera_object_detector/const.py):

```python
MOONDREAM_SUPPORTED_OBJECTS = [
    "drying_rack",
    "person",
    "car",
    "il_tuo_oggetto",  # ← aggiungi qui
]
```

### Aggiungere Altro Servizio AI

1. Crea nuova classe in [ai_client.py](custom_components/camera_object_detector/ai_client.py)
2. Eredita da `AIServiceClient`
3. Implementa `analyze_image()`
4. Aggiungi costante in [const.py](custom_components/camera_object_detector/const.py)
5. Aggiorna factory in `get_ai_client()`

### Cambiare Icone

Modifica [binary_sensor.py](custom_components/camera_object_detector/binary_sensor.py#L165):

```python
def icon(self) -> str:
    if self.is_on:
        return "mdi:tua-icona-on"
    return "mdi:tua-icona-off"
```

## Prossimi Sviluppi Possibili

- [ ] Supporto AI locale (YOLO, TensorFlow)
- [ ] Multi-camera support
- [ ] Zone detection (escludi parti immagine)
- [ ] Statistiche storiche
- [ ] Salvataggio snapshot rilevamenti
- [ ] Training personalizzato
- [ ] Soglia confidence configurabile
- [ ] Integrazione meteo migliorata
- [ ] Template notifiche predefiniti

## 🐛 Troubleshooting

### Sensore sempre "unavailable"

1. Verifica telecamera funzionante
2. Controlla API key Moondream
3. Verifica connessione Internet
4. Leggi log Home Assistant

### Confidence bassa

1. Migliora illuminazione
2. Posiziona meglio telecamera
3. Prova nome oggetto più specifico
4. Verifica risoluzione immagine
5. Controlla attributo `detected_objects` per confidenza individuale

### Alta latenza

1. Aumenta scan interval
2. Verifica connessione Internet
3. Controlla quota API Moondream

## 📝 Credits

- **Sviluppato per**: Home Assistant
- **AI Service**: Moondream AI
- **Licenza**: MIT
- **Versione**: 1.0.0
