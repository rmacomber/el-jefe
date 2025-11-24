#!/usr/bin/env python3
"""
Test script for Z.AI Media Generation functionality

This script tests the image and video generation capabilities
using the Z.AI API integration.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.zai_media_generator import ZAIMediaGenerator, ImageGenerationRequest, VideoGenerationRequest


async def test_media_generation():
    """Test image and video generation functionality."""

    # Initialize with API key
    api_key = "e07f39da8b9345a29db09de5a3e74850.VkvWdw8X6MmjBVsU"
    media_gen = ZAIMediaGenerator(api_key)

    print("🎨 Testing Z.AI Media Generation")
    print("=" * 50)

    # Test 1: Get available models
    print("\n📋 Available Models:")
    models = media_gen.get_available_models()
    print(f"Image Models: {models['image']}")
    print(f"Video Models: {models['video']}")

    # Test 2: Generate a simple image
    print("\n🖼️ Testing Image Generation:")
    image_request = ImageGenerationRequest(
        prompt="A futuristic AI podcast studio with modern equipment, professional lighting, and sleek design",
        quality="standard",  # Faster for testing
        size="1024x1024"
    )

    print(f"Generating image with prompt: {image_request.prompt}")
    image_result = await media_gen.generate_image(image_request)

    if image_result.success:
        print(f"✅ Image generated successfully!")
        print(f"📸 Image URL: {image_result.media_url}")
        print(f"⏱️ Generation time: {image_result.generation_time:.2f} seconds")
        print(f"🤖 Model: {image_result.model_used}")

        # Save image locally
        local_path = "test_generated_image.jpg"
        saved = await media_gen.save_media_locally(image_result.media_url, local_path)
        if saved:
            print(f"💾 Image saved locally: {local_path}")
    else:
        print(f"❌ Image generation failed: {image_result.error_message}")

    # Test 3: Generate a video (commented out to avoid costs during testing)
    print("\n🎬 Testing Video Generation:")
    video_request = VideoGenerationRequest(
        prompt="A short animated logo reveal for an AI technology podcast, with futuristic elements",
        model="cogvideox-3",
        quality="standard",
        with_audio=False  # Faster generation
    )

    print(f"Generating video with prompt: {video_request.prompt}")
    video_result = await media_gen.generate_video(video_request)

    if video_result.success:
        print(f"✅ Video generation started!")
        print(f"🆔 Task ID: {video_result.task_id}")
        print(f"🤖 Model: {video_result.model_used}")
        print(f"⏱️ Initial generation time: {video_result.generation_time:.2f} seconds")

        # Check status (limited checks for demo)
        print("\n⏳ Checking video status...")
        for i in range(3):  # Check 3 times as demo
            await asyncio.sleep(10)  # Wait 10 seconds between checks
            status_result = await media_gen.check_video_status(video_result.task_id)

            if status_result.success:
                print(f"Check {i+1}: Status = {status_result.task_id}")
                if status_result.media_url:
                    print(f"✅ Video completed!")
                    print(f"🎥 Video URL: {status_result.media_url}")
                    if status_result.cover_image_url:
                        print(f"🖼️ Cover Image: {status_result.cover_image_url}")
                    break
                else:
                    print(f"Still processing...")
            else:
                print(f"❌ Status check failed: {status_result.error_message}")
                break
    else:
        print(f"❌ Video generation failed: {video_result.error_message}")

    # Test 4: Get generation stats
    print("\n📊 Generation Statistics:")
    stats = media_gen.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Test 5: Get active tasks
    print("\n🔄 Active Video Tasks:")
    active_tasks = media_gen.get_active_video_tasks()
    if active_tasks:
        for task_id, task_info in active_tasks.items():
            print(f"  {task_id}: {task_info['model']} - {task_info['status']}")
    else:
        print("  No active video tasks")

    print("\n🎉 Media generation test completed!")


if __name__ == "__main__":
    asyncio.run(test_media_generation())