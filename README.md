# Camera Object Detector (HA custom integration)

Integrazione custom per Home Assistant per rilevare automaticamente oggetti (stendino, persone, automobili, biciclette, animali, ecc.) analizzando le immagini delle telecamere di videosorveglianza analizzandone l'immagine con il modello `moondream.ai`.

## Caratteristiche

- **Rilevamento configurabile** di qualsiasi oggetto tramite AI
- **Object detection** con bounding box e confidenza
- **Supporto per telecamere Home Assistant** (1920x1080 e altre risoluzioni)
- **Integrazione con Moondream AI SDK** per analisi cloud delle immagini
- **Aggiornamento periodico** configurabile (da 30 secondi a 1 ora)
- **Attributi dettagliati**: conteggio oggetti, coordinate bounding box, confidenza, timestamp
- **Icone personalizzate**: gruccia quando presente, gruccia barrata quando assente
- **Multilingua**: italiano e inglese
- **Configurazione tramite UI** (niente YAML!)

## Installazione

### Metodo 1: Manuale

1. Copia la cartella `custom_components/camera_object_detector` nella directory `custom_components` di Home Assistant
2. Riavvia Home Assistant
3. Vai su **Impostazioni** → **Dispositivi e Servizi** → **Aggiungi integrazione**
4. Cerca "**Camera Object Detector**"

### Metodo 2: HACS (quando disponibile)

1. Apri HACS
2. Vai su "Integrations"
3. Clicca sui tre puntini in alto a destra
4. Scegli "Custom repositories"
5. Aggiungi l'URL del repository
6. Installa "Camera Object Detector"
7. Riavvia Home Assistant

## Configurazione

### 1. Ottieni una API Key di Moondream AI

