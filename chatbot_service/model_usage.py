import json
from training_pipeline import ModelTrainer
from transformers import AutoTokenizer, AutoModelForSequenceClassification

def test_model(model_path, text):
    trainer = ModelTrainer(model_path)
    
    # Load label mappings
    with open(f"{model_path}/label_mappings.json", "r") as f:
        mappings = json.load(f)
    trainer.id2label = mappings["id2label"]
    trainer.label2id = mappings["label2id"]
    
    trainer.tokenizer = AutoTokenizer.from_pretrained(model_path)
    trainer.model = AutoModelForSequenceClassification.from_pretrained(model_path)
    
    return trainer.predict(text)

if __name__ == "__main__":
    model_path = "result/phobert-base"
    test_text = "Mua sách học tiếng Anh 300k"
    
    result = test_model(model_path, test_text)
    print(f"Văn bản: {test_text}")
    print(f"Kết quả dự đoán: {result['category']}")
    print(f"Độ tin cậy: {result['confidence']:.2f}")