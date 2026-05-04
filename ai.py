"""
IA "castigadora" para el adversario (negro) del Backgammon.

Convención de tablero (alineada con el resto del proyecto):
  - Posiciones 1..24 son los puntos jugables.
  - Posición 0 representa la barra (middle stack).
  - Posición 25 representa el bear-off (fichas fuera).
  - El negro avanza de 1 -> 24 (origen + dado). Reentra en el rango 1..6.
  - El blanco avanza de 24 -> 1 (origen - dado). Reentra en el rango 19..24.

Snapshot:
  Diccionario {pos: (color, count)} donde color es "white" / "black" / None.
  Solo se incluyen posiciones con fichas; el resto se considera vacío.

Pesos de utilidad (definidos por el usuario):
  HIT      = 1.0   capturar fichas blancas
  PRIME    = 0.8   crear muros consecutivos
  HOME     = 0.5   anclar puntos del home board negro (19..24)
  ADVANCE  = 0.2   avance propio hacia el bear-off
"""

from itertools import permutations

W_HIT = 1.0
W_PRIME = 0.8
W_HOME = 0.5
W_ADVANCE = 0.2

BAR = 0
OFF = 25


def snapshot(all_stacks, middle_stack, white_outside_stack, black_outside_stack):
    """Lee el estado actual del tablero y devuelve un dict ligero."""
    snap = {}

    for loc, stack in all_stacks.items():
        if len(stack.pawns) > 0:
            color = stack.pawns[0].id
            snap[loc] = (color, len(stack.pawns))

    # Barra: el middle stack puede tener fichas blancas y negras intercaladas.
    if len(middle_stack.pawns) > 0:
        whites = sum(1 for p in middle_stack.pawns if p.id == "white")
        blacks = sum(1 for p in middle_stack.pawns if p.id == "black")
        # Guardamos como dos entradas auxiliares para no perder información.
        snap[("bar", "white")] = whites
        snap[("bar", "black")] = blacks

    snap[("off", "white")] = len(white_outside_stack.elements)
    snap[("off", "black")] = len(black_outside_stack.elements)

    return snap


def _bar_count(snap, color):
    return snap.get(("bar", color), 0)


def _off_count(snap, color):
    return snap.get(("off", color), 0)


def _point(snap, loc):
    """Devuelve (color, count) para un punto 1..24, o (None, 0) si vacío."""
    if loc in snap and isinstance(loc, int):
        return snap[loc]
    return (None, 0)


def _clone(snap):
    return dict(snap)


def _can_land(snap, dest, color):
    """¿Puede el color aterrizar en dest? Reglas estándar de backgammon."""
    if dest < 1 or dest > 24:
        return False
    occ_color, occ_count = _point(snap, dest)
    if occ_count == 0:
        return True
    if occ_color == color:
        return occ_count < 6  # tope visual del proyecto
    # Hay piezas del oponente: solo se puede si es exactamente 1 (blot -> hit).
    return occ_count == 1


def _all_in_home(snap, color):
    """¿Todas las fichas del color están en su home board (o fuera)?"""
    if color == "black":
        home_range = range(19, 25)
    else:
        home_range = range(1, 7)

    if _bar_count(snap, color) > 0:
        return False

    for loc, val in snap.items():
        if not isinstance(loc, int):
            continue
        c, cnt = val
        if c == color and loc not in home_range:
            return False
    return True


def _apply_step(snap, src, dest, color):
    """
    Aplica un paso (src -> dest) en una copia del snapshot. Devuelve (nuevo_snap, hit).
    src puede ser BAR (0); dest puede ser OFF (25) si bear-off.
    """
    new = _clone(snap)
    opp = "white" if color == "black" else "black"

    # Quitar la ficha del origen
    if src == BAR:
        new[("bar", color)] = _bar_count(new, color) - 1
        if new[("bar", color)] == 0:
            del new[("bar", color)]
    else:
        c, cnt = _point(new, src)
        if cnt == 1:
            del new[src]
        else:
            new[src] = (c, cnt - 1)

    hit = False

    # Aterrizar en el destino
    if dest == OFF:
        new[("off", color)] = _off_count(new, color) + 1
    else:
        c, cnt = _point(new, dest)
        if cnt == 0:
            new[dest] = (color, 1)
        elif c == color:
            new[dest] = (color, cnt + 1)
        else:
            # captura
            hit = True
            new[("bar", opp)] = _bar_count(new, opp) + 1
            new[dest] = (color, 1)

    return new, hit


