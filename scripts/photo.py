# Define the root directory containing photo directories
import itertools
import os
from datetime import datetime

PHOTO_DIR = "photos"


# Create an iterator to cycle through the photos in the current directory
class PhotoCycler:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.photos = []
        self.photo_iterator = None
        self.load_photos_for_today()

    def get_directory_for_today(self):
        # Use the day of the year to determine the directory
        subdirs = sorted(
            [
                d
                for d in os.listdir(self.root_dir)
                if os.path.isdir(os.path.join(self.root_dir, d))
            ]
        )
        if not subdirs:
            raise ValueError("No subdirectories found in the specified root directory.")
        day_of_year = datetime.now().timetuple().tm_yday
        return os.path.join(self.root_dir, subdirs[day_of_year % len(subdirs)])

    def load_photos_for_today(self):
        # Load photos from the directory corresponding to today's date
        try:
            today_dir = self.get_directory_for_today()
            self.photos = [
                os.path.join(today_dir, file)
                for file in os.listdir(today_dir)
                if file.lower().endswith(("png", "jpg", "jpeg", "gif"))
            ]
            if not self.photos:
                raise ValueError(
                    f"No photos found in the directory for today: {today_dir}."
                )
        except Exception as e:
            # Fallback to the default directory inside the root directory
            default_dir = os.path.join(self.root_dir, "default")
            if os.path.isdir(default_dir):
                self.photos = [
                    os.path.join(default_dir, file)
                    for file in os.listdir(default_dir)
                    if file.lower().endswith(("png", "jpg", "jpeg", "gif"))
                ]
            else:
                raise ValueError("Default folder not found or is empty.")
        self.photo_iterator = itertools.cycle(self.photos)

    def get_next_photo(self):
        return next(self.photo_iterator)


photo_cycler = PhotoCycler(PHOTO_DIR)
