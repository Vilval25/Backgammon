import pygame as pg
import random

import ai
import load_images
import variables
from VisualManagement import *
from variables import *

pg.init()
pg.display.set_caption('Backgammon Project 2')
screen_size = (900, 790)  # a tuple of size (width, height)
screen = pg.display.set_mode(screen_size)

# import board images:
white_pawn_outside, black_pawn_outside, white_pawn, black_pawn, background_image = load_images.board(pg)

# import animation images:
inactive_adversary_dice_button, active_adversary_dice_button, inactive_player_dice_button, \
active_player_dice_button, white_wins, black_wins, dest_light_bottom, dest_light_upper, \
house_lights_green, blank_player_dice, blank_adversary_dice, white_highlight, black_highlight \
    = load_images.animations(pg)

# create the dice lists
player_dice_list, adversary_dice_list = load_images.dices()

# LIST CONTAINS EACH TIME: [destination_stack, piece_name]
white_light_pawns = []
black_light_pawns = []

# LIST OF ALL STACKS THE THE PIECE CAN GO TO
white_possible_dest = []
black_possible_dest = []

# PIECE NAMES THAT ARE HOME
white_home = []
black_home = []


# ROLL AND SAVE DICE VALUES
def player_dice_values():
    v1 = random.randint(1, 6)
    v2 = random.randint(1, 6)

    player_dice_1.my_dice = pg.image.load(player_dice_list[v1 - 1])
    player_dice_2.my_dice = pg.image.load(player_dice_list[v2 - 1])

    variables.player_dice_values = (v1, v2)
    # Dobles: una ronda extra de 2 movimientos invisibles.
    variables.player_doubles_round = 1 if v1 == v2 else 0


def adversary_dice_values():
    v1 = random.randint(1, 6)
    v2 = random.randint(1, 6)

    adversary_dice_1.my_dice = pg.image.load(adversary_dice_list[v1 - 1])
    adversary_dice_2.my_dice = pg.image.load(adversary_dice_list[v2 - 1])

    variables.adversary_dice_values = (v1, v2)


# KEY HIGHLIGHTING
def light_white_keys(stack_list):
    for i in stack_list:
        i[1].image = white_highlight


def light_black_keys(stack_list):
    for i in stack_list:
        i[1].image = black_highlight


# UPDATE DICE IMAGE
class adversary_dice:
    def __init__(self, pic):
        self.my_dice = pg.image.load(pic)


class player_dice:
    def __init__(self, pic):
        self.my_dice = pg.image.load(pic)


# - - - create the middle stack
my_middle_stack = Pieces.ColumnStacks(0, None)
temp_middle = []
temp_x = 426
temp_y = 340

for i in range(0, 6):
    temp_middle.append((temp_x, temp_y + (i * 56)))

my_middle_stack.positions = temp_middle
# - - -

white_pawn_outside_stack = Pieces.StackMotions(0, "white")
black_pawn_outside_stack = Pieces.StackMotions(0, "black")

# INITIALISE THE PLAYER AND ADVERSARY DICES TO BLANK/EMPTY
player_dice_1 = player_dice(blank_player_dice)
player_dice_2 = player_dice(blank_player_dice)

adversary_dice_1 = adversary_dice(blank_adversary_dice)
adversary_dice_2 = adversary_dice(blank_adversary_dice)

VM = VisualManagement()
all_stacks = VM.init_stacks()  # generate the pieces and put them in a stack

# set pieces that are in home to Home
for k in all_stacks:
    val = all_stacks[k]

    if val.loc <= 6:
        for j in val.pawns:
            if j.id == "white":
                white_home.append(j)

    elif val.loc >= 19:
        for j in val.pawns:
            if j.id == "black":
                black_home.append(j)


# move piece from current stack to another
def move(current_stack, destination_stack):  # TODO RECHECK param type

    # pop from the current stack
    deleted_piece = current_stack.remove_pawn()

    if turn == "player":
        emplacements = white_light_pawns
    else:
        emplacements = black_light_pawns

    # if the deleted piece name is in the highlighted list, delete it from the list
    for i in emplacements:  # emplacements format: [destination_stack, piece_name]
        if i[1] == deleted_piece:
            del i

    destination_stack.add_pawn(deleted_piece)  # add the piece to the destination stack
    emplacements.append([destination_stack, deleted_piece])  # add the piece as a new destination possible
    # then push in desired stack


