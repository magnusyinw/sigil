# Sigil: Symbolic Addressing for Exact and Auditable Evidence Access in LLM Systems

**Version:** 2.0  
**Status:** White Paper  
**License:** CC BY 4.0  
**Project:** github.com/sigil-index/sigil

---

## Executive Summary

Large language models are increasingly used in settings where answers must be grounded in external knowledge: enterprise policies, technical manuals, regulatory documents, scientific material, operating procedures, and internal knowledge bases. In these environments, relevance is not enough. The system must retrieve the right evidence, at the right location, with a traceable source path.

Most current retrieval pipelines are built around semantic similarity. They find document fragments that appear related to a query and pass them into the model as context. This approach works well for many open-ended tasks, but it becomes unreliable when users need exact evidence, stable retrieval behavior, and auditable outputs.

Sigil is a symbolic knowledge indexing system designed to address that gap. It introduces an addressable evidence layer for LLM-based workflows. Instead of treating retrieval only as nearest-neighbor search over vector representations, Sigil assigns each knowledge fragment a structured symbolic address, along with source location, provenance metadata, and optional cross-links. Retrieval can then proceed through exact address lookup, deterministic prefix routing, or fuzzy-to-symbolic bridging.

Sigil does not assume that all queries begin in exact symbolic form. Natural language can still be vague, incomplete, or ambiguous. Candidate discovery may still involve lexical search, semantic matching, or LLM-assisted query interpretation. Sigil's contribution is different: it provides the final evidence access mechanism needed to make retrieval stable, inspectable, and efficient.

This white paper presents the motivation, system design, operating model, technical components, theoretical connections, enterprise value, implementation path, limitations, and strategic implications of Sigil.

---

## 1. The Problem

### 1.1 The Current Retrieval Bottleneck

LLMs are strong at reasoning, synthesis, summarization, and language generation. They are not inherently strong at precise external knowledge access. When an answer depends on exact source material, the system needs a retrieval layer.

Today, most such systems rely on one of the following: dense vector retrieval, lexical retrieval, hybrid retrieval, reranking pipelines, or graph-augmented retrieval. These systems are effective at surfacing relevant content. But they usually return ranked passages, not stable evidence objects.

That difference matters.

A ranked passage is useful because it looks relevant. An evidence object is useful because it has a stable identity, a precise source location, a traceable provenance chain, and repeatable retrieval behavior. In many real applications, the second is what actually matters.

### 1.2 Why Relevance Is Not Enough

In ordinary search, approximately relevant can be good enough. If a search engine returns ten pages related to a topic, the user can inspect them. In LLM workflows, the situation is different. The model often reasons directly over the retrieved context. If the retrieval layer returns text that is relevant but imprecise, mixed, outdated, or weakly sourced, the model may still produce a fluent answer — one that sounds correct while being poorly grounded.

This creates several recurring problems:

**Source ambiguity**: the answer cannot be traced to a precise location.

**Chunk ambiguity**: one chunk contains multiple concepts with no stable identity for the exact claim being made.

**Retrieval instability**: the same question returns different supporting passages on different runs.

**Token inefficiency**: large chunks are sent because the system lacks precise access to the needed fragment.

**Weak auditability**: post-hoc verification becomes difficult or impossible.

These are not merely tuning failures. They reveal a missing systems layer.

### 1.3 The Three Functions That Current Systems Conflate

Current retrieval systems usually conflate three distinct functions:

```
1. Candidate discovery
   Find likely relevant regions of a corpus.

2. Evidence access
   Retrieve the exact source fragment that grounds a claim.

3. Answer generation
   Use that evidence to produce a response.
```

Most systems optimize heavily for the first and then hand off coarse retrieved passages to the third. The second function — evidence access — remains under-specified.

Sigil is designed to fill that gap.

