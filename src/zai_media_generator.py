"""
Z.AI Media Generator Module

Provides comprehensive integration with Z.AI's image and video generation APIs.
Supports CogView-4 image generation and multiple video generation models.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from pathlib import Path
import aiohttp
import aiofiles


@dataclass
class ImageGenerationRequest:
    """Image generation request parameters."""
    prompt: str
    model: str = "cogview-4-250304"
    quality: str = "hd"  # "hd" or "standard"
    size: str = "1024x1024"  # 512px-2048px
    user_id: Optional[str] = None


@dataclass
class VideoGenerationRequest:
    """Video generation request parameters."""
    prompt: str
    model: str = "cogvideox-3"  # cogvideox-3, viduq1-text, viduq1-image, vidu2-image, viduq1-start-end, vidu2-reference
    quality: str = "hd"
    size: str = "1280x720"
    duration: Optional[int] = None  # in seconds
    fps: Optional[int] = None
    with_audio: bool = True
    user_id: Optional[str] = None


@dataclass
class MediaGenerationResult:
    """Result of media generation operation."""
    success: bool
    media_url: Optional[str] = None
    cover_image_url: Optional[str] = None  # For videos
    task_id: Optional[str] = None  # For async video generation
    error_message: Optional[str] = None
    generation_time: Optional[float] = None
    model_used: Optional[str] = None
    content_filter: Optional[Dict[str, Any]] = None


class ZAIMediaGenerator:
    """
    Comprehensive media generation using Z.AI APIs.

    Supports:
    - CogView-4 image generation
    - Multiple video generation models (CogVideoX, Vidu series)
    - Async video status checking
    - Error handling and retry logic
    """

    def __init__(self, api_key: str, base_url: str = "https://api.z.ai/api"):
        """
        Initialize Z.AI Media Generator.

        Args:
            api_key: Z.AI API key from https://z.ai/manage-apikey/apikey-list
            base_url: API base URL (default: https://api.z.ai/api)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept-Language": "en-US,en"
        }

        # Available models
        self.image_models = ["cogview-4-250304"]
        self.video_models = [
            "cogvideox-3", "viduq1-text", "viduq1-image",
            "vidu2-image", "viduq1-start-end", "vidu2-reference"
        ]

        # Generation tracking
        self.active_video_tasks: Dict[str, Dict] = {}
        self.generation_history: List[Dict] = []

    async def generate_image(self, request: ImageGenerationRequest) -> MediaGenerationResult:
        """
        Generate an image using CogView-4.

        Args:
            request: Image generation parameters

        Returns:
            MediaGenerationResult with image URL or error
        """
        start_time = time.time()

        try:
            # Validate parameters
            if request.model not in self.image_models:
                return MediaGenerationResult(
                    success=False,
                    error_message=f"Invalid image model: {request.model}. Available: {self.image_models}"
                )

            # Prepare request payload
            payload = {
                "model": request.model,
                "prompt": request.prompt,
                "quality": request.quality,
                "size": request.size
            }

            if request.user_id:
                payload["user_id"] = request.user_id

            # Make API request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/paas/v4/images/generations",
                    headers=self.headers,
                    json=payload
                ) as response:

                    generation_time = time.time() - start_time

                    if response.status == 200:
                        result_data = await response.json()

                        # Extract image URL and content filter info
                        image_url = result_data.get("data", [{}])[0].get("url")
                        content_filter = result_data.get("data", [{}])[0].get("content_filter")

                        if image_url:
                            # Record generation
                            generation_record = {
                                "type": "image",
                                "model": request.model,
                                "prompt": request.prompt,
                                "url": image_url,
                                "timestamp": datetime.now().isoformat(),
                                "generation_time": generation_time,
                                "parameters": {
                                    "quality": request.quality,
                                    "size": request.size
                                }
                            }
                            self.generation_history.append(generation_record)

                            return MediaGenerationResult(
                                success=True,
                                media_url=image_url,
                                generation_time=generation_time,
                                model_used=request.model,
                                content_filter=content_filter
                            )
                        else:
                            return MediaGenerationResult(
                                success=False,
                                error_message="No image URL in response",
                                generation_time=generation_time
                            )
                    else:
                        error_text = await response.text()
                        return MediaGenerationResult(
                            success=False,
                            error_message=f"API Error {response.status}: {error_text}",
                            generation_time=generation_time
                        )

        except Exception as e:
            return MediaGenerationResult(
                success=False,
                error_message=f"Generation failed: {str(e)}",
                generation_time=time.time() - start_time
            )

    async def generate_video(self, request: VideoGenerationRequest) -> MediaGenerationResult:
        """
        Generate a video using Z.AI video models.

        Args:
            request: Video generation parameters

        Returns:
            MediaGenerationResult with task ID for async processing
        """
        start_time = time.time()

        try:
            # Validate parameters
            if request.model not in self.video_models:
                return MediaGenerationResult(
                    success=False,
                    error_message=f"Invalid video model: {request.model}. Available: {self.video_models}"
                )

            # Prepare request payload
            payload = {
                "model": request.model,
                "prompt": request.prompt,
                "quality": request.quality,
                "size": request.size,
                "with_audio": request.with_audio
            }

            # Add optional parameters
            if request.duration:
                payload["duration"] = request.duration
            if request.fps:
                payload["fps"] = request.fps
            if request.user_id:
                payload["user_id"] = request.user_id

            # Make API request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/paas/v4/videos/generations",
                    headers=self.headers,
                    json=payload
                ) as response:

                    generation_time = time.time() - start_time

                    if response.status == 200:
                        result_data = await response.json()

                        # Extract task ID
                        task_id = result_data.get("task_id")

                        if task_id:
                            # Track the task
                            self.active_video_tasks[task_id] = {
                                "model": request.model,
                                "prompt": request.prompt,
                                "status": "PROCESSING",
                                "created_at": datetime.now().isoformat(),
                                "parameters": {
                                    "quality": request.quality,
                                    "size": request.size,
                                    "duration": request.duration,
                                    "fps": request.fps,
                                    "with_audio": request.with_audio
                                }
                            }

                            return MediaGenerationResult(
                                success=True,
                                task_id=task_id,
                                generation_time=generation_time,
                                model_used=request.model
                            )
                        else:
                            return MediaGenerationResult(
                                success=False,
                                error_message="No task ID in response",
                                generation_time=generation_time
                            )
                    else:
                        error_text = await response.text()
                        return MediaGenerationResult(
                            success=False,
                            error_message=f"API Error {response.status}: {error_text}",
                            generation_time=generation_time
                        )

        except Exception as e:
            return MediaGenerationResult(
                success=False,
                error_message=f"Video generation failed: {str(e)}",
                generation_time=time.time() - start_time
            )

    async def check_video_status(self, task_id: str) -> MediaGenerationResult:
        """
        Check the status of a video generation task.

        Args:
            task_id: The task ID from generate_video

        Returns:
            MediaGenerationResult with current status or video URL if complete
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/paas/v4/async-result/{task_id}",
                    headers=self.headers
                ) as response:

                    if response.status == 200:
                        result_data = await response.json()

                        task_status = result_data.get("task_status", "UNKNOWN")
                        model_used = result_data.get("model")

                        # Update task tracking
                        if task_id in self.active_video_tasks:
                            self.active_video_tasks[task_id]["status"] = task_status
                            self.active_video_tasks[task_id]["last_checked"] = datetime.now().isoformat()

                        if task_status == "SUCCESS":
                            video_results = result_data.get("video_result", [])
                            if video_results:
                                video_url = video_results[0].get("url")
                                cover_image_url = video_results[0].get("cover_image_url")

                                # Record successful generation
                                generation_record = {
                                    "type": "video",
                                    "model": model_used,
                                    "task_id": task_id,
                                    "video_url": video_url,
                                    "cover_image_url": cover_image_url,
                                    "completed_at": datetime.now().isoformat(),
                                    "parameters": self.active_video_tasks.get(task_id, {}).get("parameters", {})
                                }
                                self.generation_history.append(generation_record)

                                # Remove from active tasks
                                if task_id in self.active_video_tasks:
                                    del self.active_video_tasks[task_id]

                                return MediaGenerationResult(
                                    success=True,
                                    media_url=video_url,
                                    cover_image_url=cover_image_url,
                                    model_used=model_used,
                                    task_id=task_id
                                )
                            else:
                                return MediaGenerationResult(
                                    success=False,
                                    error_message="SUCCESS status but no video URL in response",
                                    task_id=task_id,
                                    model_used=model_used
                                )
                        elif task_status == "FAIL":
                            # Remove from active tasks on failure
                            if task_id in self.active_video_tasks:
                                del self.active_video_tasks[task_id]

                            return MediaGenerationResult(
                                success=False,
                                error_message="Video generation failed",
                                task_id=task_id,
                                model_used=model_used
                            )
                        else:  # PROCESSING
                            return MediaGenerationResult(
                                success=True,
                                task_id=task_id,
                                model_used=model_used
                            )
                    else:
                        error_text = await response.text()
                        return MediaGenerationResult(
                            success=False,
                            error_message=f"Status check error {response.status}: {error_text}",
                            task_id=task_id
                        )

        except Exception as e:
            return MediaGenerationResult(
                success=False,
                error_message=f"Status check failed: {str(e)}",
                task_id=task_id
            )

    async def wait_for_video_completion(
        self,
        task_id: str,
        timeout_minutes: int = 10,
        check_interval_seconds: int = 30
    ) -> MediaGenerationResult:
        """
        Wait for video generation to complete.

        Args:
            task_id: Video generation task ID
            timeout_minutes: Maximum time to wait
            check_interval_seconds: How often to check status

        Returns:
            MediaGenerationResult with final result
        """
        timeout = timedelta(minutes=timeout_minutes)
        start_time = datetime.now()

        while datetime.now() - start_time < timeout:
            result = await self.check_video_status(task_id)

            if not result.success and result.error_message != "Video generation failed":
                # API error, not task failure
                return result

            if result.success and result.media_url:
                # Video completed successfully
                return result

            if not result.success and result.error_message == "Video generation failed":
                # Video generation failed
                return result

            # Still processing, wait and check again
            await asyncio.sleep(check_interval_seconds)

        # Timeout reached
        return MediaGenerationResult(
            success=False,
            error_message=f"Video generation timed out after {timeout_minutes} minutes",
            task_id=task_id
        )

    def get_generation_history(self, media_type: Optional[str] = None) -> List[Dict]:
        """
        Get history of media generations.

        Args:
            media_type: Filter by "image", "video", or None for all

        Returns:
            List of generation records
        """
        if media_type:
            return [gen for gen in self.generation_history if gen.get("type") == media_type]
        return self.generation_history.copy()

    def get_active_video_tasks(self) -> Dict[str, Dict]:
        """Get all currently active video generation tasks."""
        return self.active_video_tasks.copy()

    async def save_media_locally(self, media_url: str, local_path: Union[str, Path]) -> bool:
        """
        Download and save media from URL to local file.

        Args:
            media_url: URL of the media to download
            local_path: Local path to save the file

        Returns:
            True if successful, False otherwise
        """
        try:
            local_path = Path(local_path)
            local_path.parent.mkdir(parents=True, exist_ok=True)

            async with aiohttp.ClientSession() as session:
                async with session.get(media_url) as response:
                    if response.status == 200:
                        content = await response.read()
                        async with aiofiles.open(local_path, 'wb') as f:
                            await f.write(content)
                        return True
                    else:
                        return False

        except Exception as e:
            print(f"Error saving media: {e}")
            return False

    def get_available_models(self) -> Dict[str, List[str]]:
        """Get lists of available models."""
        return {
            "image": self.image_models.copy(),
            "video": self.video_models.copy()
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get generation statistics."""
        total_generations = len(self.generation_history)
        image_generations = len([g for g in self.generation_history if g.get("type") == "image"])
        video_generations = len([g for g in self.generation_history if g.get("type") == "video"])

        return {
            "total_generations": total_generations,
            "image_generations": image_generations,
            "video_generations": video_generations,
            "active_video_tasks": len(self.active_video_tasks),
            "available_image_models": len(self.image_models),
            "available_video_models": len(self.video_models)
        }