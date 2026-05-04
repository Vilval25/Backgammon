import load_images

player_dice1_moved = False
player_dice2_moved = False
adversary_dice1_moved = False
adversary_dice2_moved = False

white_light_triggered = False
black_light_triggered = False
adversary_dice_rolled = False

turn = None
turn_rolling = False
player_dice_rolled = False
winner_declared = False
running = True

turn_adv = None
turn_pla = None

player_dice_values = (0, 0)
adversary_dice_values = (0, 0)

# Cuando el jugador tira dobles, tiene 2 movimientos extra "invisibles".
# Vale 1 (una ronda extra de 2 movimientos) en dobles, 0 en tirada normal.
player_doubles_round = 0

# Estado de la IA (adversario controlado por computadora)
ai_turn_started_at = 0      # ms cuando comenzó el turno del adversario
ai_pending_moves = []       # lista de pasos (src, dest, die) por ejecutar
ai_last_step_time = 0       # ms del último paso aplicado (o del lanzamiento de dados)
ai_planned = False          # True cuando ya pedimos la jugada al motor
ai_steps_done = 0           # cuántos pasos ya ejecutó la IA en este turno
ai_preview_step = None      # paso (src, dest, die) en fase de preview rojo
ai_preview_started_at = 0   # ms cuando empezó el preview del paso actual

# LIST CONTAINS EACH TIME: [destination_stack, piece_name]
white_light_pawns = []
black_light_pawns = []

# LIST OF ALL STACKS THE THE PIECE CAN GO TO
white_possible_dest = []
black_possible_dest = []

# PIECE NAMES THAT ARE HOME
white_home = []
black_home = []

# white_pawn_outside = None
# black_pawn_outside = None
# white_pawn = None
# black_pawn = None
# background_image = None
# inactive_adversary_dice_button = None
# active_adversary_dice_button = None
# inactive_player_dice_button = None
# active_player_dice_button = None
# white_wins = None
# black_wins = None
# dest_light_bottom = None
# dest_light_upper = None
# house_lights_green = None
# blank_player_dice = None
# blank_adversary_dice = None
# white_highlight = None
# black_highlight = None
# player_dice_list = None
# adversary_dice_list = None
#
#
# def load(pygame):
#     global pg, white_pawn_outside, black_pawn_outside, white_pawn, black_pawn, background_image, inactive_adversary_dice_button, active_adversary_dice_button, inactive_player_dice_button, \
#         active_player_dice_button, white_wins, black_wins, dest_light_bottom, dest_light_upper, \
#         house_lights_green, blank_player_dice, blank_adversary_dice, white_highlight, black_highlight, player_dice_list, adversary_dice_list
#
#
#     # import board images:
#     white_pawn_outside, black_pawn_outside, white_pawn, black_pawn, background_image = load_images.board(pygame)
#
#     # import animation images:
#     inactive_adversary_dice_button, active_adversary_dice_button, inactive_player_dice_button, \
#     active_player_dice_button, white_wins, black_wins, dest_light_bottom, dest_light_upper, \
#     house_lights_green, blank_player_dice, blank_adversary_dice, white_highlight, black_highlight \
#         = load_images.animations(pygame)
#
#     # create the dice lists
#     player_dice_list, adversary_dice_list = load_images.dices()
