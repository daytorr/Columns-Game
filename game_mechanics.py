class Jewel():
    def __init__(self, color: str) -> None:
        self._color = color
        self._state = "FROZEN"

    def color(self) -> str:
        '''Returns the color of a Jewel'''
        return self._color
    
    def state(self) -> str:
        '''Returns the state of a Jewel'''
        return self._state

    def update_state(self, state: str) -> None:
        '''Updates the state of a Jewel'''
        self._state = state


class Faller():
    def __init__(self, game_state: 'GameState', col: int, top: Jewel, middle: Jewel, bottom: Jewel) -> None:
        self._game_state = game_state
        self._row = 2
        self._col = col - 1
        top.update_state("FALLING")
        middle.update_state("FALLING")
        bottom.update_state("FALLING")
        self._components = [top, middle, bottom]
        self._state = "FALLING"

    def col(self) -> int:
        '''Returns the column that the Faller is in'''
        return self._col

    def components(self) -> list:
        '''Returns a list of the Faller components (Jewels in the Faller)'''
        return self._components

    def state(self) -> str:
        '''Returns the state of the Faller'''
        return self._state

    def move_left(self) -> None:
        '''Moves the Faller left once, given that there is space'''
        if self._col != 0:
            if self._game_state.field()[self._row][self._col - 1].color() == " ":
                self._col -= 1
        
                for i, j in zip(range(3), range(2, -1, -1)):
                    self._game_state._field[self._row - i][self._col + 1] = Jewel(" ")
                    self._game_state._field[self._row - i][self._col] = self._components[j]

    def move_right(self) -> None:
        '''Moves the Faller right once, given that there is space'''
        if self._col != self._game_state.columns() - 1:
            if self._game_state.field()[self._row][self._col + 1].color() == " ":
                self._col += 1

                for i, j in zip(range(3), range(2, -1, -1)):
                    self._game_state._field[self._row - i][self._col - 1] = Jewel(" ")
                    self._game_state._field[self._row - i][self._col] = self._components[j]

    def rotate(self) -> None:
        '''Rotates the Jewels once within the Faller'''
        if self._state != "FROZEN":
            bottom = self._components[2]
            self._components[2] = self._components[1]
            self._components[1] = self._components[0]
            self._components[0] = bottom

        for i, j in zip(range(3), range(2, -1, -1)):
            self._game_state._field[self._row - i][self._col] = self._components[j]

    def check_if_landed(self) -> None:
        '''Checks if the Faller landed and updates its state to LANDED if it did'''
        if self._state == "FALLING":
            if self._row + 1 == self._game_state.rows() + 2:
                self._landed()
            elif self._game_state.field()[self._row + 1][self._col].color() != " ":
                self._landed()

    def check_if_unlanded(self) -> None:
        '''
        Checks if the Faller was moved to a spot with a space under it
        and updates its state to FALLING if it was
        '''
        if self._state == "LANDED":
            if self._row < self._game_state.rows() - 1:
                if self._game_state.field()[self._row + 1][self._col].color() == " ":
                    self._falling()

    def frozen(self) -> None:
        '''Updates the state of the Faller and the Jewels within that Faller to FROZEN'''
        if self._state == "LANDED":
            self._state = "FROZEN"
            for jewel in self._components:
                jewel.update_state("FROZEN")
            self._game_state._faller = None

    def _falling(self) -> None:
        '''Updates the state of the Faller and the Jewels within that Faller to FALLING'''
        self._state = "FALLING"
        for jewel in self._components:
            jewel.update_state("FALLING")

    def _landed(self) -> None:
        '''Updates the state of the Faller and the Jewels within that Faller to LANDED'''
        self._state = "LANDED"
        for jewel in self._components:
            jewel.update_state("LANDED")


