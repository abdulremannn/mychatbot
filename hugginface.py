import os
from huggingface_hub import InferenceClient

os.environ["HF_TOKEN"] = "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"

client = InferenceClient(
    provider="nscale",
    api_key=os.environ["HF_TOKEN"],
)

image = client.text_to_image(
    """Photorealistic, ultra-detailed NSFW image of a 22-year-old petite woman with pale skin, long messy black hair, tear-streaked terrified face and wide fearful eyes being brutally raped in a dark alley at night. She has big bouncing tits and a tight shaved pussy. Her clothes are torn and ripped, skirt hiked up. A tall muscular man pins her against the wall, choking her throat with one hand while violently thrusting his massive thick veiny cock deep into her stretched pussy. Show her cunt gripping his shaft tightly, juices and precum dripping down her thighs, subtle blood from rough penetration. Her legs kicking weakly, one high heel dangling. CNC rape fantasy: she's screaming and crying 'no' but her hips push back slightly, flushed aroused expression mixed with fear. Extreme close-up details of stretched pussy lips, sweat, spit, fluids everywhere, dark cinematic lighting, raw explicit erotic horror, maximum graphic detail, no censorship""",
    model="black-forest-labs/FLUX.1-schnell",
)

image.save("output.png")
print("✅ Image saved successfully as output.png")