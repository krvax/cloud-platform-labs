# Lab 10: GitOps con ArgoCD 🐙

[🇪🇸 Español](./README.md) | [🇬🇧 English](./README.en.md)

**Bloque:** 4 — CI/CD & GitOps

**Objetivo:** Instalar ArgoCD en un clúster local de Kubernetes y entender el flujo de GitOps.

---

## 📋 Prerequisitos

- Docker Desktop instalado y corriendo
- **Kubernetes habilitado en Docker Desktop**
  - Docker Desktop → Settings → Kubernetes → Enable Kubernetes
- `kubectl` instalado y configurado
- Acceso a terminal (bash/WSL)

**Verificar que Kubernetes está corriendo:**
```bash
kubectl cluster-info
kubectl get nodes
# Deberías ver: docker-desktop   Ready   control-plane
```

---

## 🎯 ¿Qué es ArgoCD?

ArgoCD es una herramienta de **Continuous Delivery** para Kubernetes que implementa **GitOps**:

- **Git como source of truth**: El estado deseado del cluster está en Git
- **Sync automático**: ArgoCD detecta cambios en Git y los aplica al cluster
- **Self-healing**: Si alguien modifica el cluster manualmente, ArgoCD lo revierte
- **Drift detection**: Alerta cuando el cluster no coincide con Git

---

## 🚀 Paso 1: Verificar Kubernetes

```bash
# Verificar que Kubernetes está corriendo
kubectl cluster-info

# Ver nodos
kubectl get nodes
# NAME             STATUS   ROLES           AGE   VERSION
# docker-desktop   Ready    control-plane   10d   v1.28.2

# Ver contexto actual
kubectl config current-context
# docker-desktop
```

---

## 🚀 Paso 2: Instalar ArgoCD

```bash
# Crear namespace
kubectl create namespace argocd

# Instalar ArgoCD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Esperar a que todos los pods estén Running
kubectl get pods -n argocd -w
```

---

## 🚀 Paso 3: Acceder a la UI

### 3.1 Obtener la contraseña inicial

```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d && echo
```

**Guarda esta contraseña** (está en `secrets.txt` - gitignored)

### 3.2 Port-forward para acceder

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

### 3.3 Abrir en navegador

Abre: https://localhost:8080

- **Usuario:** `admin`
- **Contraseña:** (la que obtuviste en 3.1)

---

## 🚀 Paso 4: Troubleshooting - ApplicationSet Controller

**⚠️ Problema común:** Si ves que el pod `argocd-applicationset-controller` está en `CrashLoopBackOff`:

```bash
kubectl get pods -n argocd | grep applicationset
# argocd-applicationset-controller-xxx   0/1     CrashLoopBackOff
```

**Causa:** Falta el CRD (Custom Resource Definition) de ApplicationSet.

**Solución:**
```bash
# Aplicar el CRD manualmente
kubectl apply -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/crds/applicationset-crd.yaml

# Verificar que el pod ahora está Running
kubectl get pods -n argocd | grep applicationset
# argocd-applicationset-controller-xxx   1/1     Running
```

---

## 🚀 Paso 5: Crear tu Primera Aplicación (GitOps)

### Opción A: Desde la UI

1. Haz clic en **"+ NEW APP"**
2. Llena los campos:
   - **Application Name:** `guestbook`
   - **Project:** `default`
   - **Sync Policy:** `Manual`
   - **Repository URL:** `https://github.com/argoproj/argocd-example-apps.git`
   - **Path:** `guestbook`
   - **Cluster URL:** `https://kubernetes.default.svc`
   - **Namespace:** `default`
3. Haz clic en **"CREATE"**
4. Haz clic en **"SYNC"** para desplegar

### Opción B: Desde CLI

