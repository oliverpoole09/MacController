import cv2
import mediapipe as mp
import math
from pynput.mouse import Controller, Button
import pyautogui
import time

# overlays for morse code chart
overlay = cv2.imread("chart.png", cv2.IMREAD_UNCHANGED)
overlay = cv2.resize(overlay, (0, 0), fx=2.0, fy=2.0)

# mediapipe solutions
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mouse = Controller()

# cam init and info
cam = cv2.VideoCapture(1)
screen_w, screen_h = pyautogui.size()

# hand settings
hands = mp_hands.Hands(max_num_hands=1, 
                       min_detection_confidence=0.8, 
                       min_tracking_confidence=0.8)

# functions for getting distance between 2 points
def calc_distance(point1, point2):
    return math.sqrt((point2.x - point1.x)**2 + (point2.y - point1.y)**2)

# this function was created by gpt
def overlay_image_alpha(img, img_overlay, pos=(0, 0)):
    x, y = pos
    overlay_h, overlay_w = img_overlay.shape[:2]

    if img_overlay.shape[2] == 4:
        alpha_mask = img_overlay[:, :, 3] / 255.0
        alpha_mask = cv2.merge([alpha_mask, alpha_mask, alpha_mask])
        img_overlay_rgb = img_overlay[:, :, :3]
    else:
        alpha_mask = 1.0
        img_overlay_rgb = img_overlay

    img[y:y+overlay_h, x:x+overlay_w] = (
        alpha_mask * img_overlay_rgb +
        (1 - alpha_mask) * img[y:y+overlay_h, x:x+overlay_w]
    )
    return img

# variables
start_time = None # start time for clicking/dragging
dragging = False # check if dragging
smooth_x, smooth_y = 0, 0 # variables for smoother mouse
alpha = 0.4 # alpha that controls how smooth the mouse moves
right_click = False # check right click
mode = "Mouse" # checks for mouse or keyboard mode ("Mouse" by deafult)
last_index_toggle = 0 # check last pinky finger toggle
last_middle_toggle = 0 # check last pinky finger toggle
last_ring_toggle = 0 # check last pinky finger toggle
last_pinky_toggle = 0 # check last pinky finger toggle
enabled = True # old feature (ignore)
keyboard_mode = "main" # keyboard type, what letters to show
pattern = [] # morse code pattern
shift = False # if shift active
capslock = False # if capslock active
scrolling = False # if is scrolling

