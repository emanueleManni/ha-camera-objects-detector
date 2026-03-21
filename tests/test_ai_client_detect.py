#!/usr/bin/env python3
"""
Test per verificare che il metodo detect() sia usato correttamente.

Questo script testa il nuovo client AI che usa il metodo detect() del SDK Moondream
quando disponibile, o l'HTTP API come fallback.

Usage:
    python test_ai_client_detect.py <path_to_image> <api_key> [object_name]

Example:
    python test_ai_client_detect.py foto.jpg your-api-key-here drying_rack
"""

import asyncio
import sys
from pathlib import Path

# Fix per Windows: usa SelectorEventLoop invece di ProactorEventLoop
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Carica il modulo ai_client.py direttamente senza import del package
# per evitare dipendenze da homeassistant
ai_client_file = Path(__file__).parent.parent / "custom_components" / "camera_object_detector" / "ai_client.py"

# Leggi e esegui il file con le costanti definite localmente
with open(ai_client_file, 'r', encoding='utf-8') as f:
    code = f.read()
    
# Sostituisci l'intera sezione try/except delle costanti con definizioni locali
import re
# Trova e sostituisci il blocco try/except per le costanti
code = re.sub(
    r'# Import constants with fallback.*?AI_SERVICE_MOONDREAM = "moondream"',
    "# Costanti locali per test standalone\nAI_SERVICE_LOCAL = 'local'\nAI_SERVICE_MOONDREAM = 'moondream'",
    code,
    flags=re.DOTALL
)

# Crea un namespace ed esegui il codice
namespace = {}
exec(code, namespace)

# Estrai le classi necessarie
MoondreamAIClient = namespace['MoondreamAIClient']
MOONDREAM_SDK_AVAILABLE = namespace['MOONDREAM_SDK_AVAILABLE']


async def test_analyze_image(image_path: Path, api_key: str, detection_object: str = "drying_rack"):
    """Test dell'analisi immagine con il nuovo client."""
    
    print("="*70)
    print("🧪 TEST AI CLIENT - Metodo detect()")
    print("="*70)
    
    # Verifica disponibilità SDK
    print(f"\n📦 SDK Moondream disponibile: {'✅ SI' if MOONDREAM_SDK_AVAILABLE else '❌ NO (verrà usato HTTP API)'}")
    
    # Verifica immagine
    if not image_path.exists():
        print(f"❌ Errore: file non trovato: {image_path}")
        return None
    
    print(f"\n📷 Immagine: {image_path}")
    file_size_kb = image_path.stat().st_size / 1024
    print(f"   Dimensione: {file_size_kb:.1f} KB")
    
    # Carica immagine
    with open(image_path, "rb") as f:
        image_data = f.read()
    
    print(f"\n🔍 Oggetto da rilevare: '{detection_object}'")
    
    # Inizializza client
    print(f"\n🤖 Inizializzazione MoondreamAIClient...")
    try:
        client = MoondreamAIClient(api_key=api_key, timeout=30)
        print(f"   Modalità: {'SDK (detect method)' if client.use_sdk else 'HTTP API'}")
        
        if not MOONDREAM_SDK_AVAILABLE and sys.platform == 'win32':
            print(f"\n⚠️  NOTA: Su Windows, l'HTTP API potrebbe avere problemi con aiodns.")
            print(f"   Per test migliori, installa il SDK: pip install moondream pillow")
    except Exception as e:
        print(f"❌ Errore nell'inizializzazione: {e}")
        return None
    
    # Esegui analisi
    print(f"\n📤 Invio richiesta a Moondream AI...")
    try:
        result = await client.analyze_image(image_data, detection_object)
        return result
    except Exception as e:
        print(f"❌ Errore durante l'analisi: {e}")
        import traceback
        traceback.print_exc()
        return None


