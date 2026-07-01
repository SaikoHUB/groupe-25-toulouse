"""
Medical Chatbot Trainer
Handles training with automatic device configuration
"""
from transformers import TrainerCallback
from trl import SFTTrainer, SFTConfig
from datasets import DatasetDict
from typing import Optional
import os

from ..utils.device import detect_device, print_device_info


class ProgressCallback(TrainerCallback):
    """Callback pour afficher la progression"""
    
    def on_log(self, args, state, control, logs=None, **kwargs):
        if logs:
            if "loss" in logs:
                print(f"   📉 Step {state.global_step}: Loss = {logs['loss']:.4f}")
            if "eval_loss" in logs:
                print(f"   📊 Eval Loss = {logs['eval_loss']:.4f}")


class MedicalChatbotTrainer:
    """
    Trainer for medical chatbot fine-tuning
    Automatically configures for CUDA, MPS, or CPU
    """
    
    def __init__(
        self,
        model,
        tokenizer,
        train_dataset: DatasetDict,
        eval_dataset: Optional[DatasetDict],
        config,
        text_field: str = "text"
    ):
        """
        Initialize trainer
        
        Args:
            model: Model to train
            tokenizer: Tokenizer
            train_dataset: Training dataset
            eval_dataset: Validation dataset
            config: TrainingConfig instance
            text_field: Name of text field in dataset
        """
        self.model = model
        self.tokenizer = tokenizer
        self.train_dataset = train_dataset
        self.eval_dataset = eval_dataset
        self.config = config
        self.text_field = text_field
        
        # Detect device and adjust config
        device_type = detect_device()
        self.config.adjust_for_device(device_type)
        
        # Create output directories
        os.makedirs(self.config.output_dir, exist_ok=True)
        os.makedirs(self.config.final_model_dir, exist_ok=True)
        os.makedirs(self.config.logging_dir, exist_ok=True)
    
    def train(self):
        """Run training"""
        print(f"\n{'='*60}")
        print("🏋️  DÉMARRAGE DE L'ENTRAÎNEMENT")
        print(f"{'='*60}\n")
        
        # Print device info
        print_device_info()
        
        # Configure tokenizer max length
        # TRL 0.7+ uses tokenizer.model_max_length instead of max_seq_length parameter
        print(f"⚙️  Configuration du tokenizer...")
        print(f"   Max sequence length: {self.config.max_seq_length}")
        self.tokenizer.model_max_length = self.config.max_seq_length
        
        # Create training arguments
        training_args = self._create_training_args()
        
        # Create trainer
        print("🔧 Création du trainer...")
        
        # SFTTrainer - minimal API for TRL 0.7+
        # Most config now goes through SFTConfig (training_args)
        trainer = SFTTrainer(
            model=self.model,
            args=training_args,
            train_dataset=self.train_dataset,
            eval_dataset=self.eval_dataset,
            processing_class=self.tokenizer,
        )
        
        # Add callbacks after initialization
        trainer.add_callback(ProgressCallback())
        
        # Train
        print(f"\n{'='*60}")
        print("🚀 ENTRAÎNEMENT EN COURS")
        print(f"{'='*60}\n")
        print(f"   Époques: {self.config.num_train_epochs}")
        print(f"   Batch size: {self.config.per_device_train_batch_size}")
        print(f"   Gradient accumulation: {self.config.gradient_accumulation_steps}")
        print(f"   Effective batch size: {self.config.per_device_train_batch_size * self.config.gradient_accumulation_steps}")
        print(f"   Learning rate: {self.config.learning_rate}")
        print()
        
        try:
            trainer.train()
            
            print(f"\n{'='*60}")
            print("✅ ENTRAÎNEMENT TERMINÉ")
            print(f"{'='*60}\n")
            
            # Save final model
            self._save_model(trainer)
            
            return trainer
        
        except KeyboardInterrupt:
            print("\n⚠️  Entraînement interrompu par l'utilisateur")
            self._save_model(trainer)
            raise
        
        except Exception as e:
            print(f"\n❌ Erreur pendant l'entraînement: {e}")
            raise
    
    def _create_training_args(self) -> SFTConfig:
        """Create SFTConfig from TrainingConfig"""
        # Note: max_seq_length is NOT a parameter of SFTConfig in TRL 0.7+
        # It's handled automatically by the tokenizer's model_max_length
        return SFTConfig(
            output_dir=self.config.output_dir,
            per_device_train_batch_size=self.config.per_device_train_batch_size,
            per_device_eval_batch_size=self.config.per_device_eval_batch_size,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            learning_rate=self.config.learning_rate,
            num_train_epochs=self.config.num_train_epochs,
            lr_scheduler_type=self.config.lr_scheduler_type,
            warmup_steps=self.config.warmup_steps,
            logging_steps=self.config.logging_steps,
            eval_strategy=self.config.eval_strategy,
            eval_steps=self.config.eval_steps,
            save_strategy=self.config.save_strategy,
            save_steps=self.config.save_steps,
            save_total_limit=self.config.save_total_limit,
            load_best_model_at_end=self.config.load_best_model_at_end,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            optim=self.config.optim,
            weight_decay=self.config.weight_decay,
            max_grad_norm=self.config.max_grad_norm,
            fp16=self.config.fp16,
            bf16=self.config.bf16,
            seed=self.config.seed,
            report_to=self.config.report_to,
            logging_dir=self.config.logging_dir,
        )
    
    def _save_model(self, trainer):
        """Save trained model"""
        print(f"\n💾 Sauvegarde du modèle final dans {self.config.final_model_dir}")
        trainer.model.save_pretrained(self.config.final_model_dir)
        self.tokenizer.save_pretrained(self.config.final_model_dir)
        
        print(f"   ✅ Modèle sauvegardé!")
        print(f"\n💡 Pour charger le modèle:")
        print(f"   from peft import AutoPeftModelForCausalLM")
        print(f"   model = AutoPeftModelForCausalLM.from_pretrained('{self.config.final_model_dir}')")
