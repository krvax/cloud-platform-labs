# 🛠️ SRE Deep Dive: ElastiCache Redis, TLS & VPC Isolation

Esta guía documenta un caso de uso real de Nivel Senior SRE, demostrando la capacidad de realizar intervenciones quirúrgicas en bases de datos gestionadas por AWS (ElastiCache) bajo estrictas restricciones de seguridad de red (VPC), cifrado en tránsito (TLS) y orquestación (EKS).

[English Version](./09-elasticache-redis-troubleshooting.en.md) | [Volver al Dashboard](../MACR/00-DASHBOARD.md)

---

## 📖 El Contexto (El Problema de Negocio)

**Aplicación:** LibreChat (plataforma de IA conversacional apoyada en AWS Bedrock).  
**El Incidente:** Tras una actualización de la aplicación (o un problema de estado en los agentes de IA), las sesiones de los usuarios almacenadas en **Redis** quedaron en un estado corrupto/inconsistente, bloqueando el acceso.  
**El Objetivo SRE:** Purgar selectivamente las sesiones corruptas en Redis sin afectar la base de datos principal (RDS Postgres), sin causar downtime masivo (evitar `FLUSHALL`) y sin romper los protocolos de seguridad.

---

## 🧱 La Arquitectura del Sandbox (El Desafío SRE)

El entorno presentaba una alta complejidad y deuda técnica:

- **Aislamiento de Red (VPC):** Redis ElastiCache estaba desplegado en subnets privadas, sin acceso público ni rutas directas desde la VPN de los desarrolladores.  
- **Seguridad (TLS In-Transit):** Por cumplimiento normativo, ElastiCache requería cifrado TLS para todas las conexiones; un `redis-cli` sin TLS era rechazado.
- **Arquitectura de Datos (Cluster Mode):** Redis estaba en **Cluster Mode Enabled**, con datos fragmentados (sharded) en varios nodos.
- **Capa de Acceso Frontend (ALB/ACM):** El tráfico web entraba vía un ALB gestionado por el AWS Load Balancer Controller en EKS, usando certificados de ACM para terminación SSL.
- **Soft Multi-tenancy (Namespace Isolation):** Sandbox y Staging coexistían en el **mismo clúster EKS**, separados solo por Namespaces, elevando el radio de impacto de errores a nivel clúster.
- **Fragilidad en CI/CD (El "Fork" y ECR):** La aplicación era un fork altamente customizado (`mhchat`). El push a Amazon ECR usaba etiquetas inestables sin versionado estricto, haciendo inviables los rollbacks automáticos a nivel de código.

---

## 🔬 Ejecución Técnica Paso a Paso (La Intervención)

Para resolver el incidente no bastaba con un comando aislado; había que construir un camino de acceso seguro hasta Redis dentro de la VPC y, una vez ahí, operar correctamente sobre un clúster TLS/Cluster Mode.

### Paso 1: El Puente (Kubernetes Port-Forwarding & Bastion Pod)

*   **Restricción:** La IP privada de ElastiCache no era accesible desde mi laptop.
*   **Decisión:** Usar Kubernetes como bastión dentro de la misma VPC/namespace.
*   **Ejecución:** Desplegué un pod efímero de debug (contenedor alpine con `redis-cli`) en el mismo namespace de la aplicación.

```bash
kubectl run redis-debugger \
  --image=redis:alpine \
  --restart=Never -i --tty -- sh
```

### Paso 2: La Barrera del Certificado (TLS Handshake)

*   **Restricción:** ElastiCache exigía TLS y un certificado de CA válido; conexiones sin cifrado eran rechazadas.
*   **Decisión:** Habilitar TLS en el cliente y asegurar la cadena de confianza.
*   **Ejecución:** Un intento de conexión sin TLS fallaba inmediatamente. Se habilitó el flag correspondiente.

```bash
# ESTO FALLA (Conexión cerrada por falta de cifrado)
redis-cli -h master.librechat-redis.xxxx.use1.cache.amazonaws.com -p 6379

# La Solución: Habilitar TLS
redis-cli --tls \
  -h master.librechat-redis.xxxx.use1.cache.amazonaws.com \
  -p 6379
```

> **Nota SRE:** Si el pod de debug no tiene `ca-certificates`, el handshake falla con `certificate verify failed`; instalar o montar los certificados raíz es obligatorio.

### Paso 3: Navegando el Sharding (El Error MOVED)

*   **Restricción:** Redis estaba en Cluster Mode y la llave podía vivir en cualquier shard.
*   **Decisión:** Activar el modo cluster en el cliente para manejar redireccionamientos automáticos.
*   **Ejecución:** Al ejecutar comandos de borrado, Redis devolvía errores tipo `MOVED 10.0.1.45:6379`. Se usó el flag `-c`.

```bash
# Conexión consciente del Cluster
redis-cli -c --tls \
  -h master.librechat-redis.xxxx.use1.cache.amazonaws.com \
  -p 6379
```
Esto permite al cliente saltar entre nodos internos y purgar exactamente las llaves problemáticas sin tocar el resto del dataset.

### Paso 4: Validación Final (ALB & Ingress)

*   Tras purgar las sesiones, verifiqué que la capa L7 (ALB + Ingress Controller) seguía ruteando tráfico HTTPS solo hacia pods sanos tras el rollout.
*   Validé certificados de ACM, reglas de Ingress y health checks del ALB para asegurar que no hubiera regresiones en la capa de entrada.

---

## 🎤 La Narrativa (Cómo contarlo en Entrevistas)

**Situación:** *"En MHE, heredé un fork customizado de LibreChat (`mhchat`) en un EKS con alta deuda técnica: CI/CD inestable en ECR y aislamiento suave (Namespaces). Tras un push, las sesiones en Redis se corrompieron."*

**Tarea:** *"Necesitaba purgar la caché quirúrgicamente sin causar downtime en Staging ni romper las políticas de red de la VPC."*

**Acción:** *"Desplegué un pod de debug en EKS como bastión y usé `kubectl port-forward`. Navegué la seguridad de AWS habilitando TLS y el modo Cluster en `redis-cli` para manejar redirecciones de shards, mientras auditaba el ALB y ACM para asegurar la entrada HTTPS."*

**Resultado y Siguiente Paso:** *"Logré la estabilidad en caliente. Este éxito en el entorno pionero (Sandbox) nos permitió parametrizar la infraestructura y promover el stack hacia Staging de forma limpia y automatizada."*