def check_end_turn():
    global player_dice1_moved, player_dice2_moved, white_possible_dest, player_dice_rolled, white_light_pawns, \
        white_light_triggered, turn, black_light_triggered, adversary_dice1_moved, adversary_dice2_moved, \
        black_possible_dest, adversary_dice_rolled, black_light_pawns

    # En dobles: cuando ambos dados visibles ya fueron usados pero quedan rondas
    # extra, resetear los flags para permitir los 2 movimientos extra y restaurar
    # los iconos de los dados a su valor original.
    if player_dice1_moved and player_dice2_moved and variables.player_doubles_round > 0:
        variables.player_doubles_round -= 1
        player_dice1_moved = False
        player_dice2_moved = False
        v1, v2 = variables.player_dice_values
        player_dice_1.my_dice = pg.image.load(player_dice_list[v1 - 1])
        player_dice_2.my_dice = pg.image.load(player_dice_list[v2 - 1])
        # Sentinela para que el chequeo de "sin destinos" no dispare cierre
        # este frame; los destinos reales se recomputan en el próximo iter.
        white_possible_dest = [my_middle_stack]

    player_no_moves = (
        len(white_possible_dest) == 0 and player_dice_rolled
        and ((player_dice1_moved == player_dice2_moved == False)
             or player_dice1_moved or player_dice2_moved)
    )
    player_both_used = player_dice1_moved and player_dice2_moved

    if player_both_used or player_no_moves:
        # Si el turno termina porque no hay jugadas válidas, mostrar los dados
        # un momento para que el humano vea por qué se le cede el turno.
        if player_no_moves and not player_both_used:
            pg.time.delay(1200)

        player_dice1_moved = False
        player_dice2_moved = False
        white_light_triggered = False
        variables.player_doubles_round = 0  # cerrar cualquier ronda extra pendiente

        player_dice_rolled = False
        player_dice_1.my_dice = pg.image.load(blank_player_dice)
        player_dice_2.my_dice = pg.image.load(blank_player_dice)

        for i in white_light_pawns:
            i[1].image = white_pawn

        white_light_pawns = []
        white_possible_dest = []
        turn = "adversary"

    # Para el adversario (IA): cerrar turno cuando ambos dados están consumidos,
    # no quedan pasos pendientes, y pasó un cool-down desde la última acción
    # (lanzamiento de dados o último movimiento). Esto da tiempo a que el humano
    # vea el último estado / los dados en pantalla antes de pasar el turno.
    AI_END_TURN_COOLDOWN = 1200
    if (adversary_dice1_moved and adversary_dice2_moved
            and not variables.ai_pending_moves
            and pg.time.get_ticks() - variables.ai_last_step_time > AI_END_TURN_COOLDOWN):
        adversary_dice_rolled = False
        adversary_dice1_moved = False
        adversary_dice2_moved = False
        black_light_triggered = False

        adversary_dice_1.my_dice = pg.image.load(blank_adversary_dice)
        adversary_dice_2.my_dice = pg.image.load(blank_adversary_dice)

        for i in black_light_pawns:
            i[1].image = black_pawn

        black_light_pawns = []
        black_possible_dest = []
        turn = "player"

        # Resetear estado de la IA para el próximo turno del adversario.
        variables.ai_turn_started_at = 0
        variables.ai_planned = False
        variables.ai_pending_moves = []
        variables.ai_steps_done = 0
        variables.ai_preview_step = None
        variables.ai_preview_started_at = 0


