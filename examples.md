# Esempio di configurazione

## automation.yaml

```yaml
# Notifica se lo stendino è fuori e sta per piovere
automation:
  - alias: "Avviso stendino prima della pioggia"
    description: "Notifica se lo stendino è in giardino e il meteo prevede pioggia"
    trigger:
      - platform: state
        entity_id: weather.home
        to: "rainy"
    condition:
      - condition: state
        entity_id: binary_sensor.stendino_presente
        state: "on"
    action:
      - service: notify.mobile_app_iphone
        data:
          title: "⚠️ Attenzione Stendino!"
          message: "Lo stendino è ancora in giardino e sta per piovere!"
          data:
            push:
              sound: "default"
            tag: "stendino-alert"

  - alias: "Promemoria stendino al tramonto"
    description: "Ricorda di ritirare lo stendino prima che faccia buio"
    trigger:
      - platform: sun
        event: sunset
        offset: "-00:30:00"  # 30 minuti prima del tramonto
    condition:
      - condition: state
        entity_id: binary_sensor.stendino_presente
        state: "on"
    action:
      - service: notify.mobile_app_iphone
        data:
          title: "🌅 Promemoria Sera"
          message: "Ricordati di ritirare lo stendino dal giardino!"

  - alias: "Alert stendino lasciato di notte"
    description: "Avviso importante se lo stendino è ancora fuori dopo le 21:00"
    trigger:
      - platform: time
        at: "21:00:00"
    condition:
      - condition: state
        entity_id: binary_sensor.stendino_presente
        state: "on"
    action:
      - service: notify.mobile_app_iphone
        data:
          title: "🌙 Stendino dimenticato!"
          message: "Lo stendino è ancora in giardino!"
      - service: light.turn_on
        target:
          entity_id: light.lampada_ingresso
        data:
          flash: "short"

  - alias: "Notifica quando stendino viene ritirato"
    description: "Conferma quando lo stendino viene ritirato"
    trigger:
      - platform: state
        entity_id: binary_sensor.stendino_presente
        from: "on"
        to: "off"
    action:
      - service: notify.mobile_app_iphone
        data:
          title: "✅ Stendino OK"
          message: "Lo stendino è stato ritirato dal giardino."
```

## lovelace-ui.yaml

```yaml
# Card semplice
type: entities
entities:
  - entity: binary_sensor.stendino_presente
    secondary_info: last-changed
    name: Stendino in giardino
title: 🏡 Controllo Giardino

---

# Card con immagine telecamera
type: vertical-stack
cards:
  - type: picture-entity
    entity: camera.giardino
    name: Vista Giardino
    show_state: false
  
  - type: entities
    entities:
      - entity: binary_sensor.stendino_presente
        name: Stendino rilevato
        secondary_info: last-changed
      - type: attribute
        entity: binary_sensor.stendino_presente
        attribute: confidence
        name: Confidenza rilevamento
      - type: attribute
        entity: binary_sensor.stendino_presente
        attribute: ai_service
        name: Servizio AI

---

# Card condizionale (mostra solo se stendino presente)
type: conditional
conditions:
  - entity: binary_sensor.stendino_presente
    state: "on"
card:
  type: markdown
  content: |
    ## ⚠️ Attenzione!
    
    Lo stendino è ancora in giardino!
    
    **Confidenza:** {{ state_attr('binary_sensor.stendino_presente', 'confidence') }}
    
    **Ultimo controllo:** {{ relative_time(states.binary_sensor.stendino_presente.last_changed) }}
  title: Alert Stendino

---

# Card con pulsante per forzare aggiornamento
type: vertical-stack
cards:
  - type: glance
    entities:
      - entity: binary_sensor.stendino_presente
        name: Stendino
    title: Stato Stendino
  
  - type: button
    entity: automation.update_stendino_now
    name: Controlla ora
    icon: mdi:refresh
    tap_action:
      action: call-service
      service: homeassistant.update_entity
      service_data:
        entity_id: binary_sensor.stendino_presente

---

# Card completa con statistiche
type: vertical-stack
cards:
  - type: picture-entity
    entity: camera.giardino
    camera_image: camera.giardino
    show_name: false
    show_state: false

  - type: markdown
    content: |
      ## 📊 Dettagli Rilevamento
      
      **Oggetto cercato:** {{ state_attr('binary_sensor.stendino_presente', 'detection_object') }}
      
      **Oggetti trovati:** {{ state_attr('binary_sensor.stendino_presente', 'object_count') }}
      
      {% set objects = state_attr('binary_sensor.stendino_presente', 'detected_objects') %}
      {% if objects %}
      ### Oggetti rilevati:
      {% for obj in objects %}
      - **Confidenza:** {{ (obj.confidence * 100)|round }}%
        - Posizione: ({{ obj.x }}, {{ obj.y }})
        - Dimensioni: {{ obj.width }}x{{ obj.height }}
      {% endfor %}
      {% endif %}
      
      **Ultimo controllo:** {{ relative_time(states.binary_sensor.stendino_presente.last_changed) }}
    title: Analisi AI

  - type: entities
    title: 🏡 Controllo Stendino
    entities:
      - entity: binary_sensor.stendino_presente
        name: Stato attuale
        icon: mdi:hanger
      
      - type: section
      
      - type: attribute
        entity: binary_sensor.stendino_presente
        attribute: object_count
        name: Oggetti rilevati
        
      - type: attribute
        entity: binary_sensor.stendino_presente
        attribute: detection_object
        name: Oggetto cercato
        
      - type: attribute
        entity: binary_sensor.stendino_presente
        attribute: last_image_time
        name: Ultimo controllo
        
      - type: attribute
        entity: binary_sensor.stendino_presente
        attribute: camera_entity
        name: Telecamera
```