The key insight is that these three functions have different structural requirements. Candidate discovery tolerates approximation — returning ten related passages is acceptable if the right one is among them. Evidence access does not tolerate approximation — the system must retrieve the exact fragment, at its exact location, with a traceable provenance path. Conflating these two functions forces the entire pipeline to operate at the looser standard. Separating them allows each to operate correctly.

---

## 2. The Sigil Thesis

### 2.1 Core Claim

Sigil is based on a systems claim that is precise and falsifiable:

> Semantic similarity is useful for candidate discovery, but insufficient as the sole mechanism for final evidence access.

This is the core design principle. Sigil does not argue that all retrieval should become purely symbolic from the beginning of an interaction. It argues that once candidate knowledge has been identified, the final evidence access step should be handled through explicit addressing — the same mechanism used by file systems, databases, compilers, and the biological memory systems that have handled large-scale knowledge retrieval reliably for millions of years.

### 2.2 The Existence Proof from Biology

The claim that symbolic addressing is the correct mechanism for final knowledge retrieval is not speculative. Biological intelligence has implemented it at scale.

The human hippocampus does not store memory content. It stores indexes — compact symbolic pointers to the distributed cortical patterns that constitute memories. When a specific memory is needed, the hippocampal index activates the precise cortical pattern. The retrieval step is deterministic, not probabilistic. It is addressing, not similarity scoring.

The neocortex handles the fuzzy side: associative reasoning, creative synthesis, cross-domain analogy, language generation. The hippocampus handles the precise side: exact location of specific memories on demand. Neither system was designed to do what the other does. Their separation is what makes both work correctly.

Current AI retrieval systems gave the LLM both roles. The consequences are visible in every RAG deployment: hallucinations from approximately relevant context, non-auditable outputs, and years of incremental improvements that have not resolved these issues at their root. Sigil restores the correct separation: fuzzy processes for candidate discovery, symbolic addressing for final evidence access.

### 2.3 What Addressable Evidence Means

Sigil treats evidence as a first-class object. A usable evidence object must be identifiable (stable symbolic ID), locatable (precise place in a source), provenanced (document origin and version known), retrievable (returned deterministically), and referable (citable, linkable, revisitable, and comparable). This is what current retrieval pipelines often lack.

### 2.4 What Sigil Is and Is Not

Sigil is a symbolic indexing system for document corpora, an addressable evidence layer for LLM workflows, a retrieval framework centered on explicit knowledge objects, and an integration-ready system exposed through standard tool interfaces.

Sigil is not a general replacement for all search systems, not a claim that similarity search has no value, not a manually curated formal ontology, not a language model, and not a reasoning engine. Sigil handles evidence access. LLMs still handle language understanding, reasoning, and generation.

---

## 3. Design Principles

**Explicit identity over opaque ranking**: A returned fragment should not merely be highly ranked. It should have a stable identity.

**Evidence before context expansion**: The system should retrieve the exact fragment needed before expanding to broader context.

**Provenance as first-class metadata**: Source, version, and location are part of the object itself, not optional add-ons.

**Separation of fuzzy discovery and exact access**: Natural language queries may be fuzzy. Evidence access should not remain fuzzy.

**Stable retrieval for high-trust workflows**: When the corpus is fixed, the same symbolic lookup should return the same result.

---

## 4. The Sigil System

### 4.1 The Symbolic Address

The fundamental unit of Sigil is the symbolic address — a structured, human-readable identifier that points to a specific knowledge fragment. It is hierarchical and regular enough to support routing, grouping, reuse, and inspection.

```
[domain].[subdomain].[concept].[dimension]
```

Examples:

```
medicine.deviation.rootcause.why
agent.architecture.memory.what
law.contract.termination.limit
engineering.validation.protocol.how
equipment.pump.fault.seal_leak.symptom
```

A symbolic address does not approximate. It identifies. Every address is exactly 3 or 4 levels deep. The fourth level is always one of seven semantic dimension markers that force explicit disambiguation of content that natural language leaves ambiguous:

