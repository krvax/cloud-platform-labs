# Kubernetes: Deployment, ReplicaSet y Replicas

> Guía simple y clara para entender estos 3 conceptos fundamentales

---

## 🎯 Los 3 Conceptos en 30 Segundos

```
REPLICAS     = Número de copias idénticas de un pod que quieres corriendo
               Ejemplo: replicas: 3 → quiero 3 pods idénticos

REPLICASET   = Controlador que mantiene ese número de replicas
               Si un pod muere, crea uno nuevo automáticamente

DEPLOYMENT   = Abstracción de alto nivel que maneja ReplicaSets
               Maneja actualizaciones, rollbacks, y cambios sin downtime
```

---

## 📊 La Jerarquía

```
┌─────────────────────────────────────────────────┐
│ DEPLOYMENT (lo que tú creas)                    │
│ "Quiero 3 replicas de nginx:1.25"              │
└────────────────┬────────────────────────────────┘
                 │ crea y maneja
                 ↓
┌─────────────────────────────────────────────────┐
│ REPLICASET (creado automáticamente)             │
│ "Voy a asegurar que haya 3 pods corriendo"     │
└────────────────┬────────────────────────────────┘
                 │ crea y monitorea
                 ↓
         ┌───────┴───────┐
         ↓       ↓       ↓
    ┌────────┐ ┌────────┐ ┌────────┐
    │ Pod 1  │ │ Pod 2  │ │ Pod 3  │  ← 3 REPLICAS
    │nginx   │ │nginx   │ │nginx   │
    └────────┘ └────────┘ └────────┘
```

---

## 1️⃣ REPLICAS

### ¿Qué son?

**Replicas** son copias idénticas de un pod corriendo al mismo tiempo.

```yaml
spec:
  replicas: 3  # Kubernetes mantiene 3 pods idénticos corriendo
```

### ¿Para qué sirven?

#### **Alta Disponibilidad (High Availability)**
```
1 replica:  Si el pod muere → aplicación caída ❌
3 replicas: Si 1 pod muere → los otros 2 siguen funcionando ✅
```

#### **Balanceo de Carga (Load Balancing)**
```
1 replica:  Todo el tráfico va a 1 pod (puede saturarse)
3 replicas: El tráfico se distribuye entre 3 pods
```

#### **Escalabilidad (Scaling)**
```
Poco tráfico  → replicas: 2
Mucho tráfico → replicas: 10
```

### Ejemplo Visual

```
replicas: 1          replicas: 3              replicas: 5
┌─────────┐         ┌─────────┐              ┌─────────┐
│  Pod 1  │         │  Pod 1  │              │  Pod 1  │
└─────────┘         ├─────────┤              ├─────────┤
                    │  Pod 2  │              │  Pod 2  │
                    ├─────────┤              ├─────────┤
                    │  Pod 3  │              │  Pod 3  │
                    └─────────┘              ├─────────┤
                                             │  Pod 4  │
                                             ├─────────┤
                                             │  Pod 5  │
                                             └─────────┘
```

---

## 2️⃣ REPLICASET

### ¿Qué es?

**ReplicaSet** es un controlador de bajo nivel que asegura que un número específico de replicas de un pod estén corriendo en todo momento.

### ¿Qué hace?

1. **Monitorea** constantemente cuántos pods están corriendo
2. **Compara** con el número deseado de replicas
3. **Actúa** si hay diferencia:
   - Si faltan pods → crea nuevos
   - Si sobran pods → elimina los extras

### Ejemplo de Comportamiento

```
Estado deseado: 3 replicas
Estado actual:  3 pods corriendo
ReplicaSet:     ✅ Todo bien, no hago nada

Estado actual:  2 pods corriendo (1 se cayó)
ReplicaSet:     ⚠️ Faltan pods, creo 1 nuevo
                ✅ Ahora hay 3 pods de nuevo

Estado actual:  4 pods corriendo (alguien creó uno extra)
ReplicaSet:     ⚠️ Sobran pods, elimino 1
                ✅ Ahora hay 3 pods de nuevo
```

### ¿Cuándo lo usas directamente?

**Casi nunca.** En producción, siempre usas Deployments en lugar de ReplicaSets directos.

```yaml
# ❌ Casi nunca haces esto (ReplicaSet directo):
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: nginx-rs
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    spec:
      containers:
      - name: nginx
        image: nginx:1.25
```