## script.yaml

```yaml
# Script per controllare manualmente lo stendino
check_stendino_now:
  alias: "Controlla Stendino Ora"
  sequence:
    - service: homeassistant.update_entity
      target:
        entity_id: binary_sensor.stendino_presente
    - delay:
        seconds: 5
    - service: notify.mobile_app_iphone
      data:
        title: "Controllo Stendino"
        message: >
          Stendino {{ 'presente' if is_state('binary_sensor.stendino_presente', 'on') else 'non presente' }} in giardino.
          Oggetti rilevati: {{ state_attr('binary_sensor.stendino_presente', 'object_count') }}

# Script avanzato con dettagli bbox
check_stendino_detailed:
  alias: "Controlla Stendino con Dettagli"
  sequence:
    - service: homeassistant.update_entity
      target:
        entity_id: binary_sensor.stendino_presente
    - delay:
        seconds: 5
    - service: notify.mobile_app_iphone
      data:
        title: "Controllo Stendino Dettagliato"
        message: >
          {% set objects = state_attr('binary_sensor.stendino_presente', 'detected_objects') %}
          {% if objects %}
            Trovati {{ objects|length }} oggetti:
            {% for obj in objects %}
            - Confidenza: {{ (obj.confidence * 100)|round }}%
              Posizione: ({{ obj.x }}, {{ obj.y }})
              Dimensioni: {{ obj.width }}x{{ obj.height }}
            {% endfor %}
          {% else %}
            Nessun oggetto rilevato.
          {% endif %}
```

## Integrazioni con Google Assistant / Alexa

```yaml
# configuration.yaml
intent_script:
  CheckStendinoIntent:
    speech:
      text: >
        {% if is_state('binary_sensor.stendino_presente', 'on') %}
          Lo stendino è attualmente in giardino.
        {% else %}
          Lo stendino non è in giardino.
        {% endif %}
```

## Node-RED Flow (se usi Node-RED)

```json
[
    {
        "id": "stendino_check",
        "type": "server-state-changed",
        "name": "Stendino State",
        "server": "home_assistant",
        "entityid": "binary_sensor.stendino_presente",
        "outputinitially": false,
        "state_type": "str",
        "output_only_on_state_change": true
    },
    {
        "id": "notify_if_present",
        "type": "switch",
        "name": "Check if Present",
        "property": "payload",
        "rules": [
            {
                "t": "eq",
                "v": "on"
            }
        ]
    }
]
```
