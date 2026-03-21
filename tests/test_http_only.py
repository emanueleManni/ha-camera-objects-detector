"""Test Moondream AI client using HTTP API only (bypass SDK)."""

import asyncio
import sys
import os

# Add parent directory to path to import the AI client
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'custom_components', 'camera_object_detector'))

# Mock the SDK as unavailable to force HTTP mode
import ai_client
ai_client.MOONDREAM_SDK_AVAILABLE = False

from ai_client import MoondreamAIClient

async def test_http_only(image_path, api_key, object_name):
    """Test HTTP-only mode."""
    print("=" * 70)
    print("🧪 TEST HTTP-ONLY MODE")
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
    
    # Create client (force HTTP mode)
    client = MoondreamAIClient(api_key, timeout=30)
    print(f"🤖 Client creato - Modalità: {'SDK' if client.use_sdk else 'HTTP'}")
    print()
    
    # Analyze
    print("📤 Invio richiesta a Moondream HTTP API...")
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
            print(f"   {i}. Confidence: {obj['confidence']:.2%}")
            print(f"      Posizione: x={obj['x']}, y={obj['y']}")
            print(f"      Dimensione: {obj['width']}x{obj['height']} px")
            print(f"      Normalized: ({obj['x_min']:.3f}, {obj['y_min']:.3f}) → ({obj['x_max']:.3f}, {obj['y_max']:.3f})")
    else:
        print("❌ Nessun oggetto rilevato")
    print()

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python test_http_only.py <image_path> <api_key> <object_name>")
        sys.exit(1)
    
    # Windows event loop fix
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(test_http_only(sys.argv[1], sys.argv[2], sys.argv[3]))
