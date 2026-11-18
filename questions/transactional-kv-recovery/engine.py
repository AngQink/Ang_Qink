"""Prototype engine: public examples are not a complete correctness argument."""
from wal import Journal


class Engine:
    def __init__(self, directory):
        self.journal = Journal(directory)
        self.version = 0
        self.data = {}
        self.transactions = {}
        for version, writes in self.journal.recover():
            self._publish(version, writes)

    def _publish(self, version, writes):
        for key, value in writes.items():
            if value is None:
                self.data.pop(key, None)
            else:
                self.data[key] = value
        self.version = version

    def execute(self, command):
        op, name = command["op"], command["tx"]
        if op == "begin":
            self.transactions[name] = {
                "version": self.version, "snapshot": self.data.copy(),
                "writes": {}, "reads": set(), "savepoints": [],
            }
            return {"ok": True, "version": self.version}
        tx = self.transactions[name]
        writes = tx["writes"]
        if op == "get":
            key = command["key"]
            tx["reads"].add(key)
            return {"value": writes.get(key, tx["snapshot"].get(key))}
        if op == "scan":
            lo, hi = command["start"], command["end"]
            merged = tx["snapshot"] | writes
            return {"items": [[k, v] for k, v in sorted(merged.items())
                              if v is not None and (lo is None or lo <= k)
                              and (hi is None or k < hi)]}
        if op in ("put", "delete"):
            writes[command["key"]] = command.get("value") if op == "put" else None
        elif op == "savepoint":
            tx["savepoints"].append((command["name"], writes.copy()))
        elif op == "rollback":
            for index in range(len(tx["savepoints"]) - 1, -1, -1):
                label, saved = tx["savepoints"][index]
                if label == command["name"]:
                    tx["writes"] = saved.copy()
                    tx["savepoints"] = tx["savepoints"][:index + 1]
                    break
            tx["reads"].clear()
        elif op == "abort":
            del self.transactions[name]
        elif op == "commit":
            del self.transactions[name]
            if writes:
                self.journal.append(self.version + 1, writes)
                self._publish(self.version + 1, writes)
            return {"ok": True, "version": self.version}
        return {"ok": True}

    def close(self):
        self.journal.close()
