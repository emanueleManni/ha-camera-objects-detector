#!/usr/bin/env python3
"""
Script standalone per testare Moondream AI prima di installare l'integrazione.

Requisiti:
    pip install moondream pillow

Usage:
    python test_moondream_standalone.py <path_to_image> <api_key> [object_name]

Example:
    python test_moondream_standalone.py foto_giardino.jpg your-api-key-here drying_rack
    python test_moondream_standalone.py foto.jpg your-api-key-here person

Note:
    L'API key si ottiene da https://moondream.ai/
"""

import sys
from pathlib import Path

try:
    import moondream as md
    from PIL import Image
except ImportError as e:
    print(f"❌ Errore: {e}")
    print("\nInstalla i pacchetti richiesti con:")
    print("  pip install moondream pillow")
    sys.exit(1)


def analyze_image(image_path: Path, api_key: str, detection_object: str = "drying_rack"):
    """Analizza un'immagine con Moondream AI usando object detection."""
    
    # Leggi l'immagine
    if not image_path.exists():
        print(f"❌ Errore: file non trovato: {image_path}")
        return None
    
    print(f"📷 Caricamento immagine: {image_path}")
    
    # Carica immagine
    try:
        image = Image.open(image_path)
    except Exception as e:
        print(f"❌ Errore nel caricamento immagine: {e}")
        return None
    
    # Info immagine
    print(f"   Dimensioni: {image.size[0]}x{image.size[1]}")
    print(f"   Formato: {image.format}")
    print(f"   Modalità: {image.mode}")
    
    file_size_kb = image_path.stat().st_size / 1024
    print(f"   Dimensione: {file_size_kb:.1f} KB")
    
    # Inizializza modello Moondream
    print(f"\n🤖 Inizializzazione Moondream AI...")
    print(f"   Oggetto da rilevare: '{detection_object}'")
    
    try:
        model = md.vl(api_key=api_key)
    except Exception as e:
        print(f"\n❌ Errore nell'inizializzazione del modello: {e}")
        return None
    
    # Esegui detection
    print(f"\n📤 Invio richiesta a Moondream AI...")
    
    try:
        result = model.detect(image, detection_object)
        return result, image
    except Exception as e:
        print(f"\n❌ Errore durante la detection: {e}")
        return None


def print_result(result_data):
    """Stampa il risultato in modo leggibile."""
    if not result_data:
        print("❌ Nessun risultato")
        return
    
    result, image = result_data
    
    print("\n" + "="*60)
    print("📊 RISULTATO ANALISI")
    print("="*60)
    
    # Estrai dati
    objects = result.get("objects", [])
    request_id = result.get("request_id", "N/A")
    
    print(f"\n🔍 Request ID: {request_id}")
    print(f"📦 Oggetti rilevati: {len(objects)}")
    
    if objects:
        print("\n✅ OGGETTI TROVATI:")
        for i, obj in enumerate(objects, 1):
            confidence = obj.get("confidence", 0)
            x = obj.get("x", 0)
            y = obj.get("y", 0)
            width = obj.get("width", 0)
            height = obj.get("height", 0)
            
            print(f"\n   Oggetto #{i}:")
            print(f"      Confidenza: {confidence:.0%}")
            
            # Valutazione confidenza
            if confidence >= 0.8:
                print( "      → Alta confidenza ✅")
            elif confidence >= 0.6:
                print("      → Media confidenza ⚠️")
            else:
                print("      → Bassa confidenza ❌")
            
            print(f"      Posizione: x={x}, y={y}")
            print(f"      Dimensioni: {width}x{height}")
            
            # Calcola posizione percentuale nell'immagine
            if hasattr(image, 'size'):
                img_width, img_height = image.size
                x_pct = (x / img_width) * 100 if img_width > 0 else 0
                y_pct = (y / img_height) * 100 if img_height > 0 else 0
                print(f"      Posizione %: {x_pct:.1f}%, {y_pct:.1f}%")
    else:
        print("\n❌ NESSUN OGGETTO RILEVATO")
        print("   L'oggetto cercato non è presente nell'immagine")
    
    print("\n" + "="*60)


def main():
    """Funzione principale."""
    print("🏡 Test Moondream AI - Object Detection")
    print("="*60 + "\n")
    
    # Verifica argomenti
    if len(sys.argv) < 3:
        print("Usage: python test_moondream_standalone.py <image_path> <api_key> [object_name]")
        print("\nExample:")
        print("  python test_moondream_standalone.py foto.jpg your-api-key-here drying_rack")
        print("  python test_moondream_standalone.py foto.jpg your-api-key-here person")
        print("  python test_moondream_standalone.py foto.jpg your-api-key-here car")
        print("\nOggetti comuni supportati:")
        print("  - drying_rack (stendibiancheria)")
        print("  - person (persona)")
        print("  - car (auto)")
        print("  - bicycle (bicicletta)")
        print("  - dog, cat (animali)")
        print("  - chair, table (mobili)")
        print("  - umbrella, bag, bottle (oggetti)")
        print("\nNote:")
        print("  - Puoi specificare qualsiasi oggetto in inglese")
        print("  - L'API key si ottiene da https://moondream.ai/")
        sys.exit(1)
    
    image_path = Path(sys.argv[1])
    api_key = sys.argv[2]
    detection_object = sys.argv[3] if len(sys.argv) > 3 else "drying_rack"
    
    # Analizza
    result_data = analyze_image(image_path, api_key, detection_object)
    
    # Stampa risultato
    print_result(result_data)
    
    # Suggerimenti
    print("\n💡 SUGGERIMENTI:")
    print("   1. Se non rileva oggetti, verifica che siano ben visibili")
    print("   2. Prova con nomi di oggetti diversi se non sei sicuro")
    print("   3. Assicurati che ci sia buona illuminazione")
    print("   4. Gli oggetti piccoli o parzialmente nascosti potrebbero non essere rilevati\n")


if __name__ == "__main__":
    main()
