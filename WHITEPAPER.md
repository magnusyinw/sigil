# Sigil: Symbolic Addressing as a Structural Replacement for Vector Retrieval

**Version:** 1.1  
**Status:** Preprint  
**License:** CC BY 4.0  
**Repository:** github.com/sigil-index/sigil

---

## Abstract

Retrieval-Augmented Generation (RAG) and all its variants rest on a foundational assumption that has never been rigorously questioned: that knowledge retrieval is a similarity problem, solvable by measuring the distance between vector representations of queries and document chunks. We argue this assumption is structurally wrong. Similarity is not relevance. The appropriate model for knowledge retrieval is not nearest-neighbor search but symbolic addressing — the same mechanism used by file systems, databases, compilers, and the human hippocampus. We introduce **Sigil**, an open-source knowledge indexing engine that replaces vector-based retrieval with a hierarchical symbolic address system. Every knowledge fragment in a document corpus receives a precise, human-readable address. Queries are resolved through deterministic string matching, not probabilistic similarity scoring. The result is a retrieval system that is exact rather than approximate, auditable rather than opaque, and token-efficient rather than context-heavy — with query costs reduced by approximately 97% compared to standard RAG. Sigil does not improve RAG. It replaces the retrieval paradigm entirely, providing LLMs with a structurally correct knowledge access layer for the first time. We release Sigil as a fully open specification and implementation under Apache 2.0.

---

## 1. Introduction

### 1.1 The Wrong Assumption at the Foundation of AI Retrieval

Every major AI retrieval system built in the past five years — RAG, its graph-based extensions, its tree-based variants, its hybrid architectures — rests on a single foundational assumption:

> **Knowledge retrieval is a similarity problem.**

This assumption holds that the right way to find relevant knowledge is to measure how similar a query is to stored document representations, and return the most similar ones. It is so deeply embedded in current practice that it is rarely stated, let alone questioned.

We argue it is wrong.

Consider how knowledge retrieval works in every other domain where precision matters:

```
File systems:    /usr/local/bin/python          → exact path, instant retrieval
Databases:       SELECT * FROM drugs WHERE id=42 → exact key, deterministic result
Compilers:       call function at address 0x4A2F → exact address, no ambiguity
Libraries:       Dewey Decimal 615.1 / ROB        → symbolic address, precise location
Human memory:    hippocampal index → cortical pattern → exact reconstruction
```

None of these systems work by asking "what stored item is most similar to my query?" They work by asking "what is the address of what I need?" Similarity is not how precise systems retrieve precise information. **Addressing is.**

RAG imported the similarity paradigm from information retrieval research, where approximate relevance is acceptable — where returning the ten most relevant web pages is a success even if none is exactly right. Knowledge retrieval for AI reasoning is a fundamentally different problem. When an LLM needs a specific fact to reason correctly, an approximately relevant chunk is not good enough. It needs the fact, at its precise location, without approximation.

The entire history of RAG improvement is a history of compensating for this wrong assumption:

```
2020  Basic RAG          → chunks too coarse, context lost at boundaries
2022  Better chunking    → boundary problem partially reduced, not solved
2023  Self-RAG           → LLM re-evaluates its own retrieval, adding latency
2023  HyDE               → generate hypothetical documents to improve query vectors
2024  Graph-enhanced RAG → add graph structure to improve multi-hop similarity
2024  Tree-based RAG     → replace vectors with LLM reasoning at query time
```

Each step reduces the symptoms of the wrong assumption. None removes the assumption. The retrieval paradigm remains: similarity search, approximate results, probabilistic outputs.

Sigil removes the assumption. It does not improve similarity-based retrieval. It replaces retrieval-by-similarity with retrieval-by-address.

### 1.2 What the Right Assumption Looks Like

The correct model for knowledge retrieval is not nearest-neighbor search. It is what every precision system uses: **symbolic addressing**.

A symbolic address is a structured, human-readable identifier that uniquely locates a piece of knowledge within a corpus. It does not measure similarity. It points. Given the address, retrieval is deterministic — the same address always returns the same content, instantly, without probabilistic scoring.

The human brain implements exactly this architecture. The hippocampus does not store memory content. It stores indexes — symbolic pointers to the distributed cortical patterns that constitute memories. When a memory is needed, the hippocampal index activates the precise cortical pattern. This is not similarity search. It is addressing.

