# Release 1.2 Package C Fix — Job Intelligence

## Fixed

- Salary extraction now supports adjacent salary values such as `85000 100000`.
- Job Intelligence tests now validate salary extraction with simple numeric ranges.

## Notes

This fix replaces `role_extractor.py` with a safer salary extraction implementation.
