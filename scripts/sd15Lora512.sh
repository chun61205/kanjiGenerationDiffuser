export PROJECT_NAME="kanjiGeneration"
export WANDB_ENTITY="chun61205"
export WANDB_NAME="kanjiGeneration11"

accelerate launch examples/dreambooth/train_dreambooth_lora.py \
  --pretrained_model_name_or_path="stable-diffusion-v1-5/stable-diffusion-v1-5"  \
  --instance_data_dir="dataset/data" \
  --instance_prompt="" \
  --output_dir="runs/$WANDB_NAME" \
  --projectName=$PROJECT_NAME \
  --resolution=128 \
  --train_batch_size=1 \
  --gradient_accumulation_steps=4 \
  --checkpointing_steps=100 \
  --learning_rate=1e-5 \
  --lr_scheduler="constant" \
  --lr_warmup_steps=0 \
  --rank=4 \
  --max_train_steps=4000 \
  --validation_prompt="A kanji meaning above, up" \
  --validation_epochs=50 \
  --seed=0 \
  --report_to="wandb" \