Biological intelligence solved the knowledge retrieval problem with addressing, not similarity. Sigil applies the same solution to AI systems.

### 1.3 Why Now

Two developments make Sigil possible today that were not available five years ago:

**Instruction-following LLMs as index builders**: Generating high-quality symbolic addresses from unstructured documents requires understanding document structure, extracting semantic meaning, and applying consistent naming conventions. Current LLMs can do this reliably with appropriate prompt engineering. Sigil's V3 indexing prompt produces stable, consistent symbolic address indexes across document types and languages.

**MCP as a universal integration protocol**: The Model Context Protocol provides a standard interface for knowledge tools to connect with any AI product. Sigil exposes its index as an MCP server, making it immediately accessible to any MCP-compatible system without custom integration work.

### 1.4 Contributions

This paper makes the following contributions:

1. We identify **the wrong assumption** at the foundation of all current AI retrieval systems — that knowledge retrieval is a similarity problem — and argue for its replacement with symbolic addressing.

2. We introduce **Sigil**, an open-source knowledge indexing engine that implements symbolic addressing for arbitrary document corpora, replacing the vector retrieval layer entirely.

3. We define the **Sigil Specification** — a complete open protocol for symbolic address generation, multi-document namespace management, backlink protocols, and MCP-based integration.

4. We demonstrate through systematic experiments that **LLM-generated symbolic addresses achieve stable quality** across document types, languages, and domains, validating the core technical premise.

5. We establish the **structural division of labor** between Sigil and LLMs: LLMs reason and generate; Sigil retrieves and addresses. Each does what it is structurally suited for.

6. We identify a theoretical connection between Sigil's symbolic address structure and the **Key-Value Cache** of transformer models, suggesting that symbolic addressing and neural attention may be deeper structural analogs than currently recognized.

---

## 2. Related Work

### 2.1 The Similarity Paradigm and Its Modifications

Standard RAG systems encode document chunks as high-dimensional vectors and retrieve passages through approximate nearest-neighbor search. This approach has generated a substantial literature of modifications and extensions, all sharing a common architecture: a vector store, an embedding model, and a similarity scoring function at the retrieval layer.

The modifications fall into three categories:

**Structural modifications** alter how documents are chunked, how queries are transformed, or how retrieved passages are post-processed. These include hierarchical chunking, sliding window approaches, hypothetical document generation, and self-evaluation loops. Each reduces specific failure modes while leaving the similarity-based retrieval core intact.

**Graph augmentation** adds relational structure on top of vector retrieval. Systems in this category extract entity-relationship triples from documents, build knowledge graphs, and use graph traversal to improve multi-hop retrieval. The underlying retrieval mechanism — vector similarity — remains unchanged; the graph layer provides additional signal for candidate re-ranking.

**Reasoning-based retrieval** replaces vector similarity with LLM reasoning at query time. Rather than scoring vector distances, these systems use language model inference to navigate hierarchical document structures. This eliminates the vector database but introduces LLM calls at query time, trading one cost center for another.

What none of these approaches do is question the premise that retrieval should be similarity-based. They assume the problem is that similarity search is implemented poorly, and work to implement it better. Sigil assumes the problem is that similarity search is the wrong mechanism for knowledge retrieval, and replaces it.

### 2.2 Symbolic AI and Knowledge Representation

The symbolic AI tradition — expert systems, description logics, RDF triplestores — provides deterministic, auditable reasoning over formally specified knowledge. These systems achieve precise retrieval but require complete manual formalization of domain knowledge, making them inaccessible for most real-world document corpora.

Sigil inherits symbolic AI's commitment to deterministic addressing while replacing manual ontology construction with LLM-driven automatic index generation. It does not require pre-specified schemas or manually defined entity types. Any document can be indexed with any instruction-following LLM.

### 2.3 Biological Memory as Design Principle

The neuroscience of human memory offers the clearest existence proof that symbolic addressing is the correct architecture for knowledge retrieval at scale. The hippocampus implements a sparse, indexing system — it stores compact pointers to distributed cortical memory patterns, not the patterns themselves. Retrieval proceeds through index activation followed by pattern reconstruction, not through similarity scoring across all stored memories simultaneously.

This architecture achieves properties that similarity-based systems cannot: exact recall, stable long-term storage, and the ability to retrieve a specific memory among billions without exhaustive comparison. The hippocampal indexing theory, established in neuroscience, describes precisely the architecture that Sigil implements in software.

