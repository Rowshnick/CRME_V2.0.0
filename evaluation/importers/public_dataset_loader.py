from datetime import datetime


class PublicDatasetLoader:
    """
    External public dataset metadata loader

    Supports:
    - UCI
    - OpenML
    - Other repositories
    """


    def create_metadata(
        self,
        name,
        provider,
        url,
        description=""
    ):

        return {

            "name": name,

            "source": "public",

            "provider": provider,

            "url": url,

            "description": description,

            "registered_at":
                datetime.utcnow()
                .isoformat()
        }

