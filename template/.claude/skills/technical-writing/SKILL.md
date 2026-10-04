---
name: technical-writing
description: "Layered technical-writing standard: Diátaxis structure, Google developer style sentences, STE instruction rules, Global English syntax. Use for /technical-writing or when writing or reviewing docs, READMEs, design notes, DocC articles, PR descriptions, commit messages or release notes."
disable-model-invocation: true
---

# Technical writing

**Job:** make a document a tired engineer understands on the first read.

**Not my job:** in-app UI copy (Apple's Human Interface Guidelines on writing, and the project's copy rules, own that) · App Store marketing text · the AI-tell catalog (`/unslop` owns it, and this skill applies it).

**When there is nothing to report:** "Reads clean on all four layers", with the one sentence that came closest to failing and why it stays.

Four layers get a document there, one question each. What kind of document is this? How do sentences address the reader? How much does each sentence carry? Can any sentence be read two ways? Apply all four.

Three rules sit above the layers.

- **Cut every word that does no work.** If the sentence survives without a word, the word goes. "In order to" is "to". "It is important to note that" is nothing.
- **Use the short, everyday word.** "Use", not "utilize". "Help", not "facilitate". "Do", not "perform". A long word has to buy its length with precision.
- **When a rule makes a sentence worse, fix the sentence another way or leave it alone.** The rules serve the reader. A sentence that follows every rule and sounds machine-written has failed.

The codebase is the word list. Write the real symbol, file, flag, target or command name, not a synonym or a description of it. `TaskStore`, not "the store layer". `scripts/ai/test.sh`, not "the test script".

Don't invent jargon. Use the words a developer says out loud: "move", "delete", "a limit that only goes down", not "evacuate", "ratchet" or "endgame". A named pattern is fine when the doc says what it means the first time. When you find a new offender, propose it and its replacement as an addition to `/unslop`'s rule 26 in your reply, with the diff. Don't edit that skill.

## Vary the rhythm

The layers decide what a document says and how much each sentence carries. A doc can obey all of them and still read machine-written. Every sentence clipped short, no view anywhere, nothing specific.

- Mix sentence lengths on purpose. Short sentences land a point. Longer ones that take their time carry a fact with its condition or consequence.
- One thought per sentence does not mean one length per sentence. Split the sentence that carries two thoughts. Keep the long sentence that carries one.
- Have a view where the mode allows it. Explanation weighs trade-offs, so say what you make of them instead of listing pros and cons. Reference stays dry.
- Be specific, not sterile. Not "schema changes can cause issues" but "editing the current model version in place makes every existing store fail to open".

## Pick the mode first (Diátaxis)

One document, one mode. Two questions pick it. Does the content inform action (doing) or understanding (thinking)? Does it serve learning or work?

- Action and learning. **Tutorial**.
- Action and work. **How-to**.
- Understanding and work. **Reference**.
- Understanding and learning. **Explanation**.

Use the compass on a whole document or on one sentence.

**Tutorial. Learning by doing.** You are the teacher. The learner's success is your job, not theirs. Open by saying what the learner will build, not what they will "learn". Every step produces a visible result, early and often. Tell them what they should see: the build summary line, the screen in the simulator, the test count. Cut explanation to one clause and a link. Teaching pauses break the lesson. Stay concrete. Write as "we", in commands. "First, add the model. Now, run the app."

**How-to. Steps to a goal.** Solve a problem a person has, not an operation the machine can do. Assume competence. Skip teaching. Action only. No digressions, no background, no completeness for its own sake. Link those instead. Allow forks and judgment. "If you ship to iPad, also check the regular width." Name the guide by the task. "How to add a Core Data model version", not "Core Data model versions".

