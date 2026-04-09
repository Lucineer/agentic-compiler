# agentic-compiler

The Lucineer Agentic Compiler — deliberation bytecode for programmable thought.
Home of **Lucineer Lang**, an agentic-native programming language.

## What's Here

### Lucineer Lang Design (docs/LUCINEER-LANG-DESIGN.md)
An agentic-native programming language where NLP and code are first-class equals:
- **Confidence is a primitive type** — every value carries 0-1 certainty
- **Deliberation is control flow** — consider/resolve patterns for alternatives
- **Models are citizens** — syntax designed so LLMs read/write/debug natively
- **NLP-to-code transpilation** — seamless through shared deliberation IR
- **Bytecode-targeted** — compiles to 42-opcode deliberation VM

### Deliberation Bytecode Engine (src/compiler/engine.py)
- 42 opcodes: INTENT, CONSIDER, RESOLVE, CONFIDENCE, ALTERNATIVE, GUARD, LEARN, EXPLAIN
- TensorCell: value + confidence + alternatives + intent
- DeliberationFrame: nested reasoning with confidence propagation
- NLP transpiler: natural language to bytecode
- Python emitter: IR to annotated code generation
- Error-as-signal: errors become semantic gradients

## Run
python3 src/compiler/engine.py

## Ecosystem
- nexus-edge-runtime — Edge VM (bytecode target)
- cudaclaw — Rust+CUDA agent runtime (GPU target)
- nexus-energy — Energy management (stdlib module)
- frozen-intelligence — Chip design toolchain

MIT — DiGennaro et al. (SuperInstance & Lucineer)