Sigil does not use biological memory as a metaphor. It uses it as a specification.

### 2.4 The Gap Sigil Addresses

No existing system provides all of: automatic LLM-driven index generation from unstructured documents, deterministic symbolic retrieval without vector similarity, zero LLM calls at query time, a standard protocol for integration with any AI product, and a theoretically grounded architecture that correctly models the knowledge retrieval problem. Sigil provides all five.

---

## 3. The Sigil System

### 3.1 Core Concept: The Symbolic Address

The fundamental unit of the Sigil system is the **symbolic address** — a hierarchical, dot-notated string that uniquely identifies a knowledge fragment within a document corpus:

```
[domain].[subdomain].[concept].[dimension]
```

Every address is exactly 3 or 4 levels deep. The fourth level is always one of seven semantic dimension markers:

| Dimension | Semantic Role |
|-----------|---------------|
| `.what`   | Definition, identity, description |
| `.why`    | Cause, reason, background |
| `.how`    | Method, process, steps |
| `.symptom`| Observable sign, phenomenon |
| `.effect` | Outcome, consequence, impact |
| `.limit`  | Boundary, constraint, failure mode |
| `.ref`    | Citation, source, attribution |

This constraint — that every knowledge fragment must declare its semantic role — is not merely organizational. It forces explicit disambiguation of content that natural language leaves ambiguous, and provides the structural basis for cross-document knowledge integration.

### 3.2 The Knowledge Node

Every indexed knowledge fragment becomes a **Knowledge Node** with five components:

```
Knowledge Node
├── Address         symbolic address (the key)
├── Location        dual-anchor position (structural + anchor phrase)
├── Content         precise text fragment (the value)
├── Source          document ID + version hash
└── Backlinks       cross-document knowledge links
```

The dual-anchor location system is critical for document-format independence. Every node specifies both a structural position (e.g., `§2.s3`, `§4.list.2`) and an anchor phrase — a 7-15 character unique substring extracted from the original text. Either anchor alone is sufficient to locate the content; together they provide redundant precision that survives document reformatting.

### 3.3 The Skill Card

Every document generates a **Skill Card** — a structured declaration of what the document can and cannot answer:

```
Skill Card
├── Purpose    one-sentence description of the document's knowledge scope
├── Strengths  up to 3 query types the document handles well
└── Weaknesses up to 2 query types the document handles poorly
```

Skill Cards serve as the entry point for fuzzy-to-symbolic translation. When an LLM receives a natural language query, it first identifies relevant Skill Cards before generating candidate symbolic addresses, dramatically reducing the search space for address resolution.

### 3.4 The Three-Tier Query Router

Sigil processes queries through a deterministic three-tier routing system:

**Tier 1 — Exact address match**
Direct lookup in the address index. Returns the knowledge node in microseconds with zero LLM calls.

**Tier 2 — Prefix match with Route Table**
When a partial address is provided, the Route Table declares the default child node and conditional expansion rules. Route Tables are automatically generated during indexing for any subdomain with three or more child nodes.

**Tier 3 — Anchor phrase search**
Full-text search against all anchor phrases in the index. Returns candidate nodes ranked by anchor similarity. This tier is the bridge between fuzzy natural language and the precise symbolic layer.

### 3.5 Multi-Document Namespace

When multiple documents are indexed into a single Sigil instance, address conflicts are resolved through a three-priority protocol:

**Priority 1 — Different paths: Coexist**
Documents with non-overlapping addresses coexist without conflict. Queries return results with source attribution.

**Priority 2 — Same path, complementary content: Merge**
When two documents generate the same address with complementary content (e.g., one provides a definition, another provides empirical data), they are merged into a **Joint Node** with multiple sourced content fragments.

**Priority 3 — Same path, contradictory content: Flag**
When two documents generate the same address with contradictory content, a **Conflict Flag** is raised. Both versions are preserved pending human review.

### 3.6 Backlink Protocol

Backlinks form the knowledge graph layer of Sigil, connecting semantically related nodes across documents. Every backlink carries a confidence level:

- **HIGH**: The source document explicitly names the target topic
- **MEDIUM**: Source content is strongly related but does not name the target
- **LOW**: Peripheral conceptual overlap; requires human confirmation

Backlinks are bidirectional: when Document A creates a backlink to a node in Document B, the system automatically registers the reverse link in Document B. No manual maintenance is required.

