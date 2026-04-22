# Local Parakeet beats hosted for interview-length ASR

For transcribing a batch of hour-long research interviews on Apple Silicon, [`parakeet-mlx`](https://github.com/senstella/parakeet-mlx) running locally beats the hosted [Parakeet TDT 0.6B v3](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3) endpoints we tried, on every axis that mattered: speed, reliability, and the shape of the output. The cloud path isn't faster, isn't more accurate, and costs more friction than money.

The workload: 10 MP4 screen recordings totaling 8.3 hours of mixed English speech, with long silent gameplay spans between the instruction and interview phases. The goal: time-coded transcripts Ivan could drop into a subtitle-aware video player for qualitative coding.

## Numbers from the run

On an M3 Max with bf16 weights cached, the full batch through `parakeet-mlx` ran at **~0.011 realtime factor** — ~90× faster than playback — for a total wall time of 5:47 across all ten files. The same model hosted on [Together AI](https://www.together.ai/models/parakeet-tdt-0-6b-v3) *without* timestamps landed near the same RTF when healthy, but jumped to ~0.14 as soon as we asked for word-level timestamps, and returned `service_unavailable` on a healing-model request the same afternoon.

Speed wasn't the real pitch, though. Local won on three things the benchmarks don't show.

**Sentence segmentation is part of the model, not a post-step.** The parakeet-mlx CLI emits native sentence boundaries with per-token confidence scores, tunable by silence-gap threshold (`--silence-gap 0.8`), max-words-per-sentence, and max-duration-per-sentence. Together's wrapper returns one whole-clip segment plus a flat word list; the client has to re-split. For research data that's going into subtitle files, having the model's own sentence judgment in the output is worth more than shaving seconds.

**Per-token confidence + timestamps makes "LLM healing" unnecessary.** The standard next step after ASR is sometimes to run the transcript through an instruct model to fix homophones and clean up disfluencies. Tempting, but for research transcripts it's actively harmful: instruct models silently paraphrase, truncate, and reorder. The first cleanup probe we ran on Llama-3.3-70B turned "so before I have you uh onboarded into our system" into "Before I am onboarded into your system" — wrong speaker, wrong meaning, cleanly confident. Confidence scores and precise timestamps let a human listen to the ambiguous span directly, which is what they'd need to do for any genuinely contested word anyway.

**The output shape is friendlier.** parakeet-mlx's JSON is `{text, sentences: [{text, start, end, duration, confidence, tokens: [...]}]}`. Converting that to SRT is 40 lines of Python. Converting Together's flat word list into the same shape requires a punctuation-based sentence splitter plus a per-chunk-offset reconciliation step, because the API returns times relative to each uploaded chunk, not the source timeline.

## Gotchas worth recording

- **The [oMLX](https://github.com/jundot/omlx) server's `/v1/audio/transcriptions` endpoint silently drops timestamp requests.** `response_format` and `timestamp_granularities` are documented as "accepted for OpenAI compatibility but not yet implemented". If you want timestamps, skip the server and shell out to `uvx parakeet-mlx` directly. Text-only oMLX is great — ~8 s for 10 min of audio once the model is warm — but it's not the right tool for subtitle work.
- **Long audio OOMs on Metal.** A full 37-minute FLAC through oMLX's endpoint triggered a `[metal::malloc]` attempting ~51 GB vs a ~42 GB max. `parakeet-mlx` handles this itself via `--chunk-duration 300`; the server doesn't.
- **Hosted Parakeet wants 16 kHz mono WAV or FLAC.** Feed it MP4 and you get an unhelpful HTTP 500. Extract audio first: `ffmpeg -i in.mp4 -vn -ac 1 -ar 16000 -c:a flac out.flac`. `parakeet-mlx` accepts the MP4 path directly and does the ffmpeg call internally, one less moving part.
- **Together's word-timestamp response is non-deterministic.** Passing `timestamp_granularities=word` alone gives you 0 words ~30% of the time; you have to pass both `word` and `segment` as bare repeated form fields (not `[]` syntax) to reliably get them back. This is undocumented and cost us a retry loop we didn't end up needing.

> Context: this came out of a graduate user study my student Ivan is running on an in-game coaching agent. We budgeted a hosted API for transcription but probe-tested a local path first, and the local path was just better. The `togetherai-api` skill we built along the way has been deleted; the `omlx-api` skill has been updated to warn that the transcription endpoint is timestamp-free and to point at `parakeet-mlx` for that work. The whole pipeline — download from Drive, extract audio, transcribe, emit SRT — fits in about 150 lines of shell and Python.
