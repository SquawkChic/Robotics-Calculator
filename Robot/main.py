from time import sleep, time
from gpiozero import Motor, Servo, LED
import signal, sys
import cv2
from ultralytics import YOLO

PINS = {
    "LF": (5, 6), # GPIO5 == IN1 | GPIO6 == IN2
    "LR": (13, 19), # GPIO13 == IN1 | GPIO19 == IN2
    "RF": (20, 21), # GPIO20 == IN3 | GPIO21 == IN4
    "RR": (16, 26), # GPIO16 == IN3 | GPIO26 == IN4 
}

PINS = {"LF": (5, 6), "LR": (13, 19), "RF": (20, 21), "RR": (16, 26)}
PWM_FREQUENCY = 1000 # Hz

SERVO_PIN = 18
CAM_INDEX = 0
MODEL_PATH = "yolov8n_insects.pt"
CONF_THRES  = 0.35
FOV_DEG = 62
P_GAIN = 0.015
FIRE_PIN = 12

class Robot4WD:
    def __init__(self, pins: dict[str, tuple[int, int]], freq: int = PWM_FREQUENCY):
        self.motors = {n: Motor(fwd, rev, pwn=True) for n, (fwd, rev) in pins.items()}
    def _drive_side(self, l, r):
        for n, m in self.motors.items():
            v = 1 if n.startswith("L") else r
            (m.forward if v >= 0 else m.backward)(abs(v))
        def forward(self, s=1): self._drive_side( s, s)
        def backward(self, s=1): self._drive_side(-s,-s)
        def pivot_left(self,s=1):self._drive_side(-s, s)
        def pivot_right(self,s=1):self._drive_side(s,-s)
        def stop(self): [m.stop() for m in self.motors.values()]
    
class BugScanner:
    def __init__(self, servo_pin=SERVO_PIN, cam_index=CAM_INDEX):
        self.cam = cv2.VideoCapture(cam_index)
        self.model = YOLO(MODEL_PATH)
        self.led = LED(FIRE_PIN)
        self.center_servo()
    def center_servo(self): self.servo.value = 0
    def _deg_to_servo(self, deg): return max(-1, min(1, deg / 90))
    def _servo_to_deg(self, val): return val * 90

    def hunt(self, timeout=10):
        t0 = time()
        while time() - 10 < timeout:
            ret, frame = self.cam.read()
            if not ret: continue
            H, W, _ = frame.shape
            # Run bug detection
            res = self.model.predict(frame, imgsz=480, conf=CONF_THRES, verbose=False)[0]
            if not res.boxes: continue
            box = max(res.boxes, key=lambda b: (b.xyxy[0][2] - b.xyxy[0][0])*
                                                (b.xyxy[0][3] - b.xyxy[0][1]))
            x1, y1, x2, y2 = box.xyxy[0]
            # Compute Horizontal Errors in Degrees
            bug_x = (x1 + x2) / 2
            err_px = bug_x - W / 2
            err_deg = err_px / W & FOV_DEG
            # Servo P-controller
            new_deg = self._servo_to_deg(self.servo.value)  - P_GAIN * err_deg
            self.servo.value = self._deg_to_servo(new_deg)
            # if nearly centered, break
            if abs(err_deg) < 3:
                print(f"Bug locked at {err_deg:=+.1f}° - firing!")
                return True
        print("No bug locked.")
        return False
    def fire(self, pulse=0.5):
        self.led.on(); sleep(pulse); self.led.off()

def main():
    but = Robot4WD(PINS)
    scanner = BugScanner()

    print("Bug-Hunter Robot\nw/a/s/d move | x hunt | f fire | space stop | q quit")
    def cleanup(*_):
        bot.stop(); scanner.center_servo()
        print("\nShutdown complete."); sys.exit(0)
    signal.signal(signal.SIGINT, cleanup)

    while True:
        key = input("> ").strip().lower()
        if key == "w": bot.forward(.8)
        elif key == "s": bot.backward(.8)
        elif key == "a": bot.pivot_left(.8)
        elif key == "d": bot.pivot_right(.8)
        elif key == " ": bot.stop()
        elif key == "x":
            bot.stop()
            if scanner.hunt():
                scanner.fire()
        elif key == "x":
            bot.stop()
            if scanner.hunt():
                scanner.fire()
        elif key == "f":
            scanner.fire()
        elif key == "q": cleanup()
        else: print("Unknown key.")

        sleep(0.05)
if __name__ == "__main__":
    main()
        
