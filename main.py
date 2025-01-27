import subprocess
import json
import tempfile
import os 
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from pathlib import Path
import cv2
from rich.console import Console
from rich.table import Table
from ascii_magic import AsciiArt
import hashlib
from typing import Dict, Optional
import pygame
from concurrent.futures import ThreadPoolExecutor
import time
from time import sleep

class YoutubeBrowser:

    def __init__(self, cache_dir: Optional[str] = None):
        self.console = Console()
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Initialize pygame and mixer with proper settings
        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
        
        # Initialize cache directories
        self.cache_dir = Path(cache_dir) if cache_dir else Path.home() / '.younix_cache'
        self.video_cache_dir = self.cache_dir / 'videos'
        self.search_cache_dir = self.cache_dir / 'searches'
        self.video_cache_dir.mkdir(parents=True, exist_ok=True)
        self.search_cache_dir.mkdir(parents=True, exist_ok=True)

        # In-memory cache for search results
        self.search_cache: Dict[str, list] = {}
        
        self._check_dependencies()

    def _check_dependencies(self) -> None:
        try:
            subprocess.run(['yt-dlp', '--version'], capture_output=True, check=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            raise RuntimeError("yt-dlp not found. Install with: pip install yt-dlp")

    def _get_cache_key(self, data: str) -> str:
        """Generate a cache key using MD5 hash"""
        return hashlib.md5(data.encode()).hexdigest()

    def search_videos(self, query: str, limit: int = 5) -> list:
        cache_key = self._get_cache_key(f"{query}_{limit}")
        
        # Check in-memory cache first
        if cache_key in self.search_cache:
            self.console.print("[green]Using cached search results[/green]")
            return self.search_cache[cache_key]
        
        # Check file cache
        cache_file = self.search_cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            self.console.print("[green]Loading search results from file cache[/green]")
            with open(cache_file, 'r') as f:
                results = json.load(f)
                self.search_cache[cache_key] = results
                return results

        try:
            cmd = ['yt-dlp', '--dump-json', f'ytsearch{min(limit, 10)}:{query}']
            proc = subprocess.run(cmd, text=True, capture_output=True, timeout=30, check=True)
            results = [json.loads(line) for line in proc.stdout.splitlines()]
            
            # Save to both memory and file cache
            self.search_cache[cache_key] = results
            with open(cache_file, 'w') as f:
                json.dump(results, f)
            
            return results
        except Exception as e:
            self.console.print(f"[red]Search error: {e}[/red]")
            return []

    def play_video(self, video_url: str) -> None:
        try:
            # Ensure mixer is initialized before playing
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
            
            self._clear_screen()  # Clear screen before playback
            
            cache_key = self._get_cache_key(video_url)
            cached_video_path = self.video_cache_dir / f"{cache_key}.mp4"
            cached_audio_path = self.video_cache_dir / f"{cache_key}.mp3"
            
            output_path = self._get_or_download_video(video_url, cached_video_path)
            if not output_path:
                return
            
            # Play video and audio concurrently
            with ThreadPoolExecutor(max_workers=2) as executor:
                try:
                    video_future = executor.submit(self._play_video_frames, cv2.VideoCapture(str(output_path)))
                    audio_future = executor.submit(self._play_audio, cached_audio_path)
                    
                    # Wait for both to complete
                    video_future.result()
                    audio_future.result()
                except KeyboardInterrupt:
                    pygame.mixer.music.stop()
                    executor.shutdown(wait=False, cancel_futures=True)
                    print("\nPlayback stopped")
                    return
            
        except Exception as e:
            self.console.print(f"Error playing video: {str(e)}", style="bold red")
        finally:
            pygame.mixer.quit()  # Clean up mixer when done
            self._clear_screen()  # Clear screen after playback

    def _get_or_download_video(self, video_url: str, cached_path: Path) -> Optional[Path]:
        if cached_path.exists():
            self.console.print("[green]Using cached video file[/green]")
            return cached_path
        
        try:
            self._download_video(video_url, cached_path)
            return cached_path
        except Exception as e:
            self.console.print(f"[red]Download error: {e}[/red]")
            return None

    def _download_video(self, video_url: str, cached_path: Path) -> None:
        try:
            # Download video and audio separately
            video_cmd = [
                'yt-dlp',
                '-f', 'worst[ext=mp4]',
                video_url,
                '-o', str(cached_path)
            ]
            audio_cmd = [
                'yt-dlp',
                '-x',  # Extract audio
                '--audio-format', 'mp3',  # Force MP3 format
                '--audio-quality', '5',  # Lowest quality (0 is best)
                video_url,
                '-o', str(cached_path.with_suffix('.mp3'))
            ]
            self.console.print("Downloading video and audio...")
            subprocess.run(video_cmd, check=True)
            subprocess.run(audio_cmd, check=True)
            
            # Verify audio file exists and has size
            audio_path = cached_path.with_suffix('.mp3')
            if audio_path.exists():
                size = audio_path.stat().st_size
                self.console.print(f"[green]Audio file downloaded: {size} bytes[/green]")
            else:
                self.console.print("[red]Audio file not created![/red]")
                
        except Exception as e:
            self.console.print(f"[red]Download error: {e}[/red]")

    def _play_video_frames(self, cap: cv2.VideoCapture) -> None:
        try:
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_time = 1.0 / fps  # seconds per frame
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            # Get terminal size
            terminal_columns = os.get_terminal_size().columns
            frame_count = 0

            start_time = time.time()

            # Clear screen once at start and move cursor to top
            print("\033[2J\033[H", end='', flush=True)

            # Reduce effective frame rate for smoother ASCII playback
            frame_skip = max(1, int(fps / 15))  # Target ~15 fps for ASCII art
            while cap.isOpened() and frame_count < total_frames:
                target_time = start_time + (frame_count * frame_time)
                ret, frame = cap.read()
                if not ret:
                    break
                # Skip frames to reduce flickering
                if frame_count % frame_skip != 0:
                    frame_count += 1
                    continue

                current_time = time.time()
                sleep_time = target_time - current_time
                if sleep_time > 0:
                    time.sleep(sleep_time)

                # Reduce resolution before converting to ASCII
                scale_factor = 0.5
                resized_frame = cv2.resize(frame, None, fx=scale_factor, fy=scale_factor)
                
                frame_path = self.temp_dir / f"frame.png"
                cv2.imwrite(str(frame_path), resized_frame)
                art = AsciiArt.from_image(str(frame_path))
                
                # Move cursor to top-left only (don't clear screen each time)
                print("\033[H", end='', flush=True)
                art.to_terminal(columns=min(terminal_columns, 80), monochrome=True)
                frame_path.unlink()
                
                frame_count += 1

        except Exception as e:
            self.console.print(f"[red]Playback error: {e}[/red]")
        finally:
            cap.release()

    def _play_audio(self, audio_path: Path) -> None:
        try:
            if not audio_path.exists():
                self.console.print("[red]Audio file not found![/red]")
                return
                
            pygame.mixer.music.load(str(audio_path))
            pygame.mixer.music.play()
            
            clock = pygame.time.Clock()
            while pygame.mixer.music.get_busy():
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                        pygame.mixer.music.stop()
                        return
                clock.tick(10)
            
        except Exception as e:
            self.console.print(f"[red]Audio playback error: {str(e)}[/red]")

    def display_results(self, videos: list) -> None:
        table = Table(title="Search Results")
        table.add_column("#", justify="right", style="cyan")
        table.add_column("Title", style="white")
        table.add_column("Duration", justify="right", style="green")
        
        for idx, video in enumerate(videos, 1):
            duration = f"{video.get('duration', 0) // 60}:{video.get('duration', 0) % 60:02d}"
            table.add_row(str(idx), video.get('title', 'Unknown'), duration)
        
        self.console.print(table)

    def run(self) -> None:
        try:
            while True:
                query = input("\nSearch (q to quit): ").strip()
                if query.lower() == 'q':
                    break

                videos = self.search_videos(query)
                if videos:
                    self.display_results(videos)
                    choice = input("\nSelect # to play (Enter to skip): ").strip()
                    if choice.isdigit():
                        idx = int(choice) - 1
                        if 0 <= idx < len(videos):
                            self.play_video(videos[idx].get('webpage_url'))
        finally:
            self.cleanup()

    def cleanup(self) -> None:
        if self.temp_dir.exists():
            import shutil
            shutil.rmtree(self.temp_dir)

    def _clear_screen(self) -> None:
        """Clear the terminal screen in a cross-platform way"""
        os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    browser = YoutubeBrowser()
    browser.run()