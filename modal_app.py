import modal

image = modal.Image.debian_slim(python_version="3.11").pip_install_from_pyproject(
  "pyproject.toml"
)

app = modal.App("prompt-injection-detector", image=image)

@app.function(
    image=image, 
    keep_warm=1,
    gpu="any"
)
@modal.asgi_app()
def fastapi_app():
  from src.pid.api.main import app
    
  return app