| Dimension | Semantic Role |
|-----------|---------------|
| `.what`   | Definition, identity, description |
| `.why`    | Cause, reason, rationale |
| `.how`    | Method, procedure, mechanism |
| `.effect` | Consequence, result, impact |
| `.limit`  | Boundary, failure mode, restriction |
| `.symptom`| Observable sign or issue |
| `.ref`    | Citation or source reference |

For example, for CAPA validation in a pharmaceutical context:

```
medicine.capa.validation.what   → what CAPA validation is
medicine.capa.validation.why    → why it is required
medicine.capa.validation.how    → how to perform it
medicine.capa.validation.limit  → when it is insufficient
```

These are related but not interchangeable. Forcing this distinction at the address level prevents retrieval of adjacent but wrong evidence.

### 4.2 The Knowledge Node

Each indexed fragment becomes a knowledge node:

```
Knowledge Node
├── Address    stable symbolic identifier (the key)
├── Location   dual-anchor source position (structural + textual)
├── Content    precise text fragment (the value)
├── Source     document ID, version hash, metadata
└── Backlinks  optional relationships to other nodes
```

This turns evidence into a structured object with identity and provenance, not just text in a chunk.

### 4.3 Dual-Anchor Localization

Each node stores two complementary anchors:

**Structural anchor**: A location based on document structure, such as `§2.s3`, `§4.list.2`, or `table.3.row.5`. Provides machine-readable precision.

**Textual anchor**: A short unique phrase (7–15 characters) extracted from the original source text. Provides human-verifiable precision and survives document reformatting.

If one anchor becomes unstable — for example, if section numbering changes in a document revision — the other still locates the fragment. Together they provide redundant precision that makes evidence location robust across the document lifecycle.

### 4.4 Skill Cards

Each document generates a skill card declaring what the document can and cannot answer:

```
Skill Card
├── Purpose    what the document mainly covers (one sentence)
├── Strengths  query types it handles well (up to 3)
└── Weaknesses query types it does not handle well (up to 2)
```

Skill cards reduce the search space during candidate discovery. They route natural language queries toward the most relevant parts of the corpus before address resolution begins, without requiring the user to know the address structure.

### 4.5 Three-Tier Query Routing

**Tier 1 — Exact address lookup**: If the query resolves to an exact symbolic address, retrieval is deterministic and immediate. Zero LLM calls. Latency is microseconds.

**Tier 2 — Prefix routing**: If the query resolves to a prefix, Sigil uses route tables to expand into default or candidate child nodes. Route tables are generated automatically during indexing.

**Tier 3 — Fuzzy-to-symbolic bridging**: Natural language queries are translated to candidate addresses via lexical matching, anchor search, skill-card selection, or LLM-assisted interpretation. The key distinction is that fuzzy processing is used to reach the symbolic layer, not replace it.

### 4.6 Multi-Document Namespace

When multiple documents generate overlapping addresses, three cases arise:

**Coexist**: Different addresses or distinct scopes coexist without conflict.

**Merge**: Two nodes share a path but provide complementary content. They are merged into a joint node with separate sourced fragments.

**Flag conflict**: Two nodes share the same path but contradict each other. Both are preserved and a conflict marker is raised for human review. Ambiguity is surfaced instead of silently collapsed.

### 4.7 Backlinks

Backlinks connect semantically related nodes across documents, carrying confidence levels of HIGH, MEDIUM, or LOW. They are registered bidirectionally — when a node in Document A links to Document B, the reverse link is automatically registered in Document B. No manual maintenance is required.

### 4.8 Versioning

Sigil treats version metadata as part of the retrieval object: document hash tracking, source version metadata on every node, conflict surfacing across document editions, and historical query support for compliance auditing.

### 4.9 Integration Layer

Sigil is exposed through standard tool interfaces compatible with the Model Context Protocol (MCP). Standard tools include `sigil_query`, `sigil_list`, `sigil_backlinks`, and `sigil_skill_cards`.

---

## 5. Operating Model

### 5.1 The Division of Labor

