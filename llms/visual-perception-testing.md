# Visual perception testing for VLMs

Before building elaborate tool scaffolding around a vision-language model (ruler overlays, multi-view screenshots, clever inner loops), run a small probe battery through the actual rendering pipeline and find out what the model can really see. With a coding agent writing the driver, this is a 15-minute detour and under a dollar of API calls, and it pays back many times over by preventing design work against a baseline we don't understand.

The shape of the workflow we used:

- Pick 5–7 **single-turn** visual questions that each isolate one capability: a transport sanity check, a fine-alignment task, a coarse comparison task, a counting task, a coordinate-readout task, a legibility sweep. Keep each probe's answer a single token or a short string so scoring is mechanical.
- Render the stimuli through the **same path the real system uses**, not a parallel test rig. Our production path sends PNGs from a headless browser via [rodney](https://github.com/simonw/rodney); the probe battery does the same. ([Playwright](https://playwright.dev/python/) works equally well for this.) The point is to measure what the model sees in the field.
- Randomize every trial (positions, colors, magnitudes) across several seeds so the model can't pattern-match.
- Fan out with `asyncio.Semaphore(8)` + [`httpx.AsyncClient`](https://www.python-httpx.org/async/). Embarrassingly parallel; a full battery goes from 30 minutes sequential to under 10 minutes.
- Save every request, response, and reasoning trace per trial. The scalar scores are the least interesting artifact.

## What we found

**Our scorers were buggy before the model was.** On the first pass, roughly half of what looked like "interesting findings" turned out to be parsing mistakes. A scorer that substring-scans for `left` / `right` will false-positive on "the LEFT panel" and false-negative on "the left endpoint". A scorer that expects "column index difference" will return zero on every trial because the model answered the question we actually asked ("cells between"), and its answer is off by one. I now budget more time for scorer review than for probe authoring, and read raw replies individually before trusting any aggregate.

**Scaffolding leverage is measurable.** Labeled ruler ticks turn a blind coordinate-guess into real sub-tick interpolation; the model computes fractional positions between labeled marks. Side-by-side framing beats single-canvas nudging. A uniquely-colored anchor object beats three visually-equal shapes. All of these are cheap to add to a screenshot pipeline and show up as step-changes in probe scores, which means you can rank candidate scaffolds by actual effect before committing any of them to the real system.

**Confidence is inverted at the acuity ceiling.** When a reasoning VLM is working on a hard-but-solvable problem, its trace is full of self-interruption ("Wait, let me look again", "Actually, maybe I should count more carefully"). When it's working past its perceptual threshold, the hedging disappears and it writes a clean, confident, wrong answer. I now treat high confidence on a fine visual judgment as a red flag, not a green one, and count the "Wait"s in a reasoning trace as a usable proxy signal.

**Language choice moves scores more than I expected.** "Cells between A and B" and "the column index of A minus the column index of B" are the same question to me; they are different questions to the model, and one of them is reliably off by one. Arithmetic phrasing beats spatial phrasing on counting tasks. This is a prompt-engineering win hiding inside what looks like a perception finding.

> Context: this came out of building a VLM-driven SVG drawing harness. Our drawing loop kept oscillating on a small pixel offset, and it wasn't obvious whether that was a harness bug, a prompt bug, or a perceptual limit. A quick probe battery answered the question (mostly perception, partly phrasing, plus two scorer bugs that had been masquerading as findings) and reset the design brief for the scaffolding layer.
