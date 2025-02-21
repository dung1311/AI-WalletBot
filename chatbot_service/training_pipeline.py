import os
import json
import torch
import logging
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    DataCollatorWithPadding
)
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

# Thiết lập logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelTrainer:
    def __init__(self, model_name, num_labels=None):
        self.model_name = model_name
        self.num_labels = num_labels
        self.tokenizer = None
        self.model = None
        self.trainer = None
        
    def prepare_data(self, data_path):
        """Đọc và chuẩn bị dữ liệu"""
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Chuẩn bị dữ liệu
        texts = [item['input'] for item in data]
        categories = [item['output']['category'] for item in data]
        
        # Lấy danh sách unique categories nếu chưa có num_labels
        if self.num_labels is None:
            unique_categories = list(set(categories))
            self.num_labels = len(unique_categories)
            self.label2id = {label: i for i, label in enumerate(unique_categories)}
            self.id2label = {i: label for label, i in self.label2id.items()}
        
        # Chuyển categories thành số
        labels = [self.label2id[category] for category in categories]
        
        # Chia dataset
        train_texts, val_texts, train_labels, val_labels = train_test_split(
            texts, labels, test_size=0.2, random_state=42
        )
        
        # Tạo datasets
        train_dataset = Dataset.from_dict({
            'text': train_texts,
            'label': train_labels
        })
        val_dataset = Dataset.from_dict({
            'text': val_texts,
            'label': val_labels
        })
        
        return train_dataset, val_dataset
    
    def preprocess_function(self, examples):
        """Tiền xử lý dữ liệu"""
        return self.tokenizer(
            examples['text'],
            truncation=True,
            padding=True,
            max_length=128
        )
    
    def compute_metrics(self, pred):
        """Tính toán các metrics"""
        labels = pred.label_ids
        preds = pred.predictions.argmax(-1)
        precision, recall, f1, _ = precision_recall_fscore_support(
            labels, preds, average='weighted'
        )
        acc = accuracy_score(labels, preds)
        return {
            'accuracy': acc,
            'f1': f1,
            'precision': precision,
            'recall': recall
        }
    
    def train(self, data_path, output_dir):
        """Huấn luyện mô hình"""
        # Tạo thư mục output nếu chưa tồn tại
        os.makedirs(output_dir, exist_ok=True)
        
        # Chuẩn bị dữ liệu
        train_dataset, val_dataset = self.prepare_data(data_path)
        
        # Khởi tạo tokenizer và model
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name,
            num_labels=self.num_labels,
            id2label=self.id2label,
            label2id=self.label2id
        )
        
        # Tokenize datasets
        tokenized_train = train_dataset.map(
            self.preprocess_function,
            batched=True
        )
        tokenized_val = val_dataset.map(
            self.preprocess_function,
            batched=True
        )
        
        # Thiết lập training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            learning_rate=2e-5,
            per_device_train_batch_size=16,
            per_device_eval_batch_size=16,
            num_train_epochs=3,
            weight_decay=0.01,
            evaluation_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
            metric_for_best_model="f1"
        )
        
        # Khởi tạo trainer
        self.trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=tokenized_train,
            eval_dataset=tokenized_val,
            tokenizer=self.tokenizer,
            data_collator=DataCollatorWithPadding(self.tokenizer),
            compute_metrics=self.compute_metrics
        )
        
        # Huấn luyện mô hình
        logger.info(f"Bắt đầu huấn luyện mô hình {self.model_name}")
        self.trainer.train()
        
        with open(f"{output_dir}/label_mappings.json", "w") as f:
            json.dump({
                "id2label": self.id2label,
                "label2id": self.label2id
            }, f)

        # Lưu mô hình và tokenizer
        self.trainer.save_model(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        
        # Đánh giá mô hình
        metrics = self.trainer.evaluate()
        logger.info(f"Kết quả đánh giá: {metrics}")
        
        return metrics
    
    def predict(self, text):
        """Dự đoán với mô hình đã huấn luyện"""
        inputs = self.tokenizer(
            text,
            truncation=True,
            padding=True,
            max_length=128,
            return_tensors="pt"
        )
        
        outputs = self.model(**inputs)
        predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        predicted_label = predictions.argmax().item()
        
        return {
            'category': self.id2label[predicted_label],
            'confidence': predictions.max().item()
        }

def train_models(models_config, data_path):
    """Huấn luyện nhiều mô hình"""
    results = {}
    
    for model_name in models_config:
        logger.info(f"Bắt đầu huấn luyện mô hình {model_name}")
        
        # Tạo thư mục output cho mô hình
        output_dir = os.path.join('result', model_name.split('/')[-1])
        
        # Khởi tạo và huấn luyện mô hình
        trainer = ModelTrainer(model_name)
        metrics = trainer.train(data_path, output_dir)
        
        results[model_name] = metrics
        
    return results

# Sử dụng pipeline
if __name__ == "__main__":
    # Danh sách các mô hình muốn huấn luyện
    models = [
        "vinai/phobert-base",
        "vinai/phobert-large",
    ]
    
    # Đường dẫn đến file dữ liệu
    data_path = "./data/data.txt"
    
    # Huấn luyện các mô hình
    results = train_models(models, data_path)
    
    # In kết quả
    for model_name, metrics in results.items():
        print(f"\nKết quả cho mô hình {model_name}:")
        print(metrics)