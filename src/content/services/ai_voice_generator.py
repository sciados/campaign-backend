# src/content/services/ai_voice_generator.py
"""
AI Voice Generation Service for Video Voiceovers
Generates high-quality speech from text using ElevenLabs, AWS Polly, or Google TTS
"""

from typing import Dict, List, Optional, Any, Union
import asyncio
import aiohttp
import logging
from dataclasses import dataclass
from datetime import datetime
import base64
import os
import json
from urllib.parse import urljoin
import boto3
from google.cloud import texttospeech
import tempfile
import wave

logger = logging.getLogger(__name__)

@dataclass
class VoiceGenerationRequest:
    text: str
    voice_id: str
    voice_settings: Dict[str, Any]
    output_format: str = "mp3"
    sample_rate: int = 24000

@dataclass
class GeneratedVoice:
    audio_url: str
    local_path: str
    duration_seconds: float
    voice_id: str
    provider: str
    generation_time: float
    metadata: Dict[str, Any]

class AIVoiceGenerator:
    """
    Handles AI voice generation for video narration using multiple providers
    """
    
    def __init__(self):
        self.providers = {
            "elevenlabs": ElevenLabsProvider(),
            "aws-polly": AWSPollyProvider(),
            "google-tts": GoogleTTSProvider()
        }
        self.default_provider = "elevenlabs"
        
        # Create local storage directory
        self.storage_dir = os.path.join(os.getcwd(), "generated_assets", "audio")
        os.makedirs(self.storage_dir, exist_ok=True)
    
    async def generate_voiceover(
        self,
        script_text: str,
        voice_type: str,
        intelligence_data: Dict[str, Any],
        provider: Optional[str] = None
    ) -> GeneratedVoice:
        """
        Generate voiceover from script text
        """
        
        provider_name = provider or self.default_provider
        voice_provider = self.providers.get(provider_name)
        
        if not voice_provider:
            raise ValueError(f"Unsupported voice provider: {provider_name}")
        
        logger.info(f"Generating voiceover using {provider_name}")
        
        # Map voice type to specific voice ID
        voice_config = self._get_voice_config(voice_type, provider_name, intelligence_data)
        
        # Preprocess script text
        processed_text = self._preprocess_script(script_text, intelligence_data)
        
        # Create generation request
        request = VoiceGenerationRequest(
            text=processed_text,
            voice_id=voice_config["voice_id"],
            voice_settings=voice_config["settings"]
        )
        
        start_time = datetime.now()
        
        try:
            # Generate voice using provider
            audio_data = await voice_provider.generate_voice(request)
            
            # Save audio locally
            local_path = await self._save_audio_locally(
                audio_data, voice_type, provider_name
            )
            
            # Calculate duration
            duration = await self._get_audio_duration(local_path)
            
            generation_time = (datetime.now() - start_time).total_seconds()
            
            return GeneratedVoice(
                audio_url=audio_data.get("url", ""),
                local_path=local_path,
                duration_seconds=duration,
                voice_id=voice_config["voice_id"],
                provider=provider_name,
                generation_time=generation_time,
                metadata=audio_data.get("metadata", {})
            )
            
        except Exception as e:
            logger.error(f"Failed to generate voiceover: {e}")
            raise
    
    async def generate_scene_narrations(
        self,
        scenes: List[Dict[str, Any]],
        voice_type: str,
        intelligence_data: Dict[str, Any],
        provider: Optional[str] = None
    ) -> List[GeneratedVoice]:
        """
        Generate separate voice files for each scene
        """
        
        tasks = []
        for i, scene in enumerate(scenes):
            script_text = scene.get("narration", "")
            if script_text.strip():
                # Add scene timing cues
                scene_text = f"[Scene {i+1}] {script_text}"
                task = self.generate_voiceover(
                    scene_text, voice_type, intelligence_data, provider
                )
                tasks.append((i, task))
        
        results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
        
        # Process results
        scene_voices = []
        for (scene_index, _), result in zip(tasks, results):
            if isinstance(result, Exception):
                logger.error(f"Voice generation failed for scene {scene_index}: {result}")
            else:
                scene_voices.append(result)
        
        return scene_voices
    
    def _get_voice_config(
        self,
        voice_type: str,
        provider: str,
        intelligence_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get voice configuration based on type and brand context
        """
        
        # Base voice configurations by provider
        voice_configs = {
            "elevenlabs": {
                "male_professional": {
                    "voice_id": "ErXwobaYiN019PkySvjV",  # Antoni
                    "settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.8,
                        "style": 0.2,
                        "use_speaker_boost": True
                    }
                },
                "female_professional": {
                    "voice_id": "EXAVITQu4vr4xnSDxMaL",  # Bella
                    "settings": {
                        "stability": 0.6,
                        "similarity_boost": 0.8,
                        "style": 0.3,
                        "use_speaker_boost": True
                    }
                },
                "young_energetic": {
                    "voice_id": "pNInz6obpgDQGcFmaJgB",  # Adam
                    "settings": {
                        "stability": 0.4,
                        "similarity_boost": 0.7,
                        "style": 0.6,
                        "use_speaker_boost": True
                    }
                },
                "authoritative": {
                    "voice_id": "VR6AewLTigWG4xSOukaG",  # Arnold
                    "settings": {
                        "stability": 0.7,
                        "similarity_boost": 0.9,
                        "style": 0.1,
                        "use_speaker_boost": True
                    }
                }
            },
            "aws-polly": {
                "male_professional": {
                    "voice_id": "Matthew",
                    "settings": {
                        "Engine": "neural",
                        "OutputFormat": "mp3",
                        "SampleRate": "24000",
                        "TextType": "ssml"
                    }
                },
                "female_professional": {
                    "voice_id": "Joanna",
                    "settings": {
                        "Engine": "neural",
                        "OutputFormat": "mp3",
                        "SampleRate": "24000",
                        "TextType": "ssml"
                    }
                },
                "young_energetic": {
                    "voice_id": "Justin",
                    "settings": {
                        "Engine": "neural",
                        "OutputFormat": "mp3",
                        "SampleRate": "24000",
                        "TextType": "ssml"
                    }
                },
                "authoritative": {
                    "voice_id": "Brian",
                    "settings": {
                        "Engine": "neural",
                        "OutputFormat": "mp3",
                        "SampleRate": "24000",
                        "TextType": "ssml"
                    }
                }
            },
            "google-tts": {
                "male_professional": {
                    "voice_id": "en-US-News-M",
                    "settings": {
                        "language_code": "en-US",
                        "ssml_gender": "MALE",
                        "audio_encoding": "MP3"
                    }
                },
                "female_professional": {
                    "voice_id": "en-US-News-K",
                    "settings": {
                        "language_code": "en-US",
                        "ssml_gender": "FEMALE",
                        "audio_encoding": "MP3"
                    }
                }
            }
        }
        
        provider_configs = voice_configs.get(provider, {})
        config = provider_configs.get(voice_type)
        
        if not config:
            # Fallback to default
            config = provider_configs.get("female_professional", {
                "voice_id": "default",
                "settings": {}
            })
        
        # Adjust settings based on intelligence data
        brand_analysis = intelligence_data.get("brand_analysis", {})
        if brand_analysis.get("tone"):
            tone = brand_analysis["tone"].lower()
            if "energetic" in tone or "dynamic" in tone:
                if provider == "elevenlabs" and "style" in config["settings"]:
                    config["settings"]["style"] = min(0.8, config["settings"]["style"] + 0.2)
            elif "calm" in tone or "professional" in tone:
                if provider == "elevenlabs" and "stability" in config["settings"]:
                    config["settings"]["stability"] = min(0.9, config["settings"]["stability"] + 0.1)
        
        return config
    
    def _preprocess_script(
        self,
        script_text: str,
        intelligence_data: Dict[str, Any]
    ) -> str:
        """
        Preprocess script text for better voice generation
        """
        
        processed_text = script_text.strip()
        
        # Add pronunciation guides for brand names
        brand_analysis = intelligence_data.get("brand_analysis", {})
        if brand_analysis.get("name"):
            brand_name = brand_analysis["name"]
            # Could add SSML pronunciation tags here
            # processed_text = processed_text.replace(brand_name, f"<phoneme alphabet=\"ipa\" ph=\"...\">{brand_name}</phoneme>")
        
        # Add pauses for better pacing
        processed_text = processed_text.replace(".", ".<break time=\"0.5s\"/>")
        processed_text = processed_text.replace("!", "!<break time=\"0.5s\"/>")
        processed_text = processed_text.replace("?", "?<break time=\"0.5s\"/>")
        
        # Wrap in SSML if needed
        if "<break" in processed_text:
            processed_text = f"<speak>{processed_text}</speak>"
        
        return processed_text
    
    async def _save_audio_locally(
        self,
        audio_data: Dict[str, Any],
        voice_type: str,
        provider: str
    ) -> str:
        """
        Save generated audio to local storage
        """
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"voiceover_{voice_type}_{provider}_{timestamp}.mp3"
        file_path = os.path.join(self.storage_dir, filename)
        
        try:
            if "url" in audio_data:
                # Download from URL
                async with aiohttp.ClientSession() as session:
                    async with session.get(audio_data["url"]) as response:
                        if response.status == 200:
                            audio_bytes = await response.read()
                            with open(file_path, 'wb') as f:
                                f.write(audio_bytes)
            
            elif "base64" in audio_data:
                # Decode base64
                audio_bytes = base64.b64decode(audio_data["base64"])
                with open(file_path, 'wb') as f:
                    f.write(audio_bytes)
            
            elif "bytes" in audio_data:
                # Direct bytes
                with open(file_path, 'wb') as f:
                    f.write(audio_data["bytes"])
            
            else:
                raise ValueError("No valid audio data found")
            
            return file_path
            
        except Exception as e:
            logger.error(f"Failed to save audio locally: {e}")
            raise
    
    async def _get_audio_duration(self, file_path: str) -> float:
        """
        Get duration of audio file in seconds
        """
        try:
            # For MP3 files, we can use a simple approach
            # In production, you might want to use a library like mutagen
            import subprocess
            
            result = subprocess.run([
                'ffprobe', '-v', 'quiet', '-show_entries',
                'format=duration', '-of', 'csv=p=0', file_path
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                return float(result.stdout.strip())
            else:
                # Fallback estimation (rough)
                file_size = os.path.getsize(file_path)
                return file_size / 32000  # Rough estimation for MP3
                
        except Exception as e:
            logger.warning(f"Could not determine audio duration: {e}")
            return 30.0  # Default assumption

class BaseVoiceProvider:
    """Base class for voice generation providers"""
    
    async def generate_voice(self, request: VoiceGenerationRequest) -> Dict[str, Any]:
        raise NotImplementedError

class ElevenLabsProvider(BaseVoiceProvider):
    """ElevenLabs AI voice generation"""
    
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.api_url = "https://api.elevenlabs.io/v1"
    
    async def generate_voice(self, request: VoiceGenerationRequest) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("ElevenLabs API key not configured")
        
        url = f"{self.api_url}/text-to-speech/{request.voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        payload = {
            "text": request.text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": request.voice_settings
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    audio_bytes = await response.read()
                    return {
                        "bytes": audio_bytes,
                        "metadata": {
                            "provider": "elevenlabs",
                            "voice_id": request.voice_id,
                            "model": "eleven_multilingual_v2"
                        }
                    }
                else:
                    error_text = await response.text()
                    raise Exception(f"ElevenLabs API error: {error_text}")

class AWSPollyProvider(BaseVoiceProvider):
    """AWS Polly text-to-speech"""
    
    def __init__(self):
        self.client = None
        try:
            self.client = boto3.client('polly')
        except Exception as e:
            logger.warning(f"AWS Polly client not configured: {e}")
    
    async def generate_voice(self, request: VoiceGenerationRequest) -> Dict[str, Any]:
        if not self.client:
            raise ValueError("AWS Polly client not configured")
        
        try:
            response = self.client.synthesize_speech(
                Text=request.text,
                VoiceId=request.voice_id,
                **request.voice_settings
            )
            
            audio_bytes = response['AudioStream'].read()
            
            return {
                "bytes": audio_bytes,
                "metadata": {
                    "provider": "aws-polly",
                    "voice_id": request.voice_id,
                    "engine": request.voice_settings.get("Engine", "standard")
                }
            }
            
        except Exception as e:
            raise Exception(f"AWS Polly error: {e}")

class GoogleTTSProvider(BaseVoiceProvider):
    """Google Cloud Text-to-Speech"""
    
    def __init__(self):
        self.client = None
        try:
            self.client = texttospeech.TextToSpeechClient()
        except Exception as e:
            logger.warning(f"Google TTS client not configured: {e}")
    
    async def generate_voice(self, request: VoiceGenerationRequest) -> Dict[str, Any]:
        if not self.client:
            raise ValueError("Google TTS client not configured")
        
        try:
            synthesis_input = texttospeech.SynthesisInput(text=request.text)
            voice = texttospeech.VoiceSelectionParams(
                name=request.voice_id,
                language_code=request.voice_settings.get("language_code", "en-US"),
                ssml_gender=getattr(
                    texttospeech.SsmlVoiceGender,
                    request.voice_settings.get("ssml_gender", "NEUTRAL")
                )
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=getattr(
                    texttospeech.AudioEncoding,
                    request.voice_settings.get("audio_encoding", "MP3")
                )
            )
            
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            return {
                "bytes": response.audio_content,
                "metadata": {
                    "provider": "google-tts",
                    "voice_id": request.voice_id,
                    "language": request.voice_settings.get("language_code", "en-US")
                }
            }
            
        except Exception as e:
            raise Exception(f"Google TTS error: {e}")

# Factory function for easy instantiation
def create_ai_voice_generator() -> AIVoiceGenerator:
    """Create and return an AI voice generator instance"""
    return AIVoiceGenerator()