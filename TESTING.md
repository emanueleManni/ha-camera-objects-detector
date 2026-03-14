# Test dell'integrazione Camera Object Detector

Questa directory contiene test di esempio per l'integrazione.

## Come eseguire i test localmente

### Setup ambiente di sviluppo

```bash
# Crea virtual environment
python -m venv venv

# Attiva virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Installa dipendenze base (per test standalone)
pip install -r requirements.txt

# Oppure, per sviluppo completo:
pip install -r requirements-dev.txt

# Note: alcuni pacchetti in requirements-dev.txt richiedono Python 3.13+
# (homeassistant, pytest-homeassistant-custom-component)
# Se hai Python 3.12 o inferiore, installa solo moondream e pillow
```

## Test manuale

### Test del client Moondream AI SDK

Usa lo script standalone fornito:

```bash
# Test con immagine e oggetto default (drying_rack)
python tests/try_moondream_standalone.py foto_giardino.jpg YOUR_API_KEY

# Test con oggetto specifico
python tests/try_moondream_standalone.py foto.jpg YOUR_API_KEY person
python tests/try_moondream_standalone.py foto.jpg YOUR_API_KEY car
python tests/try_moondream_standalone.py foto.jpg YOUR_API_KEY bicycle
```

**Esempio Output:**

```text
🏡 Test Moondream AI - Object Detection
============================================================

📷 Caricamento immagine: foto.jpg
   Dimensioni: 1920x1080
   Formato: JPEG
   Modalità: RGB
   Dimensione: 456.3 KB

🤖 Inizializzazione Moondream AI...
   Oggetto da rilevare: 'drying_rack'

📤 Invio richiesta a Moondream AI...

============================================================
📊 RISULTATO ANALISI
============================================================

🔍 Request ID: req_abc123
📦 Oggetti rilevati: 2

✅ OGGETTI TROVATI:

   Oggetto #1:
      Confidenza: 95%
      → Alta confidenza ✅
      Posizione: x=450, y=320
      Dimensioni: 150x200
      Posizione %: 23.4%, 29.6%

   Oggetto #2:
      Confidenza: 87%
      → Alta confidenza ✅
      Posizione: x=650, y=310
      Dimensioni: 140x195
      Posizione %: 33.9%, 28.7%

============================================================
```

### Test con Home Assistant Development

1. Copia l'integrazione nella tua installazione HA di sviluppo:

   ```text
   <config>/custom_components/camera_object_detector/
   ```

2. Riavvia Home Assistant

3. Abilita debug logging in `configuration.yaml`:

   ```yaml
   logger:
     default: info
     logs:
       custom_components.camera_object_detector: debug
   ```

4. Configura l'integrazione tramite UI

5. Monitora i log:

   ```bash
   tail -f home-assistant.log | grep camera_object
   ```

## Test delle automazioni

### Test scenario: pioggia in arrivo

1. Imposta manualmente il sensore meteo su "rainy"
2. Verifica che l'automazione si attivi se lo stendino è presente
3. Controlla le notifiche

### Test scenario: tramonto

1. Usa Developer Tools > Services per simulare il tramonto:

   ```yaml
   service: sun.set_elevation
   data:
     elevation: -6
   ```

2. Verifica l'automazione

## Checklist test completa

- [ ] ✅ Configurazione tramite UI
- [ ] ✅ Selezione telecamera funziona
- [ ] ✅ API key validata correttamente
- [ ] ✅ Selezione oggetto da rilevare funziona
- [ ] ✅ Oggetto custom accettato
- [ ] ✅ Sensore binario creato
- [ ] ✅ Stati on/off corretti (basati su object_count)
- [ ] ✅ Attributi object_count, detected_objects, detection_object disponibili
- [ ] ✅ Bounding box coordinate corrette
- [ ] ✅ Confidenza per oggetto individuale
- [ ] ✅ Icone cambiano correttamente
- [ ] ✅ Intervallo di scansione rispettato
- [ ] ✅ Options flow funziona
- [ ] ✅ Cambio oggetto da options flow aggiorna rilevamento
- [ ] ✅ Rimozione integrazione pulisce tutto
- [ ] ✅ Automazioni si attivano correttamente
- [ ] ✅ Notifiche funzionano
- [ ] ✅ Traduzioni IT/EN corrette

## Problemi comuni

### Cliente Moondream non risponde

- Verifica API key
- Controlla connessione Internet
- Verifica quota API

### Sensore sempre "unavailable"

- Controlla che la telecamera sia accessibile
- Verifica i log per errori
- Aumenta timeout in ai_client.py

### Rilevamenti imprecisi

- Verifica qualità immagine telecamera
- Controlla illuminazione
- Prova con nome oggetto più specifico
- Verifica attributo `detected_objects` per confidenza individuale
- Assicurati che l'oggetto sia ben visibile e non parzialmente nascosto

## Contribuire con i test

Se vuoi contribuire con test automatizzati, segui questa struttura:

```text
tests/
├── __init__.py
├── conftest.py              # Fixtures pytest
├── test_config_flow.py      # Test configurazione
├── test_binary_sensor.py    # Test sensore
├── test_ai_client.py        # Test client AI
└── fixtures/
    └── test_images/         # Immagini di test
```
