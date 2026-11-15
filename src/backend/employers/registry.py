from src.backend.schemas.employer import EmployerProfile


class EmployerRegistry:
    def __init__(self, employers: tuple[EmployerProfile, ...] = ()) -> None:
        employer_map = {employer.company_id: employer for employer in employers}
        if len(employer_map) != len(employers):
            raise ValueError("company identifiers must be unique")
        self._employers = employer_map

    def list(self) -> list[EmployerProfile]:
        return list(self._employers.values())

    def get(self, company_id: str) -> EmployerProfile:
        try:
            return self._employers[company_id]
        except KeyError as exc:
            raise KeyError("employer not found") from exc


_registry = EmployerRegistry()


def get_employers() -> list[EmployerProfile]:
    return _registry.list()


def get_employer(company_id: str) -> EmployerProfile:
    return _registry.get(company_id)
