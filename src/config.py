"""Configuration for Blogger XML to Yearly Reflection Generator"""
from pathlib import Path
from dataclasses import dataclass


@dataclass
class Config:
    """Configuration settings for the blog reflection generator"""

    # Input - XML file path (can be passed as argument)
    xml_file: Path = Path(r"c:\Users\tdevr\My Drive\Blog\Digital Memory Palace\2023 Export\blog-12-30-2023.xml")

    # Output - Fixed to /dmp/reflection directory
    output_dir: Path = Path(r"c:\GIT\dmp\reflection")

    # Templates and static assets
    templates_dir: Path = Path(r"c:\GIT\dmp\templates")
    static_dir: Path = Path(r"c:\GIT\dmp\static")

    # Image download settings
    image_timeout: int = 30
    image_retry_count: int = 3
    max_image_size_mb: int = 10

    # Processing settings
    max_preview_length: int = 200

    def __post_init__(self):
        """Ensure paths are Path objects"""
        self.xml_file = Path(self.xml_file)
        self.output_dir = Path(self.output_dir)
        self.templates_dir = Path(self.templates_dir)
        self.static_dir = Path(self.static_dir)
