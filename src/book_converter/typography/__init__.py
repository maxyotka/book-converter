"""Typography plugins — registers built-in languages on import."""
from book_converter.typography.registry import register
from book_converter.typography.russian import RussianTypography

register(RussianTypography())
