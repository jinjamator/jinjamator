#requires lib dnspython

import dns.resolver
import dns.reversename
import base64
import json as json_o
import os
import time
from typing import Any, Dict, Tuple

import dns.message

#Resolver instance for dns
# r = network.dns.connect(nameservers=dns_servers)
# cache = network.dns.create_cache(path_to_cache_file)
# cache.load(ignore_ttl=True)
# r.cache = cache

# print(network.dns.ptr(r,ip_addr)[0])


def connect(**kwargs):
    """
    Create and configure a DNS resolver instance.

    Supported keyword arguments:
        nameservers (str | list[str], optional):
            One nameserver IP/address or a list of nameserver IPs to use.
            If omitted, the resolver keeps its default empty configuration
            because ``configure=False`` is used.
        port (int, optional):
            DNS server port number.
        timeout (float, optional):
            Per-request timeout in seconds.
        lifetime (float, optional):
            Total time in seconds to spend trying to resolve a query.

    Returns:
        dns.resolver.Resolver:
            A configured resolver instance.

    Notes:
        The resolver is created with ``configure=False``, so it does not read
        system DNS configuration automatically.
    """
    nameservers = kwargs.get('nameservers',False)
    port = kwargs.get('port',False)
    timeout = kwargs.get('timeout',False)
    lifetime = kwargs.get('lifetime',False)
    
    req = dns.resolver.Resolver(configure=False)

    if nameservers: 
        if isinstance(nameservers,list): req.nameservers = nameservers
        else: req.nameservers = [nameservers]
    
    if port: req.port = port
    if timeout: req.timeout = timeout
    if lifetime: req.lifetime = lifetime

    return req



def ptr(req,query_string,**kwargs):
    """
    Perform a PTR lookup for an IP address or reverse lookup name.

    Args:
        req (network.dns.connect()):
            Resolver instance used to perform the lookup.
        query_string (str):
            Either an IP address or a fully qualified reverse DNS name ending
            with ``.in-addr.arpa.``.
        **kwargs:
            Additional keyword arguments passed through to :func:`query`.

            Supported keyword arguments:
                return_list (bool, optional):
                    If ``True`` and an error occurs, return a one-item list
                    containing the error string. If ``False``, return the
                    ``dns_error`` instance directly. Defaults to ``True``.

    Returns:
        list[str] | dns_error:
            On success, returns a list of PTR target names with trailing dots
            removed. On failure, returns either a list containing the error
            string or a ``dns_error`` object depending on ``return_list``.
    """
    return_list = kwargs.get("return_list",True)

    if not str(query_string).endswith(".in-addr.arpa."): query_string = dns.reversename.from_address(query_string)

    ans = query(req,query_string, "PTR",**kwargs)
    if not isinstance(ans,dns_error): return [rr.to_text().rstrip(".") for rr in ans]
    else: 
        if return_list: return [str(ans)]
        else: return ans




def query (req,query,q_type,**kwargs):
    """
    Execute a DNS query and normalize common resolver exceptions.

    Args:
        req (network.dns.connect()):
            Resolver instance used to perform the lookup.
        query (str | dns.name.Name):
            DNS name to query.
        q_type (str):
            Record type to request, such as ``"A"``, ``"AAAA"``, ``"MX"``,
            or ``"PTR"``.
        **kwargs:
            Reserved for compatibility with callers. Currently unused.

    Returns:
        dns.resolver.Answer | dns_error:
            A resolver answer object on success, or a ``dns_error`` instance
            describing the failure.

    Error mapping:
        - ``NXDOMAIN`` -> queried name does not exist
        - ``NoAnswer`` -> queried name exists but not for the requested type
        - ``Timeout`` -> resolver timed out
        - ``NoNameservers`` -> all configured nameservers failed
        - any other exception -> ``UNKNOWN_ERROR``
    """
    try:
        ans = req.resolve(query, q_type)
        return ans
    
    except dns.resolver.NXDOMAIN:
        log.debug(f"dns query for {query} returned NXDOMAIN")
        return dns_error("NXDOMAIN")  # no such reverse name
    
    except dns.resolver.NoAnswer:
        log.debug(f"dns query for {query} returned NoAnswer")
        return dns_error("NoAnswer")  # exists but not the correct type
    
    except dns.resolver.Timeout:
        log.debug(f"dns query for {query} returned Timeout")
        return dns_error("Timeout")  # server didn't respond in time
    
    except dns.resolver.NoNameservers:
        log.debug(f"dns query for {query} returned NoNameservers")
        return dns_error("NoNameservers")  # all nameservers failed (SERVFAIL/REFUSED/etc.)
    
    except Exception as e:
        log.debug(f"dns query for {query} returned unknown error")
        log.debug(e)
        return dns_error("UNKNOWN_ERROR")



