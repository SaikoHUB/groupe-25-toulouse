#!/usr/bin/env python3
"""
Main training script for Phi-3 Medical Chatbot
Supports CUDA, Mac Silicon (MPS), and CPU
No HuggingFace login required for public datasets
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import TrainingConfig, ModelConfig, DataConfig
from src.data import MedicalDatasetLoader
from src.model import ModelLoader
from src.training import MedicalChatbotTrainer
from src.utils.device import print_device_info
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Train Phi-3 Medical Chatbot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Entraînement standard
  python scripts/train.py

  # Test avec 5000 exemples
  python scripts/train.py --max-samples 5000 --epochs 1

  # Custom dataset
  python scripts/train.py --dataset your/dataset --output ./custom-output

  # Mac Silicon avec paramètres réduits
  python scripts/train.py --max-samples 10000 --epochs 1
        """
    )
    
    parser.add_argument("--dataset", type=str, default="ruslanmv/ai-medical-chatbot",
                        help="Dataset name or path")
    parser.add_argument("--max-samples", type=int, default=None,
                        help="Max samples to use (None = all)")
    parser.add_argument("--epochs", type=int, default=3,
                        help="Number of training epochs")
    parser.add_argument("--output", type=str, default="./output",
                        help="Output directory")
    parser.add_argument("--final-model", type=str, default="./medical-phi3-model",
                        help="Final model directory")
    parser.add_argument("--batch-size", type=int, default=None,
                        help="Batch size (auto if not specified)")
    parser.add_argument("--learning-rate", type=float, default=2e-4,
                        help="Learning rate")
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("🏥 PHI-3 MEDICAL CHATBOT TRAINING")
    print("="*60)
    print(f"\n✨ Features:")
    print(f"   ✅ No HuggingFace login required")
    print(f"   ✅ Auto-detects GPU (CUDA/MPS)")
    print(f"   ✅ Mac Silicon optimized")
    print(f"   ✅ Medical dataset: 257k conversations")
    
    # Print device info
    print_device_info()
    
    # Create configurations
    print("⚙️  Configuration...")
    
    model_config = ModelConfig()
    
    data_config = DataConfig(
        dataset_name=args.dataset,
        max_samples=args.max_samples
    )
    
    training_config = TrainingConfig(
        output_dir=args.output,
        final_model_dir=args.final_model,
        num_train_epochs=args.epochs,
        learning_rate=args.learning_rate,
    )
    
    if args.batch_size:
        training_config.per_device_train_batch_size = args.batch_size
    
    # Load dataset
    print("\n" + "="*60)
    print("📚 CHARGEMENT DU DATASET")
    print("="*60)
    
    dataset_loader = MedicalDatasetLoader(
        dataset_name=data_config.dataset_name,
        train_split=data_config.train_split,
        max_samples=data_config.max_samples,
    )
    
    dataset_dict = dataset_loader.load()
    train_dataset = dataset_dict["train"]
    eval_dataset = dataset_dict.get("validation", None)
    
    # Load model
    model_loader = ModelLoader(
        model_id=model_config.model_id,
        lora_r=model_config.lora_r,
        lora_alpha=model_config.lora_alpha,
        lora_dropout=model_config.lora_dropout,
        target_modules=model_config.target_modules,
    )
    
    model, tokenizer = model_loader.load()
    
    # Create trainer
    trainer = MedicalChatbotTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        config=training_config,
        text_field=data_config.text_field,
    )
    
    # Train
    trainer.train()
    
    print(f"\n{'='*60}")
    print("🎉 TOUT EST TERMINÉ!")
    print(f"{'='*60}")
    print(f"\n📁 Modèle final: {args.final_model}")
    print(f"📊 Logs TensorBoard: {args.output}/logs")
    print(f"\n🧪 Pour tester:")
    print(f"   python scripts/inference.py --model {args.final_model}")
    print()


if __name__ == "__main__":
    main()