def _legal_moves_for_die(snap, die, color):
    """Lista de movimientos (src, dest) legales con ese dado para el color."""
    moves = []

    # Si hay fichas del color en la barra, OBLIGATORIO reentrar primero.
    if _bar_count(snap, color) > 0:
        if color == "black":
            dest = die  # 1..6
        else:
            dest = 25 - die  # 19..24
        if _can_land(snap, dest, color):
            moves.append((BAR, dest))
        return moves

    # Movimiento normal o bear-off.
    for loc, val in snap.items():
        if not isinstance(loc, int):
            continue
        c, cnt = val
        if c != color or cnt == 0:
            continue

        if color == "black":
            dest = loc + die
        else:
            dest = loc - die

        if 1 <= dest <= 24 and _can_land(snap, dest, color):
            moves.append((loc, dest))
            continue

        # Bear-off: solo si todas las fichas están en home.
        if _all_in_home(snap, color):
            if color == "black":
                # dest exacto = 25, o dest > 25 con la ficha más atrasada del home
                if dest == 25:
                    moves.append((loc, OFF))
                elif dest > 25:
                    # solo permitido si no hay fichas más atrasadas (más cercanas a 19)
                    own_locs = [l for l, v in snap.items()
                                if isinstance(l, int) and v[0] == color]
                    farthest = min(own_locs) if own_locs else loc
                    if loc == farthest:
                        moves.append((loc, OFF))
            else:
                if dest == 0:
                    moves.append((loc, OFF))
                elif dest < 0:
                    own_locs = [l for l, v in snap.items()
                                if isinstance(l, int) and v[0] == color]
                    farthest = max(own_locs) if own_locs else loc
                    if loc == farthest:
                        moves.append((loc, OFF))

    return moves


def generate_move_sequences(snap, dice_values, color="black"):
    """
    Devuelve lista de (lista_de_pasos, snap_resultante).
    Cada paso es un tuple (src, dest, die_used).
    Aplica la regla: si solo se puede usar un dado, hay que jugar el mayor posible.
    """
    d1, d2 = dice_values
    if d1 == d2:
        dice_orders = [(d1, d1, d1, d1)]
    else:
        dice_orders = list(set(permutations((d1, d2))))

    raw_results = []  # (steps, final_snap)

    def dfs(current_snap, remaining_dice, steps_so_far):
        if not remaining_dice:
            raw_results.append((list(steps_so_far), current_snap))
            return

        die = remaining_dice[0]
        rest = remaining_dice[1:]
        legal = _legal_moves_for_die(current_snap, die, color)

        if not legal:
            # No se puede usar este dado; registrar el estado parcial.
            raw_results.append((list(steps_so_far), current_snap))
            return

        for (src, dest) in legal:
            new_snap, _hit = _apply_step(current_snap, src, dest, color)
            steps_so_far.append((src, dest, die))
            dfs(new_snap, rest, steps_so_far)
            steps_so_far.pop()

    for order in dice_orders:
        dfs(snap, list(order), [])

    if not raw_results:
        return []

    # Filtrar: regla de máximo uso de dados.
    max_steps = max(len(s) for s, _ in raw_results)
    filtered = [(s, fs) for s, fs in raw_results if len(s) == max_steps]

    # Si solo se puede usar un dado y los dos son distintos, hay que jugar el mayor.
    if max_steps == 1 and d1 != d2:
        bigger = max(d1, d2)
        with_bigger = [(s, fs) for s, fs in filtered if s[0][2] == bigger]
        if with_bigger:
            filtered = with_bigger

    # Eliminar duplicados (por snap final + secuencia de pasos).
    seen = set()
    unique = []
    for s, fs in filtered:
        snap_key = tuple(sorted(((str(k), v) for k, v in fs.items()), key=lambda x: x[0]))
        key = (tuple(s), snap_key)
        if key not in seen:
            seen.add(key)
            unique.append((s, fs))

    return unique


# --- Función de utilidad castigadora ---

def _hits_done(snap_after, snap_before):
    """Cuántas fichas blancas más están en la barra tras la jugada."""
    return _bar_count(snap_after, "white") - _bar_count(snap_before, "white")


def _prime_score(snap, color):
    """Suma de (largo_run^2) para cada secuencia de puntos consecutivos con >=2 fichas del color."""
    score = 0
    run = 0
    for loc in range(1, 25):
        c, cnt = _point(snap, loc)
        if c == color and cnt >= 2:
            run += 1
        else:
            if run > 0:
                score += run * run
            run = 0
    if run > 0:
        score += run * run
    return score


def _home_board_anchors(snap, color):
    """Cuántos puntos anclados (>=2 fichas) hay en el home board del color."""
    if color == "black":
        rng = range(19, 25)
    else:
        rng = range(1, 7)
    count = 0
    for loc in rng:
        c, cnt = _point(snap, loc)
        if c == color and cnt >= 2:
            count += 1
    return count