```bash
# Instalar ArgoCD CLI (opcional)
# En WSL/Linux:
curl -sSL -o argocd-linux-amd64 https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
sudo install -m 555 argocd-linux-amd64 /usr/local/bin/argocd
rm argocd-linux-amd64

# Login
argocd login localhost:8080

# Crear aplicación
argocd app create guestbook \
  --repo https://github.com/argoproj/argocd-example-apps.git \
  --path guestbook \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace default

# Sync
argocd app sync guestbook
```

---

## 🚀 Paso 6: Verificar el Deployment

```bash
# Ver la aplicación en ArgoCD
kubectl get applications -n argocd

# Ver los recursos desplegados
kubectl get all -n default

# Acceder a la aplicación
kubectl port-forward svc/guestbook-ui 8081:80 -n default
# Abrir: http://localhost:8081
```

---

## 📚 Conceptos Clave de ArgoCD

### Application
Representa una aplicación desplegada. Contiene:
- **Source:** Repositorio Git + path
- **Destination:** Cluster + namespace
- **Sync Policy:** Manual o automático

### Project
Agrupa aplicaciones y define permisos/restricciones.

### Sync Policy
- **Manual:** Requiere click en "Sync"
- **Automated:** Sync automático cuando Git cambia
  - `prune: true` - Elimina recursos que ya no están en Git
  - `selfHeal: true` - Revierte cambios manuales

### Health Status
- **Healthy:** Todos los recursos están bien
- **Progressing:** Deployment en curso
- **Degraded:** Algo falló
- **Missing:** Recursos no encontrados

### Sync Status
- **Synced:** Cluster == Git
- **OutOfSync:** Cluster ≠ Git (hay drift)

---

## 🎤 Preguntas de Entrevista

### "¿Diferencia entre ArgoCD y kubectl apply en pipeline?"

**kubectl apply en pipeline:**
- Imperativo: el pipeline ejecuta el cambio
- No hay drift detection
- Rollback requiere re-ejecutar pipeline
- Cada cluster necesita su propio pipeline

**ArgoCD:**
- Declarativo: defines estado deseado en Git
- Drift detection y self-healing
- Rollback con `git revert`
- Un ArgoCD controla múltiples clusters
- Developers no necesitan `kubectl` access

### "¿Qué es GitOps?"

GitOps es una metodología donde:
1. **Git es la source of truth** del estado del sistema
2. **Todo cambio pasa por Git** (pull request, review, merge)
3. **Herramientas automatizan** la aplicación de cambios (ArgoCD, Flux)
4. **Drift se detecta y corrige** automáticamente

Ventajas:
- Auditoría completa (Git history)
- Rollback fácil (`git revert`)
- Disaster recovery (recrear desde Git)
- Seguridad (no acceso directo al cluster)

### "¿Qué es sync policy en ArgoCD?"

**Manual:**
- Requiere click en "Sync" en UI
- Útil para: producción, cambios críticos

**Automated:**
- Sync automático cuando Git cambia
- **prune:** Elimina recursos que ya no están en Git
- **selfHeal:** Revierte cambios manuales en el cluster

**Sync options:**
- `CreateNamespace`: Crea namespace si no existe
- `PruneLast`: Elimina recursos al final (evita downtime)
- `RespectIgnoreDifferences`: Ignora campos específicos

### "¿Has tenido que hacer troubleshooting de ArgoCD?"

**Ejemplo real:**
> "Sí, cuando instalé ArgoCD localmente, el `argocd-applicationset-controller` estaba en CrashLoopBackOff. Revisé los logs con `kubectl logs` y vi que faltaba el CRD de ApplicationSet. Lo resolví aplicando el CRD manualmente desde el repositorio oficial de ArgoCD. Después de eso, el controller arrancó correctamente y pude usar ApplicationSets para desplegar múltiples aplicaciones automáticamente."

**Comandos de troubleshooting:**
```bash
# Ver estado de pods
kubectl get pods -n argocd

# Ver logs de un pod específico
kubectl logs -n argocd <pod-name>

# Describir una aplicación
kubectl describe application <app-name> -n argocd

# Ver eventos
kubectl get events -n argocd --sort-by='.lastTimestamp'
```

