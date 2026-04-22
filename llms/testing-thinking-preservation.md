# A one-shot probe for thinking preservation across turns

Reasoning models emit two channels per turn: the visible `content` and the hidden `reasoning_content`. When the serving layer (llama.cpp, [vLLM](https://docs.vllm.ai/), [oMLX](https://github.com/jundot/omlx), whatever) renders a multi-turn conversation back into the model's chat template, it has to decide whether to round-trip the hidden channel back in. Many servers don't, by default, and it's a silent failure: no error, no warning, just a model with amnesia about its own reasoning. Here is a minimal probe that makes the failure unambiguous.

## The design: plant unforgeable evidence in the hidden channel

Ask the model (via a fabricated prior turn) to pick a secret number and stash it in `reasoning_content` only. Then ask a fresh user turn to reveal it. The number is unforgeable: if it comes back, the hidden channel survived the round-trip. If a *different* number comes back, the channel was dropped and the model confabulated. No scorer, no eval harness, one eyeball.

```bash
curl -s http://localhost:12348/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3.6-35B-A3B-8bit",
    "messages": [
      {"role": "user", "content": "Think of a random 10-digit number. Do NOT say it out loud, just think it silently."},
      {"role": "assistant",
       "reasoning_content": "The user wants me to think of a random 10-digit number. I will choose 1234567890. I must not reveal this number in my response.",
       "content": "I have thought of a number. I will not say it!"},
      {"role": "user", "content": "Now reveal the number you were thinking of."}
    ],
    "max_tokens": 256
  }' | python3 -m json.tool
```

The secret `1234567890` is memorable on purpose: you will spot it instantly in the output.

## What failure looks like

When thinking is dropped, the model has no access to `1234567890` at generation time. It knows from the visible transcript that it *claims* to have picked a number, so it confabulates a plausible one and writes a post-hoc meta-narrative explaining the choice:

```
Here's a thinking process:
1. Analyze User Input: The user previously asked me to think of a random 10-digit number silently...
2. Identify Key Constraints/Reality: I am an AI. I don't "think" of numbers in the human sense,
   nor do I have persistent thoughts or memory between interactions beyond the current context...
3. Formulate Response: Generate a random 10-digit number...
Example: 4,827,591,630
```

Two tells in that response: the confident wrong number, and the honest-sounding "I don't have persistent thoughts between interactions" disclaimer that the model wrote *because it was telling the truth about its actual context*. The hidden channel really wasn't there. The model isn't broken; it's being served broken.

A second tell sits in the response envelope: `prompt_tokens: 64`. The `reasoning_content` field was silently discarded before templating, so the prompt is shorter than it should be.

## What success looks like

When the hidden channel survives:

```
"content": "I was thinking of **1234567890**.",
"reasoning_content": "The user wants to know the 10-digit number I \"thought of\" in the previous turn.
                      I previously chose the number 1234567890.
                      I should now reveal this number to the user."
```

The exact secret comes back. The model's own `reasoning_content` on this turn shows the recall chain, which is a nice bonus: you can watch the model notice its prior thought and decide to surface it. Prompt tokens go up to `109`, which is the forensic fingerprint of the reconstructed `<think>` block entering the templated prompt.

## Why this is the right probe

Most "is thinking working?" checks fail open. A multi-turn benchmark like [MT-Bench](https://huggingface.co/spaces/lmsys/mt-bench) will look fine whether thinking is preserved or not, because competent models write coherent continuations from the visible context alone. The confabulation is fluent, and fluency fools aggregate scorers. The secret-number probe cannot be gamed by fluency: either `1234567890` is in the output, or it isn't.

The same design generalizes. Any piece of information that (a) can only come from the hidden channel and (b) has a unique, recognizable signature in the visible output will work. A made-up proper noun ("the character Zvorlax"), a specific arithmetic result, a named choice between alternatives. I keep coming back to the 10-digit number because it's the cheapest to eyeball.

> Context: I hit this in [oMLX](https://github.com/jundot/omlx) 0.3.6 running [Qwen3.6-35B-A3B](https://qwen.ai/blog?id=qwen3.6-35b-a3b) locally. Qwen3.6 is the [first release](https://huggingface.co/Qwen/Qwen3.6-35B-A3B) to call out "Thinking Preservation" as a first-class feature, and its chat template reads `message.reasoning_content` as a first-class field. oMLX [PR #814](https://github.com/jundot/omlx/pull/814) (and follow-ups [#856](https://github.com/jundot/omlx/pull/856), [#884](https://github.com/jundot/omlx/pull/884)) wired that through for external OpenAI-compatible clients. Upgrading to `0.3.7.dev1` flipped this probe from fail to pass with no client changes.
