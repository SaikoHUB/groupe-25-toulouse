#!/usr/bin/env python3
"""
Inference script for Medical Chatbot
Interactive chat or single prompt mode
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
from peft import AutoPeftModelForCausalLM
from transformers import AutoTokenizer, GenerationConfig
import argparse


def load_model(model_path: str):
    """Load trained model"""
    print(f"📥 Chargement du modèle depuis {model_path}...")
    
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        
        model = AutoPeftModelForCausalLM.from_pretrained(
            model_path,
            device_map="auto",
            torch_dtype=torch.float16,
        )
        
        print(f"✅ Modèle chargé avec succès!")
        return model, tokenizer
        
    except Exception as e:
        print(f"❌ Erreur lors du chargement: {e}")
        sys.exit(1)


def generate_response(
    model,
    tokenizer,
    prompt: str,
    max_new_tokens: int = 256,
    temperature: float = 0.7,
    top_p: float = 0.9,
    top_k: int = 50,
):
    """Generate response from model"""
    
    # Format prompt for Phi-3
    if not prompt.startswith("<|"):
        formatted_prompt = f"<|user|>\n{prompt}<|end|>\n<|assistant|>\n"
    else:
        formatted_prompt = prompt
    
    inputs = tokenizer(formatted_prompt, return_tensors="pt")
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    
    generation_config = GenerationConfig(
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        top_p=top_p,
        top_k=top_k,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id,
        eos_token_id=tokenizer.eos_token_id,
    )
    
    with torch.no_grad():
        outputs = model.generate(**inputs, generation_config=generation_config)
    
    full_response = tokenizer.decode(outputs[0], skip_special_tokens=False)
    
    # Extract assistant response
    if "<|assistant|>" in full_response:
        response = full_response.split("<|assistant|>")[-1]
        response = response.replace("<|end|>", "").strip()
    else:
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        response = response[len(prompt):].strip()
    
    return response


def interactive_mode(model, tokenizer, args):
    """Interactive chat mode"""
    print("\n" + "="*60)
    print("💬 MODE INTERACTIF - MEDICAL CHATBOT")
    print("="*60)
    print("Tapez votre question médicale et appuyez sur Entrée")
    print("\nCommandes:")
    print("  'quit' ou 'exit' - Quitter")
    print("  'clear' - Effacer l'historique")
    print("  'config' - Voir la configuration")
    print("="*60 + "\n")
    
    print("⚠️  DISCLAIMER:")
    print("    Ce chatbot est à usage éducatif uniquement.")
    print("    Consultez toujours un professionnel de santé.")
    print()
    
    while True:
        try:
            user_input = input("👤 Vous: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit']:
                print("\n👋 Au revoir!")
                break
            
            if user_input.lower() == 'clear':
                print("\n🗑️  Historique effacé\n")
                continue
            
            if user_input.lower() == 'config':
                print(f"\n⚙️  Configuration:")
                print(f"   max_tokens: {args.max_tokens}")
                print(f"   temperature: {args.temperature}")
                print(f"   top_p: {args.top_p}\n")
                continue
            
            # Generate response
            print("\n⏳ Génération en cours...")
            response = generate_response(
                model,
                tokenizer,
                user_input,
                max_new_tokens=args.max_tokens,
                temperature=args.temperature,
                top_p=args.top_p,
                top_k=args.top_k,
            )
            
            print(f"\n🤖 Assistant: {response}\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Au revoir!")
            break
        except Exception as e:
            print(f"\n❌ Erreur: {e}\n")


def single_prompt_mode(model, tokenizer, prompt, args):
    """Single prompt mode"""
    print("\n💬 Question:")
    print(f"   {prompt}\n")
    
    print("⏳ Génération en cours...")
    response = generate_response(
        model,
        tokenizer,
        prompt,
        max_new_tokens=args.max_tokens,
        temperature=args.temperature,
        top_p=args.top_p,
        top_k=args.top_k,
    )
    
    print(f"\n🤖 Réponse:")
    print(f"   {response}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Test Medical Chatbot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Mode interactif
  python scripts/inference.py --model ./medical-phi3-model

  # Prompt unique
  python scripts/inference.py --model ./medical-phi3-model --prompt "What are the symptoms of diabetes?"

  # Avec paramètres personnalisés
  python scripts/inference.py --model ./medical-phi3-model --temperature 0.9 --max-tokens 512
        """
    )
    
    parser.add_argument("--model", type=str, default="./medical-phi3-model",
                        help="Path to trained model")
    parser.add_argument("--prompt", type=str, default=None,
                        help="Single prompt (otherwise interactive mode)")
    parser.add_argument("--max-tokens", type=int, default=256,
                        help="Maximum tokens to generate")
    parser.add_argument("--temperature", type=float, default=0.7,
                        help="Temperature (0.0-2.0)")
    parser.add_argument("--top-p", type=float, default=0.9,
                        help="Top-p sampling")
    parser.add_argument("--top-k", type=int, default=50,
                        help="Top-k sampling")
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("🏥 PHI-3 MEDICAL CHATBOT INFERENCE")
    print("="*60)
    
    # Load model
    model, tokenizer = load_model(args.model)
    
    # Run inference
    if args.prompt:
        single_prompt_mode(model, tokenizer, args.prompt, args)
    else:
        interactive_mode(model, tokenizer, args)


if __name__ == "__main__":
    main()
