"""
Device detection and configuration
Supports CUDA (NVIDIA), MPS (Mac Silicon), and CPU
"""
import torch
from typing import Tuple, Optional


def detect_device() -> str:
    """
    Detect available device: cuda, mps, or cpu
    
    Returns:
        str: Device type ('cuda', 'mps', or 'cpu')
    """
    if torch.cuda.is_available():
        return "cuda"
    elif torch.backends.mps.is_available():
        return "mps"
    else:
        return "cpu"


def get_device_info() -> Tuple[str, Optional[str], Optional[float]]:
    """
    Get detailed device information
    
    Returns:
        Tuple of (device_type, device_name, memory_gb)
    """
    device_type = detect_device()
    
    if device_type == "cuda":
        device_name = torch.cuda.get_device_name(0)
        memory_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        return device_type, device_name, memory_gb
    
    elif device_type == "mps":
        # Mac Silicon - memory is unified RAM
        device_name = "Apple Silicon GPU"
        return device_type, device_name, None
    
    else:
        return device_type, "CPU", None


def print_device_info():
    """Print formatted device information"""
    device_type, device_name, memory = get_device_info()
    
    print(f"\n{'='*60}")
    print("🖥️  DEVICE INFORMATION")
    print(f"{'='*60}")
    
    if device_type == "cuda":
        print(f"✅ Type: NVIDIA GPU (CUDA)")
        print(f"   Name: {device_name}")
        print(f"   VRAM: {memory:.2f} GB")
        print(f"   CUDA: {torch.version.cuda}")
        if memory < 8:
            print(f"   ⚠️  Warning: Less than 8GB VRAM")
    
    elif device_type == "mps":
        print(f"✅ Type: Apple Silicon (MPS)")
        print(f"   Device: {device_name}")
        print(f"   ℹ️  Using unified memory (RAM)")
        print(f"   ℹ️  No 4-bit quantization support")
    
    else:
        print(f"⚠️  Type: CPU only")
        print(f"   Warning: Training will be VERY slow")
    
    print(f"{'='*60}\n")


def supports_quantization(device_type: str) -> bool:
    """
    Check if device supports bitsandbytes quantization
    
    Args:
        device_type: Device type from detect_device()
    
    Returns:
        bool: True if quantization is supported
    """
    if device_type != "cuda":
        return False
    
    try:
        import bitsandbytes
        return True
    except ImportError:
        return False


def get_torch_dtype(device_type: str):
    """
    Get appropriate torch dtype for device
    
    Args:
        device_type: Device type from detect_device()
    
    Returns:
        torch.dtype: Appropriate dtype for the device
    """
    if device_type == "cuda":
        return torch.bfloat16
    else:
        return torch.float16
