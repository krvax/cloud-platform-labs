"""
Lab 17 — Ejercicio 03: Mini Observability Pipeline (SOLID)

Demuestra:
- SRP: Cada componente (Collector, Processor, Exporter) hace UNA cosa
- OCP: Agregar nuevo exporter sin modificar código existente
- DIP: Pipeline recibe abstracciones, no concretos
- DRY: Lógica compartida en base classes

Arquitectura:
  Collector → Processor → Exporter
  (lee)       (transforma)  (envía)

Uso:
  python pipeline.py
  
  # O con config:
  METRICS_SOURCE=file METRICS_FILE=./sample_metrics.txt python pipeline.py
"""

import os
import time
import random
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Protocol

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


# --- Domain Model ---

@dataclass
class Metric:
    """Representa una métrica individual."""
    name: str
    value: float
    labels: dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def __str__(self) -> str:
        labels_str = ",".join(f'{k}="{v}"' for k, v in self.labels.items())
        return f"{self.name}{{{labels_str}}} {self.value}"


# --- Collector (SRP: solo recolecta) ---

class Collector(Protocol):
    """Interfaz: cualquier cosa que produzca métricas."""
    def collect(self) -> list[Metric]: ...


class RandomCollector:
    """Genera métricas simuladas (para demo/testing)."""
    def collect(self) -> list[Metric]:
        return [
            Metric("http_requests_total", random.randint(100, 1000), {"method": "GET", "status": "200"}),
            Metric("http_requests_total", random.randint(10, 100), {"method": "GET", "status": "500"}),
            Metric("http_request_duration_seconds", random.uniform(0.01, 2.0), {"endpoint": "/api/jobs"}),
            Metric("memory_usage_bytes", random.randint(100_000_000, 500_000_000), {"pod": "worker-1"}),
            Metric("cpu_usage_percent", random.uniform(10, 95), {"pod": "worker-1"}),
        ]


class FileCollector:
    """Lee métricas de un archivo (formato: name value label1=v1,label2=v2)."""
    def __init__(self, filepath: str):
        self.filepath = filepath

    def collect(self) -> list[Metric]:
        metrics = []
        try:
            with open(self.filepath) as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        name, value = parts[0], float(parts[1])
                        labels = {}
                        if len(parts) > 2:
                            for pair in parts[2].split(","):
                                k, v = pair.split("=")
                                labels[k] = v
                        metrics.append(Metric(name, value, labels))
        except FileNotFoundError:
            logging.error(f"Metrics file not found: {self.filepath}")
        return metrics


# --- Processor (SRP: solo transforma/filtra) ---

class Processor(Protocol):
    """Interfaz: transforma métricas."""
    def process(self, metrics: list[Metric]) -> list[Metric]: ...


class ThresholdProcessor:
    """Filtra métricas que exceden umbrales (para alerting)."""
    def __init__(self, thresholds: dict[str, float]):
        self.thresholds = thresholds  # {"cpu_usage_percent": 80, "http_request_duration_seconds": 1.0}

    def process(self, metrics: list[Metric]) -> list[Metric]:
        alerts = []
        for m in metrics:
            threshold = self.thresholds.get(m.name)
            if threshold and m.value > threshold:
                m.labels["alert"] = "threshold_exceeded"
                alerts.append(m)
        return alerts


class PassthroughProcessor:
    """No filtra nada — pasa todo (útil para logging completo)."""
    def process(self, metrics: list[Metric]) -> list[Metric]:
        return metrics


# --- Exporter (SRP: solo envía) ---

class Exporter(Protocol):
    """Interfaz: envía métricas a un destino."""
    def export(self, metrics: list[Metric]) -> None: ...


class StdoutExporter:
    """Exporta a stdout (mock de Prometheus remote_write)."""
    def export(self, metrics: list[Metric]) -> None:
        if not metrics:
            logging.info("No metrics to export.")
            return
        print("\n--- Metrics Export ---")
        for m in metrics:
            print(f"  {m}")
        print(f"--- {len(metrics)} metrics exported ---\n")


class JsonExporter:
    """Exporta a archivo JSON (mock de log shipping)."""
    def __init__(self, output_file: str = "metrics_export.json"):
        self.output_file = output_file

    def export(self, metrics: list[Metric]) -> None:
        import json
        data = [{"name": m.name, "value": m.value, "labels": m.labels, "ts": m.timestamp} for m in metrics]
        with open(self.output_file, "w") as f:
            json.dump(data, f, indent=2)
        logging.info(f"Exported {len(metrics)} metrics to {self.output_file}")


# --- Pipeline Orchestrator (DIP: recibe abstracciones) ---

class ObservabilityPipeline:
    """
    Orquesta el flujo: Collect → Process → Export.
    
    Principios:
    - DIP: Recibe interfaces, no implementaciones concretas
    - OCP: Agregar nuevo collector/processor/exporter sin modificar esta clase
    - SRP: Solo coordina, no implementa lógica de negocio
    """
    def __init__(self, collector: Collector, processor: Processor, exporter: Exporter):
        self.collector = collector
        self.processor = processor
        self.exporter = exporter

    def run(self) -> None:
        logging.info("Pipeline starting...")
        
        # Collect
        raw_metrics = self.collector.collect()
        logging.info(f"Collected {len(raw_metrics)} metrics")
        
        # Process
        processed = self.processor.process(raw_metrics)
        logging.info(f"After processing: {len(processed)} metrics")
        
        # Export
        self.exporter.export(processed)
        logging.info("Pipeline complete.")


# --- Factory (construye pipeline desde config) ---

def create_pipeline_from_env() -> ObservabilityPipeline:
    """
    Factory que construye el pipeline según env vars (12-Factor #3).
    Demuestra cómo config externalizada + DIP = flexibilidad total.
    """
    # Collector
    source = os.environ.get("METRICS_SOURCE", "random")
    if source == "file":
        collector = FileCollector(os.environ.get("METRICS_FILE", "metrics.txt"))
    else:
        collector = RandomCollector()

    # Processor
    mode = os.environ.get("PROCESSOR_MODE", "threshold")
    if mode == "passthrough":
        processor = PassthroughProcessor()
    else:
        processor = ThresholdProcessor({
            "cpu_usage_percent": float(os.environ.get("CPU_THRESHOLD", "80")),
            "http_request_duration_seconds": float(os.environ.get("LATENCY_THRESHOLD", "1.0")),
        })

    # Exporter
    export_to = os.environ.get("EXPORT_TO", "stdout")
    if export_to == "json":
        exporter = JsonExporter(os.environ.get("EXPORT_FILE", "metrics_export.json"))
    else:
        exporter = StdoutExporter()

    return ObservabilityPipeline(collector, processor, exporter)


# --- Entry Point ---

if __name__ == "__main__":
    pipeline = create_pipeline_from_env()
    pipeline.run()
