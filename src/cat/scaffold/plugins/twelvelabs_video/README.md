# TwelveLabs

A video-understanding agent powered by [TwelveLabs](https://twelvelabs.io)
**Pegasus**, a video-language model. Give the agent a public video URL and a
question — it *watches* the footage and answers in natural language: summaries,
scene descriptions, on-screen text, "what happens when…", and more.

This plugin is **opt-in** and **non-breaking**: it adds one new agent
(`twelvelabs`) and changes no defaults. The `twelvelabs` SDK is imported lazily
inside the tool, so the plugin loads even when the dependency isn't installed.

## 1. Install the dependency

```bash
uv add twelvelabs
```

## 2. Configure your API key

Grab a free key at [twelvelabs.io](https://twelvelabs.io) — there's a generous
free tier — and set it in the environment (or your project `.env`):

```bash
export TWELVELABS_API_KEY=tlk_...
```

## 3. Ask the agent about a video

Address the agent by its `slug`:

```json
POST /agents/twelvelabs/message
{
  "messages": [
    { "role": "user", "content": "Summarise https://example.com/clip.mp4" }
  ]
}
```

The agent calls its `analyze_video(video_url, prompt)` tool, which Pegasus
fetches and analyses server-side. The `video_url` must be publicly reachable.

## Model

| Tool            | Model        | Input             | Output                  |
| --------------- | ------------ | ----------------- | ----------------------- |
| `analyze_video` | `pegasus1.5` | Public video URL  | Natural-language answer |