**Problema:** Si quieres actualizar la imagen de nginx:1.25 a nginx:1.26, tienes que:
1. Eliminar el ReplicaSet manualmente
2. Crear uno nuevo con la nueva imagen
3. Resultado: **downtime** mientras se recrean los pods

---

## 3️⃣ DEPLOYMENT

### ¿Qué es?

**Deployment** es una abstracción de alto nivel que maneja ReplicaSets automáticamente y proporciona funcionalidades avanzadas.

### ¿Qué hace?

1. **Crea y maneja ReplicaSets** por ti
2. **Rolling updates** - actualiza pods gradualmente sin downtime
3. **Rollback** - revierte a versiones anteriores si algo falla
4. **Historial** - mantiene versiones anteriores de ReplicaSets
5. **Declarativo** - describes el estado deseado, Kubernetes lo hace realidad

### Ejemplo Completo

```yaml
# ✅ Siempre haces esto (Deployment):
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.25
        ports:
        - containerPort: 80
```

### ¿Qué pasa cuando lo aplicas?

```bash
kubectl apply -f nginx-deployment.yaml
```

**Paso a paso:**

```
1. Kubernetes crea el Deployment "nginx-deployment"
   
2. El Deployment crea un ReplicaSet automáticamente
   Nombre: nginx-deployment-abc123 (hash generado)
   
3. El ReplicaSet crea 3 pods
   Nombres: 
   - nginx-deployment-abc123-pod1
   - nginx-deployment-abc123-pod2
   - nginx-deployment-abc123-pod3
   
4. Resultado: 3 pods de nginx:1.25 corriendo
```

### Rolling Update (Sin Downtime)

**Escenario:** Quieres actualizar de nginx:1.25 a nginx:1.26

```bash
kubectl set image deployment/nginx-deployment nginx=nginx:1.26
```

**¿Qué pasa internamente?**

```
Estado inicial:
ReplicaSet-v1 (nginx:1.25): 3 pods corriendo
ReplicaSet-v2 (nginx:1.26): 0 pods

Paso 1:
ReplicaSet-v1: 3 pods
ReplicaSet-v2: 1 pod nuevo ← crea 1 pod con nueva versión

Paso 2:
ReplicaSet-v1: 2 pods ← elimina 1 pod viejo
ReplicaSet-v2: 2 pods ← crea 1 pod más

Paso 3:
ReplicaSet-v1: 1 pod
ReplicaSet-v2: 3 pods

Paso 4:
ReplicaSet-v1: 0 pods ← elimina último pod viejo
ReplicaSet-v2: 3 pods ← todos con nueva versión

Resultado: Actualización completa sin downtime ✅
```

### Rollback (Si Algo Sale Mal)

```bash
# Ver historial de versiones
kubectl rollout history deployment/nginx-deployment

# Regresar a la versión anterior
kubectl rollout undo deployment/nginx-deployment

# Regresar a una versión específica
kubectl rollout undo deployment/nginx-deployment --to-revision=2
```

---

## 🔄 Comparación Directa

| Característica | ReplicaSet | Deployment |
|----------------|------------|------------|
| Mantiene replicas | ✅ Sí | ✅ Sí (vía ReplicaSet) |
| Rolling updates | ❌ No | ✅ Sí |
| Rollback | ❌ No | ✅ Sí |
| Historial de versiones | ❌ No | ✅ Sí |
| Actualizaciones declarativas | ❌ No | ✅ Sí |
| **Uso en producción** | ❌ Casi nunca | ✅ Siempre |

---

## 📝 Ejemplo Real: Tu Lab

```yaml
# labs/lab-04-eks-cluster/k8s/nginx-deployment.yaml
apiVersion: apps/v1
kind: Deployment                    # ← DEPLOYMENT
metadata:
  name: nginx-deployment
spec:
  replicas: 2                       # ← REPLICAS (quieres 2 copias)
  selector:
    matchLabels:
      app: nginx
  template:                         # ← Template del pod
    metadata:
      labels:
        app: nginx
    spec:
      containers:
        - name: nginx
          image: nginx:1.25.3       # ← Versión específica
          ports:
            - containerPort: 80
```

**¿Qué pasa cuando aplicas este archivo?**

```
1. kubectl apply -f nginx-deployment.yaml

2. Kubernetes crea Deployment "nginx-deployment"

3. Deployment crea ReplicaSet "nginx-deployment-xyz789"

4. ReplicaSet crea 2 pods:
   - nginx-deployment-xyz789-abc
   - nginx-deployment-xyz789-def

5. Resultado: 2 copias de nginx:1.25.3 corriendo
```

