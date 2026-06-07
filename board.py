from dataclasses import dataclass

from piece import Piece, King
from constants import CellType, Army, PieceType, Flavor


@dataclass
class Cell:
    """ Represents a single hexagonal cell on the board using axial coordinates.
    """
    q: int
    r: int
    cell_type: CellType
    piece: Piece | None = None

    @property
    def s(self) -> int:
        return -self.q - self.r


class Board:
    """ Represents the gaming board."""
    def __init__(self) -> None:
        self.cells: dict[tuple[int, int], Cell] = {}
        self._generate_board()
        self._setup_pieces()

    def _generate_board(self) -> None:
        """ Generates the exact 25-cell diamond geometry from the rulebook.
        """
        # Maps each column (q) to its (r_start, r_end) to center the board
        column_bounds = {
            -4: (2, 2),    # 1 Antineutrino cell
            -3: (1, 2),    # 2 Antineutrino cells
            -2: (0, 2),    # 3 Antineutrino cells (King at r=1)
            -1: (-1, 2),   # 4 Battle cells
             0: (-2, 2),   # 5 Battle cells (Center)
             1: (-2, 1),   # 4 Battle cells
             2: (-2, 0),   # 3 Neutrino cells (King at r=-1)
             3: (-2, -1),  # 2 Neutrino cells
             4: (-2, -2)   # 1 Neutrino cell
        }

        for q, (r_start, r_end) in column_bounds.items():
            for r in range(r_start, r_end + 1):
                cell_type = CellType.BATTLE

                # Define Deployment Zones (Outer 3 columns on each side)
                if q <= -2 or q >= 2:
                    cell_type = CellType.DEPLOYMENT

                # Define Kings (Perfectly centered in the 3-cell columns)
                if (q, r) == (-2, 1) or (q, r) == (2, -1):
                    cell_type = CellType.KING

                self.cells[(q, r)] = Cell(q, r, cell_type)
    
    def _setup_pieces(self) -> None:
        """ Sets up the pieces to their deployment positions.
        """
        starting_positions = {
            # Neutrino King
            (2, -1): King(Army.NEUTRINO, PieceType.KING, Flavor.ELECTRONIC),
            # Neutrino Front Line (e)
            (2, -2): Piece(Army.NEUTRINO, PieceType.REGULAR, Flavor.ELECTRONIC),
            (2, 0): Piece(Army.NEUTRINO, PieceType.REGULAR, Flavor.ELECTRONIC),
            # Neutrino Middle Line (μ)
            (3, -2): Piece(Army.NEUTRINO, PieceType.REGULAR, Flavor.MUONIC),
            (3, -1): Piece(Army.NEUTRINO, PieceType.REGULAR, Flavor.MUONIC),
            # Neutrino Back Line (τ)
            (4, -2): Piece(Army.NEUTRINO, PieceType.REGULAR, Flavor.TAUONIC),

            # Anti-neutrino King
            (-2, 1): King(Army.ANTI_NEUTRINO, PieceType.KING, Flavor.ELECTRONIC),
            # Anti-neutrino Front Line (e)
            (-2, 0): Piece(Army.ANTI_NEUTRINO, PieceType.REGULAR, Flavor.ELECTRONIC),
            (-2, 2): Piece(Army.ANTI_NEUTRINO, PieceType.REGULAR, Flavor.ELECTRONIC),
            # Anti-neutrino Middle Line (μ)
            (-3, 1): Piece(Army.ANTI_NEUTRINO, PieceType.REGULAR, Flavor.MUONIC),
            (-3, 2): Piece(Army.ANTI_NEUTRINO, PieceType.REGULAR, Flavor.MUONIC),
            # Anti-neutrino Back Line (τ)
            (-4, 2): Piece(Army.ANTI_NEUTRINO, PieceType.REGULAR, Flavor.TAUONIC)
        }

        for position, piece in starting_positions.items():
            self.cells[position].piece = piece

    def find_king(self, army: Army) -> Cell:
        """ Returns the cell where the King of the given army is located.
        """
        for cell in self.cells.values():
            if cell.piece:
                if cell.piece.piece_type == PieceType.KING and cell.piece.army == army:
                    return cell
        raise ValueError("King not found!")