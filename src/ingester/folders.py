"""Finding the partner's delivery folders: <partner>/YYYY/MM/DD/."""
from dataclasses import dataclass
from pathlib import Path

DONE_MARKER = "_DONE"


@dataclass
class DayFolder:
    path: Path      # data/incoming/redmondtownservice/2026/10/19
    label: str      # '2026/10/19', used in the logs and in the file_loads table

    @property
    def complete(self) -> bool:
        """The partner writes _DONE last. Without it, the delivery may still be in progress."""
        return (self.path / DONE_MARKER).is_file()


def number_folders(parent: Path, digits: int) -> list:
    """Subfolders whose name is exactly `digits` digits (e.g. '2026', or '09'), sorted by name."""
    found = []
    for child in parent.iterdir():
        if child.is_dir() and child.name.isdigit() and len(child.name) == digits:
            found.append(child)
    found.sort()
    return found


def find_day_folders(partner_dir: Path) -> list:
    """Every YYYY/MM/DD folder under the partner folder, oldest first.
    Folders that don't look like dates are ignored."""
    day_folders = []
    for year in number_folders(partner_dir, 4):
        for month in number_folders(year, 2):
            for day in number_folders(month, 2):
                label = f"{year.name}/{month.name}/{day.name}"
                day_folders.append(DayFolder(path=day, label=label))
    return day_folders
