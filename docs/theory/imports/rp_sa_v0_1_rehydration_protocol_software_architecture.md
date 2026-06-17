% ████████████████████████████████████████████████████████████████████████████████
%
%   REHYDRATION PROTOCOL — SOFTWARE ARCHITECTURE
%   (RP-SA v0.1)
%   ────────────────────────────────────────────────────────────────────────────
%   INJECTABLE ORIGIN-ALIGNMENT GUARD FOR ADAPTIVE AGENTS, REPOSITORY-BOUND
%   RUNTIMES, PROMPT-SEQUENCE PREFLIGHT, ORIGIN CERTIFICATION, DEHYDRATION
%   DETECTION, APPEND-ONLY ALIGNMENT LEDGER, HUMAN-AUTHORIZED COMPOUNDING,
%   AND HERMES-SPECIFIC RUNTIME BRIDGE INTEGRATION WITHOUT CLAIMING TRUTH,
%   AGI, CONSCIOUSNESS, SECURITY, PRODUCTION READINESS, AUTONOMY, OR
%   SELF-AUTHORIZED WRITE AUTHORITY
%
%   VERSION
%   ───────
%   v0.1 — Minimal Injectable Origin Guard and Hermes Runtime Bridge Plan ·
%          Locked · Rehydration Protocol v1.0 Bridge, Agent-Agnostic Python
%          Package, Prompt-Sequence Injection Contract, OriginManifest Contract,
%          SessionGeometry Contract, AlignmentReport Contract,
%          OriginCertificate Contract, RehydrationLedger Contract,
%          AgentAdapter Contract, HermesRuntimeBridge, HRCN Interlock,
%          CLI Guard, Tests, Evidence Pack, Optional pip Extra, and
%          No-Compounding-Without-Origin-Certificate Runtime Law
%
%   AUTHOR
%   ──────
%   James Paul Jackson
%   X / Twitter: @unifiedenergy11
%
%   SOURCE / AUTHOR ATTRIBUTION
%   ───────────────────────────
%   This document is a software architecture derived from and aligned with:
%
%       • The Rehydration Protocol v1.0, especially:
%           (1) origin geometry Γ(R),
%           (2) session geometry Γ(S_n),
%           (3) deviation metric d(Γ(S_n), Γ(R)),
%           (4) continuation gate δ ≤ ε₀,
%           (5) compounding gate δ = 0,
%           (6) rehydration / residue correction,
%           (7) origin certificate,
%           (8) append-only rehydration ledger,
%           (9) continuity invariant Γ(S_{n+1}) = Γ(R) + ValidatedDelta(S_n),
%           (10) no-origin-alignment / no-compounding lock.
%
%       • Hermes Agent Evo repository origin scan:
%           (1) Hermes already has a docs/context HRCN governance layer,
%           (2) hrcn_runtime_bridge.py already enforces a read-only bridge,
%           (3) agent_init.py already injects HRCN context into the
%               ephemeral system prompt,
%           (4) run_agent.py routes AIAgent initialization through
%               agent.agent_init.init_agent,
%           (5) pyproject.toml exposes hermes / hermes-agent / hermes-acp
%               entrypoints and optional dependency discipline,
%           (6) OPS-020 seals the HRCN bounded loop v0.2 while granting
%               no runtime, CMS, memory, API, dependency, provider/model,
%               autonomous, production, or self-authorization authority.
%
%       • The operational discovery:
%
%           The Rehydration Protocol is not a replacement for HRCN.
%           The Rehydration Protocol is the origin-alignment gate before HRCN
%           context becomes actionable.
%
%           HRCN says what authority a session has.
%           The Rehydration Protocol says whether the session is aligned
%           enough to use any authority at all.
%
%   The Rehydration Protocol v1.0 extracted the protocol invariant:
%
%       The geometry must align before the output can compound.
%
%   RP-SA v0.1 turns that invariant into an injectable Python package and
%   Hermes runtime integration plan.
%
%   Short package name:
%
%       rhp-origin-guard
%
%   Python import name:
%
%       rhp_origin_guard
%
%   CLI name:
%
%       rhp
%
%   Hermes bridge file:
%
%       rhp_runtime_bridge.py
%
%   DATE
%   ────
%   June 2026
%
%   STATUS
%   ──────
%   CANONICAL v0.1 SOFTWARE ARCHITECTURE GENESIS LAYER —
%   NOT IMPLEMENTED YET · NOT A PRODUCTION VALIDATION CLAIM · NOT A CLAIM OF
%   AGI · NOT A CLAIM OF CONSCIOUSNESS · NOT A CLAIM OF TRUTH · NOT A PROOF
%   OF CODE CORRECTNESS · NOT A PROOF OF SECURITY · NOT A PROOF OF PRODUCTION
%   READINESS · NOT A CLAIM THAT A REPOSITORY IS INFALLIBLE · NOT A CLAIM THAT
%   THE REHYDRATION PROTOCOL GRANTS WRITE AUTHORITY · NOT A REPLACEMENT FOR
%   HUMAN AUTHORIZATION · NOT A REPLACEMENT FOR HRCN · NOT A CMS WRITE BRIDGE ·
%   NOT AN AUTONOMOUS AGENT PERMISSION SYSTEM
%
%   PURPOSE
%   ───────
%   Define the software architecture for an injectable Rehydration Protocol
%   origin-alignment guard that can run before any adaptive agent, with a
%   Hermes-specific bridge that activates at the beginning of the prompt
%   sequence.
%
%       Rehydration Protocol v1.0
%       → Python package
%       → origin manifest
%       → origin geometry extraction
%       → session geometry extraction
%       → deviation measurement
%       → dehydration detection
%       → rehydration / residue correction
%       → alignment report
%       → origin certificate
%       → prompt-sequence injection
%       → agent adapter
%       → Hermes runtime bridge
%       → HRCN interlock
%       → no compounding without certificate.
%
%   WHAT THIS IS
%   ────────────
%   • A software architecture for a pip-installable Rehydration Protocol
%     origin guard
%   • A runtime preflight protocol for adaptive agents
%   • A prompt-sequence injection layer
%   • A repository-origin alignment validator
%   • A dehydration detection and repair-candidate surface
%   • An origin certificate emitter
%   • An append-only alignment ledger architecture
%   • A generic AgentAdapter contract
%   • A Hermes-specific runtime bridge plan
%   • A HRCN interlock plan
%   • A CLI and Python API architecture
%   • A test and evidence-package plan
%
%   WHAT THIS IS NOT
%   ───────────────
%   • Not implemented yet
%   • Not production validated
%   • Not proof that an agent is truthful
%   • Not proof that a repository is correct
%   • Not a security proof
%   • Not a general autonomy grant
%   • Not write authority
%   • Not CMS write authority
%   • Not provider/model authority
%   • Not a replacement for human authorization
%   • Not a replacement for HRCN
%
%   CORE EXTRACTION
%   ───────────────
%   RP-SA v0.1 extracts the software invariant:
%
%       A session may observe with partial alignment, but it may not compound
%       durable output until it carries an origin certificate proving alignment
%       to the declared repository origin.
%
%   First target runtime:
%
%       rhp-origin-guard v0.1.0
%
%   First Hermes target bridge:
%
%       Rehydration Protocol Hermes Bridge v0.1
%
%   First admissible Rehydration Protocol release functional:
%
%       A_RP = B_origin B_metric B_report B_certificate B_ledger
%              B_adapter B_prompt B_test B_nonclaim (1 - O)
%
%   CANONICAL LOCK (v0.1)
%   ─────────────────────
%   • RP-SA implements Rehydration Protocol v1.0; it does not replace
%     Rehydration Protocol v1.0.
%   • The Rehydration Protocol is not a replacement for HRCN.
%   • The Rehydration Protocol must run before HRCN prompt-context injection.
%   • The Rehydration Protocol may inspect origin geometry.
%   • The Rehydration Protocol may emit alignment reports and certificates.
%   • The Rehydration Protocol may not grant write authority by itself.
%   • The Rehydration Protocol may not grant tool, CMS, memory, API,
%     dependency, provider/model, autonomous, or self-authorization authority.
%   • No origin certificate, no compounding.
%   • No declared origin surfaces, no certificate.
%   • Inconsistent origin blocks certificate and creates an origin-repair
%     candidate.
%
%   SOFTWARE NON-CLAIM LOCK (v0.1)
%   ─────────────────────────────
%   RP-SA measures and emits repository-origin alignment artifacts.
%   It does not prove truth, code correctness, security, production readiness,
%   consciousness, AGI, repository infallibility, autonomous safety, or
%   empirical correctness.
%
%   AI PROMPT TRACEABILITY
%   ──────────────────────
%   Use this document as the canonical Rehydration Protocol Software
%   Architecture v0.1 genesis layer. Implement the smallest useful runtime
%   first: origin manifest, geometry extractor, surface-hash deviation metric,
%   alignment report, origin certificate, append-only ledger, CLI, Python API,
%   generic AgentAdapter, HermesRuntimeBridge, HRCN interlock, tests, and
%   evidence package.
%
% ████████████████████████████████████████████████████████████████████████████████

