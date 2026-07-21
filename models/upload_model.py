from huggingface_hub import HfApi

api = HfApi()
api.create_repo(repo_id="lucasena/pid-classifier-v1", private=True, exist_ok=True)

api.upload_folder(
  folder_path="models/pid-classifier-v1",
  repo_id="lucasena/pid-classifier-v1",
  repo_type="model",
)