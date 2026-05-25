# Entendiendo Ingress, ALB y Target Groups en EKS

> 📚 Documento de referencia para los labs de Kubernetes en AWS EKS.

## Tabla de contenidos

- [Analogía general](#analogía-general)
- [Componentes clave](#componentes-clave)
  - [Pod](#1--pod)
  - [Service](#2--service)
  - [Ingress](#3--ingress)
  - [Ingress Controller](#4--ingress-controller)
- [ALB y Target Groups](#alb-y-target-groups)
- [Flujo completo](#flujo-completo)
- [Errores comunes](#errores-comunes)
- [Comandos de diagnóstico](#comandos-de-diagnóstico)
- [Referencias](#referencias)

---

## Analogía general

Imagina que tu cluster de EKS es un **edificio de oficinas**:

```text
🌐 Internet (usuarios)
       │
       ▼
   🚪 INGRESS        ← La recepción del edificio
       │                 (decide a qué oficina te manda)
       ▼
   🔀 SERVICE         ← El directorio de pisos
       │                 (sabe dónde está cada equipo)
       ▼
   📦 PODS            ← Las oficinas donde se trabaja
                         (tu app corriendo)
```

---

## Componentes clave

### 1. 📦 Pod

Es la unidad mínima en Kubernetes. Tu contenedor corre dentro de un Pod.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: mi-app
spec:
  containers:
    - name: mi-app
      image: mi-imagen:latest
      ports:
        - containerPort: 3080
```

> ⚠️ El Pod por sí solo **no es accesible** desde fuera del cluster.

---

### 2. 🔀 Service

Expone los Pods internamente dentro del cluster. Funciona como un DNS interno.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: mi-app-service
spec:
  selector:
    app: mi-app
  ports:
    - port: 80
      targetPort: 3080
  type: ClusterIP
```

**Tipos de Service:**

| Tipo | Accesibilidad |
|------|--------------|
| `ClusterIP` | Solo dentro del cluster |
| `NodePort` | Expone un puerto en cada nodo |
| `LoadBalancer` | Crea un LB externo (costoso, uno por servicio) |

> 💡 Con `ClusterIP` otros servicios internos pueden comunicarse,
> pero **sigue sin ser accesible desde internet**.

---

### 3. 🚪 Ingress

Recurso de Kubernetes que define **reglas de enrutamiento** para
tráfico externo hacia los Services internos.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: mi-app-ingress
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/healthcheck-path: /
spec:
  rules:
    - host: app.midominio.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: mi-app-service
                port:
                  number: 80
```

**Annotations importantes para AWS ALB:**

| Annotation | Descripción |
|-----------|-------------|
| `kubernetes.io/ingress.class: alb` | Usa el ALB como ingress controller |
| `alb.ingress.kubernetes.io/scheme` | `internet-facing` o `internal` |
| `alb.ingress.kubernetes.io/target-type` | `ip` (directo a pod) o `instance` (al nodo) |
| `alb.ingress.kubernetes.io/healthcheck-path` | Ruta para verificar salud del pod |
| `alb.ingress.kubernetes.io/certificate-arn` | ARN del certificado SSL en ACM |

> ⚠️ El Ingress **solo define reglas**. Por sí solo no hace nada.
> Necesita un **Ingress Controller** que las ejecute.

---

### 4. 🎛️ Ingress Controller

Es el componente que **lee las reglas del Ingress** y crea
la infraestructura real.

En AWS EKS se usa el **AWS Load Balancer Controller**:

```text
Ingress YAML (reglas)
    │
    ▼
AWS Load Balancer Controller
    │
    ├──→ Crea un ALB en AWS
    ├──→ Crea Target Groups
    ├──→ Configura listeners y reglas
    └──→ Registra Pods/IPs como targets
```

**Instalación con Helm:**

```bash
helm repo add eks https://aws.github.io/eks-charts
helm repo update

helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=<NOMBRE_CLUSTER> \
  --set serviceAccount.create=false \
  --set serviceAccount.name=aws-load-balancer-controller

# Verificar
kubectl get deployment -n kube-system aws-load-balancer-controller
```

> 🔑 **Prerequisito:** El controller necesita un IAM Role con permisos
> para crear ALBs, Target Groups, etc.

---

## ALB y Target Groups

### ¿Qué es el ALB?

**Application Load Balancer** — Balanceador de carga de AWS.

```text
🌐 Usuario → app.midominio.com
        │
        ▼
┌──────────────────┐
│       ALB        │
│  (Capa 7 - HTTP) │
│                  │
│  Listeners:      │
│  :80  → reglas   │
│  :443 → reglas   │
└────────┬─────────┘
         │
         ▼
   Target Groups
```

**Características:**
- Opera en **capa 7** (HTTP/HTTPS)
- Entiende URLs, headers, paths
- Puede enrutar por path: `/api` → backend, `/` → frontend
- Soporta SSL/TLS termination
- Lo crea **automáticamente** el AWS LB Controller

### ¿Qué es un Target Group?

Es la **lista de destinos** donde el ALB envía el tráfico.

```text
┌────────────────────────┐
│     Target Group       │
│                        │
│  Pod 1: ✅ healthy     │  ← Recibe tráfico
│  Pod 2: ✅ healthy     │  ← Recibe tráfico
│  Pod 3: ❌ unhealthy   │  ← NO recibe tráfico
│                        │
│  Health Check:         │
│  GET / → 200 OK       │
└────────────────────────┘
```

---

## Flujo completo

```text
helm install mi-app ./chart
        │
        ├── Crea Deployment → Pods (app corriendo)
        ├── Crea Service (expone pods internamente)
        └── Crea Ingress (reglas de enrutamiento)
                │
                ▼
    AWS LB Controller (detecta el Ingress)
                │
                ├── Crea ALB en AWS
                ├── Crea Target Group
                ├── Registra Pod IPs como targets
                └── Configura health checks
                        │
                        ▼
    ✅ app.midominio.com → ALB → Target Group → Pod → App
```

---

## Errores comunes

### ❌ Error 1: ALB Controller no instalado

**Síntoma:** El Ingress no obtiene ADDRESS.

```bash
kubectl get ingress
# NAME              HOSTS   ADDRESS   PORTS   AGE
# mi-app-ingress    *                 80      5m
#                           ^^^^^^^^ VACÍO = problema
```

**Solución:** Instalar el AWS Load Balancer Controller.

---

### ❌ Error 2: Targets unhealthy

**Síntoma:** ALB devuelve 502 Bad Gateway.

**Causas comunes:**
- El pod crashea (faltan env vars, secrets)
- `healthcheck-path` incorrecto
- `targetPort` no coincide con el puerto del contenedor
- Security Groups bloqueando tráfico

---

### ❌ Error 3: Permisos IAM faltantes

**Síntoma:** El controller no puede crear recursos en AWS.

```bash
kubectl logs -n kube-system -l app.kubernetes.io/name=aws-load-balancer-controller
# "AccessDenied: User is not authorized..."
```

**Solución:** Verificar IAM Role del ServiceAccount.

---

### ❌ Error 4: Annotations incorrectas

```yaml
# ✅ Annotations mínimas necesarias
metadata:
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/healthcheck-path: /
```

---

## Comandos de diagnóstico

```bash
# === INGRESS ===
kubectl get ingress
kubectl describe ingress <nombre>

# === PODS ===
kubectl get pods
kubectl logs <pod-name>
kubectl describe pod <pod-name>

# === ALB CONTROLLER ===
kubectl get pods -n kube-system | grep load-balancer
kubectl logs -n kube-system -l app.kubernetes.io/name=aws-load-balancer-controller

# === AWS CLI ===
aws elbv2 describe-load-balancers
aws elbv2 describe-target-groups
aws elbv2 describe-target-health --target-group-arn <arn>
```

---

## Referencias

- [AWS Load Balancer Controller](https://kubernetes-sigs.github.io/aws-load-balancer-controller)
- [Kubernetes Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/)
- [AWS ALB Docs](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/)
- [EKS Best Practices](https://aws.github.io/aws-eks-best-practices/)

---

> 🏷️ Tags: `kubernetes` `eks` `ingress` `alb` `aws` `networking`

---

## 📖 Navegación

- **⬅️ Anterior:** [00-concepts-overview.md](./00-concepts-overview.md) — Mapa de conceptos
- **➡️ Siguiente:** [02-terraform-basics.md](./02-terraform-basics.md) — Fundamentos de Terraform
- **🏠 Inicio:** [README.md](./README.md) — Índice de documentación