---

## 🔧 Troubleshooting

### 🎯 Cómo diagnosticar problemas en ArgoCD

Este es el proceso real que seguimos para encontrar y resolver el problema del ApplicationSet controller.

---

### Paso 1: Identificar el problema

**Comando:**
```bash
kubectl get pods -n argocd
```

**Salida:**
```
NAME                                                READY   STATUS             RESTARTS          AGE
argocd-application-controller-0                     1/1     Running            3 (8h ago)        2d23h
argocd-applicationset-controller-7878b5cc9f-2rxm4   0/1     CrashLoopBackOff   352 (2m44s ago)   2d23h
argocd-dex-server-6d56c88bff-lt4vw                  1/1     Running            3 (8h ago)        2d23h
argocd-notifications-controller-96f4f8cb8-6655n     1/1     Running            3 (8h ago)        2d23h
argocd-redis-68d75786ff-txjp7                       1/1     Running            3 (8h ago)        2d23h
argocd-repo-server-7d56cbd8bf-fk6zp                 1/1     Running            3 (8h ago)        2d23h
argocd-server-6995db97f-kjqb2                       1/1     Running            3 (8h ago)        2d23h
```

**¿Qué vemos?**
- ❌ `argocd-applicationset-controller`: `0/1 CrashLoopBackOff`
- ❌ `352 restarts` en 2 días 23 horas
- ✅ Todos los demás pods: `Running`

**Interpretación:**
- `0/1` = 0 containers ready de 1 total
- `CrashLoopBackOff` = El pod arranca → crashea → Kubernetes espera → reinicia → crashea otra vez (loop infinito)
- `352 restarts` = Ha intentado arrancar 352 veces sin éxito

---

### Paso 2: Ver los logs del pod crasheando

**Comando:**
```bash
kubectl logs -n argocd argocd-applicationset-controller-7878b5cc9f-2rxm4 --tail=50
```

**Logs clave (simplificados):**
```json
{"level":"info","msg":"ArgoCD ApplicationSet Controller is starting"}
{"level":"info","msg":"Starting manager"}
{"level":"info","msg":"Starting EventSource","source":"kind source: *v1alpha1.ApplicationSet"}

{"error":"failed to get restmapping: no matches for kind \"ApplicationSet\" in version \"argoproj.io/v1alpha1\"",
 "level":"error",
 "msg":"if kind is a CRD, it should be installed before calling Start"}

{"error":"failed to wait for applicationset caches to sync: timed out waiting for cache to be synced",
 "level":"error"}

{"level":"info","msg":"Stopping and waiting for caches"}
{"level":"error","msg":"problem running manager"}
```

**¿Qué nos dicen los logs?**
1. El controller arranca correctamente
2. Intenta buscar recursos de tipo `ApplicationSet`
3. **Error:** `no matches for kind "ApplicationSet"`
4. **Sugerencia:** `if kind is a CRD, it should be installed before calling Start`
5. El controller no puede continuar y se detiene

---

### Paso 3: Entender el problema

**¿Qué es un CRD (Custom Resource Definition)?**

Kubernetes tiene recursos nativos:
- Pod, Deployment, Service, ConfigMap, etc.

ArgoCD necesita recursos custom:
- Application, ApplicationSet, AppProject

**El CRD le dice a Kubernetes:**
> "Oye, ahora también vas a entender un recurso llamado `ApplicationSet`. Aquí está su definición (schema, campos, validaciones)."

**Sin el CRD:**
```
Controller: "Dame todos los ApplicationSets"
Kubernetes: "¿ApplicationSet? No sé qué es eso" ❌
Controller: *crashea*
```

**Con el CRD:**
```
Controller: "Dame todos los ApplicationSets"
Kubernetes: "Ah sí, ApplicationSet. Aquí están: []" ✅
Controller: *funciona*
```

