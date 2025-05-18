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
            # 计算点击位置对应的值
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
        layout.setSpacing(5)  # 减小布局间距
        layout.setContentsMargins(5, 5, 5, 5)  # 减小边距
        
        # 时间轴容器
        timeline_container = QWidget()
        timeline_layout = QVBoxLayout(timeline_container)
        timeline_layout.setSpacing(2)  # 减小时间轴布局间距
        
        # 开始帧时间轴
        begin_layout = QHBoxLayout()  # 改为水平布局
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
        
        # 结束帧时间轴
        end_layout = QHBoxLayout()  # 改为水平布局
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
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        self.confirm_btn = QPushButton("Confirm")
        self.cancel_btn = QPushButton("Cancel")
        self.confirm_btn.setFixedHeight(30)  # 减小按钮高度
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

class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Processing Tool")
        self.setGeometry(100, 100, 1280, 720)
        
        # 初始化变量
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
        
        # 创建UI
        self.init_ui()
        
        # 设置定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        
    def init_ui(self):
        # 创建工具栏
        self.create_toolbar()
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 视频显示区域
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
        self.video_label.setText("Drag and drop video file here\nor click to open file")
        self.video_label.setStyleSheet(self.video_label.styleSheet() + """
            QLabel {
                color: #666;
                font-size: 16px;
            }
        """)
        self.video_label.mousePressEvent = self.open_file_dialog
        main_layout.addWidget(self.video_label)
        
        # 创建堆叠部件
        self.stacked_widget = QStackedWidget()
        
        # 创建默认控制界面
        default_widget = QWidget()
        default_layout = QVBoxLayout(default_widget)
        
        # 播放控制区域
        play_controls = QHBoxLayout()
        
        # 播放/暂停按钮
        self.play_button = QPushButton()
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_button.clicked.connect(self.toggle_play)
        self.play_button.setEnabled(False)  # 初始禁用
        play_controls.addWidget(self.play_button)
        
        # 时间滑块
        self.time_slider = TimeSlider(Qt.Horizontal)
        self.time_slider.sliderPressed.connect(self.slider_pressed)
        self.time_slider.sliderReleased.connect(self.slider_released)
        self.time_slider.valueChanged.connect(self.slider_value_changed)
        self.time_slider.clicked.connect(self.time_slider_clicked)
        self.time_slider.setEnabled(False)  # 初始禁用
        play_controls.addWidget(self.time_slider)
        
        # 时间标签
        self.time_label = QLabel("00:00 / 00:00")
        play_controls.addWidget(self.time_label)
        
        default_layout.addLayout(play_controls)
        
        # 保存控制区域
        save_controls = QHBoxLayout()
        
        # 保存格式选择
        self.save_format = QComboBox()
        self.save_format.addItems([".mp4", ".avi", ".mkv", ".jpg", ".png"])
        self.save_format.setFixedHeight(40)
        self.save_format.setEnabled(False)  # 初始禁用
        save_controls.addWidget(self.save_format)
        
        # 保存按钮
        self.save_button = QPushButton("Save")
        self.save_button.setFixedHeight(40)
        self.save_button.clicked.connect(self.save_current)
        self.save_button.setEnabled(False)  # 初始禁用
        save_controls.addWidget(self.save_button)
        
        default_layout.addLayout(save_controls)
        
        # 创建Segment界面
        self.segment_widget = SegmentWidget(self)
        
        # 添加界面到堆叠部件
        self.stacked_widget.addWidget(default_widget)
        self.stacked_widget.addWidget(self.segment_widget)
        
        main_layout.addWidget(self.stacked_widget)
        
        # 设置拖放
        self.setAcceptDrops(True)
        
    def create_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # 文件打开按钮
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_file_dialog)
        toolbar.addAction(open_action)
        
        # Segment 功能
        segment_action = QAction("Segment", self)
        segment_action.triggered.connect(self.toggle_segment_mode)
        toolbar.addAction(segment_action)
        
        # Clip 功能
        clip_action = QAction("Clip", self)
        clip_action.triggered.connect(self.start_clip_mode)
        toolbar.addAction(clip_action)
        
        # Resize 功能
        resize_action = QAction("Resize", self)
        resize_action.triggered.connect(self.show_resize_dialog)
        toolbar.addAction(resize_action)
        
        # Speed 功能
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
            # 设置新的位置
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
            base_path = os.path.splitext(self.input_file)[0] + '_frames'
            os.makedirs(base_path, exist_ok=True)
            
            if format in ['.jpg', '.png']:
                # Save single frame
                save_path = os.path.join(base_path, f"{self.current_frame_number:06d}{format}")
                # frame_rgb = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
                # 使用numpy保存图片，避免中文路径问题
                cv2.imencode(format, self.current_frame)[1].tofile(save_path)
            else:
                save_path = os.path.join(base_path, f"{self.segment_begin:06d}-{self.segment_end:06d}{format}")
                self.save_video_segment(save_path)
                
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
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(save_path, fourcc, self.fps, (width, height))
            
            if not out.isOpened():
                raise Exception("Failed to create output video file")
            
            # Set start position
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.segment_begin)
            
            # Write frames
            for _ in range(self.segment_begin, self.segment_end):
                ret, frame = self.cap.read()
                if ret:
                    out.write(frame)
                else:
                    break
                    
            out.release()
        except Exception as e:
            if out and out.isOpened():
                out.release()
            raise e
            
    def update_display(self, frame):
        # 转换颜色空间从BGR到RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        
        # 转换为QImage并显示
        qt_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(qt_image).scaled(
            self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            
        # 更新时间标签
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
            
    def open_file_dialog(self, event):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Video File",
            self.last_directory,
            "Video Files (*.mp4 *.avi *.mkv *.mov);;All Files (*.*)"
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
            
        if not file_path.lower().endswith(('.mp4', '.avi', '.mkv', '.mov')):
            QMessageBox.warning(self, "Warning", "Unsupported file format!")
            return
            
        try:
            if self.cap is not None:
                self.cap.release()
                
            self.cap = cv2.VideoCapture(file_path)
            if not self.cap.isOpened():
                raise Exception("Failed to open video file")
                
            self.input_file = file_path
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
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
            
            # 检查是否达到片段结束位置
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
        QMessageBox.information(self, "Info", "Clip mode will be implemented in the next step.")
        
    def show_resize_dialog(self):
        QMessageBox.information(self, "Info", "Resize dialog will be implemented in the next step.")
        
    def show_speed_dialog(self):
        QMessageBox.information(self, "Info", "Speed dialog will be implemented in the next step.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec_()) 