1. Vai su [moondream.ai](https://moondream.ai/)
2. Crea un account
3. Ottieni la tua API key dalla dashboard

### 2. Configura l'integrazione

1. Vai su **Impostazioni** → **Dispositivi e Servizi**
2. Clicca su **Aggiungi integrazione**
3. Cerca "**Camera Object Detector**"
4. Compila il form:
   - **Telecamera**: seleziona la telecamera che inquadra il giardino
   - **Servizio AI**: seleziona "Moondream AI (Cloud)"
   - **API Key**: inserisci la tua API key di Moondream
   - **Oggetto da Rilevare**: scegli dal menu a tendina (drying_rack, person, car, dog, ecc.) o inserisci un nome custom
   - **Intervallo di scansione**: imposta ogni quanto analizzare (default: 300 secondi = 5 minuti)

5. Clicca su **Invia**

### 3. Utilizza il sensore

Dopo la configurazione, avrai un nuovo sensore binario:

```text
binary_sensor.stendino_presente
```

**Stati possibili:**

- `on` = Oggetto rilevato in giardino
- `off` = Oggetto non rilevato

**Attributi disponibili:**

- `object_count`: numero di oggetti rilevati
- `detected_objects`: lista oggetti con coordinate bounding box (x, y, width, height) e confidenza
- `detection_object`: tipo di oggetto cercato
- `request_id`: ID richiesta Moondream
- `last_image_time`: timestamp dell'ultima analisi
- `ai_service`: servizio AI utilizzato
- `camera_entity`: telecamera utilizzata

## Esempi di utilizzo

### Notifica se lo stendino è fuori e sta per piovere

```yaml
automation:
  - alias: "Avviso stendino prima della pioggia"
    trigger:
      - platform: state
        entity_id: weather.home
        to: "rainy"
    condition:
      - condition: state
        entity_id: binary_sensor.stendino_presente
        state: "on"
    action:
      - service: notify.mobile_app
        data:
          title: "⚠️ Attenzione!"
          message: "Lo stendino è ancora in giardino e sta per piovere!"
```

### Notifica se lo stendino è fuori di sera

```yaml
automation:
  - alias: "Promemoria stendino al tramonto"
    trigger:
      - platform: sun
        event: sunset
        offset: "-00:30:00"  # 30 minuti prima del tramonto
    condition:
      - condition: state
        entity_id: binary_sensor.stendino_presente
        state: "on"
    action:
      - service: notify.mobile_app
        data:
          title: "🌅 Promemoria"
          message: "Ricordati di ritirare lo stendino dal giardino!"
```

### Card in Lovelace

```yaml
type: entities
entities:
  - entity: binary_sensor.stendino_presente
    secondary_info: last-changed
    name: Stendino in giardino
title: 🏡 Controllo Giardino
```

### Card condizionale con immagine telecamera

```yaml
type: conditional
conditions:
  - entity: binary_sensor.stendino_presente
    state: "on"
card:
  type: picture-entity
  entity: camera.giardino
  name: "⚠️ Stendino rilevato!"
  show_state: true
```

## Configurazione avanzata

### Modifica delle impostazioni

Puoi modificare le impostazioni in qualsiasi momento:

1. Vai su **Impostazioni** → **Dispositivi e Servizi**
2. Trova "Camera Object Detector"
3. Clicca su **Configura**
4. Modifica l'intervallo di scansione, API key, o servizio AI

### Oggetti supportati

L'integrazione supporta il rilevamento di qualsiasi oggetto. Alcuni oggetti comuni:

- `drying_rack` - stendibiancheria
- `person` - persona
- `car` - automobile
- `bicycle` - bicicletta
- `dog`, `cat` - animali
- `chair`, `table` - mobili
- `umbrella`, `bag`, `bottle` - oggetti vari

Puoi specificare qualsiasi nome di oggetto in inglese durante la configurazione.

### Aggiungere supporto per altri servizi AI

Il codice è strutturato per supportare facilmente altri servizi AI. Crea una nuova classe che eredita da `AIServiceClient` in `ai_client.py`.

## Risoluzione problemi

### Il sensore non si aggiorna

1. Verifica che la telecamera sia accessibile
2. Controlla i log di Home Assistant per errori
3. Verifica che l'API key di Moondream sia valida
4. Aumenta l'intervallo di scansione se l'API è sovraccarica

### Rilevamenti imprecisi

1. Assicurati che la telecamera abbia una buona visuale dell'oggetto
2. Controlla che l'illuminazione sia adeguata
3. Prova ad aumentare la risoluzione della telecamera
4. Verifica l'attributo `detected_objects` per vedere la confidenza di ciascun oggetto rilevato
5. Prova con nomi di oggetti più specifici (es. "folding drying rack" invece di "drying rack")

### Errori API

Se ricevi errori dall'API Moondream:

- Verifica di avere crediti API sufficienti
- Controlla che la connessione Internet funzioni
- Verifica i log per il messaggio di errore specifico

## Costi

**Moondream AI:**

- Piano gratuito: limitato
- Piano a pagamento: verifica su [moondream.ai](https://moondream.ai/pricing)
- Stima: con scansione ogni 5 minuti = ~8.640 richieste/mese

## Sviluppo

### Struttura del progetto

```text
custom_components/camera_object_detector/
├── __init__.py              # Inizializzazione integrazione
├── binary_sensor.py         # Sensore binario
├── config_flow.py           # Configurazione UI
├── const.py                 # Costanti
├── ai_client.py            # Client per servizi AI
├── manifest.json           # Metadata integrazione
├── strings.json            # Traduzioni base
└── translations/
    ├── en.json             # Traduzioni inglese
    └── it.json             # Traduzioni italiano
```

### Contribuire

Contributi sono benvenuti! Per favore:

1. Fai un fork del repository
2. Crea un branch per la tua feature
3. Committa le modifiche
4. Apri una Pull Request

## License

MIT License - vedi LICENSE file per dettagli

## Credits

- Sviluppato per Home Assistant
- Utilizza [Moondream AI](https://moondream.ai/) per l'analisi delle immagini
- Icone da Material Design Icons

## Supporto

Per bug, feature request o domande, apri una issue su GitHub.
