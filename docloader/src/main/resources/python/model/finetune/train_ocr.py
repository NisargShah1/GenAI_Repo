import torch
from torch.utils.data import Dataset
from PIL import Image
import os
from transformers import (
    VisionEncoderDecoderModel,
    TrOCRProcessor,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments
)
from dataclasses import dataclass
from typing import Any, Dict, List

# ------------------------------
# 1️⃣ Dataset
# ------------------------------
class OCRDataset(Dataset):
    def __init__(self, root_dir, processor, max_target_length=128):
        self.root_dir = root_dir
        self.processor = processor

        # Read labels
        label_file = os.path.join(root_dir, "labels.txt")
        with open(label_file, "r", encoding="utf-8") as f:
            self.labels = [line.strip() for line in f.readlines()]

        # Match images and labels
        self.image_paths = sorted([
            os.path.join(root_dir, fname)
            for fname in os.listdir(root_dir)
            if fname.lower().endswith(('.png', '.jpg', '.jpeg'))
        ])
        assert len(self.image_paths) == len(self.labels), \
            "Mismatch between image count and labels.txt lines"

        self.max_target_length = max_target_length

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        image = Image.open(self.image_paths[idx]).convert("RGB")
        text = self.labels[idx]

        pixel_values = self.processor(images=image, return_tensors="pt").pixel_values.squeeze()
        labels = self.processor.tokenizer(
            text,
            padding="max_length",
            truncation=True,
            max_length=self.max_target_length
        ).input_ids

        return {"pixel_values": pixel_values, "labels": torch.tensor(labels)}


# ------------------------------
# 2️⃣ Data collator (fallback)
# ------------------------------
@dataclass
class DataCollatorForVision2Seq:
    processor: Any
    model: Any

    def __call__(self, features: List[Dict[str, Any]]) -> Dict[str, torch.Tensor]:
        pixel_values = torch.stack([f["pixel_values"] for f in features])
        labels = [f["labels"] for f in features]
        labels = torch.nn.utils.rnn.pad_sequence(
            labels,
            batch_first=True,
            padding_value=self.processor.tokenizer.pad_token_id
        )
        return {"pixel_values": pixel_values, "labels": labels}


# ------------------------------
# 3️⃣ Model & processor
# ------------------------------
model_name = "microsoft/trocr-base-handwritten"
processor = TrOCRProcessor.from_pretrained(model_name)
model = VisionEncoderDecoderModel.from_pretrained(model_name)

# 🔧 Fix: Set special tokens
model.config.decoder_start_token_id = processor.tokenizer.bos_token_id
model.config.pad_token_id = processor.tokenizer.pad_token_id
model.config.eos_token_id = processor.tokenizer.eos_token_id
model.config.vocab_size = model.config.decoder.vocab_size

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# ------------------------------
# 4️⃣ Datasets
# ------------------------------
train_dataset = OCRDataset("dataset/train", processor)
val_dataset = OCRDataset("dataset/val", processor)

# ------------------------------
# 5️⃣ Training args (CPU-safe)
# ------------------------------
training_args = Seq2SeqTrainingArguments(
    output_dir="./trocr-finetuned",
    per_device_train_batch_size=1,
    per_device_eval_batch_size=1,
    num_train_epochs=1,
    save_total_limit=1,
    logging_dir="./logs",
    logging_steps=10,
    learning_rate=5e-5,
    predict_with_generate=False,
    report_to=[],  # Disable wandb/tensorboard auto-init
)

# ------------------------------
# 6️⃣ Trainer
# ------------------------------
data_collator = DataCollatorForVision2Seq(processor=processor, model=model)

trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    data_collator=data_collator,
)

# ------------------------------
# 7️⃣ Train
# ------------------------------
trainer.train()
