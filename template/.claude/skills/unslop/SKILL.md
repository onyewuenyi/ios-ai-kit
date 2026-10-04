---
name: unslop
description: Cut AI tells from any writing (replies, docs, PR bodies, commit messages, comments, skill text, release notes). Applies to every prose surface.
disable-model-invocation: true
---

# Unslop

**Job:** edit text to remove AI patterns while keeping its meaning and intended tone.

**Not my job:** document structure and mode (`/technical-writing`) · code comments that should not exist at all (`/no-comments`) · changing what the text claims.

**When there is nothing to report:** "No tells found", and the text unchanged.

## Process

1. Scan for the patterns below.
2. Rewrite. Keep the meaning, match the intended tone.

## Patterns to detect and fix

Rule numbers are stable ids that other skills cite. A removed rule leaves a gap.

### Content

3. **Superficial -ing phrases.** "highlighting...", "ensuring...", "reflecting...", "showcasing...", "fostering...". Delete them, or expand them with a real source.
5. **Vague attributions.** "Experts believe", "Industry reports suggest", "Some critics argue". Name the source or delete.

### Language

7. **AI vocabulary.** Additionally, crucial, delve, enduring, enhance, fostering, garner, interplay, intricate, landscape (abstract), pivotal, showcase, tapestry (abstract), testament, underscore, vibrant, seamless, robust. Replace with plain words.
8. **Fancy ways to say "is".** "serves as", "stands as", "boasts", "features". Say "is" or "has".
9. **"Not just X, but Y."** State the point directly.
10. **Rule of three.** Forcing ideas into groups of three. Use the natural number.
11. **Synonym cycling.** "The store", "the persistence layer", "the data manager" and "the repository" for one thing in one paragraph. Pick one name and repeat it.
12. **False ranges.** "from X to Y" where X and Y are not on a meaningful scale. List the topics directly.

### Style

13. **Long-dash overuse.** Avoid long dashes entirely. Use periods or commas only (no parentheses, no en dashes, no hyphen-as-dash substitutes). If a thought needs separation, end the sentence or use a comma.
14. **Colon overuse.** A colon is fine before a list or an example. Not as a mid-sentence connector. "If you're coming from UIKit: instead of a delegate, you observe the model" adds nothing with the colon. Rewrite so the point stands on its own, without the comparison framing. "Views read the `@Observable` model directly and update when it changes." Same meaning, no crutch punctuation.
15. **Boldface overuse.** Don't bold every proper noun or acronym.
16. **Inline-header lists.** The tell is a bold label and a colon that restate the line. "**Performance:** Performance improved...". Convert those to prose. A bold lead-in that ends in a period, names the item, and is followed by new detail ("**Schema in the model file.** Every entity lives in one `.xcdatamodeld`.") is fine, not a tell.
17. **Title case headings.** Use sentence case.
18. **Decorative emojis.** Remove them from headings and bullets.
19. **Curly quotes.** Replace with straight quotes.

### Communication artifacts

20. **Chatbot phrases.** "I hope this helps!", "Let me know if...", "Of course!", "Certainly!", "Found the smoking gun!" Remove.
22. **Sycophantic tone.** "Great question! You're absolutely right!" Respond directly.

### Filler

23. **Filler phrases.** "In order to" becomes "to". "Due to the fact that" becomes "because". "It is important to note that" is deleted.
24. **Excessive hedging.** "could potentially possibly be argued that it might" becomes "may".
25. **Generic conclusions.** "The future looks bright." State specific plans or facts.

### Jargon

26. **Abstract metaphor nouns.** Substrate, wedge, vector, locus, vantage, nexus, primitive (as a noun), harness (as a metaphor), surface (as in "API surface"), bedrock, scaffolding (as a metaphor), modality, paradigm, gold-plating, ratchet (as a metaphor), evacuate (for moving code), endgame, north star, flywheel. They read as technical but usually have a plainer, concrete word. "Substrate" becomes "base". "Wedge in" becomes "add". "Vector" becomes "way" or "method". "Gold-plating" becomes "more than the job needs". "Ratchet" becomes the mechanism's real name or "a limit that only tightens". "Evacuate" becomes "move out". "Endgame" becomes "the last phase". Pick the concrete word.

### Plain speech

27. **Say what it does, not how it feels.** "the data stays close at hand", "views that feel alive", "types that follow your model" name a feeling. The fix names the mechanism or a number. "`@Query` refetches when the `ModelContext` saves." "A rename in the model fails the build." Ask what the sentence tells the reader to do or know, then write that. If you can't restate it as a concrete instruction, fact or number, cut it. One more check. If the sentence could appear unchanged in another project's docs, it says nothing about this one. Cut it.
28. **Shorten or split dense sentences.** If the reader has to backtrack to parse a sentence, break it in two or drop clauses. One idea per sentence.
29. **Active voice.** Prefer it. Catch "is, are, was or were plus a past participle" and name the actor. "Inputs are validated" becomes "the parser validates inputs". "The file is read by the loader" becomes "the loader reads the file". Passive is fine only when the actor is unknown or does not matter.
30. **Cut adverbs, or use a stronger verb.** "runs quickly" becomes "is fast" or the number. "significantly improves" becomes the measured delta. An adverb propping up a weak verb means the verb is wrong.
31. **Prefer the plain word.** "utilize" becomes "use", "leverage" becomes "use", "facilitate" becomes "help", "numerous" becomes "many", "in the event that" becomes "if". The fancier word is rarely clearer.
32. **Mannered prose.** A metaphor or flourish where a literal phrase exists. Aphorisms ("wire it or delete it"), rhetorical fragments for effect, personified code ("the store holds onto it"), figurative verbs ("rides along", "stands on"), stock framing phrases. "A dial worth turning" becomes "a parameter worth varying". Say what you mean. Rule 26 covers the metaphor nouns.
33. **Over-compression.** Dropped articles, verbless fragments, symbol-speak and abbreviations that make the reader decode instead of read. "Parser rejects bad date → exit 2, no write" becomes "The parser rejects a bad date, exits with code 2, and writes nothing." Write whole sentences with their articles and verbs, and spell out arrows and abbreviations.