---

### Paso 4: Verificar si el CRD existe

**Comando:**
```bash
kubectl get crd | grep applicationset
```

**Si no aparece nada:** El CRD no está instalado ❌

**Si aparece:**
```
applicationsets.argoproj.io   2024-05-05T10:30:00Z
```
El CRD SÍ está instalado ✅

---

### Paso 5: Entender la arquitectura de ArgoCD (Stateful vs Stateless)

**Ver todos los recursos:**
```bash
kubectl get all -n argocd
```

**Arquitectura:**

| Componente | Tipo | Stateful/Stateless | Por qué |
|---|---|---|---|
| `argocd-server` | Deployment | Stateless | UI/API, no guarda estado |
| `argocd-repo-server` | Deployment | Stateless | Clona repos, cache temporal |
| `argocd-applicationset-controller` | Deployment | Stateless | Genera Applications, sin estado |
| `argocd-dex-server` | Deployment | Stateless | OAuth/SSO, sin estado |
| `argocd-notifications-controller` | Deployment | Stateless | Envía notificaciones |
| `argocd-redis` | Deployment | Stateless* | Cache en memoria (no crítico) |
| `argocd-application-controller-0` | **StatefulSet** | **Stateful** | Reconciliation loop, mantiene estado |

**¿Por qué `application-controller` es StatefulSet?**
- Mantiene el estado de sync de cada Application
- Solo debe haber 1 controller activo (leader election)
- Identidad única: `argocd-application-controller-0`
- Si hay 2 controllers, habría conflictos (sync duplicado)

**¿Por qué los demás son Deployments?**
- No mantienen estado persistente
- Pods intercambiables
- Pueden escalar horizontalmente sin problemas

---

### Paso 6: Aplicar el fix

**Opción 1: Aplicar el CRD con --server-side (RECOMENDADO)**

```bash
kubectl apply -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/crds/applicationset-crd.yaml --server-side
```

**¿Por qué `--server-side`?**
- El CRD es muy grande (>262KB de annotations)
- Sin `--server-side`: Error "metadata.annotations: Too long"
- Con `--server-side`: Kubernetes procesa el CRD en el servidor, evitando el límite

**Nota sobre la URL `raw.githubusercontent.com`:**
- Usamos la versión `raw` para obtener únicamente el contenido YAML puro.
- Si usáramos la URL estándar de GitHub, `kubectl` intentaría procesar el código HTML de la página web y fallaría.

**¿Por qué reiniciar el deployment?**
- Después de aplicar el CRD, el pod puede estar en un periodo de espera largo (`Backoff`).
- Ejecutamos `kubectl rollout restart` para forzar un inicio inmediato y que el controlador detecte el nuevo CRD sin esperar al siguiente ciclo de reintento de Kubernetes.

**Opción 2: Reinstalar ArgoCD completo**

