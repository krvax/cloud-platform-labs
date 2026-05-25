# 08 — Git Submodules Workflow

> Guía para trabajar con el lab-11 que está en GitLab como submódulo

---

## ¿Por qué dos repositorios?

### Repositorio Principal (GitHub)
- **URL:** `https://github.com/krvax/epam-aws-devops-prep`
- **Propósito:** Material de preparación, documentación, labs
- **Visibilidad:** Público, para portfolio

### Repositorio Lab-11 (GitLab)
- **URL:** `https://gitlab.com/krvax/gitlab-oidc`
- **Propósito:** Lab de GitLab CI/CD con OIDC
- **Razón:** GitLab CI solo funciona en repositorios de GitLab

---

## Arquitectura de Submódulos

```
epam-aws-devops-prep/ (GitHub)
│
├── labs/
│   ├── lab-01-vpc/           ← código directo en GitHub
│   ├── lab-02-iam/           ← código directo en GitHub
│   ├── ...
│   └── lab-11-gitlab-oidc-mini/  ← GIT SUBMODULE → GitLab
│       ├── .git/             ← apunta a gitlab.com/krvax/gitlab-oidc
│       ├── app/
│       ├── terraform/
│       └── .gitlab-ci.yml    ← este archivo necesita estar en GitLab
│
└── .gitmodules               ← configuración del submódulo
```

---

## Comandos Esenciales

### 1. Clonar el repo con submódulos

```bash
# Primera vez
git clone --recurse-submodules https://github.com/krvax/epam-aws-devops-prep

# Si ya clonaste sin --recurse-submodules
cd epam-aws-devops-prep
git submodule init
git submodule update
```

---

### 2. Ver estado de submódulos

```bash
# Ver qué submódulos tienes
git submodule status

# Ver configuración
cat .gitmodules

# Ver commit actual del submódulo
cd labs/lab-11-gitlab-oidc-mini
git log -1
```

---

### 3. Actualizar el submódulo a la última versión

```bash
# Desde la raíz del repo principal
git submodule update --remote labs/lab-11-gitlab-oidc-mini

# Verificar qué cambió
git status
# Verás: modified: labs/lab-11-gitlab-oidc-mini (new commits)

# Commit el cambio en el repo principal
git add labs/lab-11-gitlab-oidc-mini
git commit -m "chore: update lab-11 to latest version"
git push origin main
```

---

### 4. Hacer cambios en el lab-11

#### Opción A: Trabajar directamente en el submódulo

```bash
# 1. Entrar al submódulo
cd labs/lab-11-gitlab-oidc-mini

# 2. Asegurarte de estar en main
git checkout main
git pull origin main

# 3. Hacer cambios
vim app/app.py

# 4. Commit y push a GitLab
git add .
git commit -m "feat: add new endpoint"
git push origin main

# 5. Volver al repo principal
cd ../..

# 6. Actualizar la referencia del submódulo
git add labs/lab-11-gitlab-oidc-mini
git commit -m "chore: update lab-11 submodule reference"
git push origin main
```

#### Opción B: Clonar el repo de GitLab por separado

```bash
# Clonar en otra carpeta
cd ~/src/learning/EPAM/
git clone git@gitlab.com:krvax/gitlab-oidc.git lab-11-standalone

# Trabajar ahí
cd lab-11-standalone
# ... hacer cambios ...
git push origin main

# Luego actualizar el submódulo en el repo principal
cd ~/src/learning/EPAM/epam-aws-devops-prep/
git submodule update --remote labs/lab-11-gitlab-oidc-mini
git add labs/lab-11-gitlab-oidc-mini
git commit -m "chore: sync lab-11 submodule"
git push origin main
```

---

### 5. Sincronizar cambios entre repos

```bash
# Flujo completo:

# 1. Hacer cambios en GitLab (lab-11)
cd labs/lab-11-gitlab-oidc-mini
git pull origin main
# ... hacer cambios ...
git push origin main

# 2. Actualizar referencia en GitHub (repo principal)
cd ../..
git submodule update --remote labs/lab-11-gitlab-oidc-mini
git add labs/lab-11-gitlab-oidc-mini
git commit -m "chore: update lab-11 submodule"
git push origin main
```

---

## Troubleshooting

### Problema: "El submódulo está vacío"

```bash
# Solución
git submodule init
git submodule update
```

---

### Problema: "Cambios no guardados en el submódulo"

```bash
# Ver qué cambió
cd labs/lab-11-gitlab-oidc-mini
git status

# Opción 1: Commit los cambios
git add .
git commit -m "fix: save changes"
git push origin main

# Opción 2: Descartar cambios
git reset --hard HEAD
```

---

### Problema: "El submódulo apunta a un commit viejo"

