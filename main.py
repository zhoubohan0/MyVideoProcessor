import sys
import os
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QSlider, 
                            QFileDialog, QStyle, QMessageBox, QToolBar, 
                            QAction, QDialog, QSpinBox, QComboBox, QLineEdit,
                            QStackedWidget)
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QImage, QPixmap, QDragEnterEvent, QDropEvent, QIcon, QCursor
from PyQt5.QtCore import pyqtSignal

class TimeSlider(QSlider):
    clicked = pyqtSignal(int)
    
    def __init__(self, orientation):
        super().__init__(orientation)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Calculate the value corresponding to the clicked position
            pos = event.pos().x()
            slider_width = self.width()
            value = int((pos / slider_width) * self.maximum())
            self.clicked.emit(value)
        super().mousePressEvent(event)

class SegmentWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.is_updating = False
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(5)  # Reduce layout spacing
        layout.setContentsMargins(5, 5, 5, 5)  # Reduce margins
        
        # Timeline container
        timeline_container = QWidget()
        timeline_layout = QVBoxLayout(timeline_container)
        timeline_layout.setSpacing(2)  # Reduce timeline layout spacing
        
        # Begin timeline
        begin_layout = QHBoxLayout()  # Changed to horizontal layout
        begin_layout.setSpacing(5)
        begin_label = QLabel("Begin:")
        begin_label.setFixedWidth(50)
        begin_layout.addWidget(begin_label)
        
        self.begin_slider = TimeSlider(Qt.Horizontal)
        self.begin_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #666666;
                margin: 2px 0;
            }
            QSlider::handle:horizontal {
                background: #4CAF50;
                border: 1px solid #4CAF50;
                width: 18px;
                margin: -2px 0;
                border-radius: 3px;
            }
        """)
        self.begin_slider.clicked.connect(self.begin_slider_clicked)
        self.begin_slider.valueChanged.connect(self.begin_slider_changed)
        begin_layout.addWidget(self.begin_slider)
        
        self.begin_input = QLineEdit()
        self.begin_input.setFixedWidth(80)
        self.begin_input.editingFinished.connect(self.update_begin_input)
        begin_layout.addWidget(self.begin_input)
        
        timeline_layout.addLayout(begin_layout)
        
        # End timeline
        end_layout = QHBoxLayout()  # Changed to horizontal layout
        end_layout.setSpacing(5)
        end_label = QLabel("End:")
        end_label.setFixedWidth(50)
        end_layout.addWidget(end_label)
        
        self.end_slider = TimeSlider(Qt.Horizontal)
        self.end_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #666666;
                margin: 2px 0;
            }
            QSlider::handle:horizontal {
                background: #FF5722;
                border: 1px solid #FF5722;
                width: 18px;
                margin: -2px 0;
                border-radius: 3px;
            }
        """)
        self.end_slider.clicked.connect(self.end_slider_clicked)
        self.end_slider.valueChanged.connect(self.end_slider_changed)
        end_layout.addWidget(self.end_slider)
        
        self.end_input = QLineEdit()
        self.end_input.setFixedWidth(80)
        self.end_input.editingFinished.connect(self.update_end_input)
        end_layout.addWidget(self.end_input)
        
        timeline_layout.addLayout(end_layout)
        layout.addWidget(timeline_container)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        self.confirm_btn = QPushButton("Confirm")
        self.cancel_btn = QPushButton("Cancel")
        self.confirm_btn.setFixedHeight(30)  # Reduce button height
        self.cancel_btn.setFixedHeight(30)
        self.confirm_btn.clicked.connect(self.confirm_selection)
        self.cancel_btn.clicked.connect(self.cancel_selection)
        button_layout.addWidget(self.confirm_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
    def set_range(self, total_frames):
        self.is_updating = True
        self.begin_slider.setRange(0, total_frames)
        self.end_slider.setRange(0, total_frames)
        self.begin_input.setText("0")
        self.end_input.setText(str(total_frames))
        self.begin_slider.setValue(0)
        self.end_slider.setValue(total_frames)
        self.is_updating = False
        
    def begin_slider_changed(self, value):
        if self.is_updating:
            return
        self.is_updating = True
        try:
            end_value = int(self.end_input.text() or 0)
            if value >= end_value:
                value = end_value - 1
                self.begin_slider.setValue(value)
            self.begin_input.setText(str(value))
            if self.parent:
                self.parent.update_preview_frame(value)
        finally:
            self.is_updating = False
            
    def end_slider_changed(self, value):
        if self.is_updating:
            return
        self.is_updating = True
        try:
            begin_value = int(self.begin_input.text() or 0)
            if value <= begin_value:
                value = begin_value + 1
                self.end_slider.setValue(value)
            self.end_input.setText(str(value))
            if self.parent:
                self.parent.update_preview_frame(value)
        finally:
            self.is_updating = False
            
    def begin_slider_clicked(self, value):
        if self.is_updating:
            return
            
        self.is_updating = True
        try:
            end_value = int(self.end_input.text() or 0)
            if value >= end_value:
                value = end_value - 1
            self.begin_input.setText(str(value))
            self.begin_slider.setValue(value)
            if self.parent:
                self.parent.update_preview_frame(value)
        finally:
            self.is_updating = False
            
    def end_slider_clicked(self, value):
        if self.is_updating:
            return
            
        self.is_updating = True
        try:
            begin_value = int(self.begin_input.text() or 0)
            if value <= begin_value:
                value = begin_value + 1
            self.end_input.setText(str(value))
            self.end_slider.setValue(value)
            if self.parent:
                self.parent.update_preview_frame(value)
        finally:
            self.is_updating = False
            
    def update_begin_input(self):
        if self.is_updating:
            return
            
        self.is_updating = True
        try:
            value = int(self.begin_input.text() or 0)
            end_value = int(self.end_input.text() or 0)
            if value >= end_value:
                value = end_value - 1
                self.begin_input.setText(str(value))
            elif value < 0:
                value = 0
                self.begin_input.setText("0")
            self.begin_slider.setValue(value)
            if self.parent:
                self.parent.update_preview_frame(value)
        except ValueError:
            self.begin_input.setText("0")
        finally:
            self.is_updating = False
            
    def update_end_input(self):
        if self.is_updating:
            return
            
        self.is_updating = True
        try:
            value = int(self.end_input.text() or 0)
            begin_value = int(self.begin_input.text() or 0)
            if value <= begin_value:
                value = begin_value + 1
                self.end_input.setText(str(value))
            elif value > self.begin_slider.maximum():
                value = self.begin_slider.maximum()
                self.end_input.setText(str(value))
            self.end_slider.setValue(value)
            if self.parent:
                self.parent.update_preview_frame(value)
        except ValueError:
            self.end_input.setText(str(self.begin_slider.maximum()))
        finally:
            self.is_updating = False
            
    def confirm_selection(self):
        if self.parent:
            self.parent.confirm_segment(
                int(self.begin_input.text() or 0),
                int(self.end_input.text() or 0)
            )
            
    def cancel_selection(self):
        if self.parent:
            self.parent.cancel_segment()

class ClipWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.Window)  # Make it a window
        self.parent = parent
        self.init_ui()
        
        # Crop area related variables
        self.crop_rect = None  # Crop rectangle area
        self.dragging_corner = None  # Currently dragging corner
        self.corner_size = 40  # Increased corner size
        self.original_frame = None  # Original frame
        self.display_frame = None  # Display frame
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Video display area
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet("""
            QLabel {
                background-color: black;
                border: 2px solid #666;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.video_label)
        
        # Button area
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.confirm_btn = QPushButton("Confirm")
        self.cancel_btn = QPushButton("Cancel")
        self.confirm_btn.setFixedHeight(30)
        self.cancel_btn.setFixedHeight(30)
        
        self.confirm_btn.clicked.connect(self.confirm_clip)
        self.cancel_btn.clicked.connect(self.cancel_clip)
        
        button_layout.addWidget(self.confirm_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
    def showEvent(self, event):
        # Position the window to match parent window
        if self.parent:
            self.setGeometry(self.parent.geometry())
        super().showEvent(event)

    def set_frame(self, frame):
        if frame is None:
            return
            
        self.original_frame = frame.copy()
        self.display_frame = frame.copy()
        
        # Initialize crop area to full frame
        h, w = frame.shape[:2]
        self.crop_rect = [0, 0, w, h]  # [x1, y1, x2, y2]
        
        self.update_display()
        
    def update_display(self):
        if self.original_frame is None:
            return
            
        # Create a copy of the display frame
        display = self.original_frame.copy()
        
        # Create semi-transparent mask
        mask = np.zeros_like(display)
        mask[:] = (128, 128, 128)  # Gray background
        
        # Draw crop area
        x1, y1, x2, y2 = self.crop_rect
        mask[y1:y2, x1:x2] = (255, 200, 200)  # Lighter red area
        
        # Merge original frame and mask
        alpha = 0.3  # More transparent
        display = cv2.addWeighted(display, 1, mask, alpha, 0)
        
        # Draw crop frame
        cv2.rectangle(display, (x1, y1), (x2, y2), (255, 255, 255), 2)
        
        # Draw four corners with larger circles
        corners = [(x1, y1), (x2, y1), (x1, y2), (x2, y2)]
        for corner in corners:
            # Draw outer circle
            cv2.circle(display, corner, self.corner_size, (255, 255, 255), -1)
            # Draw inner circle
            cv2.circle(display, corner, self.corner_size - 2, (0, 0, 0), 1)
        
        # Convert to QImage and display
        h, w, ch = display.shape
        bytes_per_line = ch * w
        qt_image = QImage(display.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(qt_image).scaled(
            self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            
    def mousePressEvent(self, event):
        if self.original_frame is None:
            return
            
        pos = event.pos()
        label_pos = self.video_label.mapFrom(self, pos)
        
        # Get the actual image position from the video label
        pixmap = self.video_label.pixmap()
        if pixmap is None:
            return
            
        # Calculate the actual position in the label
        scaled_size = pixmap.size()
        label_size = self.video_label.size()
        x_offset = (label_size.width() - scaled_size.width()) // 2
        y_offset = (label_size.height() - scaled_size.height()) // 2
        
        # Convert to image coordinates
        img_x = int((label_pos.x() - x_offset) * self.original_frame.shape[1] / scaled_size.width())
        img_y = int((label_pos.y() - y_offset) * self.original_frame.shape[0] / scaled_size.height())
        
        # Check if clicked corner
        corners = [(self.crop_rect[0], self.crop_rect[1]),  # Top left
                  (self.crop_rect[2], self.crop_rect[1]),  # Top right
                  (self.crop_rect[0], self.crop_rect[3]),  # Bottom left
                  (self.crop_rect[2], self.crop_rect[3])]  # Bottom right
        
        for i, corner in enumerate(corners):
            if abs(img_x - corner[0]) <= self.corner_size and abs(img_y - corner[1]) <= self.corner_size:
                self.dragging_corner = i
                break
                
    def mouseMoveEvent(self, event):
        if self.dragging_corner is None or self.original_frame is None:
            return
            
        pos = event.pos()
        label_pos = self.video_label.mapFrom(self, pos)
        
        # Get the actual image position from the video label
        pixmap = self.video_label.pixmap()
        if pixmap is None:
            return
            
        # Calculate the actual position in the label
        scaled_size = pixmap.size()
        label_size = self.video_label.size()
        x_offset = (label_size.width() - scaled_size.width()) // 2
        y_offset = (label_size.height() - scaled_size.height()) // 2
        
        # Convert to image coordinates
        img_x = int((label_pos.x() - x_offset) * self.original_frame.shape[1] / scaled_size.width())
        img_y = int((label_pos.y() - y_offset) * self.original_frame.shape[0] / scaled_size.height())
        
        # Limit coordinates to image range
        img_x = max(0, min(img_x, self.original_frame.shape[1]))
        img_y = max(0, min(img_y, self.original_frame.shape[0]))
        
        # Update crop area
        if self.dragging_corner == 0:  # Top left
            self.crop_rect[0] = img_x
            self.crop_rect[1] = img_y
        elif self.dragging_corner == 1:  # Top right
            self.crop_rect[2] = img_x
            self.crop_rect[1] = img_y
        elif self.dragging_corner == 2:  # Bottom left
            self.crop_rect[0] = img_x
            self.crop_rect[3] = img_y
        elif self.dragging_corner == 3:  # Bottom right
            self.crop_rect[2] = img_x
            self.crop_rect[3] = img_y
            
        # Ensure top left corner is above bottom right corner
        self.crop_rect[0] = min(self.crop_rect[0], self.crop_rect[2])
        self.crop_rect[1] = min(self.crop_rect[1], self.crop_rect[3])
        self.crop_rect[2] = max(self.crop_rect[0], self.crop_rect[2])
        self.crop_rect[3] = max(self.crop_rect[1], self.crop_rect[3])
        
        self.update_display()
        
    def mouseReleaseEvent(self, event):
        self.dragging_corner = None
        
    def confirm_clip(self):
        if self.parent and self.crop_rect:
            x1, y1, x2, y2 = self.crop_rect
            self.parent.confirm_clip(x1, y1, x2, y2)
            
    def cancel_clip(self):
        if self.parent:
            self.parent.cancel_clip()

class ResizeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.Window)  # Make it a window
        self.parent = parent
        self.setWindowTitle("Resize")
        self.init_ui()
        
    def set_current_dimensions(self, width, height):
        self.width_input.setValue(width)
        self.height_input.setValue(height)
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Size input area
        size_layout = QHBoxLayout()
        size_layout.setSpacing(5)
        
        # Width input
        width_label = QLabel("Width:")
        self.width_input = QSpinBox()
        self.width_input.setRange(1, 9999)
        self.width_input.setFixedWidth(80)
        size_layout.addWidget(width_label)
        size_layout.addWidget(self.width_input)
        
        # Height input
        height_label = QLabel("Height:")
        self.height_input = QSpinBox()
        self.height_input.setRange(1, 9999)
        self.height_input.setFixedWidth(80)
        size_layout.addWidget(height_label)
        size_layout.addWidget(self.height_input)
        
        layout.addLayout(size_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(5)
        
        self.confirm_btn = QPushButton("Confirm")
        self.cancel_btn = QPushButton("Cancel")
        self.confirm_btn.setFixedHeight(25)
        self.cancel_btn.setFixedHeight(25)
        
        self.confirm_btn.clicked.connect(self.confirm_resize)
        self.cancel_btn.clicked.connect(self.cancel_resize)
        
        button_layout.addWidget(self.confirm_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
        # Set window size
        self.setFixedSize(300, 80)
        
    def showEvent(self, event):
        # Position the window to match parent window
        if self.parent:
            parent_geometry = self.parent.geometry()
            x = parent_geometry.x() + (parent_geometry.width() - self.width()) // 2
            y = parent_geometry.y() + (parent_geometry.height() - self.height()) // 2
            self.move(x, y)
        super().showEvent(event)
        
    def confirm_resize(self):
        if self.parent:
            width = self.width_input.value()
            height = self.height_input.value()
            self.parent.confirm_resize(width, height)
            
    def cancel_resize(self):
        if self.parent:
            self.parent.cancel_resize()

    def show_resize_dialog(self):
        if not self.cap:
            QMessageBox.warning(self, "Warning", "Please load a video first!")
            return
            
        # Create resize widget if not exists
        if self.resize_widget is None:
            self.resize_widget = ResizeWidget(self)
            
        # Set dimensions - use last resize dimensions if available, otherwise use current frame dimensions
        if self.last_resize_dimensions is not None:
            self.resize_widget.set_current_dimensions(*self.last_resize_dimensions)
        elif self.current_frame is not None:
            h, w = self.current_frame.shape[:2]
            self.resize_widget.set_current_dimensions(w, h)
            
        self.resize_widget.show()
        self.pause_video()

class SpeedWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Speed slider
        speed_layout = QHBoxLayout()
        speed_layout.setSpacing(5)
        
        speed_label = QLabel("Speed:")
        speed_label.setFixedWidth(50)
        speed_layout.addWidget(speed_label)
        
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(1, 100)  # 0.1-10.0, multiplied by 10 for integer slider
        self.speed_slider.setValue(10)  # Default to 1.0
        self.speed_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #666666;
                margin: 2px 0;
            }
            QSlider::handle:horizontal {
                background: #2196F3;
                border: 1px solid #2196F3;
                width: 18px;
                margin: -2px 0;
                border-radius: 3px;
            }
        """)
        self.speed_slider.valueChanged.connect(self.speed_changed)
        speed_layout.addWidget(self.speed_slider)
        
        self.speed_input = QLineEdit()
        self.speed_input.setFixedWidth(80)
        self.speed_input.setText("1.0")
        self.speed_input.setReadOnly(True)
        speed_layout.addWidget(self.speed_input)
        
        layout.addLayout(speed_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.confirm_btn = QPushButton("Confirm")
        self.cancel_btn = QPushButton("Cancel")
        self.confirm_btn.setFixedHeight(30)
        self.cancel_btn.setFixedHeight(30)
        
        self.confirm_btn.clicked.connect(self.confirm_speed)
        self.cancel_btn.clicked.connect(self.cancel_speed)
        
        button_layout.addWidget(self.confirm_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
    def speed_changed(self, value):
        speed = value / 10.0
        self.speed_input.setText(f"{speed:.1f}")
        
    def confirm_speed(self):
        if self.parent:
            speed = float(self.speed_input.text())
            self.parent.confirm_speed(speed)
            
    def cancel_speed(self):
        if self.parent:
            self.parent.cancel_speed()

class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Processing Tool")
        self.setGeometry(100, 100, 1280, 720)
        
        # Initialize variables
        self.cap = None
        self.current_frame = None
        self.is_playing = False
        self.fps = 0
        self.total_frames = 0
        self.current_frame_number = 0
        self.last_directory = ""
        self.segment_begin = 0
        self.segment_end = 0
        self.input_file = ""
        self.is_processing = False
        self.clip_rect = None  # Crop area
        self.clip_widget = None  # Will be created when needed
        self.resize_widget = None  # Will be created when needed
        self.resize_dimensions = None  # (width, height)
        self.last_resize_dimensions = None  # Store last resize dimensions
        self.speed_widget = None  # Will be created when needed
        self.playback_speed = 1.0  # Current playback speed
        self.original_fps = 0  # Store original FPS
        
        # Create UI
        self.init_ui()
        
        # Set up timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        
    def init_ui(self):
        # Create toolbar
        self.create_toolbar()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Video display area
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet("""
            QLabel {
                background-color: black;
                border: 2px dashed #666;
                border-radius: 5px;
            }
            QLabel:hover {
                border: 2px dashed #999;
            }
        """)
        self.video_label.setText("Drag and drop video file here")
        self.video_label.setStyleSheet(self.video_label.styleSheet() + """
            QLabel {
                color: #666;
                font-size: 16px;
            }
        """)
        main_layout.addWidget(self.video_label)
        
        # Create stacked widget
        self.stacked_widget = QStackedWidget()
        
        # Create default control interface
        default_widget = QWidget()
        default_layout = QVBoxLayout(default_widget)
        
        # Playback control area
        play_controls = QHBoxLayout()
        
        # Play/Pause button
        self.play_button = QPushButton()
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_button.clicked.connect(self.toggle_play)
        self.play_button.setEnabled(False)  # Initially disabled
        play_controls.addWidget(self.play_button)
        
        # Time slider
        self.time_slider = TimeSlider(Qt.Horizontal)
        self.time_slider.sliderPressed.connect(self.slider_pressed)
        self.time_slider.sliderReleased.connect(self.slider_released)
        self.time_slider.valueChanged.connect(self.slider_value_changed)
        self.time_slider.clicked.connect(self.time_slider_clicked)
        self.time_slider.setEnabled(False)  # Initially disabled
        play_controls.addWidget(self.time_slider)
        
        # Time label
        self.time_label = QLabel("00:00 / 00:00")
        play_controls.addWidget(self.time_label)
        
        default_layout.addLayout(play_controls)
        
        # Speed control area (initially hidden)
        self.speed_control = QWidget()
        speed_layout = QVBoxLayout(self.speed_control)
        speed_layout.setSpacing(5)
        
        # Speed slider area
        slider_layout = QHBoxLayout()
        slider_layout.setSpacing(5)
        
        speed_label = QLabel("Speed:")
        speed_label.setFixedWidth(50)
        slider_layout.addWidget(speed_label)
        
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(0, 100)  # 0-100 for logarithmic scale
        self.speed_slider.setValue(50)  # Default to 1.0
        self.speed_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #666666;
                margin: 2px 0;
            }
            QSlider::handle:horizontal {
                background: #2196F3;
                border: 1px solid #2196F3;
                width: 18px;
                margin: -2px 0;
                border-radius: 3px;
            }
        """)
        self.speed_slider.valueChanged.connect(self.speed_changed)
        slider_layout.addWidget(self.speed_slider)
        
        self.speed_input = QLineEdit()
        self.speed_input.setFixedWidth(80)
        self.speed_input.setText("1.0")
        self.speed_input.setReadOnly(True)
        slider_layout.addWidget(self.speed_input)
        
        speed_layout.addLayout(slider_layout)
        
        # Speed buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.speed_confirm_btn = QPushButton("Confirm")
        self.speed_cancel_btn = QPushButton("Cancel")
        self.speed_confirm_btn.setFixedHeight(30)
        self.speed_cancel_btn.setFixedHeight(30)
        
        self.speed_confirm_btn.clicked.connect(self.confirm_speed)
        self.speed_cancel_btn.clicked.connect(self.cancel_speed)
        
        button_layout.addWidget(self.speed_confirm_btn)
        button_layout.addWidget(self.speed_cancel_btn)
        speed_layout.addLayout(button_layout)
        
        self.speed_control.hide()
        default_layout.addWidget(self.speed_control)
        
        # Save control area
        save_controls = QHBoxLayout()
        
        # Save format selection
        self.save_format = QComboBox()
        self.save_format.addItems([".mp4", ".avi", ".jpg", ".png", "*.jpg", "*.png"])
        self.save_format.setFixedHeight(40)
        self.save_format.setEnabled(False)  # Initially disabled
        save_controls.addWidget(self.save_format)
        
        # Save button
        self.save_button = QPushButton("Save")
        self.save_button.setFixedHeight(40)
        self.save_button.clicked.connect(self.save_current)
        self.save_button.setEnabled(False)  # Initially disabled
        save_controls.addWidget(self.save_button)
        
        default_layout.addLayout(save_controls)
        
        # Create Segment interface
        self.segment_widget = SegmentWidget(self)
        
        # Add interfaces to stacked widget
        self.stacked_widget.addWidget(default_widget)
        self.stacked_widget.addWidget(self.segment_widget)
        
        main_layout.addWidget(self.stacked_widget)
        
        # Enable drag and drop
        self.setAcceptDrops(True)
        
    def create_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # File open button
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_file_dialog)
        toolbar.addAction(open_action)
        
        # Segment function
        segment_action = QAction("Segment", self)
        segment_action.triggered.connect(self.toggle_segment_mode)
        toolbar.addAction(segment_action)
        
        # Clip function
        clip_action = QAction("Clip", self)
        clip_action.triggered.connect(self.start_clip_mode)
        toolbar.addAction(clip_action)
        
        # Resize function
        resize_action = QAction("Resize", self)
        resize_action.triggered.connect(self.show_resize_dialog)
        toolbar.addAction(resize_action)
        
        # Speed function
        speed_action = QAction("Speed", self)
        speed_action.triggered.connect(self.show_speed_dialog)
        toolbar.addAction(speed_action)
        
    def toggle_segment_mode(self):
        if not self.cap:
            QMessageBox.warning(self, "Warning", "Please load a video first!")
            return
            
        self.segment_widget.set_range(self.total_frames)
        self.stacked_widget.setCurrentIndex(1)
        self.pause_video()
        
    def update_preview_frame(self, frame_number):
        if self.cap is not None:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = self.cap.read()
            if ret:
                self.update_display(frame)
                
    def confirm_segment(self, begin, end):
        self.segment_begin = begin
        self.segment_end = end
        self.stacked_widget.setCurrentIndex(0)
        self.time_slider.setRange(self.segment_begin, self.segment_end)
        self.time_slider.setValue(self.segment_begin)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.segment_begin)
        self.play_video()
        
    def cancel_segment(self):
        self.stacked_widget.setCurrentIndex(0)
        self.time_slider.setRange(0, self.total_frames)
        self.time_slider.setValue(self.current_frame_number)
        self.segment_begin = 0
        self.segment_end = self.total_frames
        
    def slider_pressed(self):
        self.timer.stop()
        
    def slider_released(self):
        if self.is_playing:
            self.timer.start(int(1000/self.fps))
            
    def slider_value_changed(self, value):
        if self.cap is not None:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, value)
            ret, frame = self.cap.read()
            if ret:
                self.current_frame = frame
                self.current_frame_number = value
                self.update_display(frame)
                
    def time_slider_clicked(self, value):
        if self.time_slider.orientation() == Qt.Horizontal:
            # Set new position
            self.time_slider.setValue(value)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, value)
            ret, frame = self.cap.read()
            if ret:
                self.current_frame = frame
                self.current_frame_number = value
                self.update_display(frame)
                
    def save_current(self):
        if not self.cap or self.current_frame is None:
            QMessageBox.warning(self, "Warning", "Please load a video first!")
            return
            
        if self.is_processing:
            QMessageBox.warning(self, "Warning", "A video processing task is in progress, please wait!")
            return
            
        try:
            self.is_processing = True
            format = self.save_format.currentText()
            
            # Use os.path.join for cross-platform path construction
            base_path = os.path.join(os.path.dirname(self.input_file), 
                                    os.path.splitext(os.path.basename(self.input_file))[0] + '_frames')
            os.makedirs(base_path, exist_ok=True)
            
            if format == '.jpg' or format == '.png':
                # Save single frame
                save_path = os.path.join(base_path, f"{self.current_frame_number:06d}{format}")
                # Use imencode instead of imwrite
                _, buffer = cv2.imencode(format, self.current_frame)
                with open(save_path, 'wb') as f:
                    f.write(buffer)
                print(f"Saved to {save_path}")
                QMessageBox.information(self, "Success", f"Saved to {save_path}")
            elif format == '*.jpg' or format == '*.png':
                # Save all frames in the segment
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.segment_begin)
                frame_count = self.segment_begin
                total_frames = self.segment_end - self.segment_begin
                
                while frame_count < self.segment_end:
                    ret, frame = self.cap.read()
                    if not ret:
                        break
                        
                    # Apply crop if exists
                    if self.clip_rect:
                        x1, y1, x2, y2 = self.clip_rect
                        frame = frame[y1:y2, x1:x2]
                        
                    # Apply resize if exists
                    if self.resize_dimensions:
                        width, height = self.resize_dimensions
                        frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_LINEAR)
                    
                    # Save frame using imencode
                    save_path = os.path.join(base_path, f"{frame_count:06d}{format[1:]}")
                    _, buffer = cv2.imencode(format[1:], frame)
                    with open(save_path, 'wb') as f:
                        f.write(buffer)
                    frame_count += 1
                    
                    # Update progress
                    progress = (frame_count - self.segment_begin) / total_frames * 100
                    print(f"\rSaving frames: {progress:.1f}%", end="")
                    
                print("\nDone!")
                print(f"Saved to {base_path}")
                QMessageBox.information(self, "Success", f"Saved to {base_path}")
            else:
                save_path = os.path.join(base_path, f"{self.segment_begin:06d}-{self.segment_end:06d}{format}")
                # Use absolute path
                abs_save_path = os.path.abspath(save_path)
                os.makedirs(os.path.dirname(abs_save_path), exist_ok=True)
                self.save_video_segment(abs_save_path)
                print(f"Saved to {save_path}")
                QMessageBox.information(self, "Success", f"Saved to {save_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Save failed: {str(e)}")
        finally:
            self.is_processing = False
            
    def save_video_segment(self, save_path):
        try:
            # Get video properties
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Apply crop if exists
            if self.clip_rect:
                x1, y1, x2, y2 = self.clip_rect
                width = x2 - x1
                height = y2 - y1
                
            # Apply resize if exists
            if self.resize_dimensions:
                width, height = self.resize_dimensions
            
            # Choose codec based on platform
            if sys.platform == 'darwin':  # macOS
                fourcc = cv2.VideoWriter_fourcc(*'avc1')  # H.264 codec
            elif sys.platform == 'linux':  # Linux
                fourcc = cv2.VideoWriter_fourcc(*'XVID')  # XVID codec
            else:  # Windows
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            
            # Create video writer
            out = cv2.VideoWriter(save_path, fourcc, self.fps, (width, height))
            
            if not out.isOpened():
                raise Exception("Failed to create output video file")
            
            # Set start position
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.segment_begin)
            
            # Write frames
            for _ in range(self.segment_begin, self.segment_end):
                ret, frame = self.cap.read()
                if ret:
                    # Apply crop if exists
                    if self.clip_rect:
                        x1, y1, x2, y2 = self.clip_rect
                        frame = frame[y1:y2, x1:x2]
                        
                    # Apply resize if exists
                    if self.resize_dimensions:
                        width, height = self.resize_dimensions
                        frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_LINEAR)
                        
                    out.write(frame)
                else:
                    break
                    
            out.release()
        except Exception as e:
            if out and out.isOpened():
                out.release()
            raise e
            
    def update_display(self, frame):
        if frame is None:
            return
            
        # Apply crop
        if self.clip_rect:
            x1, y1, x2, y2 = self.clip_rect
            frame = frame[y1:y2, x1:x2]
            
        # Apply resize
        if self.resize_dimensions:
            width, height = self.resize_dimensions
            frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_LINEAR)
            
        # Convert color space from BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        
        # Convert to QImage and display
        qt_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(qt_image).scaled(
            self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            
        # Update time label
        current_time = self.current_frame_number / self.fps
        total_time = self.segment_end / self.fps
        self.time_label.setText(f"{int(current_time//60):02d}:{int(current_time%60):02d} / "
                              f"{int(total_time//60):02d}:{int(total_time%60):02d}")
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
            self.video_label.setStyleSheet(self.video_label.styleSheet() + """
                QLabel {
                    border: 2px dashed #4CAF50;
                    background-color: rgba(76, 175, 80, 0.1);
                }
            """)
        else:
            event.ignore()
            
    def dragLeaveEvent(self, event):
        self.video_label.setStyleSheet(self.video_label.styleSheet().replace(
            "border: 2px dashed #4CAF50; background-color: rgba(76, 175, 80, 0.1);",
            "border: 2px dashed #666;"
        ))
            
    def dropEvent(self, event: QDropEvent):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files:
            self.load_video(files[0])
        self.video_label.setStyleSheet(self.video_label.styleSheet().replace(
            "border: 2px dashed #4CAF50; background-color: rgba(76, 175, 80, 0.1);",
            "border: 2px dashed #666;"
        ))
            
    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Video File",
            self.last_directory,
            "Video Files (*.mp4 *.avi *.mov);;All Files (*.*)"
        )
        if file_path:
            self.load_video(file_path)
            
    def load_video(self, file_path):
        if self.is_processing:
            QMessageBox.warning(self, "Warning", "A video processing task is in progress, please wait!")
            return
            
        if not os.path.exists(file_path):
            QMessageBox.critical(self, "Error", "File does not exist!")
            return
            
        if not file_path.lower().endswith(('.mp4', '.avi', '.mov')):
            QMessageBox.warning(self, "Warning", "Unsupported file format!")
            return
            
        try:
            if self.cap is not None:
                self.cap.release()
                
            self.cap = cv2.VideoCapture(file_path)
            if not self.cap.isOpened():
                raise Exception("Failed to open video file")
                
            self.input_file = file_path
            self.original_fps = self.cap.get(cv2.CAP_PROP_FPS)
            self.fps = self.original_fps
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.time_slider.setMaximum(self.total_frames - 1)
            self.last_directory = os.path.dirname(file_path)
            
            # Enable controls
            self.play_button.setEnabled(True)
            self.time_slider.setEnabled(True)
            self.save_format.setEnabled(True)
            self.save_button.setEnabled(True)
            
            # Clear hint text
            self.video_label.setText("")
            
            # Reset segment mode
            self.segment_begin = 0
            self.segment_end = self.total_frames
            self.segment_widget.set_range(self.total_frames)
            
            # Reset speed
            self.playback_speed = 1.0
            self.fps = self.original_fps
            
            self.play_video()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load video: {str(e)}")
            if self.cap is not None:
                self.cap.release()
                self.cap = None
            # Disable controls on error
            self.play_button.setEnabled(False)
            self.time_slider.setEnabled(False)
            self.save_format.setEnabled(False)
            self.save_button.setEnabled(False)
        
    def play_video(self):
        self.is_playing = True
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        self.timer.start(int(1000/self.fps))
        
    def pause_video(self):
        self.is_playing = False
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.timer.stop()
        
    def toggle_play(self):
        if self.is_playing:
            self.pause_video()
        else:
            self.play_video()
            
    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            self.current_frame = frame
            self.current_frame_number = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            self.time_slider.setValue(self.current_frame_number)
            
            # Check if reached segment end
            if self.current_frame_number >= self.segment_end:
                self.pause_video()
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.segment_begin)
                self.current_frame_number = self.segment_begin
                self.time_slider.setValue(self.segment_begin)
            
            self.update_display(frame)
        else:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.segment_begin)
                
    def set_position(self, position):
        if self.cap is not None:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, position)
            
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.toggle_play()
            
    def closeEvent(self, event):
        if self.cap is not None:
            self.cap.release()
            # Disable controls when closing video
            self.play_button.setEnabled(False)
            self.time_slider.setEnabled(False)
            self.save_format.setEnabled(False)
            self.save_button.setEnabled(False)

    def start_clip_mode(self):
        if not self.cap:
            QMessageBox.warning(self, "Warning", "Please load a video first!")
            return
            
        # Create clip widget if not exists
        if self.clip_widget is None:
            self.clip_widget = ClipWidget(self)
            
        self.clip_widget.set_frame(self.current_frame)
        self.clip_widget.show()
        self.pause_video()
        
    def confirm_clip(self, x1, y1, x2, y2):
        self.clip_rect = (x1, y1, x2, y2)
        if self.clip_widget:
            self.clip_widget.close()
        self.play_video()
        
    def cancel_clip(self):
        if self.clip_widget:
            self.clip_widget.close()
        self.play_video()
        
    def show_resize_dialog(self):
        if not self.cap:
            QMessageBox.warning(self, "Warning", "Please load a video first!")
            return
            
        # Create resize widget if not exists
        if self.resize_widget is None:
            self.resize_widget = ResizeWidget(self)
            
        # Set dimensions - use last resize dimensions if available, otherwise use current frame dimensions
        if self.last_resize_dimensions is not None:
            self.resize_widget.set_current_dimensions(*self.last_resize_dimensions)
        elif self.current_frame is not None:
            h, w = self.current_frame.shape[:2]
            self.resize_widget.set_current_dimensions(w, h)
            
        self.resize_widget.show()
        self.pause_video()
        
    def confirm_resize(self, width, height):
        self.resize_dimensions = (width, height)
        self.last_resize_dimensions = (width, height)  # Save the dimensions
        if self.resize_widget:
            self.resize_widget.close()
        self.play_video()
        
    def cancel_resize(self):
        if self.resize_widget:
            self.resize_widget.close()
        self.play_video()
        
    def show_speed_dialog(self):
        if not self.cap:
            QMessageBox.warning(self, "Warning", "Please load a video first!")
            return
            
        # Hide save controls and show speed control
        self.save_format.hide()
        self.save_button.hide()
        self.speed_control.show()
        self.pause_video()
        
    def speed_changed(self, value):
        # Convert linear slider value (0-100) to logarithmic speed (0.1-10.0)
        # Using the formula: speed = 0.1 * (10^(value/50))
        speed = 0.1 * (10 ** (value / 50))
        self.speed_input.setText(f"{speed:.1f}")
        
    def confirm_speed(self):
        speed = float(self.speed_input.text())
        self.playback_speed = speed
        self.fps = self.original_fps * speed
        self.speed_control.hide()
        self.save_format.show()
        self.save_button.show()
        self.play_video()
        
    def cancel_speed(self):
        self.speed_control.hide()
        self.save_format.show()
        self.save_button.show()
        self.play_video()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec_()) 