**Si un pod muere:**

```
ReplicaSet detecta: "Solo hay 1 pod, necesito 2"
ReplicaSet crea: 1 pod nuevo
Resultado: Siempre 2 pods corriendo
```

---

## 🎯 Scaling: Cambiar el Número de Replicas

### Manual

```bash
# Ver estado actual
kubectl get deployment nginx-deployment

# Escalar a 5 replicas
kubectl scale deployment nginx-deployment --replicas=5

# Escalar a 2 replicas
kubectl scale deployment nginx-deployment --replicas=2
```

### Automático (HPA - Horizontal Pod Autoscaler)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: nginx-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nginx-deployment
  minReplicas: 2    # Mínimo 2 pods
  maxReplicas: 10   # Máximo 10 pods
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70  # Si CPU > 70%, escala hacia arriba
```

**Comportamiento:**

```
CPU < 70%: Mantiene 2 replicas (mínimo)
CPU > 70%: Escala gradualmente hasta 10 replicas
CPU baja:  Reduce replicas gradualmente hasta 2
```

---

## 🎤 Respuestas para la Entrevista

### "¿Qué son las replicas?"

> "**Replicas** are identical copies of a pod running at the same time. If you set `replicas: 3`, Kubernetes creates and maintains 3 identical pods. This provides high availability—if one pod crashes, the others keep serving traffic—and load balancing, since traffic is distributed across multiple pods."

### "¿Qué es un ReplicaSet?"

> "A **ReplicaSet** is a low-level controller that ensures a specific number of pod replicas are running at any time. It constantly monitors the pods and if one crashes, it automatically creates a new one to maintain the desired count. However, in production, we don't create ReplicaSets directly—we use Deployments instead."

### "¿Qué es un Deployment?"

> "A **Deployment** is a higher-level abstraction that manages ReplicaSets automatically. It provides declarative updates, rolling updates without downtime, and rollback capabilities. When you create a Deployment, it creates a ReplicaSet, which creates the pods. If you update the image, the Deployment creates a new ReplicaSet and gradually shifts traffic from the old version to the new one, ensuring zero downtime."

### "¿Cuál es la diferencia entre ReplicaSet y Deployment?"

> "A **ReplicaSet** only maintains the desired number of replicas—if you want to update the image, you have to delete the ReplicaSet and create a new one manually, causing downtime.
>
> A **Deployment** manages ReplicaSets and handles updates intelligently. It creates a new ReplicaSet with the new version and gradually shifts traffic using a rolling update strategy, ensuring zero downtime. It also keeps a history of ReplicaSets so you can rollback if something goes wrong.
>
> In practice, you always create Deployments, not ReplicaSets directly, because Deployments give you update management and rollback for free."

### "¿Cuándo usarías un ReplicaSet directamente?"

> "Honestly, in production, I can't think of a good reason to use a ReplicaSet directly. Deployments provide everything a ReplicaSet does, plus update management and rollback capabilities. The only scenario might be very advanced custom controllers, but even then, you'd probably build on top of Deployments. The Kubernetes documentation itself recommends using Deployments instead of ReplicaSets directly."

---

## ✅ Resumen Final

### Lo que necesitas recordar:

```
1. REPLICAS = Número de copias (3 replicas = 3 pods idénticos)

2. REPLICASET = Mantiene ese número automáticamente
   - Si un pod muere, crea uno nuevo
   - Casi nunca lo usas directamente

3. DEPLOYMENT = Lo que siempre usas en producción
   - Crea y maneja ReplicaSets automáticamente
   - Rolling updates sin downtime
   - Rollback si algo falla
   - Historial de versiones

4. FLUJO: Deployment → crea → ReplicaSet → crea → Pods (replicas)

5. EN PRÁCTICA: Tú solo creas Deployments, Kubernetes hace el resto
```

### Comandos útiles:

```bash
# Ver deployments
kubectl get deployments

# Ver replicasets (creados automáticamente)
kubectl get replicasets

# Ver pods
kubectl get pods

# Escalar
kubectl scale deployment nginx-deployment --replicas=5

# Actualizar imagen
kubectl set image deployment/nginx-deployment nginx=nginx:1.26

# Ver historial
kubectl rollout history deployment/nginx-deployment

# Rollback
kubectl rollout undo deployment/nginx-deployment

# Ver estado de un rollout
kubectl rollout status deployment/nginx-deployment
```

---

**Última actualización:** 2026-04-15
