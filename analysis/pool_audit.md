# Pool audit (100K AceReason-1.1-SFT subset)

Tokenizer: Qwen2.5-3B-Instruct. Truncation = prompt+response > 16384 (training cutoff_len). Contamination = >= 50% of an eval question's 8-grams present in the pool prompt.

## By domain

| domain | n | unique prompts | resp p50 | resp p90 | resp p99 | resp max | truncated | no </think> | has_boxed | flagged | contam |
|---|---|---|---|---|---|---|---|---|---|---|---|
| code | 32568 | 24391 | 6120 | 14004 | 16302 | 30785 | 2.8% | 0.0% | 0.0% | 0.0% | 27 |
| math | 67432 | 59702 | 6641 | 14238 | 17712 | 31669 | 3.7% | 0.0% | 99.3% | 0.0% | 64 |

## By source

| domain | source | n |
|---|---|---|
| math | OpenMathReasoning | 54213 |
| code | OpenCodeReasoning | 19235 |
| math | NuminaMath-CoT | 13219 |
| code | opc-sft-stage2 | 8016 |
| code | leetcode | 3101 |
| code | TACO | 1437 |
| code | MagicoderEvolInstruct | 688 |
| code | apps | 91 |

## Math: answer kinds (R1's last \boxed{})

| answer_kind | n |
|---|---|
| numeric | 35210 |
| expression | 27261 |
| text | 3632 |
| mc | 1304 |
| none | 25 |

proof_like: 4176 (6.2%). `text` answers (e.g. `\boxed{\text{The pentagon is regular.}}`) cannot be graded and give no pass-rate signal.

## Quality flags

| flag | math | all |
|---|---|---|
| flag_repetition | 4 | 6 |
| flag_lang_mix | 5 | 5 |
| flag_malformed | 0 | 0 |
| truncated | 2525 | 3452 |

## Duplicate prompts (multiple R1 responses)

| responses per prompt | prompts |
|---|---|
| 1 | 71628 |
| 2 | 10247 |
| 3 | 1546 |
| 4 | 405 |
| 5 | 129 |
| 6 | 64 |
| 7 | 37 |
| 8 | 18 |
| 9 | 9 |
| 10 | 3 |
| 11 | 7 |

## Math rows surviving the basic filter

not truncated & has_boxed & not contam & not flagged: **64646** rows, 57350 unique prompts; excluding proof_like: 60582 rows.

## Contamination: 91 pool rows match an eval question

| contam_bench | rows | eval_questions |
|---|---|---|
| amc | 4 | 4 |
| math | 54 | 19 |
| olympiadbench | 33 | 27 |

Top matches:

- `math` score 1.00 -- pool: 'Let \\( P(x) \\) be a quadratic polynomial with real coefficients satisfying \n\\[ x^2 - 2x + 2 \\le P(x) \\le 2x^2 ' / eval: 'Let $P(x)$ be a quadratic polynomial with real coefficients satisfying $x^2 - 2x + 2 \\le P(x) \\le 2x^2 - 4x + '
- `olympiadbench` score 1.00 -- pool: 'Eight students attend a Harper Valley ARML practice. At the end of the practice, they decide to take selfies t' / eval: 'Eight students attend a Harper Valley ARML practice. At the end of the practice, they decide to take selfies t'
- `olympiadbench` score 1.00 -- pool: 'Compute the smallest possible value of \\( n \\) such that two diagonals of a regular \\( n \\)-gon intersect at a' / eval: 'Compute the smallest possible value of $n$ such that two diagonals of a regular $n$-gon intersect at an angle '
- `amc` score 1.00 -- pool: 'How many ordered pairs of positive real numbers $(a,b)$ satisfy the equation\n\\[(1+2a)(2+2b)(2a+b) = 32ab?\\]' / eval: 'How many ordered pairs of positive real numbers $(a,b)$ satisfy the equation\n\\[(1+2a)(2+2b)(2a+b) = 32ab?\\]'
- `olympiadbench` score 1.00 -- pool: 'An integer-valued function \\( f \\) is called tenuous if \\( f(x) + f(y) > x^2 \\) for all positive integers \\( x' / eval: 'An integer-valued function $f$ is called tenuous if $f(x)+f(y)>x^{2}$ for all positive integers $x$ and $y$. L'
- `math` score 1.00 -- pool: 'For how many real values of $x$ is $\\sqrt{120-\\sqrt{x}}$ an integer?' / eval: 'For how many real values of $x$ is $\\sqrt{120-\\sqrt{x}}$ an integer?'
- `amc` score 1.00 -- pool: 'How many complex numbers satisfy the equation $z^{5}=\\overline{z}$, where $\\overline{z}$ is the conjugate of t' / eval: 'How many complex numbers satisfy the equation $z^5=\\overline{z}$, where $\\overline{z}$ is the conjugate of the'
- `olympiadbench` score 1.00 -- pool: 'A diagonal of a regular 2006-gon is called odd if its endpoints divide the boundary into two parts, each compo' / eval: 'A diagonal of a regular 2006-gon is called odd if its endpoints divide the boundary into two parts, each compo'

Dev-set overlap (contam_dev): 81 rows.
