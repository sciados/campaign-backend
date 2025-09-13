# src/content/services/video_assembly_pipeline.py
"""
Video Assembly Pipeline
Combines AI-generated images, voiceovers, and effects into complete videos using FFmpeg
"""

from typing import Dict, List, Optional, Any, Tuple
import asyncio
import subprocess
import logging
from dataclasses import dataclass
from datetime import datetime
import os
import json
import tempfile
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class VideoScene:
    scene_id: str
    image_path: str
    audio_path: Optional[str]
    duration: float
    text_overlay: Optional[str] = None
    transition_type: str = "fade"
    effects: Optional[List[str]] = None

@dataclass
class VideoSpec:
    width: int
    height: int
    fps: int = 30
    bitrate: str = "2M"
    codec: str = "libx264"
    audio_codec: str = "aac"
    format: str = "mp4"

@dataclass
class AssembledVideo:
    video_path: str
    duration_seconds: float
    file_size_mb: float
    specs: VideoSpec
    scenes_count: int
    assembly_time: float
    metadata: Dict[str, Any]

class VideoAssemblyPipeline:
    """
    Handles video assembly from generated assets using FFmpeg
    """
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix="video_assembly_")
        self.output_dir = os.path.join(os.getcwd(), "generated_assets", "videos")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Video format specifications
        self.video_specs = {
            "youtube_short": VideoSpec(1080, 1920, 30, "4M"),  # 9:16 vertical
            "tiktok": VideoSpec(1080, 1920, 30, "3M"),         # 9:16 vertical
            "instagram_reel": VideoSpec(1080, 1920, 30, "3M"), # 9:16 vertical
            "youtube_standard": VideoSpec(1920, 1080, 30, "5M"), # 16:9 horizontal
            "facebook_ad": VideoSpec(1200, 1200, 30, "2M"),    # 1:1 square
            "linkedin_post": VideoSpec(1200, 1200, 30, "2M")   # 1:1 square
        }
        
        # Verify FFmpeg installation
        self._verify_ffmpeg()
    
    def _verify_ffmpeg(self):
        """Verify FFmpeg is installed and accessible"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                raise Exception("FFmpeg not found or not working")
            logger.info("FFmpeg verified successfully")
        except Exception as e:
            logger.error(f"FFmpeg verification failed: {e}")
            raise Exception("FFmpeg is required for video assembly but not available")
    
    async def assemble_video(
        self,
        scenes: List[VideoScene],
        video_type: str,
        brand_config: Optional[Dict[str, Any]] = None,
        music_path: Optional[str] = None,
        output_filename: Optional[str] = None
    ) -> AssembledVideo:
        """
        Assemble complete video from scenes
        """
        
        start_time = datetime.now()
        
        try:
            # Get video specifications
            specs = self.video_specs.get(video_type, self.video_specs["youtube_short"])
            
            # Prepare scenes (resize images, sync audio)
            prepared_scenes = await self._prepare_scenes(scenes, specs)
            
            # Create video segments for each scene
            scene_videos = await self._create_scene_videos(prepared_scenes, specs)
            
            # Combine scenes into final video
            combined_video = await self._combine_scenes(
                scene_videos, specs, music_path
            )
            
            # Add brand elements if provided
            if brand_config:
                branded_video = await self._add_brand_elements(
                    combined_video, brand_config, specs
                )
            else:
                branded_video = combined_video
            
            # Move to final output location
            final_path = self._get_output_path(output_filename, video_type)
            shutil.move(branded_video, final_path)
            
            # Get video metadata
            duration = await self._get_video_duration(final_path)
            file_size = os.path.getsize(final_path) / (1024 * 1024)  # MB
            assembly_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"Video assembled successfully: {final_path}")
            
            return AssembledVideo(
                video_path=final_path,
                duration_seconds=duration,
                file_size_mb=file_size,
                specs=specs,
                scenes_count=len(scenes),
                assembly_time=assembly_time,
                metadata={
                    "video_type": video_type,
                    "scenes": len(scenes),
                    "has_music": music_path is not None,
                    "has_branding": brand_config is not None,
                    "created_at": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Video assembly failed: {e}")
            raise
        finally:
            # Cleanup temporary files
            self._cleanup_temp_files()
    
    async def _prepare_scenes(
        self,
        scenes: List[VideoScene],
        specs: VideoSpec
    ) -> List[Dict[str, Any]]:
        """
        Prepare scene assets (resize images, prepare audio)
        """
        
        prepared_scenes = []
        
        for scene in scenes:
            # Resize and format image
            prepared_image = await self._prepare_image(
                scene.image_path, specs, scene.scene_id
            )
            
            # Prepare audio if present
            prepared_audio = None
            if scene.audio_path:
                prepared_audio = await self._prepare_audio(
                    scene.audio_path, scene.duration, scene.scene_id
                )
            
            prepared_scenes.append({
                "scene_id": scene.scene_id,
                "image_path": prepared_image,
                "audio_path": prepared_audio,
                "duration": scene.duration,
                "text_overlay": scene.text_overlay,
                "transition_type": scene.transition_type,
                "effects": scene.effects or []
            })
        
        return prepared_scenes
    
    async def _prepare_image(
        self,
        image_path: str,
        specs: VideoSpec,
        scene_id: str
    ) -> str:
        """
        Resize and format image for video specifications
        """
        
        output_path = os.path.join(self.temp_dir, f"scene_{scene_id}_prepared.png")
        
        # FFmpeg command to resize and format image
        cmd = [
            'ffmpeg', '-y',  # Overwrite output
            '-i', image_path,
            '-vf', f'scale={specs.width}:{specs.height}:force_original_aspect_ratio=decrease,pad={specs.width}:{specs.height}:(ow-iw)/2:(oh-ih)/2:black',
            '-pix_fmt', 'rgba',
            output_path
        ]
        
        result = await self._run_ffmpeg_command(cmd)
        if result.returncode != 0:
            raise Exception(f"Failed to prepare image for scene {scene_id}")
        
        return output_path
    
    async def _prepare_audio(
        self,
        audio_path: str,
        target_duration: float,
        scene_id: str
    ) -> str:
        """
        Prepare audio to match scene duration
        """
        
        output_path = os.path.join(self.temp_dir, f"scene_{scene_id}_audio.mp3")
        
        # FFmpeg command to format audio and adjust duration
        cmd = [
            'ffmpeg', '-y',
            '-i', audio_path,
            '-t', str(target_duration),  # Trim to target duration
            '-ar', '44100',  # Sample rate
            '-ac', '2',      # Stereo
            '-b:a', '128k',  # Bitrate
            output_path
        ]
        
        result = await self._run_ffmpeg_command(cmd)
        if result.returncode != 0:
            raise Exception(f"Failed to prepare audio for scene {scene_id}")
        
        return output_path
    
    async def _create_scene_videos(
        self,
        prepared_scenes: List[Dict[str, Any]],
        specs: VideoSpec
    ) -> List[str]:
        """
        Create individual video clips for each scene
        """
        
        scene_videos = []
        
        for scene in prepared_scenes:
            video_path = await self._create_single_scene_video(scene, specs)
            scene_videos.append(video_path)
        
        return scene_videos
    
    async def _create_single_scene_video(
        self,
        scene: Dict[str, Any],
        specs: VideoSpec
    ) -> str:
        """
        Create video clip for a single scene
        """
        
        scene_id = scene["scene_id"]
        output_path = os.path.join(self.temp_dir, f"scene_{scene_id}.mp4")
        
        # Build FFmpeg command
        cmd = ['ffmpeg', '-y']
        
        # Input image (loop for duration)
        cmd.extend([
            '-loop', '1',
            '-i', scene["image_path"],
            '-t', str(scene["duration"])
        ])
        
        # Input audio if present
        if scene["audio_path"]:
            cmd.extend(['-i', scene["audio_path"]])
        
        # Video filters
        video_filters = []
        
        # Add zoom/pan effect for visual interest
        zoom_filter = f"zoompan=z='min(zoom+0.0015,1.3)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={specs.fps * scene['duration']}"
        video_filters.append(zoom_filter)
        
        # Add effects if specified
        for effect in scene.get("effects", []):
            if effect == "fade_in":
                video_filters.append("fade=in:0:30")
            elif effect == "fade_out":
                fade_start = int((scene["duration"] - 1) * specs.fps)
                video_filters.append(f"fade=out:{fade_start}:30")
        
        # Add text overlay if present
        if scene.get("text_overlay"):
            text = scene["text_overlay"].replace("'", "\\'")
            text_filter = f"drawtext=text='{text}':fontfile=/System/Library/Fonts/Arial.ttf:fontsize=60:fontcolor=white:x=(w-text_w)/2:y=h-150:enable='between(t,1,{scene['duration']-1})'"
            video_filters.append(text_filter)
        
        # Apply video filters
        if video_filters:
            cmd.extend(['-vf', ','.join(video_filters)])
        
        # Video encoding settings
        cmd.extend([
            '-c:v', specs.codec,
            '-pix_fmt', 'yuv420p',
            '-r', str(specs.fps),
            '-b:v', specs.bitrate,
        ])
        
        # Audio settings
        if scene["audio_path"]:
            cmd.extend([
                '-c:a', specs.audio_codec,
                '-b:a', '128k',
                '-shortest'  # End when shortest input ends
            ])
        else:
            cmd.extend(['-an'])  # No audio
        
        cmd.append(output_path)
        
        result = await self._run_ffmpeg_command(cmd)
        if result.returncode != 0:
            raise Exception(f"Failed to create video for scene {scene_id}")
        
        return output_path
    
    async def _combine_scenes(
        self,
        scene_videos: List[str],
        specs: VideoSpec,
        music_path: Optional[str] = None
    ) -> str:
        """
        Combine individual scene videos into final video
        """
        
        output_path = os.path.join(self.temp_dir, "combined_video.mp4")
        
        if len(scene_videos) == 1:
            # Single scene - just copy with music if needed
            if music_path:
                cmd = [
                    'ffmpeg', '-y',
                    '-i', scene_videos[0],
                    '-i', music_path,
                    '-c:v', 'copy',
                    '-c:a', 'aac',
                    '-filter_complex', '[1:a]volume=0.3[bg];[0:a][bg]amix=inputs=2:duration=shortest',
                    output_path
                ]
            else:
                shutil.copy(scene_videos[0], output_path)
                return output_path
        else:
            # Multiple scenes - create concat file and combine
            concat_file = os.path.join(self.temp_dir, "concat_list.txt")
            with open(concat_file, 'w') as f:
                for video in scene_videos:
                    f.write(f"file '{video}'\n")
            
            cmd = [
                'ffmpeg', '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_file
            ]
            
            # Add background music if provided
            if music_path:
                cmd.extend(['-i', music_path])
                cmd.extend([
                    '-filter_complex',
                    '[1:a]volume=0.2[bg];[0:a][bg]amix=inputs=2:duration=first:dropout_transition=0'
                ])
            
            cmd.extend([
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-shortest',
                output_path
            ])
        
        result = await self._run_ffmpeg_command(cmd)
        if result.returncode != 0:
            raise Exception("Failed to combine scene videos")
        
        return output_path
    
    async def _add_brand_elements(
        self,
        video_path: str,
        brand_config: Dict[str, Any],
        specs: VideoSpec
    ) -> str:
        """
        Add brand elements like logo, watermark, colors
        """
        
        output_path = os.path.join(self.temp_dir, "branded_video.mp4")
        
        cmd = ['ffmpeg', '-y', '-i', video_path]
        
        # Add logo if provided
        if brand_config.get("logo_url") and os.path.exists(brand_config["logo_url"]):
            logo_path = brand_config["logo_url"]
            cmd.extend(['-i', logo_path])
            
            # Position logo in corner
            logo_filter = f"[1:v]scale=120:120[logo];[0:v][logo]overlay=W-w-20:20"
            cmd.extend(['-filter_complex', logo_filter])
        
        cmd.extend([
            '-c:v', 'libx264',
            '-c:a', 'copy',
            output_path
        ])
        
        result = await self._run_ffmpeg_command(cmd)
        if result.returncode != 0:
            raise Exception("Failed to add brand elements")
        
        return output_path
    
    async def _run_ffmpeg_command(self, cmd: List[str]) -> subprocess.CompletedProcess:
        """
        Run FFmpeg command asynchronously
        """
        
        logger.debug(f"Running FFmpeg command: {' '.join(cmd)}")
        
        try:
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            return subprocess.CompletedProcess(
                args=cmd,
                returncode=result.returncode,
                stdout=stdout,
                stderr=stderr
            )
        except Exception as e:
            logger.error(f"FFmpeg command failed: {e}")
            raise
    
    async def _get_video_duration(self, video_path: str) -> float:
        """
        Get video duration in seconds using FFprobe
        """
        
        cmd = [
            'ffprobe', '-v', 'quiet',
            '-show_entries', 'format=duration',
            '-of', 'csv=p=0',
            video_path
        ]
        
        try:
            result = await self._run_ffmpeg_command(cmd)
            if result.returncode == 0:
                return float(result.stdout.decode().strip())
            else:
                return 0.0
        except Exception as e:
            logger.warning(f"Could not determine video duration: {e}")
            return 0.0
    
    def _get_output_path(self, filename: Optional[str], video_type: str) -> str:
        """
        Generate output path for final video
        """
        
        if filename:
            return os.path.join(self.output_dir, filename)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"video_{video_type}_{timestamp}.mp4"
        return os.path.join(self.output_dir, filename)
    
    def _cleanup_temp_files(self):
        """
        Clean up temporary files and directories
        """
        
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                logger.debug("Temporary files cleaned up")
        except Exception as e:
            logger.warning(f"Failed to cleanup temp files: {e}")

# Additional utility functions
class VideoEffects:
    """
    Predefined video effects that can be applied to scenes
    """
    
    @staticmethod
    def get_transition_filter(transition_type: str, duration: float = 1.0) -> str:
        """
        Get FFmpeg filter for scene transitions
        """
        
        transitions = {
            "fade": f"fade=in:0:30:alpha=1",
            "slide_left": "slide=left",
            "slide_right": "slide=right",
            "zoom_in": "zoompan=z='zoom+0.1':d=125",
            "crossfade": f"crossfade=duration={duration}:offset=0",
        }
        
        return transitions.get(transition_type, transitions["fade"])
    
    @staticmethod
    def get_text_animation(animation_type: str) -> str:
        """
        Get FFmpeg filter for text animations
        """
        
        animations = {
            "fade_in": "fade=in:0:30:alpha=1",
            "slide_up": "drawtext=enable='between(t,1,5)':y=h-t*30",
            "typewriter": "drawtext=text_shaping=1",
        }
        
        return animations.get(animation_type, "")

# Factory function
def create_video_assembly_pipeline() -> VideoAssemblyPipeline:
    """Create and return a video assembly pipeline instance"""
    return VideoAssemblyPipeline()