def _draw_ai_preview(scrn, step, stacks, middle_stack):
    """
    Resalta la ficha que la IA va a mover y la casilla destino, usando los
    mismos assets visuales que en el turno del jugador (black_highlight,
    dest_light_upper/bottom, house_lights_green).
    """
    src, dest, _die = step

    # --- Origen: mismo highlight que usa light_black_keys() ---
    src_pawn = None
    if src == 0:
        # BAR: buscar la ficha negra superior del middle stack.
        for p in reversed(middle_stack.pawns):
            if p.id == "black":
                src_pawn = p
                break
    elif 1 <= src <= 24:
        stk = stacks[src]
        if len(stk.pawns) > 0:
            src_pawn = stk.pawns[-1]

    if src_pawn is not None and src_pawn.coordinates is not None:
        scrn.blit(black_highlight, src_pawn.coordinates)

    # --- Destino: mismos assets que ColumnStacks.receiving_light() ---
    if dest == 25:
        # Bear-off del negro (mismo highlight que StackMotions.receiving_light).
        scrn.blit(house_lights_green, (838, 479))
    elif 1 <= dest <= 24:
        if dest < 13:
            scrn.blit(dest_light_upper, Pieces.position(12 - dest, 0))
        else:
            scrn.blit(dest_light_bottom, Pieces.position(dest - 13, 7))


counter = 0

