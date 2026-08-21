import asyncio
import os
import subprocess
import logging
from . import config

logger = logging.getLogger("shorts.voice")

async def _generate_edge_tts_async(text, output_audio, output_vtt, voice="tr-TR-AhmetNeural", rate="+5%"):
    import edge_tts
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    submaker = edge_tts.SubMaker()
    
    with open(output_audio, "wb") as audio_file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.create_sub((chunk["offset"], chunk["duration"]), chunk["text"])
                
    with open(output_vtt, "w", encoding="utf-8") as vtt_file:
        vtt_file.write(submaker.generate_subs())

def generate_voice_and_subs(text, output_prefix="short"):
    output_audio = os.path.join(config.DATA_DIR, f"{output_prefix}.mp3")
    output_vtt = os.path.join(config.DATA_DIR, f"{output_prefix}.vtt")
    
    logger.info(f"Seslendirme oluşturuluyor ({config.TTS_VOICE})...")
    try:
        asyncio.run(_generate_edge_tts_async(text, output_audio, output_vtt, voice=config.TTS_VOICE, rate=config.TTS_RATE))
        if os.path.exists(output_audio) and os.path.exists(output_vtt):
            logger.info(f"Ses ve altyazı hazır: {output_audio}")
            return output_audio, output_vtt
    except Exception as e:
        logger.error(f"Edge-TTS hatası: {e}")
        
    return None, None
