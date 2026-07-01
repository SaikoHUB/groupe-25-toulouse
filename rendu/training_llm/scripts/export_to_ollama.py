#!/usr/bin/env python3
"""
Export trained Phi-3 model to Ollama format
Merges LoRA weights with base model for Ollama compatibility
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
from peft import AutoPeftModelForCausalLM
from transformers import AutoTokenizer
import argparse
import shutil


def merge_and_save(model_path: str, output_path: str):
    """
    Merge LoRA weights with base model and save
    
    Args:
        model_path: Path to trained LoRA model
        output_path: Path to save merged model
    """
    print(f"\n{'='*60}")
    print("🔄 FUSION DU MODÈLE LORA AVEC LE MODÈLE DE BASE")
    print(f"{'='*60}\n")
    
    print(f"📥 Chargement du modèle depuis: {model_path}")
    
    try:
        # Load model with LoRA weights
        model = AutoPeftModelForCausalLM.from_pretrained(
            model_path,
            device_map="cpu",  # Use CPU for merging
            torch_dtype=torch.float16,
        )
        
        print("✅ Modèle chargé")
        
        # Merge LoRA weights with base model
        print("\n🔀 Fusion des poids LoRA avec le modèle de base...")
        model = model.merge_and_unload()
        print("✅ Fusion terminée")
        
        # Load tokenizer
        print("\n📥 Chargement du tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        print("✅ Tokenizer chargé")
        
        # Save merged model
        print(f"\n💾 Sauvegarde du modèle fusionné dans: {output_path}")
        os.makedirs(output_path, exist_ok=True)
        
        model.save_pretrained(output_path)
        tokenizer.save_pretrained(output_path)
        
        print("✅ Modèle fusionné sauvegardé")
        
        # Get model size
        model_size = 0
        for root, dirs, files in os.walk(output_path):
            model_size += sum(os.path.getsize(os.path.join(root, name)) for name in files)
        
        model_size_gb = model_size / (1024**3)
        print(f"\n📊 Taille du modèle: {model_size_gb:.2f} GB")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        return False


def create_modelfile(output_path: str, model_name: str):
    """
    Create Ollama Modelfile
    
    Args:
        output_path: Path where merged model is saved
        model_name: Name for the Ollama model
    """
    print(f"\n📝 Création du Modelfile pour Ollama...")
    
    modelfile_content = f"""# Modelfile for {model_name}
FROM {output_path}

# Temperature (higher = more creative)
PARAMETER temperature 0.7

# Top-p sampling
PARAMETER top_p 0.9

# Top-k sampling
PARAMETER top_k 50

# Stop tokens
PARAMETER stop "<|end|>"
PARAMETER stop "<|user|>"
PARAMETER stop "<|assistant|>"

# System prompt
SYSTEM \"\"\"
You are a medical AI assistant trained on patient-doctor conversations.
Provide helpful, accurate medical information while always recommending 
consulting with healthcare professionals for actual medical advice.

⚠️ IMPORTANT: This is for educational purposes only. Always consult 
a qualified healthcare professional for medical advice, diagnosis, or treatment.
\"\"\"

# Template for chat format
TEMPLATE \"\"\"
<|user|>
{{ .Prompt }}<|end|>
<|assistant|>
\"\"\"
"""
    
    modelfile_path = os.path.join(output_path, "Modelfile")
    with open(modelfile_path, "w") as f:
        f.write(modelfile_content)
    
    print(f"✅ Modelfile créé: {modelfile_path}")
    return modelfile_path


def create_import_script(output_path: str, model_name: str):
    """
    Create shell script to import model into Ollama
    
    Args:
        output_path: Path where merged model is saved
        model_name: Name for the Ollama model
    """
    script_content = f"""#!/bin/bash
# Script to import {model_name} into Ollama

