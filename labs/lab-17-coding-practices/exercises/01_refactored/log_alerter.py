"""
Lab 17 — Ejercicio 01: Log Alerter (Refactored)

Principios aplicados:
- 12-Factor #3 (Config): Todo desde env vars
- 12-Factor #11 (Logs): Output a stdout
- SOLID/SRP: Cada función hace UNA cosa
- SOLID/DIP: Dependencias inyectadas
- DRY: Retry como decorator reutilizable
"""

import os
import time
import logging
from functools import wraps
from typing import Protocol, Callable
from dataclasses import dataclass

# --- Config desde env vars (12-Factor #3) ---

@dataclass
class Config:
    """Configuración externalizada. Nunca hardcoded."""
    log_file: str
    webhook_url: str
    max_errors: int = 5
    retry_attempts: int = 3
    retry_backoff: float = 2.0

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            log_file=os.environ.get("LOG_FILE", "/var/log/app.log"),
            webhook_url=os.environ["WEBHOOK_URL"],  # Falla rápido si no existe
            max_errors=int(os.environ.get("MAX_ERRORS", "5")),
            retry_attempts=int(os.environ.get("RETRY_ATTEMPTS", "3")),
            retry_backoff=float(os.environ.get("RETRY_BACKOFF", "2.0")),
        )


# --- DRY: Retry como decorator reutilizable ---

def retry(max_attempts: int = 3, backoff: float = 2.0):
    """Decorator genérico de retry con backoff exponencial."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    wait = backoff ** attempt
                    logging.warning(
                        f"Attempt {attempt}/{max_attempts} failed: {e}. "
                        f"Retrying in {wait}s..."
                    )
                    time.sleep(wait)
            raise last_exception
        return wrapper
    return decorator


# --- SOLID/DIP: Interfaz de Notifier (Protocol = duck typing formal) ---

class Notifier(Protocol):
    """Cualquier cosa que pueda enviar un mensaje."""
    def send(self, message: str) -> None: ...


class WebhookNotifier:
    """Implementación concreta: envía por webhook HTTP."""
    def __init__(self, url: str, retry_attempts: int = 3, retry_backoff: float = 2.0):
        self.url = url
        self._retry_attempts = retry_attempts
        self._retry_backoff = retry_backoff

    def send(self, message: str) -> None:
        self._post(message)

    @retry(max_attempts=3, backoff=2.0)
    def _post(self, message: str) -> None:
        import requests
        response = requests.post(self.url, json={"text": message}, timeout=10)
        response.raise_for_status()


class StdoutNotifier:
    """Mock notifier para testing — imprime a stdout."""
    def send(self, message: str) -> None:
        print(f"[NOTIFICATION] {message}")


# --- SOLID/SRP: Parser solo parsea ---

def parse_errors(log_file: str) -> list[str]:
    """Lee archivo de log y extrae líneas de error. Solo eso."""
    errors = []
    try:
        with open(log_file) as f:
            for line in f:
                if "ERROR" in line:
                    errors.append(line.strip())
    except FileNotFoundError:
        logging.error(f"Log file not found: {log_file}")
    return errors


# --- SOLID/SRP: Formatter solo formatea ---

def format_summary(errors: list[str], max_display: int = 5) -> str:
    """Genera resumen legible. Solo eso."""
    count = len(errors)
    if count == 0:
        return "✅ No errors found in logs."
    
    sample = "\n".join(f"  • {e}" for e in errors[:max_display])
    suffix = f"\n  ... and {count - max_display} more" if count > max_display else ""
    return f"🚨 Found {count} errors:\n{sample}{suffix}"


# --- Orquestador: Junta las piezas (DIP — recibe dependencias) ---

def run_alerter(config: Config, notifier: Notifier) -> None:
    """
    Orquesta el flujo: parse → format → notify.
    Recibe dependencias inyectadas (no instancia nada).
    """
    logging.info(f"Parsing logs from: {config.log_file}")
    errors = parse_errors(config.log_file)
    
    summary = format_summary(errors, max_display=config.max_errors)
    logging.info(summary)
    
    notifier.send(summary)


# --- Entry point ---

if __name__ == "__main__":
    # 12-Factor #11: Logs a stdout
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler()]  # stdout, no archivo
    )

    config = Config.from_env()

    # DIP: Elegir notifier según env (fácil de cambiar sin tocar código)
    if os.environ.get("DRY_RUN", "false").lower() == "true":
        notifier = StdoutNotifier()
    else:
        notifier = WebhookNotifier(
            url=config.webhook_url,
            retry_attempts=config.retry_attempts,
            retry_backoff=config.retry_backoff,
        )

    run_alerter(config, notifier)
