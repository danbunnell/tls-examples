from requests.adapters import HTTPAdapter


class AlternateHostnameAdapter(HTTPAdapter):
    """An adapter that handles connecting to a server using an alternate hostname

    Developed from: https://stackoverflow.com/questions/67831134/how-can-i-change-the-server-name-indication-in-a-python-request

    Also refer to Requests session config: https://requests.readthedocs.io/en/latest/user/advanced/#transport-adapters
    and underlying implementation: https://urllib3.readthedocs.io/en/stable/advanced-usage.html#custom-sni-hostname
    """

    def __init__(self, hostname: str, **kwargs):
        self._hostname = hostname
        super().__init__(**kwargs)

    def send(self, request, **kwargs):
        connection_pool_kwargs = self.poolmanager.connection_pool_kw
        if self._hostname:
            connection_pool_kwargs["assert_hostname"] = self._hostname
        elif "assert_hostname" in connection_pool_kwargs:
            connection_pool_kwargs.pop("assert_hostname", None)

        return super().send(request, **kwargs)

    def init_poolmanager(self, *args, **kwargs):
        super().init_poolmanager(
            server_hostname=self._hostname,
            *args,
            **kwargs)