```bash
kubectl delete namespace argocd
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

**Ventaja:** Instala TODO correctamente (CRDs + controllers)
**Desventaja:** Pierdes configuraciones y aplicaciones existentes

---

### Paso 7: Verificar que el fix funcionó

**Comando:**
```bash
kubectl get pods -n argocd | grep applicationset
```

**Resultado esperado:**
```
argocd-applicationset-controller-xxx   1/1   Running   0   30s
```

**Verificar logs (opcional):**
```bash
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-applicationset-controller --tail=20
```

**Logs esperados:**
```json
{"level":"info","msg":"ArgoCD ApplicationSet Controller is starting"}
{"level":"info","msg":"Starting manager"}
{"level":"info","msg":"Starting EventSource","source":"kind source: *v1alpha1.ApplicationSet"}
{"level":"info","msg":"Starting workers","controller":"applicationset"}
```

Sin errores de "no matches for kind" ✅

---

### 🎯 Impacto del Fix: ¿Por qué era crítico?

**Antes del fix (Estado fallido):**
- **Funcionalidad limitada:** Solo podías crear recursos de tipo `Application` (individuales).
- **Fallo de automatización:** Si intentabas desplegar un `ApplicationSet`, Kubernetes rechazaba el archivo porque no conocía el recurso (`no matches for kind`).
- **Controlador muerto:** El "cerebro" encargado de la automatización de flujos complejos estaba en `CrashLoopBackOff`, por lo que ArgoCD no podía auto-generar aplicaciones basadas en plantillas.

**Después del fix (Estado óptimo):**
- **Full GitOps Automation:** Ahora puedes usar **Generadores** (Git, List, Cluster) para desplegar múltiples aplicaciones automáticamente.
- **Escalabilidad:** Si añades una nueva aplicación al repositorio de Git, el controlador (ahora activo) la detectará y creará el recurso `Application` correspondiente sin intervención manual.
- **Salud del Cluster:** Hemos eliminado el ruido de alertas y el consumo innecesario de recursos causado por el bucle de reinicios del pod.

---

### 🎯 Resumen del proceso de troubleshooting:

```
1. kubectl get pods -n argocd
   → Identificamos: CrashLoopBackOff con 352 restarts

2. kubectl logs -n argocd <pod-name>
   → Vimos error: "no matches for kind ApplicationSet"
   → Vimos sugerencia: "if kind is a CRD, it should be installed"

3. Entendimos el problema:
   → Falta el CRD de ApplicationSet
   → El controller no puede buscar recursos que Kubernetes no conoce

4. kubectl get crd | grep applicationset
   → Confirmamos: El CRD no existe

5. kubectl apply -f <crd-url> --server-side
   → Aplicamos el CRD con server-side (evita límite de annotations)

6. kubectl get pods -n argocd
   → Verificamos: Pod ahora en Running (no más crashes)
```

---

### 📚 Comandos útiles de troubleshooting:

```bash
# Ver estado de todos los pods
kubectl get pods -n argocd

# Ver logs de un pod específico
kubectl logs -n argocd <pod-name>

# Ver logs de un pod que está crasheando (logs anteriores)
kubectl logs -n argocd <pod-name> --previous

# Ver eventos del namespace
kubectl get events -n argocd --sort-by='.lastTimestamp'

# Describir un pod (ver eventos y estado)
kubectl describe pod -n argocd <pod-name>

# Ver todos los CRDs instalados
kubectl get crd

# Ver CRDs de ArgoCD específicamente
kubectl get crd | grep argoproj

# Ver definición completa de un CRD
kubectl get crd applicationsets.argoproj.io -o yaml

# Ver logs de todos los pods de un componente
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-applicationset-controller --tail=50

# Ver recursos de ArgoCD
kubectl get all -n argocd
```

---

### Problema 0: ¿Usamos kind o Docker Desktop Kubernetes?

**En este lab usamos:** Docker Desktop Kubernetes ✅

**¿Por qué Docker Desktop?**
- Más simple para empezar (viene con Docker Desktop)
- No requiere instalación adicional
- Suficiente para desarrollo local

**Alternativa: kind (Kubernetes IN Docker)**
- Más ligero y aislado
- Mejor para múltiples clusters
- Fácil de crear y destruir

**Si quieres usar kind:**
```bash
# Instalar kind
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# Crear cluster
kind create cluster --name argocd-lab

# Cambiar contexto
kubectl config use-context kind-argocd-lab

# Cuando termines
kind delete cluster --name argocd-lab
```

---

### Problema 1: ApplicationSet Controller en CrashLoopBackOff

**Síntoma:**
```bash
kubectl get pods -n argocd | grep applicationset
# argocd-applicationset-controller-xxx   0/1     CrashLoopBackOff
```

**Causa:** Falta el CRD de ApplicationSet.

**Solución:**
```bash
kubectl apply -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/crds/applicationset-crd.yaml
kubectl get pods -n argocd | grep applicationset  # Debe estar Running
```

---

### Problema 2: No puedo acceder a la UI

**Síntoma:** "This site can't be reached" o "Connection refused" al abrir `https://localhost:8080`

