# DRIFT

**Decentralized Resource Identity & Trust Framework (DRIFT)**  
Created by [Slava Tykhonov](https://github.com/4tykhonov)

---

DRIFT is a decentralized identity and trust layer that propagates **traceable context** — such as sessions, prompts, user metadata, and spans — across AI tools and services in **event-driven environments** like the Model Context Protocol (MCP).

## 🧠 Background: Understanding Data Drift

In software engineering, **data drift** is a key concern that can affect system reliability and trust in data processing pipelines. DRIFT helps mitigate these risks by making identity and changes traceable.

Three common types of drift include:

- **Infrastructure Drift** – Changes in the software environment that can break or invalidate infrastructure configurations.
- **Structural Drift** – Changes to the data schema that may invalidate databases or data contracts.
- **Semantic Drift** – Changes in the meaning of data without altering its structure, often caused by multiple developers independently modifying system components.

By assigning decentralized identifiers (DIDs) and enforcing consistent, signed metadata, DRIFT supports systems in managing and auditing these types of drift.


## 🔍 What DRIFT Does

DRIFT enables trusted interoperability between distributed AI components by providing unique, verifiable identities for all parts of an AI pipeline.

## ✨ Features

- ✅ Assigns [DIDs (Decentralized Identifiers)](https://www.w3.org/TR/did-core/) to all entities:
  - Sessions
  - Prompts
  - Users
  - Tools

- 🔐 Uses **public/private key cryptography** to:
  - Sign events
  - Verify authenticity of actions and actors

- 🧱 Defines a **consistent metadata structure** for:
  - Events
  - Tools
  - Services

- 🔗 Supports **verifiable logs and data lineage**:
  - Track where and how data was processed
  - Ensure transparency in AI workflows

## 📦 Use Cases

- Model Context Protocol (MCP) pipelines
- Distributed AI systems
- Event logging with trusted provenance
- Prompt and session tracking across tools

---

## 🛠️ Getting Started

```bash
# Clone the project
cd drift
python3 drift.py
```

