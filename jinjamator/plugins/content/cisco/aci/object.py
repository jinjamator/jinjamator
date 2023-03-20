import logging

log = logging.getLogger()


class ACIDiff(object):
    def __init__(self, **kwargs):

        self._results = {"add": [], "remove": [], "change": []}
        self._log = logging.getLogger("acidiff")
        if kwargs.get("debug", False):
            self._debug = True
        else:
            self._debug = False

    def debug(self, *args):
        if self._debug:
            self._log, debug(*args)

    def diff(self, src, dst, path="", **kwargs):
        self.debug(f"called diff {path}")
        if type(src) == dict:
            self.debug("src is dict")
            for sk, sv in src.items():
                if sk not in dst:
                    if kwargs.get("second_run"):
                        self._results["add"].append({"path": path, "ref": id(src[sv])})
                        self.debug(f"add dict {sk}")
                    else:
                        self._results["remove"].append(
                            {"path": path, "ref": id(src[sv])}
                        )

                        self.debug(f"del dict {sk}")
                else:

                    res = self.diff(src[sk], dst[sk], f"{path}['{sk}']", **kwargs)
                    if res:
                        src[sk] = res
        elif type(src) == list:
            for src_idx, item in enumerate(src):
                if type(item) == dict:

                    search = list(item.keys())[0]
                    self.debug(f"search {search}")
                    delete = True
                    for dst_idx, dst_item in enumerate(dst):
                        if list(dst_item.keys())[0] == search:
                            delete = False
                            break

                    if delete:
                        if kwargs.get("second_run"):
                            self.debug(f"add src {search} {kwargs}")
                            self._results["add"].append(
                                {
                                    "path": f"{path}['children'][{src_idx}]",
                                    "ref": id(src[src_idx]),
                                }
                            )
                            if kwargs.get("patch", False):
                                dst.append(src[src_idx])

                        else:
                            self.debug(f"remove src {search}")
                            self._results["remove"].append(
                                {
                                    "path": f"{path}['children'][{src_idx}]",
                                    "ref": id(src[src_idx]),
                                }
                            )
                            name = list(src[src_idx].keys())[0]
                            if kwargs.get("patch", False):
                                src[src_idx][name]["attributes"]["status"] = "deleted"

                    else:
                        self.diff(
                            src[src_idx], dst[dst_idx], f"{path}[{src_idx}]", **kwargs
                        )

                else:
                    raise NotImplementedError(
                        "in aci there are always dicts within lists"
                    )
        elif type(src) == str:
            if src != dst:
                self._results["change"].append(
                    {"path": path, "old_value": src, "new_value": dst}
                )
                if kwargs.get("patch", False):
                    return dst
                else:
                    return src
            return src

        if path == "" and not kwargs.get("second_run"):
            self.diff(dst, src, second_run=True, **kwargs)
            return self._results

    def patch(self, src, dst):
        return self.diff(src, dst, patch=True)


def get_object(a):
    if type(a) == str:
        if a.startswith("/") or a.startswith("api"):
            adata = cisco.aci.query(a)
        else:
            try:
                adata = json.loads(a)
            except Exception as e:
                log.error(f"This is neither a dn nor a json string: {a}")
                return None


def diff(a, b, patch=False):
    a = get_object(a)
    b = get_object(b)
    d = ACIDiff()
    return d.diff(a, b)


def patch(a, b):
    return diff(a, b, True)
