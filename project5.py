from game_mechanics import Jewel, Faller, GameState, create_empty_field
import random
import pygame


_INIT_WIDTH = 600
_INIT_HEIGHT = 600
_BOARD_CELL_SIZE = 0.075
_ROW_COUNT = 13
_COLUMN_COUNT = 6
_BACKGROUND_COLOR = pygame.Color(40, 40, 40)
_BOARD_OUTLINE_COLOR = pygame.Color(255, 255, 255)
_RED = pygame.Color(255, 0, 0)
_ORANGE = pygame.Color(255, 165, 0)
_YELLOW = pygame.Color(255, 255, 0)
_GREEN = pygame.Color(0, 255, 0)
_BLUE = pygame.Color(0, 255, 255)
_PURPLE = pygame.Color(181,126,220)
_PINK = pygame.Color(255, 192, 203)
_JEWEL_COLORS = ["R", "O", "Y", "G", "B", "P", "Z"]


class Columns():
    def __init__(self) -> None:
        self._running = True
        self._fall_time = 0
        self._fall_speed = 1
        self._game_state = GameState(_ROW_COUNT, _COLUMN_COUNT, create_empty_field(_ROW_COUNT, _COLUMN_COUNT))

    def run(self) -> None:
        '''
        Runs the game: Displays the screen and board, while updating it
        depending on the various events from the user, and advances (ticks)
        the game mechanics forward by one second; when the game is determined
        to be over, a "GAME OVER" message is displayed and the program ends
        '''
        pygame.init()
        clock = pygame.time.Clock()

        try:
            self._create_surface((_INIT_WIDTH, _INIT_HEIGHT))

            while self._running:
                clock.tick()
                self._handle_events()
                self._redraw()

                if self._check_game_over():
                    self._end_game()
                    break

                self._create_faller()

                self._fall_time += clock.get_rawtime()
                if self._fall_time / 1000 > self._fall_speed:
                    self._fall_time = 0
                    self._tick()
        finally:
            pygame.quit()

    def _create_surface(self, size: tuple[int]) -> None:
        '''Creates a resizeable screen for the game with the initial width and height'''
        self._surface = pygame.display.set_mode(size, pygame.RESIZABLE)
        pygame.display.set_caption("Columns")

    def _handle_events(self) -> None:
        '''Handles various events like quitting, resizing, and key presses'''
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
            elif event.type == pygame.VIDEORESIZE:
                self._create_surface(event.size)

            self._handle_keys(event)

    def _handle_keys(self, event: pygame.event.Event) -> None:
        '''
        Handles specific key presses: left key moves the faller left,
        right key moves the faller right, space bar rotates the faller,
        and down key increases the faller's fall speed
        '''
        if event.type == pygame.KEYDOWN:
            if self._game_state.faller() != None:
                if event.key == pygame.K_LEFT:
                    self._game_state.faller().move_left()
                    self._game_state.faller().check_if_landed()
                    self._game_state.faller().check_if_unlanded()
                elif event.key == pygame.K_RIGHT:
                    self._game_state.faller().move_right()
                    self._game_state.faller().check_if_landed()
                    self._game_state.faller().check_if_unlanded()
                elif event.key == pygame.K_SPACE:
                    self._game_state.faller().rotate()

                if event.key == pygame.K_DOWN:
                    self._fall_speed = 0.1
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                self._fall_speed = 1

    def _redraw(self) -> None:
        '''Displays the screen with the background color and board'''
        surface = pygame.display.get_surface()
        surface.fill(_BACKGROUND_COLOR)
        self._draw_board()
        pygame.display.flip()

    def _draw_board(self) -> None:
        '''
        Draws the game board (according to the field in the game mechanics)
        as a grid of cells that are either empty or have Jewels in them
        '''
        start_y = self._frac_y_to_pixel(7 / _INIT_HEIGHT)

        for row in self._game_state.field()[2:]:
            start_x = self._frac_x_to_pixel(165 / _INIT_WIDTH)

            for jewel in row:
                rect = pygame.Rect(start_x, start_y, self._frac_x_to_pixel(_BOARD_CELL_SIZE), self._frac_y_to_pixel(_BOARD_CELL_SIZE))
                pygame.draw.rect(self._surface, _BOARD_OUTLINE_COLOR, rect, 1)
                self._draw_jewel(jewel, rect)

                start_x += self._frac_x_to_pixel(_BOARD_CELL_SIZE)
            start_y += self._frac_y_to_pixel(_BOARD_CELL_SIZE)

    def _draw_jewel(self, jewel: Jewel, rect: pygame.Rect) -> None:
        '''
        If there is a Jewel in the field from the game mechanics,
        a Jewel (colored circle) is drawn, along with additional features
        depending on its state (LANDING, MATCHING)
        '''
        if jewel.color() != " ":
            color = self._get_color(jewel.color())

            if jewel.state() == "LANDED":
                pygame.draw.ellipse(self._surface, color, rect.inflate(-10, -10))
                pygame.draw.rect(self._surface, _BOARD_OUTLINE_COLOR, rect.inflate(-8, -8), 1)
            elif jewel.state() == "MATCHED":
                pygame.draw.rect(self._surface, _BOARD_OUTLINE_COLOR, rect)
                pygame.draw.ellipse(self._surface, color, rect.inflate(-10, -10))
            else:
                pygame.draw.ellipse(self._surface, color, rect.inflate(-10, -10))

    def _get_color(self, color: str) -> pygame.Color:
        '''
        Returns the pygame Color depending on the string assigned
        to the Jewel in the field from the game mechanics
        '''
        if color == "R":
            return _RED
        elif color == "O":
            return _ORANGE
        elif color == "Y":
            return _YELLOW
        elif color == "G":
            return _GREEN
        elif color == "B":
            return _BLUE
        elif color == "P":
            return _PURPLE
        elif color == "Z":
            return _PINK
            
    def _create_faller(self) -> None:
        '''Creates a faller in the game mechanics'''
        if self._game_state.faller() == None and not self._game_state.check_match():
            random_column = self._random_column()
            random_colors = self._random_colors(_JEWEL_COLORS)
            self._game_state.place_faller(Faller(self._game_state,
                                                random_column,
                                                Jewel(random_colors[0]),
                                                Jewel(random_colors[1]),
                                                Jewel(random_colors[2])))

    def _random_column(self) -> int:
        '''
        Returns a random column number if that column is not full;
        if it is full, it runs again until it gets a valid column number
        '''
        while True:
            random_column = random.randint(1, 6)
            if self._game_state.field()[2][random_column - 1].color() == " ":
                break

        return random_column

    def _random_colors(self, colors: list[str]) -> list[str]:
        '''Returns a list of three random colors (strings) from a list of colors'''
        random_colors = []
        for _ in range(3):
            random_colors.append(random.choice(colors))

        return random_colors

    def _tick(self) -> None:
        '''
        Advances the game by one tick (one second) and updates
        the state of the game/field accordingly
        '''
        if self._game_state.faller() == None:
            self._game_state.remove_matches()
            self._game_state.normal_gravity()
            self._game_state.match()
        else:
            self._game_state.tick_gravity()
            if self._game_state.faller().state() == "FALLING":
                self._game_state.faller().check_if_landed()
            elif self._game_state.faller().state() == "LANDED":
                self._game_state.faller().check_if_unlanded()
                self._game_state.faller().frozen()
                self._game_state.match()

    def _check_game_over(self) -> bool:
        '''Checks if the game is over (if the GameState object's_game_over attribute is True)'''
        if self._game_state.faller() == None:
            self._game_state.check_game_over()
            if self._game_state.game_over():
                return True

    def _end_game(self) -> None:
        '''Displays "GAME OVER" on the screen when the game ends'''
        text_font = pygame.font.SysFont("Monospace", self._scale_font(100 / 600), True)
        text = text_font.render("GAME OVER", True, _RED)
        text_rect = text.get_rect(center=(self._surface.get_width() / 2, self._surface.get_height() / 2))

        self._surface.fill(_BACKGROUND_COLOR)
        self._surface.blit(text, text_rect)

        pygame.display.update()
        pygame.time.delay(2000)

    def _frac_x_to_pixel(self, frac_x: float) -> int:
        '''Converts the given fractional x-coordinate to a pixel x-coordinate'''
        return int(frac_x * self._surface.get_width())

    def _frac_y_to_pixel(self, frac_y: float) -> int:
        '''Converts the given fractional y-coordinate to a pixel y-coordinate'''
        return int(frac_y * self._surface.get_height())

    def _scale_font(self, font_scale: int) -> int:
        '''Scales the font size according to the size (width) of the screen'''
        return int(font_scale * self._surface.get_width())


if __name__ == "__main__":
    Columns().run()