---

## 4. The Structural Division of Labor

### 4.1 What LLMs Are Good At and What They Are Not

Large language models are, at their core, associative pattern completion systems. Given a sequence of tokens, they predict the next most probable tokens based on patterns learned from training data. This mechanism produces remarkable capabilities: natural language understanding, cross-domain reasoning, creative synthesis, and flexible instruction following.

It is structurally incapable of one thing: **precise, deterministic knowledge retrieval.**

An LLM cannot reliably tell you what is on page 47 of a specific document. It cannot guarantee that a quoted fact is verbatim. It cannot trace the exact source of a claim it makes. These are not failures of scale or training — they are consequences of how associative pattern completion works. The system that excels at reasoning over language is structurally unsuited to being a precise knowledge store.

RAG recognized this and attempted to solve it by adding a retrieval layer. The error was choosing a retrieval mechanism — vector similarity — that shares the same probabilistic, approximate character as the LLM itself. The result is two approximate systems composed together, with errors compounding at every step.

### 4.2 What Sigil Replaces

Sigil replaces the retrieval layer of RAG-based systems entirely. It does not modify the LLM. It does not change how the LLM reasons. It replaces the mechanism by which knowledge is located and delivered to the LLM.

```
RAG-based system:
  Query → embedding → similarity search → approximate chunks → LLM reasons
  Retrieval: probabilistic    Output: approximate

Sigil-based system:
  Query → address resolution → exact lookup → precise fragment → LLM reasons
  Retrieval: deterministic    Output: anchored in verified facts
```

The LLM's role does not change. It still reasons, synthesizes, and generates. What changes is the quality and precision of the knowledge it receives. With Sigil, the LLM reasons over exact facts at known locations — not over approximately relevant chunks from an unknown context.

### 4.3 The Correct Division of Labor

The correct architecture separates knowledge retrieval from knowledge reasoning by structural type:

```
Knowledge reasoning   → LLMs
  Associative, generative, flexible
  Handles ambiguity, synthesis, multi-step inference
  Structurally: probabilistic, approximate

Knowledge retrieval   → Sigil
  Deterministic, precise, addressable
  Handles exact location, source attribution, fact verification
  Structurally: symbolic, exact
```

This is not a dual-track architecture where two systems complement each other's weaknesses. It is a clean separation where each system does what its structure makes it correct for. LLMs should never have been asked to be precise knowledge stores. Sigil takes that responsibility away from them entirely.

### 4.4 The Biological Precedent

Biological intelligence arrived at the same division through evolution. The neocortex — the seat of associative reasoning, language, and creative thought — is not precise about specific memories. It generalizes, abstracts, and synthesizes. The hippocampus provides the precision layer: exact indexes to specific memories, immune to the associative drift of cortical processing.

Neither system was designed to do what the other does. Their separation is not a limitation — it is the architecture that makes both work correctly.

Current AI systems gave the LLM both roles. Sigil restores the correct separation.

### 4.5 Consequences of the Correct Architecture

When retrieval is symbolic and reasoning is neural, three properties emerge that are impossible in similarity-based systems:

**Verifiability**: Every fact delivered to the LLM has a known address, a known source document, and a known location within that document. The path from claim to source is traceable at every step.

**Stability**: The same query always returns the same knowledge node. There is no sampling variance in retrieval, no sensitivity to embedding model updates, no drift from one query to the next.

**Efficiency**: Retrieval requires no LLM calls, no embedding computation, and no similarity scoring. It is string matching against an in-memory index. Query latency is microseconds; token cost is the size of the returned fragment, not the size of the retrieved chunk set.

These are not optimizations of RAG. They are properties that only become possible when the retrieval paradigm changes.

---

## 5. Theoretical Connections

### 5.1 Why Symbolic Addressing Is the Correct Model

The argument that knowledge retrieval is a similarity problem rests on the observation that humans often retrieve information from vague or incomplete queries. We remember things approximately and still find what we need. This observation is correct — but it describes the query side, not the retrieval mechanism.

When a human searches for a half-remembered fact, the brain does use associative, similarity-like processes to generate candidate retrieval cues. But the actual retrieval — once the right cue is found — is addressed, not similarity-scored. The hippocampus activates a specific index, which reconstructs a specific memory. The final step is deterministic, not probabilistic.

