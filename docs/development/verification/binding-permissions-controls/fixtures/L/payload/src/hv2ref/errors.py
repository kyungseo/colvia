class ContractError(Exception):
    """Fail-closed contract error with a stable code."""

    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


class InjectedCrash(ContractError):
    """Intentional process-ordering interruption used by the bounded vertical."""

    def __init__(self, point: str):
        super().__init__("HV2-INJECTED-CRASH", point)
        self.point = point
