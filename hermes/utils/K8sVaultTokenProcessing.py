import requests


class K8sVaultTokenProcessing:
    def __init__(self, vault_url: str, vault_role_name: str):
        self.vault_url = vault_url
        self.vault_role_name = vault_role_name

    def get_ksa_jwt(self) -> str:
        """Retrieves the KSA JWT from the Kubernetes service account."""
        with open(
            "/var/run/secrets/kubernetes.io/serviceaccount/token", encoding="utf-8"
        ) as f:
            return f.read()

    def get_vault_token(self) -> str:
        headers = {
            "Content-Type": "application/json",
        }

        body = {
            "jwt": self.get_ksa_jwt(),
            "role": self.vault_role_name,
        }

        url = f"{self.vault_url}/v1/auth/kubernetes/login"
        response = requests.post(url, headers=headers, json=body, timeout=10)

        response.raise_for_status()
        return response.json()["auth"]["client_token"]