echo "🚀 Importation du modèle dans Ollama..."
echo ""

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama n'est pas installé"
    echo ""
    echo "📥 Installez Ollama depuis:"
    echo "   https://ollama.ai/download"
    exit 1
fi

echo "✅ Ollama détecté"
echo ""

# Create model from Modelfile
echo "📦 Création du modèle {model_name}..."
ollama create {model_name} -f {output_path}/Modelfile

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Modèle {model_name} créé avec succès!"
    echo ""
    echo "🧪 Pour tester:"
    echo "   ollama run {model_name}"
    echo ""
    echo "💬 Pour une conversation:"
    echo "   ollama run {model_name} 'What are the symptoms of diabetes?'"
    echo ""
    echo "🔧 Pour lister vos modèles:"
    echo "   ollama list"
else
    echo ""
    echo "❌ Erreur lors de la création du modèle"
    exit 1
fi
"""
    
    script_path = os.path.join(output_path, "import_to_ollama.sh")
    with open(script_path, "w") as f:
        f.write(script_content)
    
    # Make script executable
    os.chmod(script_path, 0o755)
    
    print(f"✅ Script d'import créé: {script_path}")
    return script_path


def main():
    parser = argparse.ArgumentParser(
        description="Export Phi-3 Medical Chatbot to Ollama",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Export avec nom par défaut
  python scripts/export_to_ollama.py --model ./medical-phi3-model

  # Export avec nom personnalisé
  python scripts/export_to_ollama.py --model ./medical-phi3-model --name medical-phi3

  # Spécifier dossier de sortie
  python scripts/export_to_ollama.py --model ./medical-phi3-model --output ./ollama-export

Après l'export:
  cd ollama-export
  ./import_to_ollama.sh
  ollama run medical-phi3
        """
    )
    
    parser.add_argument("--model", type=str, default="./medical-phi3-model",
                        help="Path to trained LoRA model")
    parser.add_argument("--output", type=str, default="./ollama-export",
                        help="Output directory for merged model")
    parser.add_argument("--name", type=str, default="medical-phi3",
                        help="Name for Ollama model")
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("🦙 EXPORT VERS OLLAMA")
    print("="*60)
    
    # Check if model exists
    if not os.path.exists(args.model):
        print(f"\n❌ Modèle non trouvé: {args.model}")
        print("\n💡 Assurez-vous d'avoir entraîné le modèle d'abord:")
        print("   python scripts/train.py")
        sys.exit(1)
    
    # Merge and save
    success = merge_and_save(args.model, args.output)
    
    if not success:
        sys.exit(1)
    
    # Create Modelfile
    modelfile_path = create_modelfile(args.output, args.name)
    
    # Create import script
    script_path = create_import_script(args.output, args.name)
    
    # Summary
    print(f"\n{'='*60}")
    print("✅ EXPORT TERMINÉ!")
    print(f"{'='*60}\n")
    
    print(f"📁 Dossier de sortie: {args.output}")
    print(f"📝 Modelfile: {modelfile_path}")
    print(f"🔧 Script d'import: {script_path}")
    
    print(f"\n🚀 Prochaines étapes:")
    print(f"\n1. Installer Ollama (si pas déjà fait):")
    print(f"   https://ollama.ai/download")
    
    print(f"\n2. Importer le modèle dans Ollama:")
    print(f"   cd {args.output}")
    print(f"   ./import_to_ollama.sh")
    
    print(f"\n3. Utiliser le modèle:")
    print(f"   ollama run {args.name}")
    
    print(f"\n💬 Exemples de questions:")
    print(f"   - What are the symptoms of diabetes?")
    print(f"   - I have a persistent cough. What should I do?")
    print(f"   - How to prevent high blood pressure?")
    
    print(f"\n⚠️  RAPPEL:")
    print(f"   Ce chatbot est à usage éducatif uniquement.")
    print(f"   Consultez toujours un professionnel de santé.")
    print()


if __name__ == "__main__":
    main()
