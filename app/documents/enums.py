from enum import StrEnum, auto


class DocumentType(StrEnum):
    MEETING_NOTES = auto()
    DESIGN = auto()
    PROJECT_REQUIREMENTS = auto()
    PITCH_DECK = auto()


# Backwards-compatible alias for the previous misspelling.
DocuementType = DocumentType
