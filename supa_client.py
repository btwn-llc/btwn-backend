import supabase
from supabase.client import Client

class SupaAdminClient:
    """
    Singleton of admin client.
    """
    __SERVICE_URL: str = "https://vhwdgdmcvvieegsganes.supabase.co"
    __SERVICE_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZod2RnZG1jdnZpZWVnc2dhbmVzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcxOTEwMjMyMSwiZXhwIjoyMDM0Njc4MzIxfQ.9abLEFKD_54jnTQbtD6QQvnFJyEHmBP5przHDdDNgG0"
    __singleton: "SupaAdminClient" = None  # type: ignore

    @classmethod
    def get(cls):
        if cls.__singleton is None:
            cls.__singleton = SupaAdminClient()
        return cls.__singleton.__client

    def __init__(self):
        if self.__singleton is not None:
            raise Exception("Singleton cannot be initialized twice!")
        self.__client: Client = supabase.create_client(
            self.__SERVICE_URL, self.__SERVICE_KEY
        )

    def __del__(self):
        self.__client.auth.sign_out()