# MAIN LOOP
while running:

    mouse = pg.mouse.get_pos()
    click = pg.mouse.get_pressed()

    # first, determine which color starts, happens only at the start of the game/once
    if not turn_rolling:
        if counter < 40:  # make a rolling animation by rolling 40 times and then take the last dice score
            turn_adv = random.randint(1, 6)
            adversary_dice_2.my_dice = pg.image.load(adversary_dice_list[turn_adv - 1])

            turn_pla = random.randint(1, 6)
            player_dice_1.my_dice = pg.image.load(player_dice_list[turn_pla - 1])
            counter += 1
        else:
            pg.time.delay(1500)  # let the user see the score of who starts
            if turn_adv != turn_pla:
                if turn_adv > turn_pla:
                    turn = "adversary"

                elif turn_adv < turn_pla:
                    turn = "player"

                player_dice_1.my_dice = pg.image.load(blank_player_dice)
                adversary_dice_2.my_dice = pg.image.load(blank_adversary_dice)

                turn_rolling = True
                counter = 0
            else:  # if dices are the same, start the rolling animation again...
                counter = 0
                turn_rolling = False

    # convert all white pawns (might be lighted or not) to normal white pawns
    if turn == "player":
        for k in all_stacks:
            for j in all_stacks[k].pawns:
                if j.id == "white":
                    j.image = white_pawn
        # También las que estén en la barra (middle stack), si no quedan
        # con el highlight pegado cuando dejan de ser jugables.
        for p in my_middle_stack.pawns:
            if p.id == "white":
                p.image = white_pawn

    # convert all black pawns (might be lighted or not) to normal black pawns image
    if turn == "adversary":
        for k in all_stacks:
            for j in all_stacks[k].pawns:
                if j.id == "black":
                    j.image = black_pawn
        for p in my_middle_stack.pawns:
            if p.id == "black":
                p.image = black_pawn

    # if the turn is not completed, turn/keep the lights on
    if white_light_triggered:
        light_white_keys(white_light_pawns)

    # if the turn is not completed, turn/keep the lights on
    if black_light_triggered:
        light_black_keys(black_light_pawns)

    # when the PLAYER/ADVERSARY finishes his turn or no other possible moves
    check_end_turn()

    screen.fill((0, 0, 0))  # add a black layer behind the background image
    screen.blit(background_image, (0, 0))  # background image on top of the filled black screen

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_RIGHT:
                pass

        if event.type == pg.MOUSEBUTTONUP and turn == "player" and 840 <= mouse[0] <= 885 and 330 <= mouse[1] <= 450:
            if event.button == 1:
                light_white_keys(white_light_pawns)
                player_dice_rolled = True
                white_light_triggered = True

        # turn of the player
        if turn == "player":
            for i in white_light_pawns:
                dice_player = variables.player_dice_values

                if event.type == pg.KEYDOWN and (event.key == pg.K_UP or event.key == pg.K_DOWN) and player_dice_rolled:
                    if any(p.id == "white" for p in my_middle_stack.pawns):
                        d1, d2 = 25 - (-(i[0].loc - dice_player[0])), 25 - (-(i[0].loc - dice_player[1]))
                    else:
                        d1, d2 = i[0].loc - dice_player[0], i[0].loc - dice_player[1]

                    if click[0] == 1 and i[1].coordinates[0] <= mouse[0] <= i[1].coordinates[0] + 56 and \
                            i[1].coordinates[1] <= mouse[1] <= i[1].coordinates[1] + 56:
                        if event.key == pg.K_UP:

                            if len(white_home) <= 15:
                                if d1 > 0 and not player_dice1_moved:
                                    if all_stacks[d1] in white_possible_dest:
                                        is_reentry = (i[0] is my_middle_stack)
                                        is_capture = (len(all_stacks[d1].pawns) == 1
                                                      and all_stacks[d1].pawns[0].id == "black")

                                        if is_reentry and is_capture:
                                            # Reentrada con captura: buscar una blanca
                                            # específica en el middle (puede haber negras
                                            # capturadas arriba si ya hubo otra reentrada
                                            # con captura antes), llevarla al tope y luego
                                            # hacer pop. Sin esto, en dobles + 2 fichas
                                            # en la barra se mueven las fichas equivocadas.
                                            white_idx = None
                                            for k in range(len(my_middle_stack.pawns) - 1, -1, -1):
                                                if my_middle_stack.pawns[k].id == "white":
                                                    white_idx = k
                                                    break
                                            if white_idx is not None:
                                                if white_idx != len(my_middle_stack.pawns) - 1:
                                                    my_middle_stack.pawns[white_idx], my_middle_stack.pawns[-1] = \
                                                        my_middle_stack.pawns[-1], my_middle_stack.pawns[white_idx]
                                                moved_white = my_middle_stack.remove_pawn()
                                                captured_black = all_stacks[d1].remove_pawn()
                                                my_middle_stack.add_pawn(captured_black)
                                                all_stacks[d1].add_pawn(moved_white)
                                        elif is_capture:
                                            move(all_stacks[d1], my_middle_stack)
                                            move(i[0], all_stacks[d1])
                                        else:
                                            move(i[0], all_stacks[d1])

                                        if all_stacks[d1].loc <= 6:
                                            if all_stacks[d1].pawns[-1] not in white_home:
                                                white_home.append(all_stacks[d1].pawns[-1])

                                        player_dice_1.my_dice = pg.image.load(blank_player_dice)
                                        player_dice1_moved = True

                                if d1 == 0 and not player_dice1_moved and len(white_home) == 15:
                                    move(i[0], white_pawn_outside_stack)
                                    player_dice1_moved = True
                                    player_dice_1.my_dice = pg.image.load(blank_player_dice)

                        if event.key == pg.K_DOWN:
                            if len(white_home) <= 15:
                                if d2 > 0 and player_dice2_moved == False:
                                    if all_stacks[d2] in white_possible_dest:
                                        is_reentry = (i[0] is my_middle_stack)
                                        is_capture = (len(all_stacks[d2].pawns) == 1
                                                      and all_stacks[d2].pawns[0].id == "black")

                                        if is_reentry and is_capture:
                                            # Reentrada con captura: ver comentario en el
                                            # bloque K_UP — buscar una blanca específica
                                            # antes de hacer pop, no asumir que está en el
                                            # tope.
                                            white_idx = None
                                            for k in range(len(my_middle_stack.pawns) - 1, -1, -1):
                                                if my_middle_stack.pawns[k].id == "white":
                                                    white_idx = k
                                                    break
                                            if white_idx is not None:
                                                if white_idx != len(my_middle_stack.pawns) - 1:
                                                    my_middle_stack.pawns[white_idx], my_middle_stack.pawns[-1] = \
                                                        my_middle_stack.pawns[-1], my_middle_stack.pawns[white_idx]
                                                moved_white = my_middle_stack.remove_pawn()
                                                captured_black = all_stacks[d2].remove_pawn()
                                                my_middle_stack.add_pawn(captured_black)
                                                all_stacks[d2].add_pawn(moved_white)
                                        elif is_capture:
                                            move(all_stacks[d2], my_middle_stack)
                                            move(i[0], all_stacks[d2])
                                        else:
                                            move(i[0], all_stacks[d2])

                                        if all_stacks[d2].loc <= 6:
                                            if all_stacks[d2].pawns[-1] not in white_home:
                                                white_home.append(all_stacks[d2].pawns[-1])

                                        player_dice_2.my_dice = pg.image.load(blank_player_dice)
                                        player_dice2_moved = True

                                if d2 == 0 and not player_dice2_moved and len(white_home) == 15:
                                    move(i[0], white_pawn_outside_stack)
                                    player_dice_2.my_dice = pg.image.load(blank_player_dice)
                                    player_dice2_moved = True

    # update the screen
    VM.screen_update(screen)

    # turn of the player
    if turn == "player":
        # 1: roll dice
        if not player_dice_rolled:
            if 840 <= mouse[0] <= 885 and 330 <= mouse[1] <= 450:
                screen.blit(active_player_dice_button, (840, 330))

                if click[0] == 1:
                    player_dice_values()
            else:
                screen.blit(inactive_player_dice_button, (840, 330))

        # 2: light pawns that are eligible to move
        light_pawns = []
        # Hay fichas en la barra mientras haya CUALQUIER blanca en el middle
        # stack (no solo si está en el tope: una negra recién capturada puede
        # quedar arriba de una blanca que aún tiene que reentrar).
        on_bar = any(p.id == "white" for p in my_middle_stack.pawns)

        if on_bar:
            for i in my_middle_stack.pawns:
                if i.id == "white":
                    light_pawns.append([my_middle_stack, i])
        else:
            for k in all_stacks:
                val = all_stacks[k]

                if len(val.pawns) > 0:
                    light_piece = val.pawns[-1]
                    if light_piece.id == "white":
                        light_pawns.append([val, light_piece])

        # Una vez tirados los dados, filtrar para resaltar SOLO las fichas
        # que tienen al menos una jugada válida con algún dado disponible.
        if player_dice_rolled:
            dice_p = variables.player_dice_values
            filtered = []
            for cand in light_pawns:
                stack_obj = cand[0]
                if on_bar:
                    d1 = 25 - (-(stack_obj.loc - dice_p[0]))
                    d2 = 25 - (-(stack_obj.loc - dice_p[1]))
                else:
                    d1 = stack_obj.loc - dice_p[0]
                    d2 = stack_obj.loc - dice_p[1]

                has_valid = False
                for d, moved in ((d1, player_dice1_moved), (d2, player_dice2_moved)):
                    if moved:
                        continue
                    if 1 <= d <= 24:
                        if all_stacks[d].check_if_receiving_light("white") == "on":
                            has_valid = True
                            break
                    elif d == 0 and len(white_home) == 15:
                        if white_pawn_outside_stack.checking_receiving_light(
                                "white", white_home, black_home) == "on":
                            has_valid = True
                            break
                if has_valid:
                    filtered.append(cand)
            light_pawns = filtered

        white_light_pawns = light_pawns

        # 3: show the possible destinations when clicked on a pawn that's eligible to move
        # Importante: recomputar SIEMPRE (aunque white_light_pawns esté vacío) para
        # que check_end_turn pueda detectar correctamente "sin jugadas válidas".
        if player_dice_rolled:
            temp_destination = []
            dice_player = variables.player_dice_values

            if len(white_home) <= 15:
                for i in white_light_pawns:
                    if any(p.id == "white" for p in my_middle_stack.pawns):
                        d1, d2 = 25 - (-(i[0].loc - dice_player[0])), 25 - (-(i[0].loc - dice_player[1]))

                    else:
                        d1, d2 = i[0].loc - dice_player[0], i[0].loc - dice_player[1]

                    if d1 > 0 and not player_dice1_moved:
                        if all_stacks[d1].check_if_receiving_light("white") == "on":
                            temp_destination.append(all_stacks[d1])

                    if d1 == 0 and player_dice1_moved == False:
                        if white_pawn_outside_stack.checking_receiving_light("white", white_home, black_home) == "on":
                            temp_destination.append(white_pawn_outside_stack)

                    if d2 > 0 and player_dice2_moved == False:
                        if all_stacks[d2].check_if_receiving_light("white") == "on":
                            temp_destination.append(all_stacks[d2])

                    if d2 == 0 and player_dice2_moved == False:
                        if white_pawn_outside_stack.checking_receiving_light("white", white_home, black_home) == "on":
                            temp_destination.append(white_pawn_outside_stack)

            white_possible_dest = temp_destination

            for i in white_light_pawns:

                if click[0] == 1 and i[1].coordinates[0] <= mouse[0] <= i[1].coordinates[0] + 56 and \
                        i[1].coordinates[1] <= mouse[1] <= i[1].coordinates[1] + 56:
                    if any(p.id == "white" for p in my_middle_stack.pawns):
                        d1, d2 = 25 - (-(i[0].loc - dice_player[0])), 25 - (-(i[0].loc - dice_player[1]))

                    else:
                        d1, d2 = i[0].loc - dice_player[0], i[0].loc - dice_player[1]

                    if len(white_home) <= 15:
                        if d1 > 0 and not player_dice1_moved:
                            all_stacks[d1].receiving_light("white", screen)

                        if d2 > 0 and not player_dice2_moved:
                            all_stacks[d2].receiving_light("white", screen)

                        if d1 == 0 and not player_dice1_moved:
                            white_pawn_outside_stack.receiving_light("white", screen, white_home, black_home)

                        if d2 == 0 and not player_dice2_moved:
                            white_pawn_outside_stack.receiving_light("white", screen, white_home, black_home)

    # turn of the adversary (IA castigadora)
    if turn == "adversary" and turn_rolling:
        # Tiempos para que el humano siga la jugada de la IA cómodamente (ms).
        AI_DELAY_BEFORE_DICE = 1000      # desde inicio de turno hasta tirar dados
        AI_DELAY_AFTER_DICE = 1200       # tras dados, antes del 1er preview
        AI_DELAY_BETWEEN_MOVES = 900     # entre fin de un movimiento y siguiente preview
        AI_PREVIEW_DURATION = 1300       # tiempo que se muestra el preview rojo
        AI_DELAY_AFTER_LAST_MOVE = 1000  # tras el último paso, antes de ceder turno

        # Marcar inicio de turno la primera vez que entramos.
        if variables.ai_turn_started_at == 0:
            variables.ai_turn_started_at = pg.time.get_ticks()
            variables.ai_planned = False
            variables.ai_pending_moves = []
            variables.ai_steps_done = 0
            variables.ai_preview_step = None
            variables.ai_preview_started_at = 0

        now = pg.time.get_ticks()

        # Mostrar el botón inactivo del adversario solo mientras "piensa".
        if not adversary_dice_rolled:
            screen.blit(inactive_adversary_dice_button, (3, 310))

        # 1) Auto-tirar los dados tras un breve delay desde el inicio del turno.
        if not adversary_dice_rolled and now - variables.ai_turn_started_at > AI_DELAY_BEFORE_DICE:
            adversary_dice_values()
            adversary_dice_rolled = True
            variables.ai_last_step_time = now  # marca el momento del lanzamiento

        # 2) Pedir el plan a la IA una vez que los dados están tirados.
        if adversary_dice_rolled and not variables.ai_planned:
            variables.ai_pending_moves = ai.pick_best_move(
                all_stacks, my_middle_stack,
                white_pawn_outside_stack, black_pawn_outside_stack,
                variables.adversary_dice_values, color="black"
            )
            variables.ai_planned = True
            # No tocar ai_last_step_time: el primer preview se muestra
            # AI_DELAY_AFTER_DICE ms después del lanzamiento.

            # Si no hay jugadas posibles: marcar dados como gastados y dejar
            # que check_end_turn cierre el turno tras el cool-down (el cool-down
            # corre desde ai_last_step_time = momento del lanzamiento de dados).
            if not variables.ai_pending_moves:
                adversary_dice1_moved = True
                adversary_dice2_moved = True

        # 3) Máquina de estados de ejecución: idle -> preview rojo -> aplicar.
        if variables.ai_pending_moves:
            if variables.ai_preview_step is None:
                # Idle: esperar a que pase el delay para mostrar el siguiente preview.
                if variables.ai_steps_done == 0:
                    threshold = AI_DELAY_AFTER_DICE
                else:
                    threshold = AI_DELAY_BETWEEN_MOVES

                if now - variables.ai_last_step_time > threshold:
                    variables.ai_preview_step = variables.ai_pending_moves[0]
                    variables.ai_preview_started_at = now
            else:
                # Preview activo: tras AI_PREVIEW_DURATION, aplicar el paso.
                if now - variables.ai_preview_started_at > AI_PREVIEW_DURATION:
                    step = variables.ai_pending_moves.pop(0)
                    ai.apply_move_step(
                        step, all_stacks, my_middle_stack,
                        black_home, black_pawn_outside_stack
                    )
                    variables.ai_preview_step = None
                    variables.ai_last_step_time = now
                    variables.ai_steps_done += 1

                    # Blanquear el dado que acabamos de gastar (mismo patrón
                    # que cuando el jugador mueve y deja en blank el dado usado).
                    _src, _dest, die_used = step
                    d1, d2 = variables.adversary_dice_values
                    if die_used == d1 and not adversary_dice1_moved:
                        adversary_dice1_moved = True
                        adversary_dice_1.my_dice = pg.image.load(blank_adversary_dice)
                    elif die_used == d2 and not adversary_dice2_moved:
                        adversary_dice2_moved = True
                        adversary_dice_2.my_dice = pg.image.load(blank_adversary_dice)

                    # Si quedaron ambos dados gastados pero aún quedan pasos
                    # (caso de dobles con 4 movimientos), restaurar los iconos
                    # a su valor original y resetear los flags para los pasos
                    # 3 y 4.
                    if (adversary_dice1_moved and adversary_dice2_moved
                            and variables.ai_pending_moves):
                        adversary_dice1_moved = False
                        adversary_dice2_moved = False
                        adversary_dice_1.my_dice = pg.image.load(adversary_dice_list[d1 - 1])
                        adversary_dice_2.my_dice = pg.image.load(adversary_dice_list[d2 - 1])

                    # Si el plan se agotó pero algún dado quedó sin usar (porque
                    # no era jugable: ej. 2 fichas en barra con dado bloqueado),
                    # forzar el blanqueo para que check_end_turn pueda cerrar.
                    if not variables.ai_pending_moves:
                        if not adversary_dice1_moved:
                            adversary_dice1_moved = True
                            adversary_dice_1.my_dice = pg.image.load(blank_adversary_dice)
                        if not adversary_dice2_moved:
                            adversary_dice2_moved = True
                            adversary_dice_2.my_dice = pg.image.load(blank_adversary_dice)

                    # El cool-down post-último-paso lo maneja check_end_turn
                    # via AI_END_TURN_COOLDOWN, así no se bloquea el render.

        # 4) Dibujar el preview de la jugada si hay uno activo.
        if variables.ai_preview_step is not None:
            _draw_ai_preview(screen, variables.ai_preview_step,
                             all_stacks, my_middle_stack)

    screen.blit(player_dice_1.my_dice, (2, 540))
    screen.blit(player_dice_2.my_dice, (2, 610))

    screen.blit(adversary_dice_1.my_dice, (2, 100))
    screen.blit(adversary_dice_2.my_dice, (2, 175))

    if len(white_pawn_outside_stack.elements) == 15:
        winner_declared = True
        screen.blit(white_wins, (0, 0))

    elif len(black_pawn_outside_stack.elements) == 15:
        winner_declared = True
        screen.blit(black_wins, (0, 0))

    if winner_declared and 0 <= mouse[0] <= 900 and 0 <= mouse[1] <= 790 and click[0] == 1:
        pass
        # pg.display.quit() # TODO finetune the end menu
        # sys.exit('end of the game')

    pg.display.update()