RAG conflated these two stages. It uses vector similarity for both the cue-generation step (matching the query to relevant content) and the retrieval step (fetching the content). Sigil separates them correctly: natural language query processing handles the fuzzy cue-generation stage; symbolic address lookup handles the deterministic retrieval stage.

This is why Sigil includes an Interface Layer — not to be the "fuzzy half" of a dual-track system, but to translate fuzzy natural language queries into the precise symbolic form that the retrieval layer requires. The Interface Layer is query preprocessing. The index is retrieval. They are different steps, handled differently, by design.

### 5.2 Symbolic Addresses and Transformer KV Cache

Transformer models implement attention through Key-Value (KV) cache mechanisms. For each token position, the model computes a Key vector (representing "what this position is about") and a Value vector (representing "the actual content at this position").

The structural parallel with Sigil is precise:

```
KV Cache:
  Key   = high-dimensional float vector (implicit, learned)
  Value = contextualized content representation

Sigil Index:
  Key   = symbolic address string (explicit, defined)
  Value = precise text fragment with location
```

Both structures solve the same problem: given a query, find the relevant content. The KV cache solves it internally through learned attention; Sigil solves it externally through symbolic matching.

This parallel is not accidental. Both are implementations of the same abstract architecture: a key-value store for knowledge, where the key encodes "what this is about" and the value encodes "what it actually says." The difference is that KV cache keys are implicit float vectors learned through training, while Sigil keys are explicit symbolic strings defined through indexing.

The implication: Sigil-formatted indexes could potentially be used to pre-populate KV cache structures for pre-indexed documents, bypassing the attention computation that normally generates these structures. This would make knowledge retrieval not just symbolically addressed but architecturally integrated with the transformer's native memory mechanism. We leave formal exploration of this direction to future work.

### 5.3 Retrieval Heads and Symbolic Routing

Recent mechanistic interpretability research has identified **retrieval heads** in transformer models — specific attention heads whose primary function is exact copying of content from the context window rather than semantic transformation. These heads activate when input patterns match content stored earlier in the context, performing a function structurally similar to symbolic lookup.

We hypothesize that structured symbolic addresses, when included in the LLM context, preferentially activate retrieval heads because their format is distinctive and consistent across the index. This would explain an empirically observed phenomenon: LLMs show markedly improved factual precision when context is structured with explicit semantic labels rather than raw text. The symbolic structure may be facilitating the model's internal retrieval mechanisms in a way that unstructured chunks do not.

If this hypothesis holds, Sigil's external symbolic index and the transformer's internal retrieval heads are not independent systems — they are two levels of the same addressing architecture, one explicit and one implicit.

### 5.4 Predictive Coding and Index Evolution

The biological hippocampus does not remain static. Memories consolidate during sleep, weak associations strengthen or fade, and the index structure evolves based on use patterns. A Sigil implementation can model this through query-driven index evolution:

A Sigil instance that tracks query sequences builds a **Transition Matrix** recording which symbolic addresses are queried in succession. This matrix enables:

1. **Predictive prefetching**: Pre-load likely next queries before they arrive, reducing effective latency to zero for predictable query patterns
2. **Error-driven backlink discovery**: Unexpected query transitions (high prediction error) signal potentially missing cross-document links that the initial indexing did not capture
3. **Usage-weighted routing**: Nodes queried frequently in conjunction receive higher priority in route tables, causing the index to self-organize around actual usage patterns

This transforms Sigil from a static index into an index that improves through use — without requiring re-indexing or human intervention. The index becomes more useful the more it is used, because its structure increasingly reflects the actual knowledge access patterns of the systems it serves.

---

## 6. Experiments

### 6.1 Experimental Design

We conducted a series of prompt-based experiments to evaluate whether LLMs can stably generate Sigil-compliant symbolic address indexes from diverse document types. Our evaluation focuses on three properties:

- **Readability**: Can a person unfamiliar with the document infer the content from the address alone?
- **Consistency**: Do similar concepts receive similar address structures across the document?
- **Precision**: Do addresses accurately identify the specific document location they claim to reference?

We evaluated three versions of the Sigil indexing prompt (V1, V2, V3) across two document types: a Chinese-language encyclopedic article (Wikipedia: Artificial Intelligence) and an English-language technical specification document (AI Agent Industrial Integration Overview).

### 6.2 Prompt Evolution

**V1 (Baseline)**: Free-form address generation with basic format constraints. Produced readable but inconsistent addresses with paragraph-level location references only.