class GameState():
    def __init__(self, rows: int, columns: int, field: list[list[Jewel]]) -> None:
        self._rows = rows
        self._columns = columns
        self._field = field
        self._faller = None
        self._game_over = False

    def rows(self) -> int:
        '''Returns the number of rows in the visible field'''
        return self._rows

    def columns(self) -> int:
        '''Returns the number of rows in the visible field'''
        return self._columns

    def field(self) -> list[list[Jewel]]:
        '''Returns the field'''
        return self._field

    def faller(self) -> Faller or None:
        '''Returns the Faller in the field or None if there is no Faller'''
        return self._faller

    def game_over(self) -> bool:
        '''Returns the True if the game is over and False if not'''
        return self._game_over

    def place_faller(self, faller: Faller) -> None:
        '''
        Updates the game state with a Faller and places the Faller in the field

        If there is no space in the field for the Faller to be created,
        the _game_over attribute is set to True
        '''
        self._faller = faller
        if self._field[2][faller.col()].color() == " ":
            for i in range(3):
                self._field[i][faller.col()] = faller.components()[i]
            faller.check_if_landed()
        else:
            self._game_over = True

    def normal_gravity(self) -> None:
        '''Drops every Jewel to the bottom of the field, leaving no spaces under them'''
        for c in range(self._columns):
            for row_count in range(self._rows + 1):
                for r in range(self._rows + 1):
                    if self._field[r][c].color() != " " and self._field[r + 1][c].color() == " ":
                        self._field[r + 1][c] = self._field[r][c]
                        self._field[r][c] = Jewel(" ")

    def tick_gravity(self) -> None:
        '''Drops every Jewel/Faller in the field once, given that there is a space under it'''
        for c in range(self._columns):
            for r in reversed(range(self._rows + 1)):
                if self._field[r][c].color() != " " and self._field[r + 1][c].color() == " ":
                    self._field[r + 1][c] = self._field[r][c]
                    self._field[r][c] = Jewel(" ")

        if self._faller != None and self._faller.state() == "FALLING":
            self._faller._row += 1

    def check_game_over(self) -> None:
        '''
        Checks if the game is over and updates the _game_over attribute to True if it is
        
        The game is over when every Jewel in the field is frozen, not matched, and there is
        a Jewel or part of a Faller existing above the visible field
        '''
        if not self.check_match():
            for i in range(self._columns):
                if self._field[0][i].color() != " " or self._field[1][i].color() != " ":
                    if self._field[0][i].state() == "FROZEN" or self._field[1][i].state() == "FROZEN":
                        self._game_over = True

    def check_match(self) -> bool:
        '''Checks if any Jewels in the field are matched'''
        for r in range(self._rows + 2):
            for c in range(self._columns):
                if self._field[r][c].state() == "MATCHED":
                    return True
        return False

    def remove_matches(self) -> None:
        '''Removes matched Jewels from the field'''
        for r in range(self._rows + 2):
            for c in range(self._columns):
                if self._field[r][c].state() == "MATCHED":
                    self._field[r][c] = Jewel(" ")

    def match(self) -> None:
        '''Traverses through the field and checks each Jewel for matching sequences'''
        for row in range(self._rows + 2):
            for col in range(self._columns):
                self._matching_sequence_begins_at(row, col)

    def _matching_sequence_begins_at(self, row: int, col: int) -> None:
        '''
        Checks if there is a matching sequence of Jewels in the field
        beginning in the given column and row and extending in any of the
        eight possible directions
        '''
        self._three_in_a_row(row, col, 0, 1) \
        or self._three_in_a_row(row, col, 1, 1) \
        or self._three_in_a_row(row, col, 1, 0) \
        or self._three_in_a_row(row, col, 1, -1) \
        or self._three_in_a_row(row, col, 0, -1) \
        or self._three_in_a_row(row, col, -1, -1) \
        or self._three_in_a_row(row, col, -1, 0) \
        or self._three_in_a_row(row, col, -1, 1)
        

    def _three_in_a_row(self, row: int, col: int, rowdelta: int, coldelta: int) -> None:
        '''
        Checks if there is a matching sequence of Jewels in the field
        beginning in the given column and row and extending in a direction
        specified by the coldelta and rowdelta

        Updates the states of the matched Jewels in the field to MATCHED
        ''' 
        start_cell = self._field[row][col].color()
        matched = []

        if start_cell != " ":
            for i in range(1, 3):
                if self._is_valid_row_number(row + rowdelta * i) \
                        and self._is_valid_column_number(col + coldelta * i) \
                        and self._field[row + rowdelta * i][col + coldelta *i].color() == start_cell:
                    matched.append(self._field[row + rowdelta * i][col + coldelta * i])
                else:
                    matched = []
                    break
            else:
                for r in range(self._rows + 2):
                    for c in range(self._columns):
                        for match in matched:
                            
                            if match == self._field[r][c]:
                                self._field[r][c].update_state("MATCHED")
                matched = []

    def _is_valid_row_number(self, row_number: int) -> bool:
        '''Returns True if the given row number is valid; returns False otherwise'''
        return 0 <= row_number < self._rows + 2

    def _is_valid_column_number(self, column_number: int) -> bool:
        '''Returns True if the given column number is valid; returns False otherwise'''
        return 0 <= column_number < self._columns


def create_empty_field(rows: int, columns: int) -> GameState:
    '''
    Returns a GameState object with an empty field whose size
    is determinedby the given row and column count
    '''
    field = [[Jewel(" ") for _ in range(columns)], [Jewel(" ") for _ in range(columns)]]
    
    for i in range(rows):
        row = []
        for j in range(columns):
            row.append(Jewel(" "))
        field.append(row)

    return field