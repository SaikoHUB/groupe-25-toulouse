"""
Model loader with automatic device detection and configuration
Supports CUDA (with QLoRA), MPS (Mac Silicon), and CPU
"""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model
from typing import Tuple, Optional

from ..utils.device import detect_device, supports_quantization, get_torch_dtype


class ModelLoader:
    """
    Load and configure Phi-3.5 model with LoRA
    Automatically adapts to available hardware
    """
    
    def __init__(
        self,
        model_id: str = "microsoft/Phi-3.5-mini-instruct",
        lora_r: int = 16,
        lora_alpha: int = 32,
        lora_dropout: float = 0.05,
        target_modules: str = "all-linear",
        trust_remote_code: bool = True
    ):
        """
        Initialize model loader
        
        Args:
            model_id: HuggingFace model ID
            lora_r: LoRA rank
            lora_alpha: LoRA alpha parameter
            lora_dropout: LoRA dropout rate
            target_modules: Target modules for LoRA
            trust_remote_code: Trust remote code
        """
        self.model_id = model_id
        self.lora_r = lora_r
        self.lora_alpha = lora_alpha
        self.lora_dropout = lora_dropout
        self.target_modules = target_modules
        self.trust_remote_code = trust_remote_code
        
        self.device_type = detect_device()
        self.use_quantization = supports_quantization(self.device_type)
    
    def load(self) -> Tuple[AutoModelForCausalLM, AutoTokenizer]:
        """
        Load model and tokenizer
        
        Returns:
            Tuple of (model, tokenizer)
        """
        print(f"\n{'='*60}")
        print("🤖 CHARGEMENT DU MODÈLE")
        print(f"{'='*60}\n")
        print(f"   Modèle: {self.model_id}")
        print(f"   Device: {self.device_type.upper()}")
        
        # Load tokenizer
        tokenizer = self._load_tokenizer()
        
        # Load model
        if self.use_quantization:
            model = self._load_quantized_model()
        else:
            model = self._load_standard_model()
        
        # Apply LoRA
        model = self._apply_lora(model)
        
        # Configure for training
        model.config.use_cache = False
        
        try:
            model.gradient_checkpointing_enable()
            print("   ✅ Gradient checkpointing activé")
        except:
            print("   ⚠️  Gradient checkpointing non disponible")
        
        print(f"\n{'='*60}")
        print("✅ MODÈLE PRÊT POUR L'ENTRAÎNEMENT")
        print(f"{'='*60}\n")
        
        return model, tokenizer
    
    def _load_tokenizer(self) -> AutoTokenizer:
        """Load tokenizer"""
        print("\n📥 Chargement du tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            self.model_id,
            trust_remote_code=self.trust_remote_code
        )
        
        # Configure pad token for Phi-3
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.padding_side = "right"
        
        print(f"   ✅ Tokenizer chargé (vocab size: {len(tokenizer)})")
        return tokenizer
    
    def _load_quantized_model(self) -> AutoModelForCausalLM:
        """Load model with 4-bit quantization (CUDA only)"""
        print("\n📥 Chargement du modèle (4-bit QLoRA)...")
        
        from transformers import BitsAndBytesConfig
        from peft import prepare_model_for_kbit_training
        
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True
        )
        
        model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=self.trust_remote_code,
            torch_dtype=torch.bfloat16,
        )
        
        model = prepare_model_for_kbit_training(model)
        print("   ✅ Modèle chargé en 4-bit (économie de VRAM)")
        
        return model
    
    def _load_standard_model(self) -> AutoModelForCausalLM:
        """Load model without quantization (Mac Silicon, CPU)"""
        dtype = get_torch_dtype(self.device_type)
        
        print(f"\n📥 Chargement du modèle ({dtype})...")
        print("   ℹ️  Nécessite plus de mémoire (pas de quantification)")
        
        model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            device_map="auto" if self.device_type == "cuda" else None,
            trust_remote_code=self.trust_remote_code,
            torch_dtype=dtype,
            low_cpu_mem_usage=True,
        )
        
        # Move to MPS if Mac Silicon
        if self.device_type == "mps":
            model = model.to("mps")
        
        print(f"   ✅ Modèle chargé ({dtype})")
        
        return model
    
    def _apply_lora(self, model: AutoModelForCausalLM) -> AutoModelForCausalLM:
        """Apply LoRA to model"""
        print(f"\n⚙️  Application de LoRA...")
        print(f"   Rank: {self.lora_r}")
        print(f"   Alpha: {self.lora_alpha}")
        print(f"   Dropout: {self.lora_dropout}")
        print(f"   Target: {self.target_modules}")
        
        lora_config = LoraConfig(
            r=self.lora_r,
            lora_alpha=self.lora_alpha,
            target_modules=self.target_modules,
            lora_dropout=self.lora_dropout,
            bias="none",
            task_type="CAUSAL_LM"
        )
        
        model = get_peft_model(model, lora_config)
        
        # Print trainable parameters
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        total_params = sum(p.numel() for p in model.parameters())
        
        print(f"   ✅ LoRA appliqué")
        print(f"   📊 Paramètres entraînables: {trainable_params:,} ({trainable_params/total_params*100:.2f}%)")
        
        return model