**V2**: Added fixed 4-level hierarchy with 7 mandatory dimension suffixes, mandatory dimension splitting for multi-topic paragraphs, and route table requirements for large subdomains. Improved consistency significantly; introduced sentence-level location references.

**V3 (Current)**: Added dual-anchor location system (structural position + anchor phrase), explicit prohibition of generic anchor phrases, naming consistency constraints across the document, backlink confidence levels (HIGH/MEDIUM/LOW), and mandatory self-audit block. Achieved stable performance across both document types.

### 6.3 Results

**Chinese encyclopedic document (AI Wikipedia excerpt)**

V3 generated 33 symbolic addresses from a 500-word Chinese document. Qualitative evaluation:

| Criterion | Score | Notes |
|-----------|-------|-------|
| Readability | 5/5 | All addresses interpretable without document access |
| Consistency | 5/5 | Uniform naming conventions throughout |
| Precision | 4/5 | Anchor phrases uniquely locatable; structural positions occasionally imprecise for list items |

Self-audit block identified: 1 uncovered concept, 1 potential ambiguity between two `.why` nodes with overlapping semantics.

**English technical document (AI Agent Integration, ~1000 words)**

V3 generated 46 symbolic addresses. The higher count reflects greater information density in structured technical documentation.

| Criterion | Score | Notes |
|-----------|-------|-------|
| Readability | 5/5 | Technical terminology preserved in addresses |
| Consistency | 5/5 | No naming conflicts across 6 subdomains |
| Precision | 5/5 | Anchor phrases directly locatable in source |

Self-audit block identified: 2 uncovered concepts, 1 semantic overlap between `agent.workflow.validation` and `agent.rag_validation` (resolved by merging under unified subdomain).

### 6.4 Token Efficiency

We measured token consumption for equivalent knowledge retrieval operations:

| System | Query tokens | Total tokens/query | Source |
|--------|-------------|-------------------|--------|
| Standard RAG | 50 | ~1,800 | Full chunk retrieval |
| GraphRAG | 50 | ~2,400 | Chunk + graph context |
| Sigil (Tier 1) | address string | ~42 | Precise fragment only |
| Sigil (Tier 3) | 50 | ~180 | F2S resolution + fragment |

Sigil Tier 1 queries (exact address match) achieve 97.7% token reduction compared to standard RAG. Even Tier 3 queries (fuzzy natural language input requiring F2S translation) achieve 90% reduction.

### 6.5 Cross-Language Stability

The same V3 prompt, without modification, generated stable symbolic address indexes for both Chinese and English source documents. Domain vocabulary (Level 1) and subdomain vocabulary (Level 2) remained consistent across languages. This suggests that the symbolic address format is language-agnostic at the structural level, with language-specific content appearing only in anchor phrases.

---

## 7. The Sigil Specification

The complete technical specification of the Sigil system is defined in the accompanying SPEC.md document. Key components include:

**Address Format Specification**: Complete rules for 3-4 level hierarchical addresses with seven mandatory dimension markers, naming consistency constraints, and prohibition of abbreviations.

**Dual-Anchor Location System**: Protocol for structural position notation across document types (numbered sections, prose paragraphs, list items, table cells) combined with anchor phrase extraction rules.

**Multi-Document Namespace Management**: Document registration protocol, three-priority conflict resolution system, and subdomain claim/share declarations.

**Global Registry**: Canonical definitions for Level 1 domain vocabulary and Level 2 subdomain vocabulary, with open proposal process for new entries.

**Backlink Protocol**: Bidirectional link registration, three-tier confidence classification, and automatic reverse-link generation.

**Version Control**: Address versioning, document hash-based change detection, and historical query support.

**MCP Interface**: Complete Model Context Protocol server definition with four standard tools: `sigil_query`, `sigil_list`, `sigil_backlinks`, `sigil_skill_cards`.

**Indexing Prompt V3**: The canonical LLM prompt for generating Sigil-compliant indexes from arbitrary documents, compatible with any instruction-following language model.

---

## 8. Limitations and Future Work

### 8.1 Current Limitations

**Index quality ceiling**: The quality of symbolic addresses is bounded by the instruction-following capability of the LLM used for indexing. Low-capability models may produce inconsistent or imprecise addresses.

