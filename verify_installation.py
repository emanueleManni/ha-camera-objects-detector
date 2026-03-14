#!/usr/bin/env python3
"""
Script di verifica installazione per Camera Object Detector.

Controlla che tutti i file necessari siano presenti e correttamente formattati.
"""

import json
import sys
from pathlib import Path


def check_file_exists(path: Path, description: str) -> bool:
    """Verifica che un file esista."""
    if path.exists():
        print(f"✅ {description}: {path.name}")
        return True
    else:
        print(f"❌ {description} MANCANTE: {path}")
        return False


def check_json_valid(path: Path, description: str) -> bool:
    """Verifica che un file JSON sia valido."""
    if not path.exists():
        print(f"❌ {description} NON TROVATO: {path}")
        return False
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            json.load(f)
        print(f"✅ {description} JSON valido: {path.name}")
        return True
    except json.JSONDecodeError as e:
        print(f"❌ {description} JSON INVALIDO: {e}")
        return False


def main():
    """Verifica l'installazione."""
    print("🔍 Verifica Installazione Camera Object Detector")
    print("=" * 60)
    
    # Determina la root del progetto
    script_dir = Path(__file__).parent
    integration_dir = script_dir / "custom_components" / "camera_object_detector"
    
    print(f"\n📁 Directory integrazione: {integration_dir}")
    
    if not integration_dir.exists():
        print(f"\n❌ ERRORE: Directory integrazione non trovata!")
        print(f"   Percorso cercato: {integration_dir}")
        sys.exit(1)
    
    print("\n📋 Verifica file essenziali...")
    
    all_ok = True
    
    # File Python essenziali
    python_files = [
        ("__init__.py", "Inizializzazione"),
        ("manifest.json", "Manifest"),
        ("const.py", "Costanti"),
        ("config_flow.py", "Config Flow"),
        ("binary_sensor.py", "Binary Sensor"),
        ("ai_client.py", "AI Client"),
    ]
    
    for filename, description in python_files:
        path = integration_dir / filename
        if not check_file_exists(path, description):
            all_ok = False
    
    print("\n📋 Verifica file JSON...")
    
    # Verifica manifest.json
    manifest_path = integration_dir / "manifest.json"
    if check_json_valid(manifest_path, "Manifest"):
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
            
        print(f"   Domain: {manifest.get('domain')}")
        print(f"   Name: {manifest.get('name')}")
        print(f"   Version: {manifest.get('version')}")
        print(f"   Config Flow: {manifest.get('config_flow')}")
        
        # Verifica campi essenziali
        required_fields = ['domain', 'name', 'version', 'config_flow', 'requirements']
        missing = [f for f in required_fields if f not in manifest]
        if missing:
            print(f"   ⚠️ Campi mancanti: {missing}")
            all_ok = False
    else:
        all_ok = False
    
    # Verifica strings.json
    strings_path = integration_dir / "strings.json"
    if not check_json_valid(strings_path, "Strings"):
        all_ok = False
    
    # Verifica traduzioni
    print("\n📋 Verifica traduzioni...")
    translations_dir = integration_dir / "translations"
    
    if translations_dir.exists():
        for lang_file in ["en.json", "it.json"]:
            lang_path = translations_dir / lang_file
            if check_json_valid(lang_path, f"Traduzione {lang_file}"):
                pass
            else:
                all_ok = False
    else:
        print(f"❌ Directory traduzioni non trovata: {translations_dir}")
        all_ok = False
    
    # Verifica documentazione
    print("\n📋 Verifica documentazione...")
    
    doc_files = [
        "README.md",
        "CHANGELOG.md",
        "LICENSE",
        "QUICKSTART.md",
    ]
    
    for doc_file in doc_files:
        path = script_dir / doc_file
        if not check_file_exists(path, f"Documentazione {doc_file}"):
            print(f"   ⚠️ File opzionale mancante")
    
    # Risultato finale
    print("\n" + "=" * 60)
    if all_ok:
        print("✅ INSTALLAZIONE COMPLETA E VALIDA!")
        print("\n📦 Prossimi passi:")
        print("   1. Copia custom_components/camera_object_detector in <config>/custom_components/")
        print("   2. Riavvia Home Assistant")
        print("   3. Vai su Impostazioni → Dispositivi e Servizi")
        print("   4. Aggiungi integrazione 'Camera Object Detector'")
        print("\n💡 Per testare Moondream AI prima:")
        print("   python test_moondream_standalone.py <image> <api_key>")
    else:
        print("❌ INSTALLAZIONE INCOMPLETA O INVALIDA")
        print("   Controlla gli errori sopra e risolvi i problemi")
        sys.exit(1)
    
    print("=" * 60)


if __name__ == "__main__":
    main()
