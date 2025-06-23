import json

# Cargar archivo JSON original
with open("clave_google.json", "r") as f:
    data = json.load(f)

# Escapar correctamente la private_key
data["private_key"] = data["private_key"].replace("\n", "\\n")

# Crear contenido TOML
with open(".streamlit/secrets.toml", "w") as f:
    f.write(f'sheet_id = "1kHRwZ82FZ6bSP55-MHX9864cNukH9LMFwQvdizs4DQQ"\n\n')
    f.write("[gcp_service_account]\n")
    for k, v in data.items():
        f.write(f'{k} = "{v}"\n')

print("✅ ¡Archivo secrets.toml generado correctamente!")