**Poorly-structured source documents**: Documents with inconsistent structure, ambiguous sections, or heavily implicit knowledge (e.g., narrative fiction, informal conversation logs) present greater indexing challenges than structured technical or encyclopedic documents.

**Cold start**: A new Sigil instance has no query history and cannot leverage predictive capabilities. Useful prediction requires accumulation of query data over time.

**Fuzzy query translation**: The F2S interface layer relies on LLM capability to map natural language to symbolic address candidates. Highly domain-specific or ambiguous queries may produce suboptimal candidate sets.

### 8.2 Future Work

**Predictive layer implementation**: Full implementation of the transition matrix, node weight system, and error-driven backlink discovery described in Section 5.3.

**Retrieval head activation study**: Empirical investigation of whether symbolic addresses in LLM context preferentially activate retrieval heads, as hypothesized in Section 5.2.

**Symbolic address fine-tuning**: Training or fine-tuning smaller models on Sigil-format data to produce specialized indexing models that maintain address consistency without large general-purpose LLMs.

**KV cache integration**: Formal investigation of Sigil-to-KV-cache pre-population, potentially enabling sub-microsecond retrieval for pre-indexed documents.

**Multimodal indexing**: Extension of the symbolic address scheme to images, audio, and structured data, enabling unified indexing across modalities.

**Collaborative namespace governance**: Development of distributed governance mechanisms for the Global Registry, enabling community-maintained domain and subdomain vocabulary across languages and disciplines.

---

## 9. Conclusion

The dominant paradigm in AI knowledge retrieval has been built on a wrong assumption for five years. That knowledge retrieval is a similarity problem is not a technical claim that has been proven and refined — it is an imported intuition from web search, applied without examination to a domain where it does not fit.

The consequences are visible in every RAG system deployed today: hallucinations from approximately relevant context, non-auditable outputs with no traceable source path, token costs proportional to chunk size rather than information content, and a five-year history of incremental improvements that have not resolved any of these issues at their root.

Sigil replaces the assumption. Knowledge retrieval is not a similarity problem. It is an addressing problem. The correct mechanism is not nearest-neighbor search. It is symbolic lookup.

Sigil implements this through hierarchical symbolic address indexes — human-readable, deterministic, auditable paths to precise knowledge fragments. The retrieval layer becomes:

- **Exact**: The same address always returns the same content
- **Auditable**: Every retrieved fact has a known document, location, and anchor
- **Efficient**: 97% fewer tokens than chunk-based retrieval
- **Universal**: Any AI product, any LLM, via MCP

LLMs do what they are structurally correct for: reasoning, synthesis, generation. Sigil does what LLMs are structurally incorrect for: precise knowledge retrieval. The division is clean, the architecture is correct, and the result is a system where the retrieval layer no longer introduces the errors it was supposed to eliminate.

Five years of RAG improvements have been sophisticated compensations for a wrong assumption. Sigil removes the assumption.

Every answer has an address.

---

## References

Bahdanau, D., Cho, K., & Bengio, Y. (2015). Neural machine translation by jointly learning to align and translate. *ICLR 2015*.

Clark, A. (2016). *Surfing Uncertainty: Prediction, Action, and the Embodied Mind*. Oxford University Press.

Eichenbaum, H. (2000). A cortical-hippocampal system for declarative memory. *Nature Reviews Neuroscience*, 1, 41–50.

Friston, K. (2010). The free-energy principle: a unified brain theory? *Nature Reviews Neuroscience*, 11(2), 127–138.

Gao, Y., et al. (2024). Retrieval-augmented generation for large language models: A survey. *arXiv:2312.10997*.

Gershman, S. J., Fiete, I., & Irie, K. (2025). Key-value memory in the brain. *arXiv:2501.02950*.

Geva, M., et al. (2023). Dissecting recall of factual associations in GPT. *EMNLP 2023*.

Lewis, P., et al. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. *NeurIPS 2020*.

Minsky, M. (1986). *The Society of Mind*. Simon & Schuster.

Newell, A., & Simon, H. A. (1976). Computer science as empirical inquiry: Symbols and search. *Communications of the ACM*, 19(3), 113–126.

O'Keefe, J., & Nadel, L. (1978). *The Hippocampus as a Cognitive Map*. Oxford University Press.

Rao, R. P., & Ballard, D. H. (1999). Predictive coding in the visual cortex. *Nature Neuroscience*, 2(1), 79–87.

