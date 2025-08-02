"""Common UI drawing helper functions to reduce code duplication."""

import pygame

from src.config.constants import (
    COLOR_BLACK,
    COLOR_RED,
    COLOR_WHITE,
    UI_HEART_SIZE,
    UI_HEART_SPACING,
    UI_TIMER_BORDER,
    UI_TIMER_PADDING,
)


def draw_heart(
    screen: pygame.Surface,
    x: int,
    y: int,
    size: int = UI_HEART_SIZE,
    filled: bool = True,
    color: tuple[int, int, int] = COLOR_RED,
) -> None:
    """Draw a heart shape at the specified position.

    Args:
        screen: The pygame surface to draw on
        x: X coordinate of the heart's top-left
        y: Y coordinate of the heart's top-left
        size: Size of the heart (default: UI_HEART_SIZE)
        filled: Whether to fill the heart or just outline
        color: Color of the heart (default: COLOR_RED)
    """
    if filled:
        # Filled heart using two circles and a polygon
        pygame.draw.circle(
            screen,
            color,
            (x + size // 4, y + size // 4),
            size // 4,
        )
        pygame.draw.circle(
            screen,
            color,
            (x + 3 * size // 4, y + size // 4),
            size // 4,
        )
        pygame.draw.polygon(
            screen,
            color,
            [
                (x, y + size // 3),
                (x + size // 2, y + size),
                (x + size, y + size // 3),
            ],
        )
    else:
        # Outline heart
        pygame.draw.circle(
            screen,
            color,
            (x + size // 4, y + size // 4),
            size // 4,
            2,
        )
        pygame.draw.circle(
            screen,
            color,
            (x + 3 * size // 4, y + size // 4),
            size // 4,
            2,
        )
        pygame.draw.lines(
            screen,
            color,
            False,
            [
                (x, y + size // 3),
                (x + size // 2, y + size),
                (x + size, y + size // 3),
            ],
            2,
        )


def draw_lives(
    screen: pygame.Surface,
    current_lives: int,
    max_lives: int,
    x: int | None = None,
    y: int = 20,
    right_align: bool = True,
) -> None:
    """Draw heart-based lives indicator.

    Args:
        screen: The pygame surface to draw on
        current_lives: Number of lives remaining
        max_lives: Maximum number of lives
        x: X coordinate (if None, will align based on right_align)
        y: Y coordinate
        right_align: Whether to align to the right side of screen
    """
    if x is None:
        if right_align:
            x = screen.get_width() - (max_lives * (UI_HEART_SIZE + UI_HEART_SPACING))
        else:
            x = UI_HEART_SPACING

    for i in range(max_lives):
        heart_x = x + i * (UI_HEART_SIZE + UI_HEART_SPACING)
        filled = i < current_lives
        color = COLOR_RED if filled else COLOR_BLACK
        draw_heart(screen, heart_x, y, UI_HEART_SIZE, filled, color)


def draw_text_with_background(
    screen: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    position: tuple[int, int],
    text_color: tuple[int, int, int] = COLOR_BLACK,
    bg_color: tuple[int, int, int] = COLOR_WHITE,
    border_color: tuple[int, int, int] = COLOR_BLACK,
    padding: int = UI_TIMER_PADDING,
    border_width: int = 3,
    center: bool = True,
) -> pygame.Rect:
    """Draw text with a background box and border.

    Args:
        screen: The pygame surface to draw on
        text: Text to display
        font: Font to use
        position: (x, y) position
        text_color: Color of the text
        bg_color: Background color
        border_color: Border color
        padding: Padding around text
        border_width: Width of the border
        center: Whether position is the center (True) or top-left (False)

    Returns:
        The rectangle of the drawn background
    """
    text_surface = font.render(text, True, text_color)

    if center:
        text_rect = text_surface.get_rect(center=position)
    else:
        text_rect = text_surface.get_rect(topleft=position)

    # Create background rectangle with padding
    bg_rect = text_rect.inflate(padding, UI_TIMER_BORDER)

    # Draw background
    pygame.draw.rect(screen, bg_color, bg_rect)

    # Draw border
    if border_width > 0:
        pygame.draw.rect(screen, border_color, bg_rect, border_width)

    # Draw text
    screen.blit(text_surface, text_rect)

    return bg_rect


def draw_progress_bar(
    screen: pygame.Surface,
    x: int,
    y: int,
    width: int,
    height: int,
    progress: float,
    bg_color: tuple[int, int, int] = COLOR_BLACK,
    fill_color: tuple[int, int, int] = COLOR_RED,
    border_color: tuple[int, int, int] = COLOR_BLACK,
    border_width: int = 2,
) -> None:
    """Draw a progress bar.

    Args:
        screen: The pygame surface to draw on
        x: X coordinate
        y: Y coordinate
        width: Total width of the bar
        height: Height of the bar
        progress: Progress value (0.0 to 1.0)
        bg_color: Background color
        fill_color: Fill color
        border_color: Border color
        border_width: Width of the border
    """
    # Clamp progress to valid range
    progress = max(0.0, min(1.0, progress))

    # Draw background
    if bg_color:
        pygame.draw.rect(screen, bg_color, (x, y, width, height))

    # Draw progress fill
    if progress > 0:
        fill_width = int(width * progress)
        pygame.draw.rect(screen, fill_color, (x, y, fill_width, height))

    # Draw border
    if border_width > 0:
        pygame.draw.rect(screen, border_color, (x, y, width, height), border_width)


def draw_instructions(
    screen: pygame.Surface,
    instructions: list,
    font: pygame.font.Font,
    start_x: int,
    start_y: int,
    line_spacing: int = 40,
    color: tuple[int, int, int] = COLOR_BLACK,
    center: bool = True,
) -> None:
    """Draw a list of instruction text lines.

    Args:
        screen: The pygame surface to draw on
        instructions: List of instruction strings
        font: Font to use
        start_x: X coordinate (center or left edge)
        start_y: Starting Y coordinate
        line_spacing: Spacing between lines
        color: Text color
        center: Whether to center the text
    """
    y = start_y
    for instruction in instructions:
        text = font.render(instruction, True, color)

        if center:
            text_rect = text.get_rect(center=(start_x, y))
        else:
            text_rect = text.get_rect(topleft=(start_x, y))

        screen.blit(text, text_rect)
        y += line_spacing
