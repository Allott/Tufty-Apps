# Icons stuff
lt_order_icon = image.load("assets/lt_order.png")
order_icon = image.load("assets/order.png")
irregular_icon = image.load("assets/irregular_order.png")
command_token_icon = image.load("assets/command_token.png")
LT_W, LT_H = lt_order_icon.width, lt_order_icon.height
ORD_W, ORD_H = order_icon.width, order_icon.height
IRR_W, IRR_H = irregular_icon.width, irregular_icon.height
CT_W, CT_H = command_token_icon.width, command_token_icon.height
ICON_SPACING = 8
G_ICON_SPACING = 12
IMAGE_PADDING_Y = 4
HIGHLIGHT_PADDING_H = 2
HIGHLIGHT_PADDING_V = -2



# Colours
BG = color.rgb(20, 25, 40)
HL = color.rgb(60, 80, 120)
SHADOW = color.rgb(0, 0, 0)
ACTIVE = color.rgb(233, 123, 22)
HOLD = color.rgb(233, 233, 100)
INACTIVE = color.rgb(180, 180, 180)

# STATES for (LT, G1, G2, CT, G1I, G2I)
counters = [1, 5, 10, 4, 0, 0]
defaults = [1, 5, 10, 4, 0, 0]
max_vals = [2, 10, 10, 5, 10, 10]

prev_counters = counters[:]

BTN_A, BTN_B, BTN_C, BTN_UP, BTN_DOWN = 0, 1, 2, 3, 4
BTN_LIST = (BTN_A, BTN_B, BTN_C, BTN_UP, BTN_DOWN)

active = 0

SCREEN_W = screen.width
SCREEN_H = screen.height
SECTION_W = SCREEN_W // 3

CHAR_W, text_h = screen.measure_text("0")
BOTTOM_Y = SCREEN_H - text_h - HIGHLIGHT_PADDING_V

CENTER_X = (
    SECTION_W >> 1,
    SECTION_W + (SECTION_W >> 1),
    (SECTION_W << 1) + (SECTION_W >> 1),
)

ICONS = (
    (lt_order_icon, LT_W, LT_H),
    (order_icon, ORD_W, ORD_H),
    (order_icon, ORD_W, ORD_H),
    (command_token_icon, CT_W, CT_H),
    (irregular_icon, IRR_W, IRR_H),
    (irregular_icon, IRR_W, IRR_H),
)

SECTIONS = (0, 1, 2, 0, 1, 2)

OFFSET_DEP = (
    (0, 0),  # dummy
    (4, -1), # 1 depends on 4 → negative
    (5, -1),
    (0, 0),
    (1, 1),  # 4 depends on 1 → positive
    (2, 1),
)

STRINGS = ("0","1","2","3","4","5","6","7","8","9","10")

STATE_IDLE = 0
STATE_A = 1
STATE_B = 2
STATE_C = 3

STATE_TO_INDEX = (0, 3, 4, 5)

state = STATE_IDLE

blit = screen.blit
text = screen.text
rect = screen.shape

def handle_input():
    global state, active

    s = 0
    p = -1

    if badge.held(BTN_A): s = 1
    elif badge.held(BTN_B): s = 2
    elif badge.held(BTN_C): s = 3

    for i in range(5):
        if badge.pressed(BTN_LIST[i]):
            p = i
            break

    state = s

    # Combo actions
    if s == 3:
        if p == 0:
            for i in range(6): counters[i] = defaults[i]
            return s
        elif p == 1:
            for i in range(6): counters[i] = 0
            return s

    if s:
        active = STATE_TO_INDEX[s]

    if p == 3 or p == 4:
        tgt = STATE_TO_INDEX[s] if s else active
        v = counters[tgt] + (1 if p == 3 else -1)
        if 0 <= v <= max_vals[tgt]:
            counters[tgt] = v

    return s


# Lazy draw changes when you can
def draw_icons():
    cnts = counters
    bottom_y = BOTTOM_Y - IMAGE_PADDING_Y

    for i in range(6):
        c = cnts[i]
        if not c:
            continue

        icon, w, h = ICONS[i]


        cx = CENTER_X[SECTIONS[i]]
        x = cx - (w >> 1)

        dep, direction = OFFSET_DEP[i]
        if dep and cnts[dep]:
            x += direction * G_ICON_SPACING

        if i == 3:
            px = 0
            for j in range(c):
                blit(icon, (px, 0))
                px += ICON_SPACING
            continue

        y = bottom_y - h
        for j in range(c):
            blit(icon, (x, y - j * ICON_SPACING))

def draw_text(s):
    cnts = counters

    if s == 1:
        idx0, idx1, idx2 = 3, 1, 2
    elif s == 2:
        idx0, idx1, idx2 = 0, 4, 2
    elif s == 3:
        idx0, idx1, idx2 = 0, 1, 5
    else:
        idx0, idx1, idx2 = 0, 1, 2

    idxs = (idx0, idx1, idx2)

    for i in range(3):
        idx = idxs[i]
        val = STRINGS[cnts[idx]]

        w = len(val) * CHAR_W
        x = CENTER_X[i] - (w >> 1)

        held = (s and idx == STATE_TO_INDEX[s])

        if held:
            col = HOLD
            hl = 1
        elif idx == active:
            col = ACTIVE
            hl = 1
        else:
            col = INACTIVE
            hl = 0

        if hl:
            screen.pen = HL
            rect(shape.rectangle(
                x - HIGHLIGHT_PADDING_H,
                BOTTOM_Y - HIGHLIGHT_PADDING_V,
                w + (HIGHLIGHT_PADDING_H << 1),
                text_h + (HIGHLIGHT_PADDING_V << 1)
            ))

        screen.pen = SHADOW
        text(val, x + 1, BOTTOM_Y + 1)
        screen.pen = col
        text(val, x, BOTTOM_Y)


dirty = True

def update():
    global dirty

    s = handle_input()

    if not dirty:
        for i in range(6):
            if counters[i] != prev_counters[i]:
                dirty = True
                break

    if not dirty:
        return

    for i in range(6):
        prev_counters[i] = counters[i]

    dirty = False

    screen.pen = BG
    rect(shape.rectangle(0, 0, SCREEN_W, SCREEN_H))

    draw_icons()
    draw_text(s)

run(update)
