"""Test Moondream HTTP API with correct authentication header."""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'custom_components', 'camera_object_detector'))

from ai_client import MoondreamAIClient

async def test_http_api(image_path, api_key, object_name):
    """Test HTTP API with X-Moondream-Auth header."""
    print("=" * 70)
    print("🧪 TEST MOONDREAM HTTP API")
    print("=" * 70)
    print()
    
    # Load image
    with open(image_path, 'rb') as f:
        image_data = f.read()
    
    print(f"📷 Immagine: {image_path}")
    print(f"   Dimensione: {len(image_data) / 1024:.1f} KB")
    print()
    print(f"🔍 Oggetto da rilevare: '{object_name}'")
    print()
    
    # Create client
    client = MoondreamAIClient(api_key, timeout=30)
    print(f"🤖 Client HTTP creato")
    print()
    
    # Analyze
    print("📤 Invio richiesta a Moondream API...")
    try:
        result = await client.analyze_image(image_data, object_name)
        
        print()
        print("=" * 70)
        print("📊 RISULTATO")
        print("=" * 70)
        print(f"✅ Oggetto presente: {result['object_present']}")
        print(f"🔢 Numero oggetti: {result['object_count']}")
        print(f"💯 Confidence: {result['confidence']:.2%}")
        print()
        
        if result['detected_objects']:
            print(f"📦 Oggetti rilevati ({len(result['detected_objects'])}):")
            for i, obj in enumerate(result['detected_objects'], 1):
                print(f"   {i}. Normalized bbox: ({obj['x_min']:.3f}, {obj['y_min']:.3f}) → ({obj['x_max']:.3f}, {obj['y_max']:.3f})")
                print(f"      Center: ({obj['x']:.3f}, {obj['y']:.3f})")
                print(f"      Size: {obj['width']:.3f} × {obj['height']:.3f}")
        else:
            print("❌ Nessun oggetto rilevato")
        print()
        
    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python test_http_api.py <image_path> <api_key> <object_name>")
        print()
        print("Example:")
        print("  python test_http_api.py ../sample-images/Presente/260127_084909_carraio.jpg YOUR_API_KEY drying_rack")
        sys.exit(1)
    
    # Windows event loop fix
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(test_http_api(sys.argv[1], sys.argv[2], sys.argv[3]))
