#!/usr/bin/env python3
"""
Dynamic Hunspell downloader and wrapper for distributable applications.
Downloads and manages Hunspell binaries and dictionaries on-demand.
"""

import asyncio
import hashlib
import platform
import subprocess
import tempfile
import zipfile
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin
import aiohttp
import aiofiles


class HunspellManager:
    """Manages Hunspell installation and dictionary downloads."""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or Path.home() / ".hunspell_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.system = platform.system().lower()
        self.arch = platform.machine().lower()
        
        # Hunspell download URLs (you'll need to host these or find reliable sources)
        self.hunspell_urls = {
            "windows": {
                "x86_64": "https://github.com/hunspell/hunspell/releases/download/v1.7.2/hunspell-1.7.2-win64.zip",
                "i386": "https://github.com/hunspell/hunspell/releases/download/v1.7.2/hunspell-1.7.2-win32.zip"
            },
            "linux": {
                "x86_64": "https://github.com/hunspell/hunspell/releases/download/v1.7.2/hunspell-1.7.2-linux-x86_64.tar.gz"
            },
            "darwin": {
                "x86_64": "https://github.com/hunspell/hunspell/releases/download/v1.7.2/hunspell-1.7.2-macos-x86_64.tar.gz",
                "arm64": "https://github.com/hunspell/hunspell/releases/download/v1.7.2/hunspell-1.7.2-macos-arm64.tar.gz"
            }
        }
        
        # Dictionary sources
        self.dict_base_url = "https://raw.githubusercontent.com/LibreOffice/dictionaries/master/"
        self.dict_mappings = {
            "en_US": "en/en_US",
            "en_GB": "en/en_GB", 
            "es_ES": "es_ES/es_ES",
            "fr_FR": "fr_FR/fr_FR",
            "de_DE": "de_DE/de_DE",
            "it_IT": "it_IT/it_IT",
            "pt_PT": "pt_PT/pt_PT",
            "ru_RU": "ru_RU/ru_RU",
        }
    
    @property
    def hunspell_executable(self) -> Path:
        """Get path to Hunspell executable."""
        exe_name = "hunspell.exe" if self.system == "windows" else "hunspell"
        return self.cache_dir / "bin" / exe_name
    
    @property
    def dict_dir(self) -> Path:
        """Get dictionary directory path."""
        return self.cache_dir / "dictionaries"
    
    async def is_hunspell_available(self) -> bool:
        """Check if Hunspell is available and working."""
        if not self.hunspell_executable.exists():
            return False
        
        try:
            process = await asyncio.create_subprocess_exec(
                str(self.hunspell_executable), "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            return process.returncode == 0
        except Exception:
            return False
    
    async def download_file(self, url: str, destination: Path, 
                          progress_callback: Optional[callable] = None) -> bool:
        """Download file with optional progress callback."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return False
                    
                    total_size = int(response.headers.get('content-length', 0))
                    downloaded = 0
                    
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    
                    async with aiofiles.open(destination, 'wb') as file:
                        async for chunk in response.content.iter_chunked(8192):
                            await file.write(chunk)
                            downloaded += len(chunk)
                            
                            if progress_callback and total_size > 0:
                                progress = (downloaded / total_size) * 100
                                await progress_callback(progress, downloaded, total_size)
                    
                    return True
        except Exception as e:
            print(f"Download failed: {e}")
            return False
    
    async def install_hunspell(self, progress_callback: Optional[callable] = None) -> bool:
        """Download and install Hunspell binary."""
        if await self.is_hunspell_available():
            return True
        
        # Get appropriate download URL
        arch_key = "x86_64" if self.arch in ["x86_64", "amd64"] else self.arch
        if self.system not in self.hunspell_urls:
            raise RuntimeError(f"Unsupported system: {self.system}")
        
        system_urls = self.hunspell_urls[self.system]
        if arch_key not in system_urls:
            raise RuntimeError(f"Unsupported architecture: {arch_key} on {self.system}")
        
        download_url = system_urls[arch_key]
        
        # Download archive
        archive_path = self.cache_dir / f"hunspell_archive_{self.system}_{arch_key}"
        
        print(f"Downloading Hunspell from {download_url}...")
        if not await self.download_file(download_url, archive_path, progress_callback):
            return False
        
        # Extract archive
        try:
            if download_url.endswith('.zip'):
                with zipfile.ZipFile(archive_path, 'r') as zip_file:
                    zip_file.extractall(self.cache_dir)
            else:
                # Handle tar.gz files
                import tarfile
                with tarfile.open(archive_path, 'r:gz') as tar_file:
                    tar_file.extractall(self.cache_dir)
            
            # Make executable (Unix systems)
            if self.system != "windows":
                self.hunspell_executable.chmod(0o755)
            
            # Clean up archive
            archive_path.unlink()
            
            return await self.is_hunspell_available()
            
        except Exception as e:
            print(f"Extraction failed: {e}")
            return False
    
    async def download_dictionary(self, language: str, 
                                progress_callback: Optional[callable] = None) -> bool:
        """Download dictionary files for specified language."""
        if language not in self.dict_mappings:
            raise ValueError(f"Unsupported language: {language}")
        
        dict_path = self.dict_mappings[language]
        self.dict_dir.mkdir(parents=True, exist_ok=True)
        
        # Download .aff and .dic files
        for ext in ['aff', 'dic']:
            filename = f"{language}.{ext}"
            url = urljoin(self.dict_base_url, f"{dict_path}.{ext}")
            destination = self.dict_dir / filename
            
            if destination.exists():
                continue  # Skip if already downloaded
            
            print(f"Downloading {filename}...")
            if not await self.download_file(url, destination, progress_callback):
                return False
        
        return True
    
    async def get_available_dictionaries(self) -> list[str]:
        """Get list of locally available dictionaries."""
        available = []
        for lang in self.dict_mappings:
            aff_file = self.dict_dir / f"{lang}.aff"
            dic_file = self.dict_dir / f"{lang}.dic"
            if aff_file.exists() and dic_file.exists():
                available.append(lang)
        return available


class AsyncHunspell:
    """Async wrapper for Hunspell operations."""
    
    def __init__(self, manager: HunspellManager, language: str = "en_US"):
        self.manager = manager
        self.language = language
        self._ensure_ready_task: Optional[asyncio.Task] = None
    
    async def ensure_ready(self, progress_callback: Optional[callable] = None) -> bool:
        """Ensure Hunspell and dictionary are available."""
        if self._ensure_ready_task is None:
            self._ensure_ready_task = asyncio.create_task(
                self._setup_hunspell(progress_callback)
            )
        return await self._ensure_ready_task
    
    async def _setup_hunspell(self, progress_callback: Optional[callable] = None) -> bool:
        """Setup Hunspell and dictionary."""
        # Install Hunspell if needed
        if not await self.manager.install_hunspell(progress_callback):
            return False
        
        # Download dictionary if needed
        if not await self.manager.download_dictionary(self.language, progress_callback):
            return False
        
        return True
    
    async def check_word(self, word: str) -> bool:
        """Check if a word is spelled correctly."""
        if not await self.ensure_ready():
            raise RuntimeError("Hunspell not available")
        
        dict_path = self.manager.dict_dir / self.language
        
        process = await asyncio.create_subprocess_exec(
            str(self.manager.hunspell_executable),
            "-d", str(dict_path),
            "-l",  # List only misspelled words
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate(input=word.encode())
        
        if process.returncode != 0:
            raise RuntimeError(f"Hunspell error: {stderr.decode()}")
        
        # If word is misspelled, it will appear in stdout
        return word not in stdout.decode().strip()
    
    async def suggest_corrections(self, word: str) -> list[str]:
        """Get spelling suggestions for a word."""
        if not await self.ensure_ready():
            raise RuntimeError("Hunspell not available")
        
        dict_path = self.manager.dict_dir / self.language
        
        process = await asyncio.create_subprocess_exec(
            str(self.manager.hunspell_executable),
            "-d", str(dict_path),
            "-a",  # Ispell compatibility mode for suggestions
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate(input=word.encode())
        
        if process.returncode != 0:
            raise RuntimeError(f"Hunspell error: {stderr.decode()}")
        
        # Parse suggestions from Hunspell output
        output = stdout.decode().strip()
        suggestions = []
        
        for line in output.split('\n'):
            if line.startswith('&'):  # Suggestions line
                parts = line.split(':')
                if len(parts) > 1:
                    suggestions = [s.strip() for s in parts[1].split(',')]
                break
        
        return suggestions[:10]  # Return top 10 suggestions
    
    async def check_text(self, text: str) -> dict[str, list[str]]:
        """Check entire text and return misspelled words with suggestions."""
        words = text.split()
        results = {}
        
        for word in words:
            # Clean word (remove punctuation)
            clean_word = ''.join(c for c in word if c.isalpha())
            if not clean_word:
                continue
            
            if not await self.check_word(clean_word):
                suggestions = await self.suggest_corrections(clean_word)
                results[clean_word] = suggestions
        
        return results


# Example usage and UI integration
async def example_usage():
    """Example of how to use the Hunspell manager."""
    
    async def progress_callback(percent: float, downloaded: int, total: int):
        print(f"Progress: {percent:.1f}% ({downloaded}/{total} bytes)")
    
    # Initialize manager
    manager = HunspellManager()
    
    # Create spell checker
    spell_checker = AsyncHunspell(manager, "en_US")
    
    # Ensure everything is ready (downloads if needed)
    print("Setting up Hunspell...")
    if not await spell_checker.ensure_ready(progress_callback):
        print("Failed to setup Hunspell!")
        return
    
    print("Hunspell ready!")
    
    # Test spell checking
    test_text = "This is a sampl text with mistaks to check."
    print(f"\nChecking: '{test_text}'")
    
    results = await spell_checker.check_text(test_text)
    
    if results:
        print("Misspelled words found:")
        for word, suggestions in results.items():
            print(f"  {word}: {', '.join(suggestions[:3])}")
    else:
        print("No misspelled words found!")


if __name__ == "__main__":
    # Install required packages first:
    # uv add aiohttp aiofiles
    
    asyncio.run(example_usage())