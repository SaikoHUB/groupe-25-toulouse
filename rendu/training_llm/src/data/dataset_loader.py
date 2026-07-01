"""
Dataset loader for medical chatbot training
Handles the ruslanmv/ai-medical-chatbot dataset and custom formats
No HuggingFace login required for public datasets
"""
from datasets import load_dataset, DatasetDict, Dataset
from typing import Optional, Dict
import os


def format_medical_conversation(example: Dict) -> Dict:
    """
    Format medical conversation for Phi-3.5 training
    
    Args:
        example: Dict with 'Patient' and 'Doctor' keys
    
    Returns:
        Dict with formatted 'text' field
    """
    patient = example.get('Patient', '').strip()
    doctor = example.get('Doctor', '').strip()
    
    if patient and doctor:
        example['text'] = f"<|user|>\n{patient}<|end|>\n<|assistant|>\n{doctor}<|end|>"
    
    return example


class MedicalDatasetLoader:
    """
    Dataset loader for medical chatbot training
    Supports both the default medical dataset and custom datasets
    """
    
    def __init__(
        self,
        dataset_name: str = "ruslanmv/ai-medical-chatbot",
        train_split: float = 0.95,
        max_samples: Optional[int] = None,
        seed: int = 42
    ):
        """
        Initialize dataset loader
        
        Args:
            dataset_name: HuggingFace dataset name or local path
            train_split: Proportion for training (0.0-1.0)
            max_samples: Maximum number of samples to use (None = all)
            seed: Random seed for splitting
        """
        self.dataset_name = dataset_name
        self.train_split = train_split
        self.max_samples = max_samples
        self.seed = seed
        self.is_medical_dataset = dataset_name == "ruslanmv/ai-medical-chatbot"
    
    def load(self) -> DatasetDict:
        """
        Load and prepare the dataset
        
        Returns:
            DatasetDict with 'train' and 'validation' splits
        """
        print(f"\n📚 Chargement du dataset: {self.dataset_name}")
        
        # Disable HuggingFace token requirement for public datasets
        os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
        
        try:
            # Load dataset
            if self.is_medical_dataset:
                dataset = self._load_medical_dataset()
            else:
                dataset = self._load_standard_dataset()
            
            # Limit samples if requested
            if self.max_samples and self.max_samples < len(dataset):
                print(f"   ⚠️  Limitation à {self.max_samples} exemples")
                dataset = dataset.select(range(self.max_samples))
            
            # Create train/validation split
            dataset_dict = self._create_splits(dataset)
            
            # Print statistics
            self._print_stats(dataset_dict)
            
            return dataset_dict
        
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            print(f"\n   💡 Vérifiez:")
            print(f"      - Connexion internet active")
            print(f"      - Nom du dataset correct")
            raise
    
    def _load_medical_dataset(self) -> Dataset:
        """Load and format medical chatbot dataset"""
        print("   📋 Dataset médical (257k conversations)")
        dataset = load_dataset(self.dataset_name, split="train")
        
        print("   🔧 Formatage des conversations...")
        dataset = dataset.map(format_medical_conversation, desc="Formatting")
        
        # Filter out empty conversations
        dataset = dataset.filter(
            lambda x: 'text' in x and len(x['text']) > 20,
            desc="Filtering"
        )
        
        print(f"   ✅ {len(dataset)} conversations formatées")
        return dataset
    
    def _load_standard_dataset(self) -> Dataset:
        """Load standard dataset with 'text' field"""
        dataset = load_dataset(self.dataset_name, split="train")
        print(f"   ✅ {len(dataset)} exemples chargés")
        
        # Verify text field exists
        if 'text' not in dataset.column_names:
            raise ValueError(
                f"Dataset must have a 'text' field. "
                f"Found: {dataset.column_names}"
            )
        
        return dataset
    
    def _create_splits(self, dataset: Dataset) -> DatasetDict:
        """Create train/validation splits"""
        if self.train_split >= 1.0:
            return DatasetDict({"train": dataset})
        
        print(f"\n   📂 Création des splits ({self.train_split*100:.0f}%/{(1-self.train_split)*100:.0f}%)...")
        
        split_dataset = dataset.train_test_split(
            test_size=1.0 - self.train_split,
            seed=self.seed
        )
        
        return DatasetDict({
            "train": split_dataset["train"],
            "validation": split_dataset["test"]
        })
    
    def _print_stats(self, dataset_dict: DatasetDict):
        """Print dataset statistics"""
        print(f"\n   {'='*50}")
        print(f"   📊 STATISTIQUES DU DATASET")
        print(f"   {'='*50}")
        print(f"   Train: {len(dataset_dict['train'])} exemples")
        
        if 'validation' in dataset_dict:
            print(f"   Validation: {len(dataset_dict['validation'])} exemples")
        
        # Show example
        example = dataset_dict['train'][0]['text']
        print(f"\n   📝 Exemple (premiers 300 caractères):")
        print(f"   {'-'*50}")
        print(f"   {example[:300]}...")
        print(f"   {'-'*50}")