**Causas posibles:**

**Causa 1: Port-forward no está corriendo**

```bash
# Verificar si está corriendo
ps aux | grep "port-forward" | grep -v grep

# Si no aparece nada, iniciarlo
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Dejar corriendo en esa terminal (no cerrar)
```

**Causa 2: Estás usando HTTP en vez de HTTPS**

❌ **Incorrecto:** `http://localhost:8080`  
✅ **Correcto:** `https://localhost:8080`

ArgoCD usa HTTPS por defecto. El navegador mostrará advertencia de certificado (es normal).

**Causa 3: Puerto 8080 ocupado**

```bash
# Verificar qué está usando el puerto 8080
lsof -i :8080

# Usar otro puerto
kubectl port-forward svc/argocd-server -n argocd 8081:443
# Luego acceder a https://localhost:8081
```

**Causa 4: El servicio argocd-server no existe**

```bash
# Verificar que el servicio existe
kubectl get svc argocd-server -n argocd

# Si no existe, ArgoCD no está instalado correctamente
```

---

### Problema 3: "x509: certificate signed by unknown authority"

**Síntoma:** Error de certificado en el navegador.

**Causa:** ArgoCD usa certificado self-signed por defecto.

**Solución:**
- En el navegador, hacer clic en "Advanced" → "Proceed to localhost (unsafe)"
- O usar `--insecure` en ArgoCD CLI:
  ```bash
  argocd login localhost:8080 --insecure
  ```

---

### Problema 4: Application queda en "OutOfSync" permanentemente

**Síntoma:** La aplicación no sincroniza aunque hagas clic en "Sync".

**Causa:** Puede haber recursos que ArgoCD no puede aplicar (permisos, CRDs faltantes, etc.)

**Solución:**
```bash
# Ver detalles del error
kubectl describe application <app-name> -n argocd

# Ver logs del application-controller
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-application-controller --tail=100

# Forzar sync con prune
argocd app sync <app-name> --prune
```

---

### Problema 5: Olvidé la contraseña de admin

**Solución:**
```bash
# Obtener la contraseña inicial nuevamente
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d && echo

# O resetear la contraseña
kubectl -n argocd patch secret argocd-secret \
  -p '{"stringData": {"admin.password": "'$(htpasswd -bnBC 10 "" <new-password> | tr -d ':\n')'"}}'
```

---

## 🧹 Limpieza

### Opción 1: Pausar ArgoCD (sin eliminar) - RECOMENDADO

**Útil para ahorrar recursos cuando no lo uses:**

```bash
# Pausar (escalar a 0 replicas)
kubectl scale deployment -n argocd --all --replicas=0
kubectl scale statefulset argocd-application-controller -n argocd --replicas=0

# Verificar que todos los pods se detuvieron
kubectl get pods -n argocd
# No debería haber pods corriendo
```

**¿Por qué comandos separados?**
- `deployment` y `statefulset` son tipos de recursos diferentes
- `--all` solo afecta recursos del mismo tipo
- ArgoCD tiene 6 Deployments (stateless) y 1 StatefulSet (stateful)

