# 💻 Preparation Guide: Scripting & Coding (DevOps)

> This section is designed to help you overcome the fear of the coding test, focusing on real problems asked in EPAM interviews for SRE/DevOps roles.

---

## 🎯 The Right Approach

In DevOps, the goal is not for you to be a complex algorithm developer (LeetCode Hard), but rather to be capable of **automating tasks** and **manipulating data**.

### Suggested Languages
1. **Python** (Highly recommended for EPAM)
2. **Bash** (Indispensable for system tasks)

---

## 📋 Frequent Topics in EPAM

### 1. Log and Text Manipulation
*   **Problem:** Read a log file and count how many requests occurred for each status code (200, 404, 500).
*   **Skill:** Python dictionaries, string manipulation, `split()`.

### 2. API Consumption (AWS SDK / Boto3)
*   **Problem:** List all EC2 instances that do not have the "Environment" tag and stop them.
*   **Skill:** Use of the `boto3` library, `for` loops, `if` conditionals.

### 3. JSON/YAML Processing
*   **Problem:** Given a configuration JSON, filter certain values and generate a new file.
*   **Skill:** `json` and `yaml` libraries in Python.

### 4. System Scripts (Bash)
*   **Problem:** Create a script that checks if a process is running; if not, starts it and sends an alert.
*   **Skill:** `ps`, `grep`, `systemctl`, environment variables.

---

## 🛠️ Hands-on Exercises (Start here)

### Exercise 1: The Log Analyzer (Python)
Create a script that reads a file named `access.log` with this format:
`192.168.1.1 - - [10/Apr/2024:10:00:00] "GET /home HTTP/1.1" 200 1234`

**Goal:** Print the total number of 5xx errors.

### Exercise 2: Boto3 Janitor (Python)
**Goal:** Identify S3 buckets that do not have versioning enabled.

---

## 💡 Tips for Test Day

1.  **Talk while you code:** Explain your logic. Often, your thought process matters more than whether the code compiles on the first try.
2.  **KISS (Keep It Simple, Stupid):** Don't try to use complex libraries if you haven't mastered them. A readable script is better than a "fancy" one.
3.  **Error Handling:** Use `try-except` blocks. Demonstrate that you care about script stability.
4.  **If you get stuck:** Be honest. "I know I need to use function X from library Y, but I don't remember the exact parameters. Can I check the documentation quickly?" (They almost always say yes).

---

## 📚 Resources for Practice

*   **Exercism (Python Track):** Excellent for basic logic.
*   **Boto3 Documentation:** Familiarize yourself with the response structure of `describe_instances`.
*   **Python for DevOps (Book):** Chapters on system automation.

---

## 📖 Navigation

- **⬅️ Previous:** [05-observability-concepts.en.md](./05-observability-concepts.en.md) — Observability
- **➡️ Next:** [07-kubernetes-deep-dive.en.md](./07-kubernetes-deep-dive.en.md) — Kubernetes Deep Dive
- **🏠 Home:** [README.en.md](../README.en.md) — Documentation index
- **🔝 Back to top:** [00-concepts-overview.en.md](./00-concepts-overview.en.md) — Concept Map

---

## 🧪 Related Labs

Put these concepts into practice:

- **[Lab Scripting — 11 Mock Exercises](../labs/scripting/README.md)**
  - 11 scripting exercises (Python + Bash)
  - Log analysis with SLO check
  - Warmup exercises (20 min)
  - Bonus practice (12 additional exercises)

- **[Lab 09 — CloudWatch Logs](../labs/lab-09-cloudwatch-logs/Readme.md)**
  - Logs Insights queries
  - Metric Filters and Alarms
  - JSON log analysis

- **[Lab 07 — Prometheus + Grafana](../labs/lab-07-monitoring/Readme.md)**
  - PromQL queries
  - Metric dashboards
  - Alerts with Alertmanager

---

## 📖 Navigation

- **⬅️ Previous:** [05-observability-concepts.en.md](./05-observability-concepts.en.md) — Observability
- **➡️ Next:** [07-kubernetes-deep-dive.en.md](./07-kubernetes-deep-dive.en.md) — K8s Deep Dive
- **🏠 Home:** [README.en.md](../README.en.md) — Documentation index
- **🔝 Back to top:** [00-concepts-overview.en.md](./00-concepts-overview.en.md) — Concept Map
