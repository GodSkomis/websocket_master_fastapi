from typing import Dict, Optional, Type, Any, Callable, Coroutine, Iterable
from inspect import signature, iscoroutine


INJECTOR_PROVIDERS = Type[Dict[Type, Callable[[], Any | Coroutine]]]
INJECTOR_PROVIDERS_DATA = Type[Dict[Type, Any | Callable[[], Any | Coroutine]]]


class NotDeliveredError(Exception):
    pass


def _raise_not_delivered(type_):
    raise NotDeliveredError(f"Value for {type_} not delivered")


class Injector:
    _ignore: Iterable[Type]= tuple()
    _providers: INJECTOR_PROVIDERS = dict()
    
    def __init__(self, providers_data: INJECTOR_PROVIDERS_DATA = None):
        if not providers_data:
            return
        self._providers = self._providers.copy()
        for key, item in providers_data.items():
            self._providers[key] = item if callable(item) else lambda: item
    
    @classmethod
    def register(cls, type_: Type, provider: Optional[Callable[[], Any]] = None):
        cls._providers[type_] = provider if provider else lambda: _raise_not_delivered(type_)
        
    def resolve_provider(self, type_: Type) -> Any | Coroutine:
        provider = self._providers.get(type_)
        if provider:
            return provider()
        raise ValueError(f"No provider registered for {type_}")

    def inject_async(self, func: Callable):
        async def wrapper(*args, **kwargs):
            sig = signature(func)
            for name, param in sig.parameters.items():
                if name not in kwargs and param.annotation != param.empty:
                    provider = self.resolve_provider(param.annotation)
                    kwargs[name] = await provider if iscoroutine(provider) else provider
            return await func(*args, **kwargs)
        return wrapper
    
    def inject_sync(self, func: Callable):
        def wrapper(*args, **kwargs):
            sig = signature(func)
            for name, param in sig.parameters.items():
                if name not in kwargs and param.annotation != param.empty:
                    provider = self.resolve_provider(param.annotation)
                    if iscoroutine(provider):
                        continue
                    kwargs[name] = provider
                return func(*args, **kwargs)
        return wrapper
