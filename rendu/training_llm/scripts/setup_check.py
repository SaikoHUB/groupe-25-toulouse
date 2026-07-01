#!/usr/bin/env python3
"""
Setup verification script
Checks environment, dependencies, and hardware
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.device import print_device_info, detect_device, supports_quantization


def check_python_version():
    """Check Python version"""
    print("🐍 Python")
    version = sys.version_info
    print(f"   Version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 9:
        print(f"   ✅ OK (>= 3.9)")
        return True
    else:
        print(f"   ❌ Python 3.9+ requis")
        return False


def check_packages():
    """Check required packages"""
    print("\n📦 Packages")
    
    packages = [
        ("torch", "PyTorch"),
        ("transformers", "Transformers"),
        ("peft", "PEFT"),
        ("datasets", "Datasets"),
        ("trl", "TRL"),
        ("accelerate", "Accelerate"),
    ]
    
    all_ok = True
    for module_name, display_name in packages:
        try:
            module = __import__(module_name)
            version = getattr(module, '__version__', 'unknown')
            print(f"   ✅ {display_name}: {version}")
        except ImportError:
            print(f"   ❌ {display_name}: non installé")
            all_ok = False
    
    # Check bitsandbytes (optional)
    try:
        import bitsandbytes
        print(f"   ✅ bitsandbytes: {bitsandbytes.__version__} (optionnel)")
    except ImportError:
        print(f"   ⚠️  bitsandbytes: non installé (optionnel, requis pour QLoRA)")
    
    return all_ok


def check_disk_space():
    """Check disk space"""
    print("\n💾 Espace disque")
    
    try:
        import shutil
        total, used, free = shutil.disk_usage(".")
        free_gb = free // (2**30)
        
        print(f"   Disponible: {free_gb} GB")
        
        if free_gb < 20:
            print(f"   ⚠️  Moins de 20GB disponible")
            return True
        else:
            print(f"   ✅ Suffisant")
            return True
    except:
        return True


def check_cuda_features():
    """Check CUDA-specific features"""
    device = detect_device()
    
    if device == "cuda":
        has_bnb = supports_quantization(device)
        print(f"\n🎯 Features CUDA")
        print(f"   QLoRA 4-bit: {'✅ Disponible' if has_bnb else '❌ bitsandbytes manquant'}")
        print(f"   bfloat16: ✅ Disponible")
        print(f"   Optimiseur: paged_adamw_32bit")
    
    elif device == "mps":
        print(f"\n🍎 Features Mac Silicon")
        print(f"   QLoRA 4-bit: ❌ Non supporté")
        print(f"   bfloat16: ❌ Non supporté")
        print(f"   Optimiseur: adamw_torch")
        print(f"   Precision: fp16")
        print(f"   ℹ️  Entraînement plus lent qu'avec CUDA")
    
    else:
        print(f"\n⚠️  CPU seulement")
        print(f"   Entraînement TRÈS lent")


def main():
    print("\n" + "="*60)
    print("🔍 VÉRIFICATION DE L'ENVIRONNEMENT")
    print("="*60)
    
    results = {}
    
    # Check Python
    results['python'] = check_python_version()
    
    # Check packages
    results['packages'] = check_packages()
    
    # Check device
    print()
    print_device_info()
    device = detect_device()
    results['device'] = device in ["cuda", "mps"]  # OK if GPU available
    
    # Check disk
    results['disk'] = check_disk_space()
    
    # Check features
    check_cuda_features()
    
    # Summary
    print("\n" + "="*60)
    print("📊 RÉSUMÉ")
    print("="*60 + "\n")
    
    print("Composant              Status")
    print("-" * 40)
    for key, value in results.items():
        status = "✅ OK" if value else "❌ PROBLÈME"
        print(f"{key.capitalize():20} {status}")
    
    critical_ok = all([results['python'], results['packages']])
    
    print("\n" + "="*60)
    if critical_ok:
        print("✅ ENVIRONNEMENT PRÊT!")
        print("="*60)
        print("\n🚀 Prochaines étapes:")
        print("   python scripts/train.py")
        print("\n💡 Test rapide (recommandé):")
        print("   python scripts/train.py --max-samples 5000 --epochs 1")
        
        if device == "mps":
            print("\n🍎 Utilisateur Mac Silicon:")
            print("   Voir docs/MAC_SILICON.md pour optimisations")
        
        return 0
    else:
        print("⚠️  PROBLÈMES DÉTECTÉS")
        print("="*60)
        
        if not results['python']:
            print("\n   - Installer Python 3.9+")
        
        if not results['packages']:
            print("\n   - Installer les dépendances:")
            print("     pip install -r requirements.txt")
        
        return 1


if __name__ == "__main__":
    sys.exit(main())