class dns_error:
    """
    Class for normalized DNS lookup errors.

    Args:
        e_type (str):
            A short error identifier such as ``"NXDOMAIN"`` or ``"Timeout"``.

    Attributes:
        error_type (str):
            Stored error identifier.

    Notes:
        This class is used instead of raising exceptions so callers can handle
        DNS failures as return values.
    """
    def __init__(self, e_type: str):
        self.error_type = e_type

    def __str__(self) -> str:
        return f"Error: {self.error_type}"

    def __repr__(self) -> str:
        return f"dns_error(error_type={self.error_type!r})"
    


def create_cache(cachefile):
    """
    Create a persistent DNS cache instance.

    Args:
        cachefile (str):
            Path to the cache file used for saving and loading cached records.

    Returns:
        PersistentDNSCache:
            A cache object bound to the given file path.
    """
    return PersistentDNSCache(cachefile)


Key = Tuple[str, int, int]  # (qname_text, rdtype, rdclass)


class PersistentDNSCache:
    """
    File-backed DNS cache for serialized dnspython responses.

    The cache stores DNS responses in memory and can persist them to disk as
    JSON. Responses are serialized in DNS wire format and restored later into
    ``dns.resolver.Answer`` objects.

    Args:
        path (str):
            File path used to save and load the cache.

    Attributes:
        path (str):
            Cache file location.
        ignore_ttl (bool):
            When ``True``, cached entries are returned even after expiration.
        _data (dict[Key, dict[str, Any]]):
            Internal mapping of cache keys to serialized response metadata.

    Notes:
        Cache keys are tuples of ``(qname_text, rdtype, rdclass)``.
    """
    def __init__(self, path: str):
        """
        Initialize an empty persistent DNS cache.

        Args:
            path (str):
                File path used for cache persistence.
        """
        self.path = path
        self._data: Dict[Key, Dict[str, Any]] = {}
        self.ignore_ttl = False #Possibility to ignore the TTL and answer from cache

    @staticmethod
    def _k_to_str(k: Key) -> str:
        """
        Convert a cache key tuple into a string form for JSON storage.

        Args:
            k (Key):
                Cache key as ``(qname_text, rdtype, rdclass)``.

        Returns:
            str:
                Pipe-delimited string representation of the key.
        """
        qname, rdtype, rdclass = k
        return f"{qname}|{rdtype}|{rdclass}"

    @staticmethod
    def _str_to_k(s: str) -> Key:
        """
        Convert a serialized key string back into a cache key tuple.

        Args:
            s (str):
                Serialized key in ``"qname|rdtype|rdclass"`` format.

        Returns:
            Key:
                Parsed cache key tuple.
        """
        qname, rdtype, rdclass = s.split("|", 2)
        return (qname, int(rdtype), int(rdclass))

    def get(self, key: Any) -> Any:
        """
        Retrieve a cached DNS answer if present and still valid.

        Args:
            key (Any):
                dnspython cache key containing ``(qname, rdtype, rdclass)``.

        Returns:
            dns.resolver.Answer | None:
                Reconstructed cached answer object if found and valid,
                otherwise ``None``.

        Notes:
            Expired entries are removed automatically unless ``ignore_ttl`` is
            enabled.
        """
        qname, rdtype, rdclass = key
        k: Key = (qname.to_text(), int(rdtype), int(rdclass))

        entry = self._data.get(k)
        if not entry or (not self.ignore_ttl and entry["expires_at"] <= time.time()):
            self._data.pop(k, None)
            return None

        #Give the cached answer
        wire = base64.b64decode(entry["wire_b64"])
        response = dns.message.from_wire(wire)

        return dns.resolver.Answer(
            qname=qname,
            rdtype=rdtype,
            rdclass=rdclass,
            response=response,
            #raise_on_no_answer=entry.get("raise_on_no_answer", True),
        )

    def put(self, key: Any, value: Any) -> None:
        """
        Store a DNS response in the cache.

        Args:
            key (Any):
                dnspython cache key containing ``(qname, rdtype, rdclass)``.
            value (Any):
                Resolver answer object. It must provide a ``response``
                attribute containing the raw DNS message.

        Returns:
            None

        Notes:
            The cached expiration time is based on the minimum TTL found across
            the DNS message answer, authority, and additional sections.
            Entries with no TTL or non-positive TTL are ignored.
        """
        qname, rdtype, rdclass = key
        response = getattr(value, "response", None)
        if response is None:
            return

        ttl = self._min_ttl(response)
        if not ttl or ttl <= 0:
            return

        k: Key = (qname.to_text(), int(rdtype), int(rdclass))
        self._data[k] = {
            "expires_at": time.time() + ttl,
            "wire_b64": base64.b64encode(response.to_wire()).decode("ascii"),
            "raise_on_no_answer": getattr(value, "raise_on_no_answer", True),
        }

    def flush(self) -> None:
        """
        Remove all cached entries from memory.

        Returns:
            None
        """
        self._data.clear()

    def save(self) -> None:
        """
        Persist the current cache contents to disk as JSON.

        Returns:
            None

        Notes:
            Parent directories are created automatically if needed.
        """
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        serializable = {self._k_to_str(k): v for k, v in self._data.items()}
        with open(self.path, "w", encoding="utf-8") as f:
            json_o.dump(serializable, f)

    def load(self,**kwargs) -> None:
        """
        Load cached entries from disk into memory.

        Args:
            **kwargs:
                Supported keyword arguments:
                    ignore_ttl (bool, optional):
                        If ``True``, load entries even if they are expired and
                        allow ``get()`` to return them. Defaults to ``False``.

        Returns:
            None

        Notes:
            If the cache file does not exist, this method does nothing.
            When ``ignore_ttl`` is ``False``, expired entries are skipped.
        """
        self.ignore_ttl = kwargs.get('ignore_ttl',False)
        if not os.path.exists(self.path):
            return
        with open(self.path, "r", encoding="utf-8") as f:
            raw: Dict[str, Dict[str, Any]] = json_o.load(f)

        now = time.time()
        self._data = {}
        for k_str, entry in raw.items():
            if self.ignore_ttl or entry.get("expires_at", 0) > now:
                self._data[self._str_to_k(k_str)] = entry

    @staticmethod
    def _min_ttl(msg: dns.message.Message) -> int | None:
        """
        Compute the minimum TTL found in a DNS message.

        Args:
            msg (dns.message.Message):
                DNS message whose RRsets will be inspected.

        Returns:
            int | None:
                The smallest TTL across answer, authority, and additional
                sections, or ``None`` if no TTL values are present.
        """
        ttls = []
        for rrset in (msg.answer + msg.authority + msg.additional):
            ttl = getattr(rrset, "ttl", None)
            if ttl is not None:
                ttls.append(int(ttl))
        return min(ttls) if ttls else None
