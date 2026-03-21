#!/usr/bin/env python3
"""
Test identico al codice del playground Moondream.
Esegue esattamente il codice suggerito da Moondream per vedere cosa restituisce.
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


def test_playground_code(image_path: str, api_key: str, detection_object: str = "drying_rack"):
    """Esegue il codice identico al playground."""
    
    print("="*70)
    print("🧪 TEST PLAYGROUND CODE - Codice Identico a Moondream Playground")
    print("="*70)
    
    # Initialize with API key
    print(f"\n🔑 Inizializzazione con API key...")
    model = md.vl(api_key=api_key)
    
    # Load an image
    print(f"📷 Caricamento immagine: {image_path}")
    image = Image.open(image_path)
    print(f"   Dimensioni: {image.size}")
    print(f"   Formato: {image.format}")
    print(f"   Modalità: {image.mode}")
    
    # Detect objects
    print(f"\n🔍 Rilevamento oggetto: '{detection_object}'")
    print(f"📤 Chiamata: model.detect(image, \"{detection_object}\")")
    
    result = model.detect(image, detection_object)
    
    # Print raw result
    print(f"\n📊 RISULTATO RAW (come dal playground):")
    print("="*70)
    import json
    print(json.dumps(result, indent=2))
    print("="*70)
    
    # Extract data
    objects = result["objects"]
    request_id = result["request_id"]
    
    print(f"\n🆔 Request ID: {request_id}")
    print(f"📦 Detected objects: {objects}")
    
    # Analyze objects
    print(f"\n📊 ANALISI DETTAGLIATA:")
    print(f"   Numero oggetti nella lista: {len(objects)}")
    
    if objects:
        for i, obj in enumerate(objects, 1):
            print(f"\n   Oggetto #{i}:")
            for key, value in obj.items():
                print(f"      {key}: {value}")
    else:
        print("   ❌ Lista oggetti vuota")
    
    return result


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python test_playground_direct.py <image_path> <api_key> [object_name]")
        print("\nExample:")
        print("  python test_playground_direct.py ../sample-images/Presente/260127_084909_carraio.jpg your-api-key drying_rack")
        sys.exit(1)
    
    image_path = sys.argv[1]
    api_key = sys.argv[2]
    detection_object = sys.argv[3] if len(sys.argv) > 3 else "drying_rack"
    
    test_playground_code(image_path, api_key, detection_object)