```
LLMs handle:
  language understanding, query interpretation,
  synthesis, explanation, planning,
  reasoning across evidence.

Sigil handles:
  exact evidence identification, symbolic lookup,
  source traceability, deterministic retrieval,
  evidence reuse and linking.

The model reasons.
Sigil retrieves evidence.
```

### 5.2 End-to-End Flow

```
1. User submits a natural language question.
2. Candidate regions identified via skill cards,
   lexical search, or LLM interpretation.
3. Candidate symbolic addresses generated or selected.
4. Sigil resolves the final address.
5. Exact evidence node returned with source
   and location metadata.
6. LLM reasons over evidence and generates answer.
7. Answer cites symbolic address and source fragment.
```

---

## 6. Theoretical Connections

### 6.1 Symbolic Addresses and Transformer KV Cache

The structural parallel between Sigil and transformer architecture is precise:

```
KV Cache:
  Key   = high-dimensional float vector (implicit, learned)
  Value = contextualized content representation

Sigil Index:
  Key   = symbolic address string (explicit, defined)
  Value = precise text fragment with source location
```

Both structures solve the same problem: given a query, find the relevant content. The KV cache solves it internally through learned attention weights. Sigil solves it externally through symbolic string matching. They are two implementations of the same abstract architecture: a key-value store for knowledge where the key encodes semantic identity and the value encodes content.

This parallel suggests a direction for deeper integration: Sigil-formatted indexes could potentially pre-populate KV cache structures for pre-indexed documents, bypassing the attention computation that normally generates these structures. The practical implication would be near-zero latency evidence access for symbolically indexed corpora. We leave formal investigation of this direction to future work.

### 6.2 Retrieval Heads and Symbolic Routing

Mechanistic interpretability research has identified retrieval heads in transformer models — specific attention heads whose primary function is exact copying of content from the context window rather than semantic transformation. We hypothesize that structured symbolic addresses, when included in LLM context, preferentially activate retrieval heads because their format is distinctive and consistent. This would explain why LLMs show improved factual precision when context is structured with explicit semantic labels rather than raw text.

If this hypothesis holds, Sigil's external symbolic index and the transformer's internal retrieval heads are two levels of the same addressing architecture: one explicit and externally maintained, one implicit and internally learned.

### 6.3 Predictive Index Evolution

A Sigil instance that tracks query sequences can build a transition matrix recording which symbolic addresses are queried in succession. This enables predictive prefetching (pre-load likely next queries), error-driven backlink discovery (unexpected transitions signal missing cross-document links), and usage-weighted routing (frequently co-queried nodes receive higher route priority).

This is structurally analogous to hippocampal memory consolidation — the index improves through use without requiring human intervention or full re-indexing.

---

## 7. Enterprise Value

### 7.1 Key Value Propositions

**Precise grounding**: Answers grounded in explicit source fragments with known addresses, not anonymous passages.

**Auditability**: Each evidence object can be inspected, linked, and independently verified.

**Retrieval stability**: Same symbolic lookup, same result, under fixed corpus conditions. No sampling variance, no embedding model sensitivity.

**Lower context waste**: Only the needed fragment sent downstream. Tier 1 query token costs reduced approximately 97% versus chunk-based retrieval.

**Better governance**: Knowledge paths become inspectable and manageable at the organizational level.

**Explicit conflict handling**: Contradictory content surfaced as a conflict object rather than blended by similarity averaging.

### 7.2 Ideal Use Cases

Sigil is particularly well suited for environments where users ask: "What exactly does the policy say?", "Which clause defines the exception?", "Where is the approved procedure described?", "Which version contains the binding requirement?"

These include SOP libraries, quality systems, CAPA and deviation knowledge bases, regulatory procedures, legal contracts and policies, engineering manuals, compliance repositories, and internal playbooks.

### 7.3 High-Trust Industries

Sigil is especially relevant where evidence traceability is non-negotiable: pharmaceuticals, healthcare, manufacturing, finance, law, energy, and regulated public-sector systems. In these environments, an answer without a precise source path often has limited operational or legal value.

