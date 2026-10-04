---
name: principle-extremes-are-the-test
description: "Apply to any UI change. Judge it at the edges, not the default (the largest accessibility text size, the smallest iPhone, iPad in both orientations if the app ships there, dark and light, Reduce Motion, VoiceOver, and the empty, one, many, error and offline states). Most layout defects live only there."
disable-model-invocation: true
---

# Extremes Are the Test

A UI change is judged at its edges. The default configuration (a mid-size iPhone, default text size, light mode, a handful of rows) is where the change looks finished and where the fewest defects are.

**Why:** Most layout defects live only at the extremes, and none of them fail a build or a unit test.
- Primary text truncated at the largest accessibility size.
- Controls pushed off screen, or under the keyboard, on the smallest iPhone.
- A scaled glyph drawn outside its fixed frame when Dynamic Type grows the font but not the container.
- A 1300-point-wide button on iPad, because the layout assumed a phone.
- A list that is fine with ten rows and empty with none, with no empty state.

**Pattern:**
- **Size.** The largest accessibility text size (`scripts/ai/sim.sh size accessibility-extra-extra-extra-large`) and the default. The smallest iPhone the app supports.
- **Device class.** iPad in portrait and landscape, and in a split view, if the app ships to iPad. Check the target's supported devices before assuming it does not.
- **Appearance.** Dark and light (`sim.sh appearance dark`).
- **Motion and assistive settings.** Reduce Motion (every animation has a non-moving form), VoiceOver (every control has a label and a sensible order), Increase Contrast.
- **Data.** Empty, one, many (enough to scroll), very long strings, an error, offline.
- **Capture the evidence.** `/verify` renders the screens in `.claude/ios-screens.txt` at the kit's sizes and appearances. The `ui-verify` agent judges them. Look at the sheets before saying done.

**The test:** For each screen the change touched, can you point to an image of it at the largest text size, in dark mode, and in its empty and many states? If not, the change has been seen only where it was least likely to fail.

The UI side of `principle-prove-it-works`.
