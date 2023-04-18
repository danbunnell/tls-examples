from requests.adapters import HTTPAdapter


class AlternateHostnameAdapter(HTTPAdapter):
    """An adapter that handles connecting to a server using an alternate hostname

    Developed from: https://stackoverflow.com/questions/67831134/how-can-i-change-the-server-name-indication-in-a-python-request

    Also refer to Requests session config: https://requests.readthedocs.io/en/latest/user/advanced/#transport-adapters
    and underlying implementation: https://urllib3.readthedocs.io/en/stable/advanced-usage.html#custom-sni-hostname
    """

    def __init__(self, hostname: str, **kwargs):
        if not hostname:
            raise ValueError("Hostname is required")
        self._hostname = hostname

        super().__init__(**kwargs)

    def init_poolmanager(self, *args, **kwargs):
        super().init_poolmanager(
            server_hostname=self._hostname,
            *args,
            **kwargs)