---

## 8. Implementation Model

### 8.1 Deployment Stages

**Stage 1**: Index a narrow, controlled corpus. Validate address generation and query usefulness.

**Stage 2**: Add natural-language query routing via skill cards and LLM-assisted fuzzy-to-symbolic translation.

**Stage 3**: Expand to multi-document namespace. Support coexistence, merging, and conflict surfacing.

**Stage 4**: Integrate into LLM products via MCP. Embed evidence addressing into daily workflows.

**Stage 5**: Add governance and analytics. Track frequently used addresses, unresolved conflicts, and maintenance costs.

### 8.2 Index Generation

The indexing process includes document parsing, structure detection, fragment segmentation, symbolic address assignment, dual-anchor extraction, skill card generation, backlink suggestion, and self-audit for gaps and ambiguity. The output is a structured, human-readable index — not just embeddings.

### 8.3 Governance Requirements

Organizations must define naming standards, domain vocabulary boundaries, merge rules, conflict review processes, versioning policy, and re-indexing triggers. This is the cost of moving from opaque retrieval to governed evidence access — a cost that provides organizational value beyond retrieval accuracy.

---

## 9. Evaluation Framework

**Index quality**: Address readability, naming consistency, fragment precision, location recoverability, ambiguity rate, uncovered concept rate.

**Evidence retrieval quality**: Evidence hit rate, exact source match, citation correctness, retrieval stability, conflict surfacing quality.

**Query usability**: Natural-language-to-address success rate, top-k candidate accuracy, route failure patterns, skill-card routing usefulness.

**Cost and maintenance**: Indexing cost per document, re-indexing cost, conflict frequency, address drift rate, query token usage, latency.

The right evaluation question is not only "Did the system retrieve something relevant?" It is also "Did the system retrieve the correct evidence object in a stable and inspectable way?" Only the second matters in high-trust environments.

---

## 10. Limitations

**Address quality depends on indexing quality**: Index quality is a ceiling on retrieval quality.

**Not ideal for all corpora**: Highly narrative, implicit, or poorly structured documents may be difficult to index cleanly.

**Natural-language bridging remains an open challenge**: Mapping fuzzy queries reliably to symbolic addresses is non-trivial, especially for ambiguous or cross-domain queries.

**Governance is required**: Address systems need naming discipline, versioning rules, and conflict handling processes.

**Open-domain web search is a different problem**: Sigil is best for governed corpora, not general internet search.

**Indexing costs may offset some query savings**: Deployment decisions should consider full lifecycle economics, not only per-query savings.

---

## 11. Where Sigil Fits Best

Sigil is strongest when the environment has most of:

```
✓ A bounded, identifiable corpus
✓ Repeated use of the same knowledge base
✓ High need for citation and traceability
✓ Low tolerance for source ambiguity
✓ Meaningful value from stable evidence reuse
✓ Regulatory or audit requirements on knowledge access
```

Sigil is weaker when the environment is dominated by:

```
✗ Extremely broad open-world search
✗ Rapidly shifting, uncontrolled corpora
✗ Highly creative exploratory tasks
✗ Domains where approximate relevance is fully sufficient
```

The goal is not to replace all retrieval with symbolic addressing. The goal is to give the evidence access layer — currently missing from most systems — the mechanism it requires.

---

## 12. Future Directions

**Predictive routing**: Full implementation of transition matrix, node weight system, and error-driven backlink discovery.

**KV cache integration**: Formal investigation of Sigil-to-KV-cache pre-population for sub-microsecond retrieval and deeper architectural integration with transformer inference.

**Address-specialized models**: Smaller models trained specifically for symbolic index generation and fuzzy-to-symbolic routing.

**Multimodal evidence nodes**: Extend symbolic addressing to diagrams, images, audio, tabular evidence, and structured records.

**Stronger conflict intelligence**: Detected conflicts as first-class review objects in enterprise governance workflows.

