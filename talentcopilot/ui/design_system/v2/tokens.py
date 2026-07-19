from dataclasses import dataclass

@dataclass(frozen=True)
class DesignTokens:
    brand_900: str = "#0B1F3A"
    brand_700: str = "#143A63"
    brand_500: str = "#2B6CB0"
    brand_100: str = "#EAF2FB"
    surface: str = "#FFFFFF"
    surface_muted: str = "#F6F8FB"
    border: str = "#D8E0EA"
    text_primary: str = "#152033"
    text_secondary: str = "#536176"
    text_muted: str = "#7A8799"
    success: str = "#1F8A5B"
    warning: str = "#C98200"
    risk: str = "#C84747"
    info: str = "#2B6CB0"
    radius_sm: int = 8
    radius_md: int = 12
    radius_lg: int = 18
    shadow_sm: str = "0 1px 2px rgba(11,31,58,.06)"
    shadow_md: str = "0 8px 24px rgba(11,31,58,.08)"

TOKENS = DesignTokens()