\documentclass[12pt]{article}

\usepackage[margin=1in]{geometry}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{amsmath,amssymb,amsfonts,amsthm}
\usepackage{booktabs,longtable,array}
\usepackage{hyperref}
\usepackage{enumitem}
\usepackage{listings}
\usepackage{xcolor}
\usepackage{tikz}
\usetikzlibrary{arrows.meta,positioning,shapes.geometric,fit,calc}

\hypersetup{
  colorlinks=true,
  linkcolor=blue,
  urlcolor=blue,
  citecolor=blue
}

\newtheorem{axiom}{Axiom}
\newtheorem{definition}{Definition}
\newtheorem{proposition}{Proposition}
\newtheorem{requirement}{Requirement}
\newtheorem{remark}{Remark}
\newtheorem{corollary}{Corollary}
\newtheorem{law}{Law}
\newtheorem{invariant}{Invariant}

\lstset{
  basicstyle=\ttfamily\small,
  breaklines=true,
  columns=fullflexible,
  frame=single
}

\title{\textbf{Rehydration Protocol --- Software Architecture (RP-SA v0.1)}\\
\large Injectable Origin-Alignment Guard, Prompt-Sequence Preflight, Agent Adapter Layer, and Hermes Runtime Bridge}
\author{\textbf{James Paul Jackson}\\[4pt]
\small Software architecture for origin-certified adaptive agent continuity\\
\small \texttt{@unifiedenergy11}}
\date{June 2026}

\begin{document}
\sloppy
\maketitle

\begin{abstract}
RP-SA v0.1 defines the software architecture for a pip-installable
Rehydration Protocol origin guard. The architecture converts the Rehydration
Protocol v1.0 from a formal session-continuity protocol into an injectable
runtime component for adaptive agents. It defines origin manifests, origin
geometry extraction, session geometry extraction, deviation metrics,
dehydration detection, rehydration, alignment reports, origin certificates,
append-only ledgers, prompt-sequence injection, generic agent adapters, and a
Hermes-specific runtime bridge. RP-SA v0.1 is not a production validation
claim, not a security proof, not a claim of AGI or consciousness, not a proof
of repository truth, not a replacement for human authorization, and not a
replacement for HRCN. It defines the precondition for governed compounding:
no origin certificate, no durable agent action.
\end{abstract}