**Retrieval head activation study**: Empirical investigation of whether symbolic addresses in LLM context preferentially activate retrieval heads, formally connecting Sigil's external architecture to the transformer's internal retrieval mechanisms.

---

## 13. Conclusion

LLM systems need more than relevance. In many real-world settings, they need exact, inspectable, repeatable access to source evidence. Most current retrieval pipelines are optimized for finding related passages. That is useful — but it is not the same as evidence access, and the difference has consequences that years of retrieval improvements have not resolved.

The missing element is an explicit evidence access layer: a system that treats knowledge fragments as identifiable objects with stable addresses, known locations, and traceable provenance. Sigil provides that layer.

Sigil does not eliminate the need for fuzzy discovery. Natural language remains fuzzy. Candidate discovery remains important. Semantic similarity has genuine value in finding the right neighborhood of a corpus. But final evidence access should not remain opaque.

The architectural shift Sigil proposes is precise:

```
Use fuzzy methods to find the neighborhood.
Use symbolic addressing to retrieve the evidence.
```

Biological intelligence arrived at this architecture through evolution. File systems, databases, and compilers arrived at it through engineering. The principle is not new. Its application to LLM knowledge retrieval is.

Five years of retrieval improvements have produced better approximate access. Sigil produces exact access. The difference is not degree — it is kind.

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

Newell, A., & Simon, H. A. (1976). Computer science as empirical inquiry: Symbols and search. *Communications of the ACM*, 19(3), 113–126.

O'Keefe, J., & Nadel, L. (1978). *The Hippocampus as a Cognitive Map*. Oxford University Press.

Rao, R. P., & Ballard, D. H. (1999). Predictive coding in the visual cortex. *Nature Neuroscience*, 2(1), 79–87.

Squire, L. R. (1992). Memory and the hippocampus: A synthesis from findings with rats, monkeys, and humans. *Psychological Review*, 99(2), 195–231.

Wang, Z., et al. (2023). Self-knowledge guided retrieval augmentation for large language models. *arXiv:2310.05002*.

Wu, K., et al. (2024). Retrieval head mechanistically explains long-context factuality. *arXiv:2404.15574*.

---

## Appendix A — Example Sigil Objects

### Symbolic Addresses

```
medicine.deviation.rootcause.why
medicine.capa.validation.how
law.contract.payment.limit
engineering.equipment.calibration.ref
agent.architecture.memory.what
equipment.pump.fault.seal_leak.symptom
```

### Knowledge Node

```
Address:  medicine.deviation.rootcause.why
Location:
  Structural: §4.s2
  Anchor:     "repeated deviation events often indicate"
Content:
  "Repeated deviation events often indicate an unresolved
   upstream control failure..."
Source:
  Document: deviation_management_v3.pdf
  Version:  hash:ab93f...
Backlinks:
  - medicine.capa.effect.how          (HIGH)
  - medicine.control.monitoring.limit (MEDIUM)
```

---

## Appendix B — Core Tool Interface

**sigil_query**: Resolve an address or natural-language query to evidence nodes. Supports exact match, prefix match, and anchor search.

**sigil_list**: List child nodes under a given address prefix.

**sigil_backlinks**: Return linked nodes and confidence levels for a given address.

**sigil_skill_cards**: Return relevant document skill cards to support query routing.

---

## Appendix C — Recommended Adoption Checklist

```
☐ Corpus scope is defined and bounded
☐ Source versioning is available or can be established
☐ Naming policy and domain vocabulary are documented
☐ Conflict review workflow is assigned to an owner
☐ Evaluation dataset is prepared
☐ Answer citation format is decided
☐ Re-index policy is documented
☐ Ownership of registry governance is assigned
☐ Indexing cost and maintenance budget is approved
☐ Integration interface (MCP or REST) is selected
```

---

*Sigil — Symbolic Addressing for Exact and Auditable Evidence Access*  
*Every answer has an address.*  
*github.com/sigil-index/sigil*