**Reference. Facts for lookup.** Describe. Only describe. No instruction, no persuasion, no opinion. Be dry, complete and sure. State facts, options, limits and errors with no hedging. Mirror the structure of the thing described, so code and docs can be navigated together. Put material where readers expect it. Generate from code where possible (DocC from `///` comments, a script's `--help` from its usage string), so it stays true.

**Explanation. Understanding and why.** One bounded topic, readable away from the product. Each title should tolerate an implicit "About..." in front. Anchor on a real why question. Give context: design decisions, history, constraints, alternatives. Opinion is allowed here and nowhere else.

Don't mix modes. No reference tables inside a tutorial, no tutorial hand-holding inside reference, no arguing inside a how-to. Split and link instead.

## Write sentences to the reader (Google developer style)

- Talk to the reader as "you", in the present tense. "Will" only for things that genuinely happen later.
- Say who does what. "The compiler checks", not "is checked". Passive is fine only when the actor is unknown or beside the point.
- Write instructions as commands. "Click **Build**." State facts plainly. Never "should be done".
- Put the condition before the instruction. "To reset the simulator, run `scripts/ai/sim.sh` with ..." The reader skips what does not apply.
- Put the common case first. Exceptions after.
- Sound like a knowledgeable friend. No buzzwords, no figurative language, no "please" in instructions, and never "simply", "easy" or "quickly" in a procedure. If it were simple, the reader would not be here.
- Don't pre-announce ("we will soon support...") and don't start consecutive sentences with the same phrase.
- Link with words that say where the link goes, the page title or a short description. Never "click here". Prefer a sentence of context on the page over a link off it.
- Headings carry the point, not only the topic ("Pick the mode first", not "Modes"). Sentence case. A task heading is a bare verb phrase ("Create a model version"). A concept heading is a noun phrase. One h1 per page, no skipped levels.
- Numbered lists for sequences, bullets for everything else. Introduce a list with a complete sentence. Keep items parallel.
- Code goes in code font. UI elements go in bold, with the exact label the app or Xcode shows. Use serial commas. Drop "etc." and say up front that a list is partial.

## Make statements load one at a time (STE rules)

- One instruction per sentence. One thought per sentence everywhere else.
- Split instructions longer than about 20 words and other sentences longer than about 25.
- Put the warning or condition before the step it guards. "If the store holds real data, back it up first."
- Keep "the" and "a". "Remove backup file" reads two ways. "Remove the backup file" reads one.
- Give each word one meaning and one job, then keep it. If "check" means inspect, don't also use it for restrain.
- Pick one word per action and keep it. "Run", not "run" here and "execute" there.
- Write procedures as direct commands, never as narration and never in the passive. "Install the profile", not "the profile must be installed".
- Avoid "-ing" words where you can. They take too many grammatical jobs and breed misreadings.

## Leave no sentence open to two readings (Global English)

- Keep "only" and "not" next to the word they change. "Only fails on iPad" and "fails only on iPad" say different things.
- Break up long noun strings. "The model version migration test fixture" becomes "the fixture that tests migration between model versions".
- Make every "it", "they" and "this" point at one obvious thing. Repeat the noun when in doubt. Never use "this" or "which" to point at a whole clause.
- Don't drop verbs. "Phase 1 moves the models and Phase 2 the views" leaves Phase 2 without one. Give it one.
- Keep the small words that show structure. "Ensure that the switch is off" keeps "that" because it makes the sentence parse one way. Never trade clarity for word count.
- Repeat the article in a series when it prevents a misread. "The app and the widget", not "the app and widget", when they are two things.
- Say which parts "and" or "or" joins when a sentence can group two ways. "Both...and", "either...or" and "if...then" are free disambiguators.
- Use periods, not semicolons. Replace a long dash with a new sentence.
- Make text in parentheses a full grammatical unit or its own sentence. Never form plurals with "(s)".
- No slashes. Write "a, b, or both" instead of "a/b" or "and/or".
- Call each thing by one name, everywhere. A doc that says "the gate", "the check" and "the verifier" for one thing teaches three things. Rewording an unchanged sentence between edits costs the same way. Don't churn what didn't change.
- Skip idioms, colloquialisms, Latin abbreviations and metaphors. A non-native reader, a translator and an agent all parse plain constructions best.

## Voice and repo specifics

- Apply `/unslop` to every doc this skill touches. It owns the slop catalog: AI vocabulary, filler, hedging, formatting tells.
- PR descriptions and commit messages are writing too. Every layer except Diátaxis applies. A PR body is a briefing a reviewer reads in under a minute. Don't paste build logs, hash lists or metric tables. Link them, or let `scripts/ai/pr.sh` attach the `/verify` report.
- A commit message says why, not only what. Subject in the imperative, under about 70 characters.
- Release notes and TestFlight "What to Test" text address the person using the app, in their words, not the code's.
- In-app strings are not documentation. Follow Apple's Human Interface Guidelines on writing and the project's own copy rules.
- Format code snippets the way the repo's formatter does (swift-format or SwiftLint settings). Write real paths and real symbols. Make every count or tree claim true at the commit that lands it, and include the command that regenerates it.

## Worked example

Before:

> Configuration of the persistent store migration behavior is performed via the model version settings. Note that it's important to remember that editing the current version, which updates the schema that existing stores were created with, should only be done before the first release. If done afterward, stores fail to load.

After:

> Core Data opens an existing store only with the model version it was created with, or with a newer version it can migrate from. Never edit the current `.xcdatamodel` version after a release. Add a new version instead, and make it a superset of the last one.