```bash
# Actualizar a la última versión
git submodule update --remote labs/lab-11-gitlab-oidc-mini

# Commit el cambio
git add labs/lab-11-gitlab-oidc-mini
git commit -m "chore: update lab-11 to latest"
git push origin main
```

---

### Problema: "Conflicto al hacer pull"

```bash
# Si el submódulo tiene conflictos
cd labs/lab-11-gitlab-oidc-mini
git status
git pull origin main
# ... resolver conflictos ...
git push origin main

# Volver al repo principal
cd ../..
git add labs/lab-11-gitlab-oidc-mini
git commit -m "chore: resolve lab-11 conflicts"
git push origin main
```

---

## Alternativas Consideradas

### 1. Duplicar el código (NO recomendado)

```
❌ Pros:
- Más simple para usuarios nuevos
- No necesitas saber de submódulos

❌ Contras:
- Mantenimiento duplicado
- Fácil que se desincronicen
- Cambios en un repo no se reflejan en el otro
```

### 2. Todo en GitLab (NO recomendado)

```
❌ Pros:
- Todo en un solo lugar
- No necesitas submódulos

❌ Contras:
- Pierdes visibilidad de GitHub
- GitHub es más común para portfolios
- GitLab tiene menos tráfico para proyectos públicos
```

### 3. Git Submodule (RECOMENDADO) ⭐

```
✅ Pros:
- Mejor de ambos mundos
- Cada repo en su plataforma correcta
- Fácil de mantener con git submodule update
- Cambios se sincronizan explícitamente

⚠️ Contras:
- Usuarios deben saber usar submódulos
- Requiere dos pasos para actualizar (GitLab + GitHub)
```

---

## Best Practices

### 1. Siempre commit en el submódulo primero

```bash
# ✅ CORRECTO
cd labs/lab-11-gitlab-oidc-mini
git add .
git commit -m "feat: new feature"
git push origin main

cd ../..
git add labs/lab-11-gitlab-oidc-mini
git commit -m "chore: update lab-11"
git push origin main
```

```bash
# ❌ INCORRECTO (no commitear en el submódulo)
cd labs/lab-11-gitlab-oidc-mini
# ... hacer cambios pero no commit ...

cd ../..
git add labs/lab-11-gitlab-oidc-mini  # ← esto no guarda los cambios del submódulo
git commit -m "update lab-11"
```

---

### 2. Mantener el submódulo actualizado

```bash
# Cada vez que alguien actualice el lab-11 en GitLab
git submodule update --remote labs/lab-11-gitlab-oidc-mini
git add labs/lab-11-gitlab-oidc-mini
git commit -m "chore: sync lab-11"
git push origin main
```

---

### 3. Documentar en el README

El README principal debe explicar:
- Que lab-11 es un submódulo
- Por qué está en GitLab
- Cómo clonar con submódulos
- Cómo actualizar el submódulo

---

## Preguntas de Entrevista

### "¿Por qué usas git submodules?"

```
"El lab-11 demuestra GitLab CI/CD con OIDC, por lo que debe estar en GitLab
para que el pipeline funcione. Uso git submodule para mantener todo el material
de preparación en un solo lugar (GitHub) mientras el lab-11 funciona
independientemente en GitLab. Esto me permite tener lo mejor de ambos mundos:
visibilidad en GitHub y funcionalidad de GitLab CI."
```

### "¿Qué alternativas consideraste?"

```
"Consideré duplicar el código en ambos repos, pero eso crea mantenimiento duplicado.
También consideré mover todo a GitLab, pero GitHub tiene más visibilidad para
portfolios. Git submodule es la solución correcta porque mantiene la separación
necesaria mientras permite gestión centralizada."
```

### "¿Cómo manejas la sincronización?"

```
"Cuando hago cambios en el lab-11, primero los commiteo y pusheo a GitLab.
Luego, en el repo principal de GitHub, ejecuto 'git submodule update --remote'
para actualizar la referencia al último commit del submódulo. Finalmente,
commiteo ese cambio en GitHub. Esto mantiene ambos repos sincronizados
explícitamente."
```

---

## Recursos

- [Git Submodules Documentation](https://git-scm.com/book/en/v2/Git-Tools-Submodules)
- [GitHub: Working with Submodules](https://github.blog/2016-02-01-working-with-submodules/)
- [Atlassian: Git Submodules](https://www.atlassian.com/git/tutorials/git-submodule)

---

**Última actualización:** 2026-04-13

---

## 📖 Navegación

- **⬅️ Anterior:** [07-kubernetes-deep-dive.md](./07-kubernetes-deep-dive.md) — Kubernetes profundo
- **🏠 Inicio:** [README.md](./README.md) — Índice de documentación
- **🔝 Volver al inicio:** [00-concepts-overview.md](./00-concepts-overview.md) — Mapa de conceptos
