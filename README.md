# YouNix

YouNix is a terminal-based YouTube video player that converts videos into ASCII art for playback directly in your terminal. It offers a unique, retro-style way to watch YouTube content with audio support.

## 🌟 Features

- Search YouTube videos directly from the terminal
- ASCII art video playback
- Audio playback support
- Smart caching system for both searches and videos
- Cross-platform compatibility
- Low bandwidth mode with worst quality video download

## 🔧 Prerequisites

- Python 3.7 or higher
- Terminal that supports ASCII characters
- Internet connection

## 📦 Required Dependencies

The following Python packages are required:

python:requirements.txt
opencv-python>=4.5.0
pygame>=2.0.0
ascii-magic>=1.0.0
rich>=10.0.0
Pillow>=8.0.0
numpy>=1.19.0
yt-dlp>=2023.0.0

## 🚀 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/younix.git
   cd younix
   ```

2. Install Python dependencies:
   ```bash
   python setup.py
   ```
   This will automatically install all required packages.

   Alternatively, you can manually install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 🎮 Usage

1. Start the program:
   ```bash
   python main.py
   ```

2. Enter a search term when prompted
3. Select a video from the search results by entering its number
4. Enjoy the ASCII video playback! Press 'q' to stop playback

## 🔍 How It Works

YouNix converts YouTube videos into ASCII art in real-time while maintaining audio playback. It features:

- Smart caching system for both search results and videos
- Optimized frame rate handling for smooth ASCII playback
- Cross-platform terminal clearing and display
- Concurrent video and audio playback using threading
- Low bandwidth mode using worst quality video download

## 🗄️ Cache Management

Videos and search results are cached in `~/.younix_cache/` to improve performance and reduce bandwidth usage:
- Videos: `~/.younix_cache/videos/`
- Searches: `~/.younix_cache/searches/`

## ⌨️ Controls

- `q`: Quit the program
- Enter: Skip current selection
- Number keys: Select video from search results

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.
