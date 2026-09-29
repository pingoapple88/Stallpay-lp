from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AdapterResult:
    status: str
    reference: str | None = None
    payload: dict[str, Any] | None = None


class ILLMProvider(ABC):
    @abstractmethod
    def parse_order(self, *, message: str, organization_id: str) -> AdapterResult:
        raise NotImplementedError


class IERPProvider(ABC):
    @abstractmethod
    def submit_order(self, *, organization_id: str, order_reference: str) -> AdapterResult:
        raise NotImplementedError


class IInventoryProvider(ABC):
    @abstractmethod
    def reconcile(self, *, organization_id: str, location_id: str) -> AdapterResult:
        raise NotImplementedError


class IInvoiceProvider(ABC):
    @abstractmethod
    def issue(self, *, organization_id: str, order_reference: str) -> AdapterResult:
        raise NotImplementedError


class IPaymentProvider(ABC):
    @abstractmethod
    def create_payment(self, *, organization_id: str, order_reference: str, amount_minor: int) -> AdapterResult:
        raise NotImplementedError

    @abstractmethod
    def verify(self, *, organization_id: str, payment_reference: str) -> AdapterResult:
        raise NotImplementedError

    @abstractmethod
    def handle_callback(self, *, organization_id: str, payload: dict[str, Any]) -> AdapterResult:
        raise NotImplementedError


class IDeviceProvider(ABC):
    @abstractmethod
    def inspect(self, *, organization_id: str, device_id: str) -> AdapterResult:
        raise NotImplementedError


class INotificationProvider(ABC):
    @abstractmethod
    def notify(self, *, organization_id: str, event: str) -> AdapterResult:
        raise NotImplementedError


class ILogisticsProvider(ABC):
    @abstractmethod
    def create_label(self, *, organization_id: str, shipment_reference: str) -> AdapterResult:
        raise NotImplementedError
