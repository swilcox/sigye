import random
from datetime import datetime, timedelta

from ...models import TimeEntry
from ...repositories import TimeEntryRepositoryFile


def generate_fake_entries(count: int) -> list[TimeEntry]:
    """Generate fake time entries for testing"""
    entries = []
    for i in range(count):
        start_time = datetime.now().astimezone() - timedelta(days=i)
        start_time = start_time.replace(hour=random.randint(7, 12))
        end_time = start_time + timedelta(hours=random.randint(1, 4))
        entries.append(
            TimeEntry(
                project=f"Project {random.choice(['A', 'B', 'C'])}",
                start_time=start_time,
                end_time=end_time,
                comment=f"Comment {i}",
                tags=set(random.choices(["tag1", "tag2", "tag3"], k=random.randint(0, 3))),
            )
        )
    return entries


def save_fake_entries(filename: str, count: int):
    """Generate and save fake time entries to a file"""
    entries = generate_fake_entries(count)
    repo = TimeEntryRepositoryFile(filename)
    for entry in entries:
        repo.save(entry)
    return entries


if __name__ == "__main__":
    save_fake_entries("fake_entries.yaml", 1000)
