# Evaluating the Quality of LLM-Generated SPARQL Queries

## Overview

This repository contains the code, datasets, and analysis developed during the EURECOM Semester Project:

**Evaluating the Quality of LLM-Generated SPARQL Queries**

The project investigates how to evaluate Text2SPARQL systems beyond traditional execution-based metrics by introducing a property-level semantic analysis framework.

Instead of only checking whether a generated SPARQL query returns the correct answer, this work studies:

* Missing Wikidata properties
* Hallucinated properties
* Property-level precision, recall, and F1 score
* Semantic differences between queries
* Execution correctness
* LLM-based semantic interpretation

---

## Motivation

Most Text2SPARQL evaluation methods rely on:

* Execution Accuracy
* Answer-level F1 Score

However, these metrics do not explain:

* Why a generated query failed
* Which properties caused the error
* Whether the generated query followed a different semantic path

This project introduces a semantic evaluation workflow based on Wikidata properties extracted from SPARQL queries.

---

## Dataset

The experiments are based on the SPINACH benchmark dataset.

SPINACH contains:

* Natural language questions
* Ground-truth SPARQL queries
* Predicted SPARQL queries
* Execution scores

Repository:

https://github.com/ad-freiburg/grasp/tree/main/data/benchmark/wikidata/spinach

Dataset characteristics:

* 320 question-query pairs
* 155 validation examples
* 165 test examples
* Real Wikidata questions
* Complex multi-hop SPARQL queries

Examples frequently include:

* FILTER
* OPTIONAL
* UNION
* Property paths
* Aggregations
* Geographic reasoning

---

## Project Workflow

### 1. Property Extraction

Properties are extracted from:

* Ground-truth SPARQL queries
* Predicted SPARQL queries

Example:

```sparql
?person wdt:P19 ?birthPlace .
?person wdt:P21 ?gender .
```

Extracted properties:

```text
P19
P21
```

---

### 2. Property Comparison

For each query pair:

```text
Ground Truth Properties
vs
Predicted Properties
```

The framework identifies:

* Missing properties
* Extra properties
* Shared properties

---

### 3. Evaluation Metrics

#### Execution Score

Measures whether both queries return the same answer.

```text
1 = Correct execution
0 = Incorrect execution
```

#### Property Precision

```text
Precision = Shared / Predicted
```

#### Property Recall

```text
Recall = Shared / Ground Truth
```

#### Property F1

```text
F1 = 2PR / (P + R)
```

---

### 4. Property Impact Analysis

For every Wikidata property, we compute:

* Impact on execution score
* Impact on property F1 score

High-impact properties indicate relations that strongly influence query correctness.

Examples:

* P279 (subclass of)
* P131 (located in the administrative territorial entity)
* P361 (part of)

---

### 5. SPARQL Structure Analysis

The repository also analyzes structural SPARQL patterns:

* Triple Patterns
* FILTER
* FILTER NOT EXISTS
* OPTIONAL
* UNION
* ORDER BY
* GROUP BY
* HAVING
* LIMIT
* DISTINCT
* COUNT
* BIND
* VALUES
* SERVICE
* MINUS

The goal is to compare the complexity and structure of generated queries against ground-truth queries.

---

### 6. LLM-Based Interpretation

The project evaluates whether LLMs can automatically explain semantic differences between queries.

Approaches:

* Zero-shot prompting
* Few-shot prompting
* Structured JSON outputs
* Reasoning-based explanations

Model used:

```text
openai/gpt-oss-120b
```

---

## Repository Structure

```text
.
├── data/
│   ├── SPINACH dataset
│   └── processed datasets
│
├── scripts/
│   ├── property extraction
│   ├── impact computation
│   ├── SPARQL pattern analysis
│   ├── statistics generation
│   └── visualization scripts
│
├── outputs/
│   ├── CSV files
│   ├── Excel reports
│   ├── PNG figures
│   └── impact graphs
│
├── report/
│   └── Semester Project Report
│
└── README.md
```

---

## Main Findings

### Property-Level Evaluation Matters

Execution accuracy alone is insufficient.

Queries may:

* Share the same properties but fail execution.
* Use different properties but still return correct answers.

---

### High-Impact Properties

Several Wikidata properties strongly affect query correctness:

* P279 (subclass of)
* P131 (located in the administrative territorial entity)
* P17 (country)
* P361 (part of)
* P1001 (applies to jurisdiction)

---

### Structural Over-Generation

Generated queries frequently overuse:

* Triple patterns
* OPTIONAL
* FILTER
* ORDER BY
* BIND

This suggests that the model often generates more complex query structures than necessary.

---

### LLM Interpretations Are Useful

LLM-generated explanations successfully identify:

* Missing properties
* Hallucinated properties
* Alternative semantic paths
* Reasons for execution failures

---

## Generated Outputs

Examples of generated artifacts:

### Property Statistics

* Top property frequencies
* Missing property statistics
* Extra property statistics

### Impact Analysis

* Property impact on execution score
* Property impact on F1 score

### SPARQL Pattern Analysis

* Operation frequency comparison
* Structural complexity analysis
* Triple pattern statistics

### Visualizations

* Property frequency plots
* Evaluation case distributions
* Impact graphs
* SPARQL operation comparison charts

---

## Future Work

Possible extensions include:

* Exact graph-based SPARQL parsing
* Average path length computation
* Multi-hop reasoning analysis
* Query execution order analysis
* Structural similarity metrics
* Cross-dataset evaluation
* Automatic error correction suggestions

---

## Author

**Yassine Trabelsi**

Master of Science in Computer Science – Data Science Track

EURECOM

2026

---

## Supervisors

* Thibault Ehrhart
* Fanfu Wei
* Raphaël Troncy
