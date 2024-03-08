from azure.storage.blob import BlobClient

from Mehmet2.settings import Settings


class AzureClient:
    settings: Settings
    _blob_client: BlobClient

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def _get_blob_client(self, container_name: str, blob_name: str):
        if not self._blob_client:
            self._blob_client = BlobClient(
                self.settings.AZURE_STORAGE_URL,
                container_name=container_name,
                blob_name=blob_name,
                credential=self.settings.AZURE_STORAGE_KEY,
            )
        return self._blob_client

    def blob_exists(self, container_name: str, blob_name: str) -> bool:
        blob_client = self._get_blob_client(container_name, blob_name)
        return blob_client.exists()
