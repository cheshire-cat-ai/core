"""
A video-understanding agent powered by TwelveLabs Pegasus.

Pegasus is a video-language model: hand it a video and a question and it
*watches* the footage to answer — describing scenes, summarising, reading
on-screen text, spotting moments. This agent exposes that as a single tool,
`analyze_video`, so the agentic loop can reach for it whenever the user asks
about a video.

Configuration
-------------
Set one environment variable with your TwelveLabs API key (free tier at
https://twelvelabs.io):

    export TWELVELABS_API_KEY=tlk_...

Then address the agent by its slug:

    POST /agents/twelvelabs/message
    { "messages": [{ "role": "user",
        "content": "Summarise https://.../sample.mp4" }] }

The tool takes a **public video URL** (Pegasus fetches it server-side). It is
opt-in: nothing here changes the default agent or any existing behaviour, and
the heavy `twelvelabs` dependency is only imported inside the tool, so the
plugin loads even when the SDK isn't installed.
"""

import asyncio
import os

from cat import Agent, tool


class TwelveLabsVideoAgent(Agent):
    slug = "twelvelabs"
    name = "TwelveLabs Video Agent"
    description = "Answers questions about videos using TwelveLabs Pegasus."

    system_prompt = (
        "You are a video analyst. When the user references a video by URL, use "
        "the `analyze_video` tool to watch it and ground your answer in what the "
        "tool reports — never guess at a video's contents. Pass the user's "
        "question through as the prompt so Pegasus answers exactly what was asked."
    )

    @tool
    async def analyze_video(self, video_url: str, prompt: str) -> str:
        """Watch a video at a public URL and answer a question about it.

        Use for any request about the contents of a video: summaries, scene
        descriptions, on-screen text, "what happens when…", etc.

        Args:
            video_url: A publicly reachable URL to the video file (mp4, etc.).
            prompt: The question or instruction about the video, in plain English.
        """

        api_key = os.getenv("TWELVELABS_API_KEY")
        if not api_key:
            return (
                "TwelveLabs is not configured. Set the TWELVELABS_API_KEY "
                "environment variable (free key at https://twelvelabs.io)."
            )

        # Imported lazily so the plugin loads without the optional SDK installed.
        from twelvelabs import TwelveLabs
        from twelvelabs.types.video_context import VideoContext_Url

        def _analyze() -> str:
            client = TwelveLabs(api_key=api_key)
            response = client.analyze(
                model_name="pegasus1.5",
                video=VideoContext_Url(url=video_url),
                prompt=prompt,
                max_tokens=2048,
            )
            return response.data or "Pegasus returned no answer for this video."

        try:
            # The SDK is synchronous; run it off the event loop.
            return await asyncio.to_thread(_analyze)
        except Exception as e:
            return f"TwelveLabs analysis failed: {e}"
