import json
from transformers import GPT2Tokenizer, GPT2LMHeadModel, Trainer, TrainingArguments
from datasets import Dataset
import os

def load_training_data(training_data_dir):
    """
    Load training data from the specified directory.

    Parameters:
        training_data_dir (str): Directory containing training data files.

    Returns:
        list: List of training data texts.
    """
    texts = []
    for filename in os.listdir(training_data_dir):
        if filename.endswith('.json'):
            with open(os.path.join(training_data_dir, filename), 'r') as file:
                data = json.load(file)
                texts.append(data["input"])
                texts.append(data["output"])
    return texts

def prepare_dataset(texts):
    """
    Prepare the dataset for training.

    Parameters:
        texts (list): List of training data texts.

    Returns:
        Dataset: Hugging Face dataset.
    """
    return Dataset.from_dict({"text": texts})

def tokenize_function(tokenizer, examples):
    """
    Tokenize the dataset examples.

    Parameters:
        tokenizer (GPT2Tokenizer): GPT2 tokenizer.
        examples (dict): Examples to tokenize.

    Returns:
        dict: Tokenized examples.
    """
    return tokenizer(examples["text"], truncation=True, padding='max_length', max_length=512)

def train_model(training_data_dir, model_dir):
    """
    Train a GPT model using the collected data.

    Parameters:
        training_data_dir (str): Directory containing training data files.
        model_dir (str): Directory to save the trained model.
    """
    texts = load_training_data(training_data_dir)

    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
    model = GPT2LMHeadModel.from_pretrained('gpt2')

    dataset = prepare_dataset(texts)
    tokenized_dataset = dataset.map(lambda examples: tokenize_function(tokenizer, examples), batched=True)

    training_args = TrainingArguments(
        output_dir=model_dir,
        num_train_epochs=3,
        per_device_train_batch_size=2,
        save_steps=10_000,
        save_total_limit=2,
        logging_dir=os.path.join(model_dir, 'logs'),
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset
    )

    trainer.train()
    model.save_pretrained(model_dir)
    tokenizer.save_pretrained(model_dir)
    print(f"Model trained and saved to {model_dir}")

if __name__ == "__main__":
    training_data_dir = "models/Veronica/training_data"
    model_dir = "models/Veronica"
    train_model(training_data_dir, model_dir)
