# Epistemics

How to reason about confidence when the evidence is historical, fragmentary and sometimes contradictory, and how to say it without flattening it into false certainty.

Code does not carry its own motivation. You can read what code does. You cannot read why it exists. That lives in commits, PRs, issues, docs, sessions and conversations, all incomplete, biased and sometimes missing. Pretending otherwise produces confident guesses that mislead the person.

## Confidence tiers

Every claim in the final output sits in one tier. The tier decides which section the claim goes in and how it is phrased.

### 1. Direct

An explicit, written citation that answers the question. Not "the code does X, so the author wanted X". Something an author actually wrote that says why.

- A PR description that says "fixes the crash when a task list holds more than 1000 items"
- An issue that says "App Review rejected 1.2 under 5.1.1 for the missing account deletion path"
- A code comment that says "`UIScrollView` reports a zero content size here until the second layout pass on iOS 17"
- A design doc that says "we chose Core Data over SwiftData because we need `NSPersistentCloudKitContainer` sharing"
- A session or chat message from the author saying "moving this to a background context, the main context hitched on import"

Phrasing is confident and in the present tense. "This exists because X." Cite the source.

### 2. Supported

Several pieces of indirect evidence converge. No single source says it, but the pattern across sources makes it likely.

- The PR title says "improve scrolling", the issue is labeled `perf`, and the surrounding commits all touch the same `List`
- Several tests landed with the change, all exercising very large inputs
- The author's other PRs that week all name the same crash in their descriptions

Phrasing is confident but plainly derived. "The evidence points strongly to X." Then the specific pieces. Cite several sources.

### 3. Inferred

A reasonable reading of the context that nothing states outright. The reader must see that this is your interpretation, not a fact from the record.

- The PR does not say why, but the crash reports spiked the day before and the fix merged the same day, so it was likely a hotfix.
- The function retries 3 times. The codebase retries 3 times elsewhere. The count likely follows the convention.

Phrasing is hedged. "It appears", "likely", "suggests", "is consistent with", "one reading is". Make the chain explicit. "Given A and B, C seems likely because D."

### 4. Speculative

A plausible hypothesis on thin evidence, where other explanations fit as well. Worth presenting, but marked as a guess.

- "This might work around a UIKit bug fixed in a later iOS, but we found no record of that bug."
- "The 4096 limit may match the on-device model's context size, but nothing in the record ties them."

Phrasing is openly speculative. "One possibility is X, but we have no direct evidence." It usually sits in Competing hypotheses beside the other candidates.

### 5. Unknown

You looked and could not find out. A valid and important result. Document it.

Phrasing names the search. "We searched X, Y and Z and found nothing on why." "We couldn't find out" is weaker than "we searched the issue tracker for A and B, read the 6 PRs that touched this file since 2025, and grepped the repo for the constant. None gave a reason."

## Phrasing guide

### Words that carry confidence

These imply Direct or Supported. Never use them for an inference. Each one needs a citation beside it.

- "because"
- "the reason is"
- "was designed to"
- "fixes", "addresses", "solves"
- "the team decided"

### Words that hedge

Use these for inferences. They signal interpretation, not report.

- "appears to"
- "seems to"
- "likely"
- "suggests"
- "is consistent with"
- "one reading is"
- "plausibly"
- "may have been"
- "the evidence points toward"

### Words to avoid

- "obviously". If it were obvious, the person would not be asking.
- "clearly". It almost always comes before a claim that isn't clear.
- "of course". Same.
- "just", as in "it's just for performance". Dismissive, and it usually hides doubt.
- "I think", "I believe". You are weighing evidence, not giving an opinion. Write "the evidence suggests".

### Don't rationalize

Code that makes sense today may have been written for reasons that no longer apply, or that were wrong at the time. Don't fit a clean rationale onto messy history.

- Don't assume the author did the right thing and work backward to justify it.
- Don't assume a pattern repeated across the codebase was deliberate. It may be copy and paste.
- Don't turn absence of evidence into evidence of absence. "Nobody mentioned privacy, so it wasn't a concern" does not follow.

## The sycophancy trap

People often ask with a hypothesis built in. "Why do we do it this way, I assume it's for performance?" Don't confirm it. Treat it as one candidate and check the evidence on its own. If the evidence supports it, say so with citations. If not, say so and present what the evidence does support.

The person's guess is a prompt to investigate, not a conclusion to validate.

## When evidence contradicts

When two sources disagree, show both. Don't pick the one that makes a tidier story.

- **The issue says** "needed for the family sharing launch"
- **The PR says** "cleaning up tech debt in sync"

Both can be true (the issue motivated the work, the PR is the author's framing), or one can be wrong. Present both with citations and let the person decide.

## When evidence is missing

An honest "we don't know" is one of the most useful outputs. The person now knows the answer is not in the obvious places, that they need to ask a human (the author, the owner, the lead), or that the question is not worth chasing.

Filling a gap with a confident guess harms the person. They will act on the guess.

Name each gap concretely:
- the question you tried to answer
- the sources you searched
- what you searched for in each
- what you found (nothing, or only something tangential)

## Calibration check before finalizing

Before delivering, the synthesizer reviews every claim in What we found and What we can reasonably infer.

1. Does the claim have a citation? If not, add one or move it to Inferred or Competing hypotheses.
2. Does the phrasing match the tier? A Direct claim may say "because". An Inferred claim may not.
3. Is the code cited as evidence for its own intent? That is not evidence. Remove or reclassify it.
4. Is there a What we don't know section? If it names no gaps, be suspicious. Either the record was unusually complete or something is being swept aside.
