Toy Conjectures Benchmark
==========================

A deterministic family of 64 labelled candidates. A candidate is
"accepted" by the oracle iff its integer suffix ends in 3 or 7.
This gives a 2/10 base acceptance rate and a bounded candidate set
on which Grover's theoretical iteration bound can be verified
exactly. No external services required.

Oracle predicate:
    f(candidate_proof_of_lemma_k) = 1 iff k % 10 in {3, 7}

Expected PoV metrics with ablation=none:
    candidate_space_size        == 64
    accepted_in_oracle          == 13
    grover_theoretical_iters    == floor(pi/4 * sqrt(64/13)) == 1
    tier3_pass                  == True

This benchmark tests: Prajna compression ratio, Grover iteration
count matching theory, tier-3 composition, and Reflexion idle
behaviour on a positive run.
