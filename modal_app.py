import modal

image = (
  modal.Image.debian_slim(python_version="3.11")
  .pip_install_from_pyproject("pyproject.toml")
  .add_local_python_source("pid")
)

app = modal.App("prompt-injection-detector", image=image)

@app.function(
  image=image,
  secrets=[modal.Secret.from_name("pid-secrets")],
  min_containers=1,
  gpu="any"
)
@modal.asgi_app()
def fastapi_app():
  from pid.api.main import app
  return app