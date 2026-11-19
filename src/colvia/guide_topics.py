"""Fixed document names shared by the bundle builder and verified guide reader."""
TOPIC_NAMES = ("plan", "work", "revision", "recovery", "git", "management", "execution")
GUIDE_FILES = {None: "SKILL.md", **{topic: topic + ".md" for topic in TOPIC_NAMES}}