# loop program every frame
while True:
    # if frame failed, break loop
    ret, frame = cam.read()
    if not ret:
        break

    # flip frame and frame color (BGR to RGB)
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)
    h, w, _ = frame.shape

    # get current time for timer
    current_time = time.time()

    # if capslock is on, just shift (easier than rewriting shift code)
    if capslock:
        shift = True

    # if hands are detected in current frame...
    if result.multi_hand_landmarks:
        # for every hand on frame (locked to just 1)
        for hand_landmarks in result.multi_hand_landmarks:
            # draw landmarks and connections for hand (not required)
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # variables that store fingertip landmarks
            thumb_tip = hand_landmarks.landmark[4]
            index_tip = hand_landmarks.landmark[8]
            middle_tip = hand_landmarks.landmark[12]
            ring_tip = hand_landmarks.landmark[16]
            pinky_tip = hand_landmarks.landmark[20]

            # ignore enabled (old feature that was scrapped)
            if enabled:
                # switch for the current mode ("Mouse"/"Keyboard")
                match mode:
                    # if current mode is "Mouse" mode
                    case "Mouse":
                        # clarify mode on screen
                        cv2.putText(frame, "Mode: Mouse", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)

                        # CALCUTLATE AND DRAW LINES AND DOTS ON HANDS
                        # -------------------------------------------

                        # calculate and draw line between index and thumb
                        x1_ti, y1_ti = int(thumb_tip.x * w), int(thumb_tip.y * h)
                        x2_ti, y2_ti = int(index_tip.x * w), int(index_tip.y * h)
                        cv2.line(frame, (x1_ti, y1_ti), (x2_ti, y2_ti), (255, 255, 255), 3)

                        # calculate middle of thumb and index, and draw a circle there
                        mid_x_ti, mid_y_ti = (x1_ti + x2_ti) // 2, (y1_ti + y2_ti) // 2
                        cv2.circle(frame, (mid_x_ti, mid_y_ti), 10, (0, 255, 0), cv2.FILLED)

                        # calculate and draw line between middle finger and thumb
                        x1_tm, y1_tm = int(thumb_tip.x * w), int(thumb_tip.y * h)
                        x2_tm, y2_tm = int(middle_tip.x * w), int(middle_tip.y * h)
                        cv2.line(frame, (x1_tm, y1_tm), (x2_tm, y2_tm), (255, 255, 255), 3)

                        # calculate middle of thumb and middle finger, and draw a circle there
                        mid_x_tm, mid_y_tm = (x1_tm + x2_tm) // 2, (y1_tm + y2_tm) // 2
                        cv2.circle(frame, (mid_x_tm, mid_y_tm), 10, (255, 0, 0), cv2.FILLED)

                        # calculate and draw line between ring finger and thumb
                        x1_tr, y1_tr = int(thumb_tip.x * w), int(thumb_tip.y * h)
                        x2_tr, y2_tr = int(ring_tip.x * w), int(ring_tip.y * h)
                        cv2.line(frame, (x1_tr, y1_tr), (x2_tr, y2_tr), (255, 255, 255), 3)

                        # calculate middle of thumb and ring finger, and draw a circle there
                        mid_x_tr, mid_y_tr = (x1_tr + x2_tr) // 2, (y1_tr + y2_tr) // 2
                        cv2.circle(frame, (mid_x_tr, mid_y_tr), 10, (0, 255, 255), cv2.FILLED)

                        # calculate and draw line between ring finger and thumb
                        x1_tp, y1_tp = int(thumb_tip.x * w), int(thumb_tip.y * h)
                        x2_tp, y2_tp = int(pinky_tip.x * w), int(pinky_tip.y * h)
                        cv2.line(frame, (x1_tp, y1_tp), (x2_tp, y2_tp), (255, 255, 255), 3)

                        # claculate middle of thumb and ring finger, and draw a circle there
                        mid_x_tp, mid_y_tp = (x1_tp + x2_tp) // 2, (y1_tp + y2_tp) // 2
                        cv2.circle(frame, (mid_x_tp, mid_y_tp), 10, (0, 0, 255), cv2.FILLED)

                        # STORE DISTANCE FROM [FINGER] TO THUMB
                        # -------------------------------------

                        # index -> thumb
                        distance_ti = calc_distance(thumb_tip, index_tip)
                        # middle -> thumb
                        distance_tm = calc_distance(thumb_tip, middle_tip)
                        # ring -> thumb
                        distance_tr = calc_distance(thumb_tip, ring_tip)
                        # pinky -> thumb
                        distance_tp = calc_distance(thumb_tip, pinky_tip)

                        # WHERE TO PUT LABELS ON FINGER TIPS
                        # ----------------------------------
                        
                        # index
                        i_x = max(0, min(int(index_tip.x * w), w-1))
                        i_y = max(0, min(int(index_tip.y * h), h-1))
                        # middle
                        m_x = max(0, min(int(middle_tip.x * w), w-1))
                        m_y = max(0, min(int(middle_tip.y * h), h-1))
                        # ring
                        r_x = max(0, min(int(ring_tip.x * w), w-1))
                        r_y = max(0, min(int(ring_tip.y * h), h-1))
                        # pinky
                        p_x = max(0, min(int(pinky_tip.x * w), w-1))
                        p_y = max(0, min(int(pinky_tip.y * h), h-1))

                        # place labels
                        cv2.putText(frame, "left click", (i_x-50, i_y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 3)
                        cv2.putText(frame, "right click", (m_x-50, m_y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 3)
                        cv2.putText(frame, "scroll", (r_x-50, r_y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
                        cv2.putText(frame, "keyboard", (p_x-50, p_y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)

                        # clicks are registered as a timer for how long the distance between them stays < 0.06 for over 0.3 seconds

                        # CLICKING, DRAGGING, SCROLLING LOGIC
                        # -----------------------------------

                        # if pinky and thumb are clicked
                        if distance_tp < 0.06 and (time.time() - last_pinky_toggle) > 0.3:
                            # toggle keyboard mode
                            mode = "Keyboard"
                            last_pinky_toggle = time.time()
                        
                        # index finger logic for clicking and dragging (tap to click, hold to drag)
                        if distance_ti < 0.06:
                            if start_time is None:
                                start_time = time.time()
                            elapsed = time.time() - start_time
                            if elapsed >= 0.3:
                                if not dragging:
                                    mouse.press(Button.left)
                                    dragging = True
                                cv2.putText(frame, "TI: Left Drag", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 0), 3)
                            else:
                                cv2.putText(frame, "TI: Left Click", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
                        else:
                            if dragging:
                                mouse.release(Button.left)
                                dragging = False
                            elif start_time is not None:
                                mouse.click(Button.left, 1)
                            start_time = None
                            cv2.putText(frame, "TI: None", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

                        # right click logic
                        if distance_tm < 0.06:
                            if not right_click:
                                mouse.click(Button.right, 1)
                                right_click = True
                            cv2.putText(frame, "TM: Right Click", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 0), 3)
                        else:
                            if right_click:
                                right_click = False
                            cv2.putText(frame, "TM: None", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

                        # scroll logic
                        if distance_tr < 0.06:
                            if mid_y_tr > int(hand_landmarks.landmark[13].y * h):
                                pyautogui.scroll(-6)
                                time.sleep(0.0001)
                            else:
                                pyautogui.scroll(6)
                                time.sleep(0.0001)

                        # margin for hand to mouse
                        margin = -600
                        # convert hand position to mouse position
                        target_x = int(mid_x_ti / w * (screen_w - 2 * margin) + margin)
                        target_y = int(mid_y_ti / h * (screen_h - 2 * margin) + margin)

                        # smoothly convert hand to mouse, otherwise it is jagedy (smooth it out iwht alpha)
                        smooth_x = smooth_x * (1 - alpha) + target_x * alpha
                        smooth_y = smooth_y * (1 - alpha) + target_y * alpha
                        # place mouse where hand is, smoothly
                        mouse.position = (int(smooth_x), int(smooth_y))

                    case "Keyboard":
                        cv2.putText(frame, "Mode: Keyboard", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 0), 3)
                        # extra settings added
                        cv2.putText(frame, f"shift: {'Off' if capslock else ('On' if shift else 'Off')}", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.5, ((0, 0, 255) if capslock else ((0, 255, 0) if shift else (0, 0, 255))), 3)
                        cv2.putText(frame, f"caps lock: {'On' if capslock else 'Off'}", (50, 250), cv2.FONT_HERSHEY_SIMPLEX, 1.5, ((0, 255, 0) if capslock else (0, 0, 255)), 3)

                        # LOOK AT MOUSE MODE FOR FULL EXPLANATION (COPY AND PASTED LOGIC)
                        # ---------------------------------------------------------------

                        x1_ti, y1_ti = int(thumb_tip.x * w), int(thumb_tip.y * h)
                        x2_ti, y2_ti = int(index_tip.x * w), int(index_tip.y * h)
                        cv2.line(frame, (x1_ti, y1_ti), (x2_ti, y2_ti), (255, 255, 255), 3)

                        mid_x_ti, mid_y_ti = (x1_ti + x2_ti) // 2, (y1_ti + y2_ti) // 2
                        cv2.circle(frame, (mid_x_ti, mid_y_ti), 10, (0, 255, 0), cv2.FILLED)

                        x1_tm, y1_tm = int(thumb_tip.x * w), int(thumb_tip.y * h)
                        x2_tm, y2_tm = int(middle_tip.x * w), int(middle_tip.y * h)
                        cv2.line(frame, (x1_tm, y1_tm), (x2_tm, y2_tm), (255, 255, 255), 3)

                        mid_x_tm, mid_y_tm = (x1_tm + x2_tm) // 2, (y1_tm + y2_tm) // 2
                        cv2.circle(frame, (mid_x_tm, mid_y_tm), 10, (255, 0, 0), cv2.FILLED)

                        x1_tp, y1_tp = int(thumb_tip.x * w), int(thumb_tip.y * h)
                        x2_tp, y2_tp = int(pinky_tip.x * w), int(pinky_tip.y * h)
                        cv2.line(frame, (x1_tp, y1_tp), (x2_tp, y2_tp), (255, 255, 255), 3)

                        mid_x_tp, mid_y_tp = (x1_tp + x2_tp) // 2, (y1_tp + y2_tp) // 2
                        cv2.circle(frame, (mid_x_tp, mid_y_tp), 10, (0, 0, 255), cv2.FILLED)

                        distance_ti = calc_distance(thumb_tip, index_tip)
                        distance_tm = calc_distance(thumb_tip, middle_tip)
                        distance_tr = calc_distance(thumb_tip, ring_tip)
                        distance_tp = calc_distance(thumb_tip, pinky_tip)

                        i_x = max(0, min(int(index_tip.x * w), w-1))
                        i_y = max(0, min(int(index_tip.y * h), h-1))

                        m_x = max(0, min(int(middle_tip.x * w), w-1))
                        m_y = max(0, min(int(middle_tip.y * h), h-1))

                        r_x = max(0, min(int(ring_tip.x * w), w-1))
                        r_y = max(0, min(int(ring_tip.y * h), h-1))

                        p_x = max(0, min(int(pinky_tip.x * w), w-1))
                        p_y = max(0, min(int(pinky_tip.y * h), h-1))

                        # switch for keyboard mode (main menu, morse menu, special chars, etc.)
                        match keyboard_mode:    
                            # main menu of keyboard mode
                            case "main":
                                # toggle back to "Mouse" mode with pinky
                                if distance_tp < 0.06 and (time.time() - last_pinky_toggle) > 0.15:
                                    mode = "Mouse"
                                    last_pinky_toggle = time.time()
                                
                                # labels
                                cv2.putText(frame, "morse", (i_x-50, i_y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 3)
                                cv2.putText(frame, "text-altering", (m_x-50, m_y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 3)
                                cv2.putText(frame, "mouse mode", (p_x-50, p_y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)

                                # toggle "morse" keyboard mode
                                if distance_ti < 0.06 and (time.time() - last_index_toggle) > 0.15:
                                    keyboard_mode = "morse"
                                    last_index_toggle = time.time()

                                # toggle text altering first state (main page)
                                if distance_tm < 0.06 and (time.time() - last_middle_toggle) > 0.15:
                                    keyboard_mode = "ta_"
                                    last_middle_toggle = time.time()
                            
                            # "morse" keyboard mode
                            case "morse":
                                # place image in bottom left corner
                                if overlay is not None:
                                    oh, ow = overlay.shape[:2]
                                    y = h - oh - 20
                                    x = 20 
                                    frame = overlay_image_alpha(frame, overlay, (x, y))

                                # go back to "main" keyboard mode
                                if distance_tp < 0.09 and (time.time() - last_pinky_toggle) > 0.15:
                                    pattern = []
                                    keyboard_mode = "main"
                                    last_pinky_toggle = time.time()

                                # add labels
                                cv2.putText(frame, "single", (i_x-50, i_y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 3)
                                cv2.putText(frame, "long", (m_x-50, m_y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 3)
                                cv2.putText(frame, "finish", (r_x-50, r_y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 3)
                                cv2.putText(frame, "back", (p_x-50, p_y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)

                                # add . to morse pattern (short)
                                if distance_ti < 0.09 and (time.time() - last_index_toggle) > 0.15:
                                    pattern.append(".")
                                    last_index_toggle = time.time()
                                
                                # add - to morse pattern (long)
                                if distance_tm < 0.09 and (time.time() - last_middle_toggle) > 0.15:
                                    pattern.append("_")
                                    last_middle_toggle = time.time()

                                # finish pattern and submit as letter
                                if distance_tr < 0.09 and (time.time() - last_ring_toggle) > 0.15:
                                    pattern_final = ''.join(pattern)
                                    
                                    # (made my custom morse code to support special characters [got inspo online])
                                    # pattern switch for converting morse code to letters
                                    match pattern_final:
                                        case "._":
                                            if shift:
                                                pyautogui.write("A")
                                                shift = False
                                            else:
                                                pyautogui.write("a")
                                        case "_...":
                                            if shift:
                                                pyautogui.write("B")
                                                shift = False
                                            else:
                                                pyautogui.write("b")
                                        case "_._.":
                                            if shift:
                                                pyautogui.write("C")
                                                shift = False
                                            else:
                                                pyautogui.write("c")
                                        case "_..":
                                            if shift:
                                                pyautogui.write("D")
                                                shift = False
                                            else:
                                                pyautogui.write("d")
                                        case ".":
                                            if shift:
                                                pyautogui.write("E")
                                                shift = False
                                            else:
                                                pyautogui.write("e")
                                        case ".._.":
                                            if shift:
                                                pyautogui.write("F")
                                                shift = False
                                            else:
                                                pyautogui.write("f")
                                        case "__.":
                                            if shift:
                                                pyautogui.write("G")
                                                shift = False
                                            else:
                                                pyautogui.write("g")
                                        case "....":
                                            if shift:
                                                pyautogui.write("H")
                                                shift = False
                                            else:
                                                pyautogui.write("h")
                                        case "..":
                                            if shift:
                                                pyautogui.write("I")
                                                shift = False
                                            else:
                                                pyautogui.write("i")
                                        case ".___":
                                            if shift:
                                                pyautogui.write("J")
                                                shift = False
                                            else:
                                                pyautogui.write("j")
                                        case "_._":
                                            if shift:
                                                pyautogui.write("K")
                                                shift = False
                                            else:
                                                pyautogui.write("k")
                                        case "._..":
                                            if shift:
                                                pyautogui.write("L")
                                                shift = False
                                            else:
                                                pyautogui.write("l")
                                        case "__":
                                            if shift:
                                                pyautogui.write("M")
                                                shift = False
                                            else:
                                                pyautogui.write("m")
                                        case "_.":
                                            if shift:
                                                pyautogui.write("N")
                                                shift = False
                                            else:
                                                pyautogui.write("n")
                                        case "___":
                                            if shift:
                                                pyautogui.write("O")
                                                shift = False
                                            else:
                                                pyautogui.write("o")
                                        case ".__.":
                                            if shift:
                                                pyautogui.write("P")
                                                shift = False
                                            else:
                                                pyautogui.write("p")
                                        case "__._":
                                            if shift:
                                                pyautogui.write("Q")
                                                shift = False
                                            else:
                                                pyautogui.write("q")
                                        case "._.":
                                            if shift:
                                                pyautogui.write("R")
                                                shift = False
                                            else:
                                                pyautogui.write("r")
                                        case "...":
                                            if shift:
                                                pyautogui.write("S")
                                                shift = False
                                            else:
                                                pyautogui.write("s")
                                        case "_":
                                            if shift:
                                                pyautogui.write("T")
                                                shift = False
                                            else:
                                                pyautogui.write("t")
                                        case ".._":
                                            if shift:
                                                pyautogui.write("U")
                                                shift = False
                                            else:
                                                pyautogui.write("u")
                                        case "..._":
                                            if shift:
                                                pyautogui.write("V")
                                                shift = False
                                            else:
                                                pyautogui.write("v")
                                        case ".__":
                                            if shift:
                                                pyautogui.write("W")
                                                shift = False
                                            else:
                                                pyautogui.write("w")
                                        case "_.._":
                                            if shift:
                                                pyautogui.write("X")
                                                shift = False
                                            else:
                                                pyautogui.write("x")
                                        case "_.__":
                                            if shift:
                                                pyautogui.write("Y")
                                                shift = False
                                            else:
                                                pyautogui.write("y")
                                        case "__..":
                                            if shift:
                                                pyautogui.write("Z")
                                                shift = False
                                            else:
                                                pyautogui.write("z")
                                        case ".____":
                                            pyautogui.write("1")
                                        case "..___":
                                            pyautogui.write("2")
                                        case "...__":
                                            pyautogui.write("3")
                                        case "...._":
                                            pyautogui.write("4")
                                        case ".....":
                                            pyautogui.write("5")
                                        case "_....":
                                            pyautogui.write("6")
                                        case "__...":
                                            pyautogui.write("7")
                                        case "___..":
                                            pyautogui.write("8")
                                        case "____.":
                                            pyautogui.write("9")
                                        case "_____":
                                            pyautogui.write("0")
                                        case "_.__._.":
                                            pyautogui.write("~")
                                        case ".__.._.":
                                            pyautogui.write("`")
                                        case "_._.__":
                                            pyautogui.write("!")
                                        case ".__._.":
                                            pyautogui.write("@")
                                        case "......":
                                            pyautogui.write("#")
                                        case "..._.._":
                                            pyautogui.write("$")
                                        case "__._..":
                                            pyautogui.write("%")
                                        case "._._..":
                                            pyautogui.write("^")
                                        case "._...":
                                            pyautogui.write("&")
                                        case "_.._._":
                                            pyautogui.write("*")
                                        case "_.__.":
                                            pyautogui.write("(")
                                        case "_.__._":
                                            pyautogui.write(")")
                                        case "_...._":
                                            pyautogui.write("-")
                                        case "..__._":
                                            pyautogui.write("_")
                                        case "._._.":
                                            pyautogui.write("+")
                                        case "_..._":
                                            pyautogui.write("=")
                                        case "_._.._":
                                            pyautogui.write("{")
                                        case "__.._.":
                                            pyautogui.write("}")
                                        case "_.__..":
                                            pyautogui.write("[")
                                        case "__.__.":
                                            pyautogui.write("]")
                                        case "._..__":
                                            pyautogui.write("|")
                                        case "..__.._":
                                            pyautogui.write("\\")
                                        case "___...":
                                            pyautogui.write(":")
                                        case "_._._.":
                                            pyautogui.write(";")
                                        case "._.._.":
                                            pyautogui.write("\"")
                                        case ".____.":
                                            pyautogui.write("'")
                                        case "._._..":
                                            pyautogui.write("<")
                                        case "__._.__":
                                            pyautogui.write(">")
                                        case "__..__":
                                            pyautogui.write(",")
                                        case "._._._":
                                            pyautogui.write(".")
                                        case "..__..":
                                            pyautogui.write("?")
                                        case "_.._.":
                                            pyautogui.write("/")
                                        case _:
                                            print("Error: Morse code pattern not identified")
                                    
                                    # add dots and dashes to array for full pattern
                                    pattern = []
                                    # set keyboard mode to "main"
                                    keyboard_mode = "main"
                                    # finish timer
                                    last_ring_toggle = time.time()
                                
                                # update pattern text
                                cv2.putText(frame, f"pattern: {' '.join(pattern)}", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
                            
                            # "text-altering" mode in keyboard mode
                            case "ta_":
                                if distance_tp < 0.09 and (time.time() - last_pinky_toggle) > 0.15:
                                    pattern = []
                                    keyboard_mode = "main"
                                    last_pinky_toggle = time.time()

                                # labels
                                cv2.putText(frame, "shft, caps, tab", (i_x-50, i_y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 3)
                                cv2.putText(frame, "del, ret, spa", (m_x-50, m_y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 3)
                                cv2.putText(frame, "esc", (r_x-50, r_y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 3)
                                cv2.putText(frame, "back", (p_x-50, p_y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)

                                # "shft, caps, tab"
                                if distance_ti < 0.06 and (time.time() - last_index_toggle) > 0.15:
                                    keyboard_mode = "ta_1"
                                    last_index_toggle = time.time()

                                # "del, ret, spa"
                                if distance_tm < 0.06 and (time.time() - last_middle_toggle) > 0.15:
                                    keyboard_mode = "ta_2"
                                    last_middle_toggle = time.time()

                                # press "esc"
                                if distance_tr < 0.06 and (time.time() - last_ring_toggle) > 0.15:
                                    pyautogui.press("esc")
                                    keyboard_mode = "main"
                                    last_ring_toggle = time.time()
                            
                            # text-altering mode 1 ("shft, caps, tab")
                            case "ta_1":
                                # go back to ta main menu
                                if distance_tp < 0.09 and (time.time() - last_pinky_toggle) > 0.15:
                                    pattern = []
                                    keyboard_mode = "main"
                                    last_pinky_toggle = time.time()
                                
                                # labels
                                cv2.putText(frame, "shift", (i_x-50, i_y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 3)
                                cv2.putText(frame, "caps lock", (m_x-50, m_y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 3)
                                cv2.putText(frame, "tab", (r_x-50, r_y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 3)
                                cv2.putText(frame, "back", (p_x-50, p_y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)

                                # shift logic
                                if distance_ti < 0.06 and (time.time() - last_index_toggle) > 0.15:
                                    if shift:
                                        shift = False
                                    else:
                                        shift = True
                                    keyboard_mode = "morse"
                                    last_index_toggle = time.time()

                                # capslock logic
                                if distance_tm < 0.06 and (time.time() - last_middle_toggle) > 0.15:
                                    if capslock:
                                        capslock = False
                                        shift = False
                                    else: 
                                        capslock = True
                                    keyboard_mode = "main"
                                    last_middle_toggle = time.time()

                                # tab logic
                                if distance_tr < 0.06 and (time.time() - last_ring_toggle) > 0.15:
                                    pyautogui.press('tab')
                                    keyboard_mode = "main"
                                    last_ring_toggle = time.time()
                            
                            # text-altering mode 2 ("del, ret, spa")
                            case "ta_2":
                                # go back to ta main menu
                                if distance_tp < 0.09 and (time.time() - last_pinky_toggle) > 0.15:
                                    pattern = []
                                    keyboard_mode = "main"
                                    last_pinky_toggle = time.time()
                                
                                # labels
                                cv2.putText(frame, "delete", (i_x-50, i_y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 3)
                                cv2.putText(frame, "return", (m_x-50, m_y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 3)
                                cv2.putText(frame, "space", (r_x-50, r_y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 3)
                                cv2.putText(frame, "back", (p_x-50, p_y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)

                                # delete logic
                                if distance_ti < 0.06 and (time.time() - last_index_toggle) > 0.15:
                                    pyautogui.press("backspace")
                                    keyboard_mode = "main"
                                    last_index_toggle = time.time()
                                
                                # return logic
                                if distance_tm < 0.06 and (time.time() - last_middle_toggle) > 0.15:
                                    pyautogui.press("return")
                                    keyboard_mode = "main"
                                    last_middle_toggle = time.time()
                                
                                # space logic
                                if distance_tr < 0.06 and (time.time() - last_ring_toggle) > 0.15:
                                    pyautogui.press("space")
                                    keyboard_mode = "main"
                                    last_ring_toggle = time.time()

    # if hand not detected
    else:
        cv2.putText(frame, "No Hand Detected", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

    cv2.putText(frame, "Press Esc to Quit", (1450, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

    # show window
    cv2.imshow("Control Mac", frame)
    # press esc to exit
    if cv2.waitKey(1) & 0xFF == 27:
        break

cam.release()
cv2.destroyAllWindows()
