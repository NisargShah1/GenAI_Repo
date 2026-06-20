from transformers import TrOCRProcessor

model_dir = "./trocr-finetuned"
base_model = "microsoft/trocr-base-handwritten"

# Reload the original processor and save it to the fine-tuned folder
processor = TrOCRProcessor.from_pretrained(base_model)
processor.save_pretrained(model_dir)

print("✅ Processor saved successfully to", model_dir)