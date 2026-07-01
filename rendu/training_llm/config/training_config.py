"""
Configuration classes for training Phi-3.5 Medical Chatbot
Optimized for both CUDA and Mac Silicon (MPS)
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class ModelConfig:
    """Model configuration"""
    model_id: str = "microsoft/Phi-3.5-mini-instruct"
    trust_remote_code: bool = True
    use_quantization: bool = True  # Auto-disabled on Mac Silicon
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    target_modules: str = "all-linear"
    

@dataclass
class DataConfig:
    """Dataset configuration"""
    dataset_name: str = "ruslanmv/ai-medical-chatbot"
    text_field: str = "text"
    train_split: float = 0.95
    max_samples: Optional[int] = None  # None = use all data
    

@dataclass
class TrainingConfig:
    """Training configuration - auto-adjusted based on device"""
    output_dir: str = "./output"
    final_model_dir: str = "./medical-phi3-model"
    
    # Training hyperparameters (adjusted by device detector)
    per_device_train_batch_size: int = 2
    per_device_eval_batch_size: int = 2
    gradient_accumulation_steps: int = 4
    learning_rate: float = 2e-4
    num_train_epochs: int = 3
    max_seq_length: int = 2048  # Auto-adjusted for Mac Silicon
    
    # Optimizer (auto-selected)
    optim: str = "paged_adamw_32bit"  # or "adamw_torch" for Mac
    weight_decay: float = 0.01
    max_grad_norm: float = 0.3
    
    # Learning rate schedule
    lr_scheduler_type: str = "cosine"
    warmup_steps: int = 100
    
    # Evaluation
    eval_strategy: str = "steps"
    eval_steps: int = 50
    save_strategy: str = "steps"
    save_steps: int = 100
    save_total_limit: int = 2
    load_best_model_at_end: bool = True
    
    # Logging
    logging_steps: int = 10
    logging_dir: str = "./output/logs"
    report_to: list = None
    
    # Precision (auto-selected)
    fp16: bool = False
    bf16: bool = True  # Auto-switched to fp16 on Mac
    
    # Misc
    seed: int = 42
    
    def __post_init__(self):
        if self.report_to is None:
            self.report_to = ["tensorboard"]
    
    def adjust_for_device(self, device_type: str):
        """Adjust config based on device type"""
        if device_type == "mps":
            # Mac Silicon optimizations
            self.per_device_train_batch_size = 1
            self.gradient_accumulation_steps = 8
            self.max_seq_length = 1024
            self.optim = "adamw_torch"
            # MPS doesn't support fp16/bf16 with Accelerate - use full precision
            self.fp16 = False
            self.bf16 = False
            print("⚙️  Config ajusté pour Mac Silicon (full precision)")
        elif device_type == "cpu":
            # CPU optimizations
            self.per_device_train_batch_size = 1
            self.gradient_accumulation_steps = 16
            self.max_seq_length = 512
            self.optim = "adamw_torch"
            self.fp16 = True
            self.bf16 = False
            print("⚙️  Config ajusté pour CPU")
        else:
            print("⚙️  Config optimisé pour GPU CUDA")
