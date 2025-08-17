from huggingface_hub import snapshot_download

model_name = "Qwen/Qwen3-4B"
local_dir = "./models/qwen3-4b"

snapshot_download(
    repo_id=model_name,
    local_dir=local_dir,
)