def _pip_count(snap, color):
    """Pip count: cuanto menor, más cerca del bear-off."""
    pip = 0
    # Barra cuenta como la peor distancia.
    bar = _bar_count(snap, color)
    if color == "black":
        pip += bar * 25  # desde la barra el negro tiene que recorrer todo
        for loc, val in snap.items():
            if not isinstance(loc, int):
                continue
            c, cnt = val
            if c == color:
                pip += cnt * (25 - loc)
    else:
        pip += bar * 25
        for loc, val in snap.items():
            if not isinstance(loc, int):
                continue
            c, cnt = val
            if c == color:
                pip += cnt * loc
    return pip


def utility(snap_after, snap_before, color="black"):
    hits = _hits_done(snap_after, snap_before)
    primes = _prime_score(snap_after, color)
    home = _home_board_anchors(snap_after, color)
    pip_before = _pip_count(snap_before, color)
    pip_after = _pip_count(snap_after, color)
    advance = (pip_before - pip_after) / 24.0  # normalizado

    return (W_HIT * hits) + (W_PRIME * primes) + (W_HOME * home) + (W_ADVANCE * advance)


def pick_best_move(all_stacks, middle_stack, white_outside_stack,
                   black_outside_stack, dice_values, color="black"):
    """
    Devuelve la lista de pasos (src, dest, die) para la mejor secuencia,
    o [] si no hay jugadas posibles.
    """
    s0 = snapshot(all_stacks, middle_stack, white_outside_stack, black_outside_stack)
    candidates = generate_move_sequences(s0, dice_values, color=color)

    if not candidates:
        return []

    best_score = None
    best_steps = []
    best_hits = -1
    best_pip_reduction = -1

    pip0 = _pip_count(s0, color)

    for steps, final_snap in candidates:
        score = utility(final_snap, s0, color=color)
        hits = _hits_done(final_snap, s0)
        pip_red = pip0 - _pip_count(final_snap, color)

        better = False
        if best_score is None or score > best_score:
            better = True
        elif score == best_score:
            # Desempate: más capturas, luego más avance.
            if hits > best_hits:
                better = True
            elif hits == best_hits and pip_red > best_pip_reduction:
                better = True

        if better:
            best_score = score
            best_steps = steps
            best_hits = hits
            best_pip_reduction = pip_red

    return best_steps


# --- Aplicación de un paso al tablero real (mutación) ---

def apply_move_step(step, all_stacks, middle_stack, black_home,
                    black_pawn_outside_stack):
    """
    Ejecuta UN paso (src, dest, die) sobre los objetos reales del juego.
    Devuelve el dado consumido (entero) para que el caller marque
    adversary_dice1_moved / adversary_dice2_moved.
    """
    src, dest, die = step

    # 1) Si hay captura (1 ficha blanca en dest), enviarla a la barra.
    if 1 <= dest <= 24:
        dest_stack = all_stacks[dest]
        if len(dest_stack.pawns) == 1 and dest_stack.pawns[0].id == "white":
            captured = dest_stack.remove_pawn()
            middle_stack.add_pawn(captured)

    # 2) Determinar la pila origen.
    if src == BAR:
        # Sacar la ficha negra superior del middle_stack.
        # Como puede haber blancas capturadas (de hits propios) por encima de
        # la negra que toca reentrar, hay que buscar la última negra y, si no
        # está en el tope, intercambiarla con el tope antes de hacer remove_pawn().
        # Esto preserva el bookkeeping interno de ColumnStacks (connected /
        # coordinates), si no, las fichas en el middle aparecen en posiciones
        # visualmente equivocadas.
        black_idx = None
        for i in range(len(middle_stack.pawns) - 1, -1, -1):
            if middle_stack.pawns[i].id == "black":
                black_idx = i
                break
        if black_idx is None:
            return die  # no hay nada que mover (no debería pasar)
        if black_idx != len(middle_stack.pawns) - 1:
            middle_stack.pawns[black_idx], middle_stack.pawns[-1] = \
                middle_stack.pawns[-1], middle_stack.pawns[black_idx]
        moving_piece = middle_stack.remove_pawn()
    else:
        src_stack = all_stacks[src]
        moving_piece = src_stack.remove_pawn()

    # 3) Aterrizar
    if dest == OFF:
        black_pawn_outside_stack.add_pawn(moving_piece)
    else:
        all_stacks[dest].add_pawn(moving_piece)
        if dest >= 19:
            if moving_piece not in black_home:
                black_home.append(moving_piece)

    return die
