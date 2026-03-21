# 🎯 Modalità "Action Only" - Disabilita Binary Sensor

## Scenario

Vuoi configurare il component per salvare le credenziali API e usare l'action `detect_object` nelle automazioni, **ma NON vuoi che il binary sensor faccia query periodiche automatiche** (per risparmiare sui costi API).

## ✅ Soluzione

Home Assistant Camera Object Detector ora supporta la **modalità "Action Only"** che permette di:
- ✅ Configurare il component tramite UI (salva ai_service, api_key, ecc.)
- ✅ Usare l'action `detect_object` nelle automazioni
- ❌ NON creare il binary sensor
- ❌ NON fare query automatiche periodiche

## 📋 Come Configurare

### Passo 1: Configura il Component

1. Vai in **Impostazioni** → **Dispositivi e Servizi**
2. Clicca **"+ Aggiungi Integrazione"**
3. Cerca **"Camera Object Detector"**
4. Compila il form:
   - **Camera**: `camera.carraio`
   - **AI Service**: `Moondream AI (Cloud)`
   - **API Key**: la tua chiave Moondream
   - **Object to Detect**: `drying_rack`
   - **Scan Interval**: `300` (irrilevante se disabilitato)
   - **✅ Disable Binary Sensor**: **ATTIVA QUESTA OPZIONE**
5. Clicca **"Invia"**

### Passo 2: Verifica

**NON verrà creato alcun binary sensor!**

Verifica:
1. Vai in **Strumenti per sviluppatori** → **Stati**
2. Cerca `binary_sensor.carraio_` - NON dovrebbe esistere
3. Vai in **Strumenti per sviluppatori** → **Servizi**
4. Cerca `camera_object_detector.detect_object` - DEVE esistere ✅

### Passo 3: Usa l'Action nelle Automazioni

Ora puoi usare l'action senza che il binary sensor faccia query automatiche:

```yaml
automation:
  - alias: "Promemoria Stendino - Action Only"
    trigger:
      # Quando piove
      - platform: numeric_state
        entity_id: sensor.gw1100a_rain_rate
        above: 0.1
      
      # Oppure alle 20:00
      - platform: time
        at: "20:00:00"
    
    action:
      # Chiama l'action ON-DEMAND (nessuna query automatica!)
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
          message: "Lo stendino è ancora fuori!"
```

## 💰 Risparmio Costi

### Con Binary Sensor Attivo (Intervallo 5 min)
- Query/giorno: ~288
- Query/mese: ~8,640
- 💸 Costo elevato

### Con Action Only (3 trigger al giorno)
- Query/giorno: ~3-4
- Query/mese: ~120
- 💚 **Risparmio 98%!**

## 🔄 Cambiare Modalità

### Da Action Only → Binary Sensor Attivo

1. Vai in **Impostazioni** → **Dispositivi e Servizi**
2. Trova "Camera Object Detector"
3. Clicca **"Configura"**
4. **Disattiva** "Disable Binary Sensor"
5. Salva
6. Riavvia Home Assistant

Risultato: Viene creato il binary sensor con query periodiche.

### Da Binary Sensor Attivo → Action Only

1. Vai in **Impostazioni** → **Dispositivi e Servizi**
2. Trova "Camera Object Detector"
3. Clicca **"Configura"**
4. **Attiva** "Disable Binary Sensor"
5. Salva
6. Riavvia Home Assistant

Risultato: Il binary sensor viene rimosso, rimane solo l'action.

## ❓ FAQ

### L'action funziona anche senza binary sensor?

✅ **Sì!** L'action è completamente indipendente dal binary sensor. Anche con binary sensor disabilitato, l'action usa le credenziali salvate nella configurazione.

### Posso avere configurazioni miste?

✅ **Sì!** Puoi avere più configurazioni:
- Una con binary sensor attivo per `camera.sala`
- Una con action only per `camera.carraio`

Esempio:
1. Aggiungi integrazione → `camera.sala` → Disable Binary Sensor: NO
2. Aggiungi integrazione → `camera.carraio` → Disable Binary Sensor: SÌ

### Cosa succede se non configuro nulla?

❌ L'action NON funzionerà! Devi sempre configurare almeno un'istanza (anche con binary sensor disabilitato) per salvare le credenziali API.

### Intervallo massimo se non voglio disabilitare?

Se preferisci tenere il binary sensor ma con query rarissime:
- Imposta **Scan Interval**: `86400` (24 ore)
- Risultato: 1 query al giorno invece di 288

## 📊 Tabella Comparativa

| Modalità | Binary Sensor | Action | Query Auto | Best For |
|----------|---------------|---------|------------|----------|
| **Standard** | ✅ Sì | ✅ Sì | ✅ Ogni N sec | Monitoraggio continuo |
| **Action Only** | ❌ No | ✅ Sì | ❌ Mai | Trigger specifici, risparmio |
| **Intervallo Lungo** | ✅ Sì | ✅ Sì | ✅ 1 volta/24h | Backup + trigger specifici |

## 🎯 Best Practice

### Usa Action Only quando:
- ✅ Hai trigger specifici (pioggia, orari)
- ✅ Vuoi massimizzare il risparmio API
- ✅ Non ti serve lo storico continuo dello stato
- ✅ Non usi il sensore in altre automazioni

### Usa Binary Sensor quando:
- ✅ Vuoi monitoraggio continuo
- ✅ Usi il sensore in condizioni di altre automazioni
- ✅ Vuoi vedere lo storico degli stati nell'UI
- ✅ I costi API non sono un problema

### Usa Intervallo Lungo quando:
- ✅ Vuoi un "backup" del monitoraggio (1 volta al giorno)
- ✅ E anche trigger specifici con l'action
- ✅ Compromesso tra monitoraggio e costi

## 💡 Esempio Pratico

### Configurazione Ottimale per lo Stendino

**Setup:**
- Configura con "Disable Binary Sensor" = **SÌ**
- Usa action solo quando serve

**Automazione:**
```yaml
automation:
  # Trigger 1: Quando piove (sensore meteo reale)
  - alias: "Stendino - Pioggia"
    trigger:
      - platform: numeric_state
        entity_id: sensor.gw1100a_rain_rate
        above: 0.1
    action:
      - service: camera_object_detector.detect_object
        data:
          camera_entity: camera.carraio
          detection_object: "drying_rack"
        response_variable: det
      - condition: template
        value_template: "{{ det.object_present }}"
      - service: notify.notify
        data:
          message: "Sta piovendo e lo stendino è fuori!"
  
  # Trigger 2: Promemoria serale
  - alias: "Stendino - Sera"
    trigger:
      - platform: time
        at: "20:00:00"
    action:
      - service: camera_object_detector.detect_object
        data:
          camera_entity: camera.carraio
          detection_object: "drying_rack"
        response_variable: det
      - condition: template
        value_template: "{{ det.object_present }}"
      - service: notify.notify
        data:
          message: "Lo stendino è ancora fuori!"
```

**Risultato:**
- 2-3 query al giorno invece di 288
- Risparmio: ~96%
- Funzionalità identica

---

**🎉 Ora puoi configurare il component e usare solo l'action quando serve, senza query superflue!**