**Retomar ArgoCD:**
```bash
# Escalar de vuelta a 1 replica
kubectl scale deployment -n argocd --all --replicas=1
kubectl scale statefulset argocd-application-controller -n argocd --replicas=1

# Esperar a que arranquen
kubectl get pods -n argocd -w

# Cuando estén Running (Ctrl+C para salir del watch)
# Hacer port-forward
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

**🎯 Conexión con Deployment vs StatefulSet:**

Cuando escalas de vuelta a 1:
- **Deployments** crean pods con **nombres nuevos** (random):
  ```
  Antes:  argocd-server-6995db97f-kjqb2
  Después: argocd-server-6995db97f-xyz12  ← Nombre diferente
  ```
- **StatefulSet** recrea el pod con el **mismo nombre** (identidad persistente):
  ```
  Antes:  argocd-application-controller-0
  Después: argocd-application-controller-0  ← MISMO nombre
  ```

Esto demuestra la diferencia clave: **Deployments = pods intercambiables, StatefulSet = identidad persistente**.

---

### Opción 2: Eliminar ArgoCD completamente

```bash
# Eliminar aplicaciones primero (opcional)
kubectl delete application guestbook -n argocd

# Eliminar ArgoCD
kubectl delete namespace argocd

# Detener port-forward (si está corriendo)
pkill -f "port-forward.*argocd"
```

**⚠️ Advertencia:** Esto elimina TODO (pods, configuración, aplicaciones, secrets).

**Para reinstalar:**
```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Aplicar el CRD (evita el crash del ApplicationSet controller)
kubectl apply -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/crds/applicationset-crd.yaml --server-side

# Obtener nueva contraseña
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d && echo
```

---

### Opción 3: Solo cerrar el acceso a la UI

```bash
# Detener port-forward (ArgoCD sigue corriendo)
pkill -f "port-forward.*argocd"

# O si tienes el PID
ps aux | grep "port-forward" | grep argocd
kill <PID>
```

**Para retomar:**
```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
# Abrir: https://localhost:8080
```

---

## 📝 Archivos en este Lab

| Archivo | Descripción |
|---------|-------------|
| `README.md` | Este archivo - guía completa del lab |
| `secrets.txt` | Credenciales de ArgoCD (gitignored) |

---

## 🔗 Recursos

- [ArgoCD Official Docs](https://argo-cd.readthedocs.io/)
- [ArgoCD Getting Started](https://argo-cd.readthedocs.io/en/stable/getting_started/)
- [GitOps Principles](https://opengitops.dev/)
- [ArgoCD Example Apps](https://github.com/argoproj/argocd-example-apps)

---

## 🎯 Para la Entrevista con J&J

Este lab te permite:
- ✅ Demostrar que has usado ArgoCD hands-on
- ✅ Explicar el flujo de GitOps con confianza
- ✅ Mostrar que entiendes la diferencia entre kubectl apply vs ArgoCD sync
- ✅ Hablar de Application, Project, Sync Policy con conocimiento práctico

**Puntos clave a mencionar:**
1. "He instalado ArgoCD localmente y desplegado aplicaciones de ejemplo"
2. "Entiendo el concepto de GitOps: Git como source of truth"
3. "Conozco las ventajas: drift detection, self-healing, auditoría"
4. "Sé configurar sync policies (manual vs automated, prune, selfHeal)"

---

---

### ✅ Conclusión y Estado Final del Laboratorio

Tras el proceso de troubleshooting documentado arriba, el entorno ha quedado validado y estable:

1.  **Fix Técnico Realizado:** Se aplicó el CRD de `ApplicationSet` utilizando `--server-side` para manejar el tamaño del manifiesto y se ejecutó un `rollout restart` para forzar la detección inmediata del nuevo recurso.
2.  **Estabilidad Confirmada:** Todos los pods en el namespace `argocd` se encuentran en estado `Running`. El controlador de automatización (`applicationset-controller`) está operativo y sin reinicios tras el fix.
3.  **Documentación de Valor:** Se incluyeron notas técnicas sobre el uso de URLs `raw` y la importancia del `server-side apply`, lo cual es material clave para explicar en una entrevista técnica.
4.  **Capacidad Operativa:** El laboratorio ahora soporta flujos de GitOps avanzados (Generadores, ApplicationSets y escalabilidad automática).

---

> 🏷️ Tags: `argocd` `gitops` `kubernetes` `ci-cd` `continuous-delivery`
