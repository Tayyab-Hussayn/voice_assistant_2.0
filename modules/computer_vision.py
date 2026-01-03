import cv2
import numpy as np
import subprocess
import time
from threading import Thread

# Try to import GUI-dependent modules
try:
    import pyautogui
    import mediapipe as mp
    GUI_AVAILABLE = True
except Exception as e:
    print(f"GUI modules not available: {e}")
    GUI_AVAILABLE = False

class ComputerVision:
    def __init__(self):
        if not GUI_AVAILABLE:
            print("⚠️ Computer vision running in limited mode - no GUI access")
            return
            
        # Initialize MediaPipe
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        # Gesture recognition
        self.gesture_buffer = []
        self.gesture_threshold = 5
        self.last_gesture = None
        self.gesture_cooldown = 0
        
        # Screen capture
        try:
            self.screen_width, self.screen_height = pyautogui.size()
        except:
            self.screen_width, self.screen_height = 1920, 1080  # Default
        
        # Camera
        self.camera = None
        self.camera_active = False
        
    def start_camera(self):
        """Start camera feed"""
        if not GUI_AVAILABLE:
            return False, "Camera not available - no GUI access"
            
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                return False, "Could not open camera"
            self.camera_active = True
            return True, "Camera started"
        except Exception as e:
            return False, f"Camera error: {e}"
    
    def stop_camera(self):
        """Stop camera feed"""
        self.camera_active = False
        if self.camera:
            self.camera.release()
        cv2.destroyAllWindows()
        return True, "Camera stopped"
    
    def take_screenshot(self, save_path=None):
        """Take a screenshot"""
        if not GUI_AVAILABLE:
            return False, "Screenshot not available - no GUI access"
            
        try:
            screenshot = pyautogui.screenshot()
            if save_path:
                screenshot.save(save_path)
                return True, f"Screenshot saved to {save_path}"
            else:
                # Save with timestamp
                timestamp = int(time.time())
                path = f"screenshot_{timestamp}.png"
                screenshot.save(path)
                return True, f"Screenshot saved as {path}"
        except Exception as e:
            return False, f"Screenshot failed: {e}"
    
    def detect_hands(self, frame):
        """Detect hands in frame"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        hand_landmarks = []
        if results.multi_hand_landmarks:
            for landmarks in results.multi_hand_landmarks:
                # Convert landmarks to pixel coordinates
                h, w, _ = frame.shape
                landmark_points = []
                for lm in landmarks.landmark:
                    x, y = int(lm.x * w), int(lm.y * h)
                    landmark_points.append((x, y))
                hand_landmarks.append(landmark_points)
                
                # Draw landmarks
                self.mp_drawing.draw_landmarks(
                    frame, landmarks, self.mp_hands.HAND_CONNECTIONS)
        
        return frame, hand_landmarks
    
    def recognize_gesture(self, landmarks):
        """Recognize hand gestures"""
        if not landmarks:
            return None
            
        # Get first hand landmarks
        points = landmarks[0]
        
        # Simple gesture recognition based on finger positions
        # Index finger tip and MCP
        index_tip = points[8]
        index_mcp = points[5]
        
        # Middle finger tip and MCP  
        middle_tip = points[12]
        middle_mcp = points[9]
        
        # Thumb tip and MCP
        thumb_tip = points[4]
        thumb_mcp = points[2]
        
        # Check if fingers are extended
        index_up = index_tip[1] < index_mcp[1]
        middle_up = middle_tip[1] < middle_mcp[1]
        thumb_up = thumb_tip[0] > thumb_mcp[0]  # Thumb extends horizontally
        
        # Gesture recognition
        if index_up and not middle_up:
            return "point"
        elif index_up and middle_up:
            return "peace"
        elif thumb_up and index_up:
            return "thumbs_up"
        elif not index_up and not middle_up:
            return "fist"
        else:
            return "open_hand"
    
    def map_hand_to_cursor(self, landmarks):
        """Map hand position to cursor movement"""
        if not landmarks:
            return None
            
        # Use index finger tip for cursor control
        index_tip = landmarks[0][8]
        
        # Map camera coordinates to screen coordinates
        # Flip X for mirror effect
        screen_x = self.screen_width - int((index_tip[0] / 640) * self.screen_width)
        screen_y = int((index_tip[1] / 480) * self.screen_height)
        
        # Smooth movement
        current_x, current_y = pyautogui.position()
        smooth_x = int(current_x * 0.7 + screen_x * 0.3)
        smooth_y = int(current_y * 0.7 + screen_y * 0.3)
        
        return smooth_x, smooth_y
    
    def execute_gesture_action(self, gesture):
        """Execute action based on gesture"""
        if self.gesture_cooldown > 0:
            self.gesture_cooldown -= 1
            return None
            
        if gesture == "point":
            # Move cursor
            return "cursor_control"
        elif gesture == "fist":
            # Click
            pyautogui.click()
            self.gesture_cooldown = 10
            return "click"
        elif gesture == "peace":
            # Right click
            pyautogui.rightClick()
            self.gesture_cooldown = 10
            return "right_click"
        elif gesture == "thumbs_up":
            # Scroll up
            pyautogui.scroll(3)
            self.gesture_cooldown = 5
            return "scroll_up"
        
        return None
    
    def gesture_control_loop(self):
        """Main gesture control loop"""
        if not self.camera_active:
            return False, "Camera not active"
            
        try:
            while self.camera_active:
                ret, frame = self.camera.read()
                if not ret:
                    break
                
                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Detect hands
                frame, landmarks = self.detect_hands(frame)
                
                if landmarks:
                    # Recognize gesture
                    gesture = self.recognize_gesture(landmarks)
                    
                    if gesture:
                        # Add to gesture buffer for stability
                        self.gesture_buffer.append(gesture)
                        if len(self.gesture_buffer) > self.gesture_threshold:
                            self.gesture_buffer.pop(0)
                        
                        # Check if gesture is consistent
                        if len(self.gesture_buffer) >= 3:
                            most_common = max(set(self.gesture_buffer), 
                                            key=self.gesture_buffer.count)
                            
                            if most_common != self.last_gesture:
                                action = self.execute_gesture_action(most_common)
                                if action == "cursor_control":
                                    cursor_pos = self.map_hand_to_cursor(landmarks)
                                    if cursor_pos:
                                        pyautogui.moveTo(cursor_pos[0], cursor_pos[1])
                                
                                self.last_gesture = most_common
                
                # Display frame
                cv2.putText(frame, f"Gesture: {self.last_gesture or 'None'}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.imshow('JARVIS Vision', frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
            return True, "Gesture control stopped"
            
        except Exception as e:
            return False, f"Gesture control error: {e}"
    
    def start_gesture_control(self):
        """Start gesture control in background thread"""
        success, msg = self.start_camera()
        if not success:
            return success, msg
            
        # Start gesture control in separate thread
        gesture_thread = Thread(target=self.gesture_control_loop)
        gesture_thread.daemon = True
        gesture_thread.start()
        
        return True, "Gesture control started - use 'q' to quit"
    
    def analyze_screen(self):
        """Analyze current screen content"""
        try:
            screenshot = pyautogui.screenshot()
            # Convert to OpenCV format
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # Simple analysis - detect windows, text areas, etc.
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours (potential UI elements)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            ui_elements = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 1000:  # Filter small elements
                    x, y, w, h = cv2.boundingRect(contour)
                    ui_elements.append({
                        'x': x, 'y': y, 'width': w, 'height': h, 'area': area
                    })
            
            return True, {
                'screen_size': (self.screen_width, self.screen_height),
                'ui_elements': len(ui_elements),
                'large_elements': len([e for e in ui_elements if e['area'] > 10000])
            }
            
        except Exception as e:
            return False, f"Screen analysis failed: {e}"
