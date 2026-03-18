"""
Error taxonomy for the agent-memory MCP.

All errors inherit from MemoryError so callers can catch them broadly
or narrowly depending on their needs.
"""


class MemoryError(Exception):
    """Base class for all agent-memory errors."""


class ConflictError(MemoryError):
    """Version token mismatch — file was modified since it was read.

    Attributes:
        current_token: The current hash of the file, so the caller can
            decide whether to re-read and retry.
    """

    def __init__(self, message: str, current_token: str | None = None):
        super().__init__(message)
        self.current_token = current_token


class NotFoundError(MemoryError):
    """File, section, or plan item does not exist."""


class ValidationError(MemoryError):
    """Frontmatter schema violation, broken invariant, or malformed content."""


class AlreadyDoneError(MemoryError):
    """Idempotency: the operation is already in the target state.

    Distinct from success so callers can tell the difference between
    'I just did it' and 'it was already done'.
    """


class StagingError(MemoryError):
    """git add/commit/mv/rm failed.

    Attributes:
        stderr: Raw stderr output from git for debugging.
    """

    def __init__(self, message: str, stderr: str = ""):
        super().__init__(message)
        self.stderr = stderr


class MemoryPermissionError(MemoryError):
    """Operation is blocked by the directory restriction policy.

    Raised before any filesystem access when the target path is in a
    protected directory (identity/, meta/, chats/, skills/).
    Also raised when cowork file-delete permission cannot be obtained.

    Attributes:
        path: The path that triggered the restriction.
    """

    def __init__(self, message: str, path: str = ""):
        super().__init__(message)
        self.path = path
