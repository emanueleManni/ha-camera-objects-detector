# Camera Object Detector - Guida Action e Automazioni

## ⚠️ IMPORTANTE: Prima di Iniziare

Per usare l'action `detect_object`, hai **due opzioni**:

### Opzione A: Configura tramite UI (Consigliato)

1. Vai in **Impostazioni** → **Dispositivi e Servizi** → **+ Aggiungi Integrazione**
2. Cerca **"Camera Object Detector"**
3. Configura con i tuoi parametri (telecamera, AI service, API key)

**Vantaggio**: L'action funzionerà automaticamente senza dover specificare `ai_service` e `api_key` ogni volta.

### Opzione B: Specifica Parametri nell'Action

Specifica `ai_service` e `api_key` direttamente nella chiamata:

```yaml
service: camera_object_detector.detect_object
data:
  camera_entity: camera.carraio
  detection_object: "drying_rack"
  ai_service: "moondream"
  api_key: !secret moondream_api_key  # Usa secrets per sicurezza
```

**Per informazioni dettagliate su come risolvere errori, vedi [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md)**

---

## 📋 Modifiche Implementate

### 1. Nome Binary Sensor con Nome Telecamera

Il nome del `binary_sensor` ora include automaticamente il nome della telecamera per permettere configurazioni multiple.

**Prima:**
- `binary_sensor.laundry_drying_rack_detection`

**Dopo:**
- `binary_sensor.carraio_laundry_drying_rack_detection` (per `camera.carraio`)
- `binary_sensor.sala_laundry_drying_rack_detection` (per `camera.sala`)

### 2. Action `detect_object` per Detection On-Demand

È stata aggiunta una nuova action che permette di rilevare oggetti su richiesta, senza dover configurare un binary sensor.

## 🚀 Come Usare l'Action

### Sintassi Base

```yaml
service: camera_object_detector.detect_object
data:
  camera_entity: camera.carraio
  detection_object: "drying_rack"
response_variable: result
```

### Parametri

| Parametro | Obbligatorio | Descrizione |
|-----------|--------------|-------------|
| `camera_entity` | ✅ Sì | ID dell'entità telecamera (es: `camera.carraio`) |
| `detection_object` | ✅ Sì | Nome dell'oggetto da rilevare (es: `drying_rack`, `person`, `car`) |
| `ai_service` | ❌ No | Servizio AI da usare (se non specificato usa la configurazione esistente) |
| `api_key` | ❌ No | Chiave API (se non specificata usa quella della configurazione) |

### Risposta

L'action restituisce un oggetto con i seguenti campi:

```yaml
{
  "object_present": true,           # true se l'oggetto è stato rilevato
  "object_count": 2,                 # numero di oggetti rilevati
  "confidence": 1.0,                 # confidenza del rilevamento (0.0-1.0)
  "image_time": "2024-03-21T...",   # timestamp dell'analisi
  "detection_object": "drying_rack", # oggetto cercato
  "detected_objects": [              # lista oggetti rilevati con coordinate
    {
      "confidence": 1.0,
      "x": 0.5,                       # coordinate normalizzate (0-1)
      "y": 0.3,
      "width": 0.2,
      "height": 0.4
    }
  ]
}
```

## 📝 Esempi di Utilizzo

### Esempio 1: Detection Semplice

```yaml
automation:
  - alias: "Verifica Stendino"
    trigger:
      - platform: time
        at: "20:00:00"
    action:
      - service: camera_object_detector.detect_object
        data:
          camera_entity: camera.carraio
          detection_object: "drying_rack"
        response_variable: result
      
      - condition: template
        value_template: "{{ result.object_present }}"
      
      - service: notify.notify
        data:
          message: "Stendino rilevato: {{ result.object_count }} oggetti"
```

### Esempio 2: Con Previsioni Meteo (Met.no)

```yaml
automation:
  - alias: "Stendino - Pioggia Prevista"
    trigger:
      - platform: state
        entity_id: weather.home
        to: 
          - "rainy"
          - "pouring"
    action:
      - service: camera_object_detector.detect_object
        data:
          camera_entity: camera.carraio
          detection_object: "drying_rack"
        response_variable: detection
      
      - condition: template
        value_template: "{{ detection.object_present }}"
      
      - service: notify.notify
        data:
          title: "⚠️ Ritira lo stendino!"
          message: "Sta per piovere e lo stendino è ancora fuori"
```

### Esempio 3: Con Sensore Pioggia GW1100A