def print_result(result: dict | None):
    """Stampa il risultato in modo dettagliato."""
    if not result:
        print("\n❌ Nessun risultato disponibile")
        return
    
    print("\n" + "="*70)
    print("📊 RISULTATO ANALISI")
    print("="*70)
    
    # Dati principali
    object_present = result.get("object_present", False)
    object_count = result.get("object_count", 0)
    confidence = result.get("confidence", 0.0)
    request_id = result.get("request_id", "N/A")
    detected_objects = result.get("detected_objects", [])
    
    print(f"\n🆔 Request ID: {request_id}")
    print(f"✅ Oggetto presente: {'SI' if object_present else 'NO'}")
    print(f"📦 Numero oggetti: {object_count}")
    print(f"🎯 Confidenza massima: {confidence:.1%}")
    
    # Info sulla soglia
    print(f"\n⚙️  Soglia minima confidenza: 50% (oggetti con confidenza < 50% sono ignorati)")
    
    if detected_objects:
        print(f"\n🔍 DETTAGLI OGGETTI RILEVATI:")
        for i, obj in enumerate(detected_objects, 1):
            conf = obj.get("confidence", 0)
            x = obj.get("x", 0)
            y = obj.get("y", 0)
            width = obj.get("width", 0)
            height = obj.get("height", 0)
            
            print(f"\n   Oggetto #{i}:")
            print(f"      Confidenza: {conf:.1%}", end="")
            
            # Valutazione confidenza
            if conf >= 0.8:
                print(" → Alta ✅")
            elif conf >= 0.6:
                print(" → Media ⚠️")
            else:
                print(" → Bassa ❌")
            
            print(f"      Posizione: ({x}, {y})")
            print(f"      Dimensioni: {width} x {height}")
    else:
        print(f"\n❌ NESSUN OGGETTO RILEVATO")
    
    # Test logica di interpretazione
    print("\n" + "="*70)
    print("🧪 VERIFICA LOGICA DI INTERPRETAZIONE")
    print("="*70)
    
    print(f"\n✓ object_present == (object_count > 0): ", end="")
    logic_ok = object_present == (object_count > 0)
    print("✅ CORRETTO" if logic_ok else "❌ ERRORE")
    
    print(f"✓ confidence == max(confidenze oggetti): ", end="")
    if detected_objects:
        max_conf = max(obj.get("confidence", 0) for obj in detected_objects)
        conf_ok = abs(confidence - max_conf) < 0.001  # Tolleranza per float
        print("✅ CORRETTO" if conf_ok else f"❌ ERRORE (atteso {max_conf}, ottenuto {confidence})")
    else:
        conf_ok = confidence == 0.0
        print("✅ CORRETTO (0.0 per nessun oggetto)" if conf_ok else f"❌ ERRORE (dovrebbe essere 0.0)")
    
    print(f"✓ detected_objects è una lista: ", end="")
    list_ok = isinstance(detected_objects, list)
    print("✅ CORRETTO" if list_ok else "❌ ERRORE")
    
    print(f"\n{'✅ TUTTI I TEST PASSATI!' if (logic_ok and conf_ok and list_ok) else '❌ CI SONO ERRORI NELLA LOGICA'}")
    print("="*70)


def main():
    """Funzione principale."""
    if len(sys.argv) < 3:
        print("Usage: python test_ai_client_detect.py <image_path> <api_key> [object_name]")
        print("\nExample:")
        print("  python test_ai_client_detect.py foto.jpg your-api-key drying_rack")
        print("  python test_ai_client_detect.py foto.jpg your-api-key person")
        sys.exit(1)
    
    image_path = Path(sys.argv[1])
    api_key = sys.argv[2]
    detection_object = sys.argv[3] if len(sys.argv) > 3 else "drying_rack"
    
    # Esegui test
    result = asyncio.run(test_analyze_image(image_path, api_key, detection_object))
    
    # Stampa risultato
    print_result(result)
    
    print("\n💡 Note:")
    print("   - Se SDK disponibile, viene usato il metodo detect() nativo")
    print("   - Altrimenti viene usato l'HTTP API REST")
    print("   - Entrambi restituiscono lo stesso formato di risultato\n")


if __name__ == "__main__":
    main()