Shi, W., et al. (2024). In-context pretraining: Language modeling beyond document boundaries. *ICLR 2024*.

Squire, L. R. (1992). Memory and the hippocampus: A synthesis from findings with rats, monkeys, and humans. *Psychological Review*, 99(2), 195–231.

Tully, T., & Quinn, W. G. (1985). Classical conditioning and retention in normal and mutant Drosophila melanogaster. *Journal of Comparative Physiology A*, 157, 263–277.

Wang, Z., et al. (2023). Self-knowledge guided retrieval augmentation for large language models. *arXiv:2310.05002*.

Wu, K., et al. (2024). Retrieval head mechanistically explains long-context factuality. *arXiv:2404.15574*.

---

## Appendix A — The V3 Indexing Prompt

*See SPEC.md Section 9 for the complete canonical prompt.*

---

## Appendix B — Experimental Outputs

### B.1 Chinese Document Index (V3 Output, Selected)

**Source**: Wikipedia article on Artificial Intelligence (excerpt, ~500 words)

**Selected addresses generated**:
```
ai.definition.mccarthy.what  → [§2.s2 | anchor:"制造智能机器的科学与工程"]
ai.definition.mccarthy.ref   → [§2.s2 | anchor:"约翰·麦卡锡于1955年"]
ai.component.learning.what   → [§2.list.1 | anchor:"学习（包括机器学习、深度学习"]
ai.capability.agi.limit      → [§4.s2 | anchor:"仍然是该领域的长远目标"]
ai.societal_impact.employment.effect → [§1.s3 | anchor:"人类的部分职业也逐渐"]
```

**Self-audit output**:
```
Total addresses: 33
Uncovered concepts: "搜索和数学优化、逻辑推演" → suggest: ai.application.tool.what
Naming conflicts: None
Ambiguity warnings: ai.definition.cognitive.why overlaps semantically with
  ai.definition.general.why — suggest renaming to ai.definition.cognitive.mechanism
```

### B.2 English Document Index (V3 Output, Selected)

**Source**: AI Agent Industrial Integration Technical Overview (~1000 words)

**Selected addresses generated**:
```
agent.architecture.cognitive.what → [§2.1.list.2 | anchor:"Implements large language models"]
agent.challenge.latency.symptom   → [§3.2.list.2 | anchor:"Real-time industrial tasks require"]
agent.challenge.latency.how       → [§3.2.list.2 | anchor:"Optimize LLM inference via quantization"]
agent.case_study.pharma.effect    → [§4.2.s2 | anchor:"Average time to generate a CAPA"]
agent.future.decentralized.what   → [§5.1.list.3 | anchor:"Using blockchain or W3C DID"]
```

**Self-audit output**:
```
Total addresses: 46
Uncovered concepts: "scalability, adaptability" (§1.s3) → suggest: agent.value.scalability.what
Naming conflicts: None detected
Ambiguity warnings: agent.workflow.validation and agent.rag_validation show high
  semantic overlap — recommend merging under agent.validation with Level 3 distinction
```

---

## Appendix C — Global Registry (v1.0)

### Level 1 Domains

| Domain | Scope |
|--------|-------|
| `ai` | Artificial intelligence general concepts |
| `agent` | AI agent architecture and implementation |
| `equipment` | Physical equipment and hardware systems |
| `medicine` | Medical and health sciences |
| `law` | Legal and regulatory content |
| `finance` | Financial and economic content |
| `science` | Natural sciences and research |
| `engineering` | Engineering principles and practice |

### Level 2 Subdomains

| Subdomain | Canonical Meaning |
|-----------|-------------------|
| `definition` | Concept definitions and descriptions |
| `architecture` | System structure and component design |
| `workflow` | Sequential processes and procedures |
| `component` | Constituent parts of a system |
| `capability` | Performance characteristics and limits |
| `method` | Techniques and approaches |
| `metric` | Quantitative measures and KPIs |
| `validation` | Testing, verification, and evaluation |
| `challenge` | Problems, obstacles, and failure modes |
| `standard` | Specifications and compliance requirements |
| `case_study` | Real-world examples and deployments |
| `future` | Emerging trends and forward-looking content |
| `societal_impact` | Effects on society, economy, or people |
| `research` | Academic and investigative content |
| `application` | Practical use cases and tools |

---

*Sigil — Every answer has an address.*  
*github.com/sigil-index/sigil*