```yaml
automation:
  - alias: "Stendino - Pioggia in Corso"
    trigger:
      - platform: numeric_state
        entity_id: sensor.gw1100a_rain_rate
        above: 0.1  # mm/h
    action:
      - service: camera_object_detector.detect_object
        data:
          camera_entity: camera.carraio
          detection_object: "drying_rack"
        response_variable: detection
      
      - condition: template
        value_template: "{{ detection.object_present }}"
      
      - service: notify.notify
        data:
          title: "⚠️ Sta piovendo!"
          message: >
            Lo stendino è ancora fuori e sta piovendo 
            ({{ states('sensor.gw1100a_rain_rate') }} mm/h)
```

### Esempio 4: Più Telecamere

```yaml
automation:
  - alias: "Verifica Stendino - Tutte le Telecamere"
    trigger:
      - platform: time
        at: "21:00:00"
    action:
      # Controlla camera carraio
      - service: camera_object_detector.detect_object
        data:
          camera_entity: camera.carraio
          detection_object: "drying_rack"
        response_variable: carraio
      
      # Controlla camera sala
      - service: camera_object_detector.detect_object
        data:
          camera_entity: camera.sala
          detection_object: "drying_rack"
        response_variable: sala
      
      # Notifica se trovato in almeno una
      - condition: template
        value_template: >
          {{ carraio.object_present or sala.object_present }}
      
      - service: notify.notify
        data:
          message: >
            Stendino trovato:
            {% if carraio.object_present %}Carraio ({{ carraio.object_count }}){% endif %}
            {% if sala.object_present %}Sala ({{ sala.object_count }}){% endif %}
```

## ⚙️ Vantaggi dell'Action

1. **Nessuna Configurazione Richiesta**: Non serve configurare un binary_sensor per usare l'action
2. **On-Demand**: Interroga il servizio AI solo quando necessario, riducendo i costi
3. **Flessibilità**: Puoi cambiare telecamera e oggetto dinamicamente
4. **Trigger Multipli**: Usa condizioni complesse (pioggia, orario, ecc.)
5. **Risparmio**: Evita query periodiche inutili quando non servono

## 🔧 Binary Sensor vs Action

### Quando Usare il Binary Sensor

- Vuoi monitoraggio continuo con intervallo fisso
- Vuoi vedere lo stato nell'interfaccia HA
- Vuoi usarlo in condizioni di altre automazioni
- Non ti preoccupano i costi delle query periodiche

### Quando Usare l'Action

- Vuoi controllare solo in momenti specifici (es: quando piove)
- Vuoi risparmiare sui costi dell'API
- Vuoi flessibilità su telecamera/oggetto dinamici
- Non ti serve lo storico dello stato

## 🌧️ Sensori Meteo Consigliati

### Opzione 1: Met.no (Previsioni)

```yaml
# Usa l'integrazione nativa di Home Assistant
weather.home  # Stati: rainy, pouring, lightning-rainy, etc.
```

**Pro**: Previsioni future, nativo in HA  
**Contro**: Può essere impreciso, è una previsione

### Opzione 2: GW1100A (Dato Reale)

```yaml
sensor.gw1100a_rain_rate      # mm/h - intensità pioggia attuale
sensor.gw1100a_event_rain_rate # mm - pioggia evento
```

**Pro**: Dato reale e preciso, locale  
**Contro**: Non prevede, solo dati attuali

### Combinazione Consigliata

Usa entrambi per una logica più robusta:

```yaml
condition:
  or:
    # Sta piovendo (dato certo)
    - condition: numeric_state
      entity_id: sensor.gw1100a_rain_rate
      above: 0.1
    
    # O pioggia prevista nelle prossime ore
    - condition: state
      entity_id: weather.home
      state: ["rainy", "pouring"]
```

## 📚 File di Riferimento

- **Esempi Completi**: Vedi `automation_example.yaml`
- **Documentazione**: Vedi `README.md` principale
- **Test**: Vedi `tests/test_http_api.py`

## 🐛 Troubleshooting

### L'action non restituisce risultati

1. Verifica che la telecamera sia accessibile: `camera.carraio`
2. Controlla che sia configurata almeno un'istanza del component
3. Guarda i log: `Configurazione > Log`

### Errore "No AI service specified"

Configura almeno un'istanza del component tramite UI per impostare il servizio AI predefinito.

### La notifica non parte

Verifica che la condition `{{ result.object_present }}` sia vera. Aggiungi un log per debug:

```yaml
- service: logbook.log
  data:
    name: "Debug Detection"
    message: "Presente: {{ result.object_present }}, Count: {{ result.object_count }}"
```
