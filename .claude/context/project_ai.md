---
## 🧠 AI Prompt Template for User Activity Analysis Monitor Development

**Project Context:**  
This project is a cross-platform desktop application to monitor and report on user activity (password, email, phone, token changes) across multiple Oracle databases.  
It follows a strict Model-View-Controller (MVC) pattern and supports SRE/SOC workflows, with detailed UI and concurrent query execution.

**Authoritative Addendum:**  
> All implementation, code generation, and design must adhere to the clarifications in the “Project Addendum & Errata: Canonical Guidance for Implementation and AI Code Generation.”  
> Reference that addendum for configuration, directory structure, concurrency model, SQL parameterization, logging, and UI requirements.

---

### ⬇️ **Prompting Template**

You are an expert Python developer.  
Your task is to implement the following “brick” of the User Activity Analysis Monitor project according to all requirements in the addendum/errata and architectural plan.

**[BRICK NAME & OBJECTIVE]**  
(Brief description, e.g. “DatabaseExecutor class for concurrent multi-DB query execution”)

**File/Directory:**  
`[canonical project path, e.g. src/oracle_activity_monitor/model/services/database_executor.py]`

**Key Requirements:**  

- Adhere to the directory structure in the canonical architecture.
- Accept configuration(s) that match the multi-DB format in `configs/databases.yaml`.
- All queries must use the standardized SQL parameters: `:user_id` (string), `:start_date` (datetime).
- Use the appropriate Pydantic models for config validation (see `ez_connect_oracle.py`).
- Implement robust error handling and logging with loguru, writing to both UI and file as described.
- If part of the UI, use CustomTkinter panels/components as modular classes.

**Additional Behaviors:**  

- (e.g. If a progress_callback is required, describe its expected use and parameters.)
- (If supporting cancellation, specify threading.Event usage.)

**Testing/UX Notes:**  

- (Add relevant testing or user experience instructions for this brick.)

**Dependencies:**  

- Reference/require only those modules, libraries, and configs explicitly defined in the canonical architecture and addendum.

---

**When you generate code, please:**

- Include docstrings and type hints.
- Use clear naming and follow the project’s style/conventions.
- Only generate the code for the [BRICK] described above.

---

**Sample Brick Description for Prompt:**

**[BRICK NAME & OBJECTIVE]**  
“DatabaseExecutor class: Manages ThreadPoolExecutor, running QueryRepository for each database in configs/databases.yaml. Accepts user_id and start_date as parameters, supports cancellation with threading.Event, and updates the UI via a progress_callback (database name, query name, status, row count). Logs all actions with loguru as per addendum.”

---

### ✨ **How to Use This Template**

- Replace the [BRICK NAME & OBJECTIVE], file path, and any brick-specific details.
- Copy this template as the top of your AI prompt or code generation request.
- Always reference the addendum/errata and provide specific instructions for UI, model, controller, or integration bricks.

---

> **This template ensures every AI/code generation effort is aligned with project standards, and all code is easily integrated into the larger system.**
