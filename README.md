
# 🧠 AI Resource Scaffold Generator

This project supports automated generation of code scaffolding for new resources in a .NET monolith, following the architecture used by `ServiceActivity`. It uses structured JSON requirements to generate full prompt files for LLMs (e.g., DeepSeek, GPT-4) that can be used to scaffold:

- Contracts
- Validation
- Domain Models
- Messaging Events
- Controllers
- Converters
- Resources
- QueryLang logic
- Tests
- Autofac Registrations

---

## 🧩 Requirements Format

Each resource starts with a requirements file (e.g., `engagementactivity-requirements.json`) like this:

```json
{
  "name": "EngagementActivity",
  "hasEvents": true,
  "hasQueryLang": true,
  "hasController": true,
  "hasResource": true,
  "hasConverter": true,
  "hasValidation": true,
  "hasDomainModel": true,
  "hasTests": true,
  "hasAutofacModuleRegistration": true,
  "contractFields": [
    { "name": "Id", "type": "int" },
    { "name": "Description", "type": "string" },
    { "name": "Date", "type": "DateTime" }
  ]
}
```

---

## ⚙️ Usage

```bash
python generate_prompts.py engagementactivity-requirements.json engagementactivity-prompts.json
```

This generates a `prompts.json` file with tailored prompts for each component of the resource. These can then be passed to DeepSeek, GPT-4, or any LLM for code generation.

---

## 📦 Files

- `generate_prompts.py` – the main prompt generator
- `*.requirements.json` – per-resource definitions
- `*-prompts.json` – output prompts for LLMs

---

