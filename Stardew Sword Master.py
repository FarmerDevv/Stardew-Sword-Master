import sys
import json
import os
import shutil
import zipfile
import re
from PIL import Image
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QSpinBox,
    QTextEdit, QFileDialog, QDoubleSpinBox, QCheckBox, QHBoxLayout, QVBoxLayout,
    QFormLayout, QScrollArea, QMessageBox, QTabWidget, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication, QPixmap

class StardewWeaponEditor(QWidget):
    def __init__(self):
        super().__init__()

        screen = QGuiApplication.primaryScreen()
        screen_size = screen.size()
        width = int(screen_size.width() * 0.9)
        height = int(screen_size.height() * 0.9)

        self.setWindowTitle("Stardew Valley Sword Master")
        self.resize(width, height)
        self.setMinimumSize(800, 600)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)

        self.image_path = ""
        self.library_file = "mod_library.json"

        main_layout = QHBoxLayout()

        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_content_tab(), "Content")
        self.tabs.addTab(self.create_manifest_tab(), "Manifest")
        self.tabs.addTab(self.create_preview_tab(), "Preview")
        self.tabs.addTab(self.create_my_library_tab(), "My Library")
        self.tabs.addTab(self.create_about_tab(), "Hakkında")

        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

        self.tabs.currentChanged.connect(self.on_tab_changed)

    def create_content_tab(self):
        content_widget = QWidget()
        layout = QVBoxLayout()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QFormLayout()

        self.weapon_id = QLineEdit()
        self.weapon_id.setPlaceholderText("Örn: samuray_bıçağı (boş bırakma!)")
        scroll_layout.addRow(QLabel("Silah ID:"), self.weapon_id)

        self.weapon_name = QLineEdit()
        self.weapon_name.setPlaceholderText("Silahın oyundaki ismi")
        scroll_layout.addRow(QLabel("İsim:"), self.weapon_name)

        self.weapon_desc = QLineEdit()
        self.weapon_desc.setPlaceholderText("Kısa açıklama")
        scroll_layout.addRow(QLabel("Açıklama:"), self.weapon_desc)

        self.min_damage = QSpinBox()
        self.min_damage.setMaximum(9999)
        self.min_damage.setValue(1)
        self.min_damage.setToolTip("Minimum hasar değeri")
        scroll_layout.addRow(QLabel("Min Damage:"), self.min_damage)

        self.max_damage = QSpinBox()
        self.max_damage.setMaximum(9999)
        self.max_damage.setValue(1)
        self.max_damage.setToolTip("Maksimum hasar değeri")
        scroll_layout.addRow(QLabel("Max Damage:"), self.max_damage)

        self.knockback = QSpinBox()
        self.knockback.setMaximum(9999)
        self.knockback.setValue(1)
        self.knockback.setToolTip("Darbe kuvveti")
        scroll_layout.addRow(QLabel("Knockback:"), self.knockback)

        self.speed = QSpinBox()
        self.speed.setMaximum(9999)
        self.speed.setValue(1)
        self.speed.setToolTip("Silah hızı")
        scroll_layout.addRow(QLabel("Speed:"), self.speed)

        self.precision = QSpinBox()
        self.precision.setMaximum(9999)
        self.precision.setValue(1)
        self.precision.setToolTip("Hassasiyet")
        scroll_layout.addRow(QLabel("Precision:"), self.precision)

        self.defense = QSpinBox()
        self.defense.setMaximum(9999)
        self.defense.setValue(0)
        self.defense.setToolTip("Savunma değeri")
        scroll_layout.addRow(QLabel("Defense:"), self.defense)

        self.crit_chance = QDoubleSpinBox()
        self.crit_chance.setRange(0, 1)
        self.crit_chance.setSingleStep(0.01)
        self.crit_chance.setValue(0.01)
        self.crit_chance.setToolTip("Kritik vuruş şansı (0-1 arası)")
        scroll_layout.addRow(QLabel("Crit Chance:"), self.crit_chance)

        self.crit_multiplier = QSpinBox()
        self.crit_multiplier.setMaximum(9999)
        self.crit_multiplier.setValue(1)
        self.crit_multiplier.setToolTip("Kritik hasar çarpanı")
        scroll_layout.addRow(QLabel("Crit Multiplier:"), self.crit_multiplier)

        self.area_of_effect = QSpinBox()
        self.area_of_effect.setMaximum(9999)
        self.area_of_effect.setValue(0)
        self.area_of_effect.setToolTip("Etki alanı")
        scroll_layout.addRow(QLabel("Area Of Effect:"), self.area_of_effect)

        self.mine_level = QSpinBox()
        self.mine_level.setMaximum(9999)
        self.mine_level.setValue(0)
        self.mine_level.setToolTip("Madencilik seviyesi")
        scroll_layout.addRow(QLabel("Mine Level:"), self.mine_level)

        self.projectiles_null = QCheckBox("Projectiles: null")
        scroll_layout.addRow(self.projectiles_null)

        self.custom_fields_null = QCheckBox("CustomFields: null")
        scroll_layout.addRow(self.custom_fields_null)

        self.texture_path = QLineEdit()
        self.texture_path.setPlaceholderText("Örn: Assets/gun.png")
        scroll_layout.addRow(QLabel("Texture (örnek: Assets/gun.png):"), self.texture_path)

        self.image_button = QPushButton("Resim Seç")
        self.image_button.clicked.connect(self.select_image)
        scroll_layout.addRow(self.image_button)

        self.shop_id = QLineEdit()
        self.shop_id.setPlaceholderText("Örn: AdventureShop")
        scroll_layout.addRow(QLabel("Shop ID:"), self.shop_id)

        self.shop_price = QSpinBox()
        self.shop_price.setMaximum(999999)
        self.shop_price.setValue(100)
        self.shop_price.setToolTip("Silahın mağaza fiyatı")
        scroll_layout.addRow(QLabel("Fiyat:"), self.shop_price)

        self.shop_condition = QLineEdit()
        self.shop_condition.setPlaceholderText("Örn: DAY_OF_WEEK Monday")
        scroll_layout.addRow(QLabel("Koşul (örn: DAY_OF_WEEK Monday):"), self.shop_condition)

        self.generate_button = QPushButton("🔄 Modu Oluştur")
        self.generate_button.clicked.connect(self.generate_mod)
        scroll_layout.addRow(self.generate_button)

        scroll_content.setLayout(scroll_layout)
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        content_widget.setLayout(layout)
        return content_widget

    def create_manifest_tab(self):
        manifest_widget = QWidget()
        layout = QFormLayout()

        self.manifest_name = QLineEdit()
        self.manifest_name.setPlaceholderText("Modunuzun adı")
        layout.addRow(QLabel("Mod Adı:"), self.manifest_name)

        self.manifest_author = QLineEdit()
        self.manifest_author.setPlaceholderText("Yazar ismi")
        layout.addRow(QLabel("Yazar:"), self.manifest_author)

        self.manifest_version = QLineEdit()
        self.manifest_version.setText("1.0.0")
        layout.addRow(QLabel("Versiyon:"), self.manifest_version)

        self.manifest_description = QLineEdit()
        self.manifest_description.setPlaceholderText("Kısa açıklama")
        layout.addRow(QLabel("Açıklama:"), self.manifest_description)

        self.manifest_uid = QLineEdit()
        self.manifest_uid.setPlaceholderText("Örn: FarmerDev.MyMod")
        layout.addRow(QLabel("Unique ID:"), self.manifest_uid)

        self.manifest_min_api = QLineEdit()
        self.manifest_min_api.setText("3.0.0")
        layout.addRow(QLabel("Minimum API Sürümü:"), self.manifest_min_api)

        self.manifest_content_for = QLineEdit()
        self.manifest_content_for.setText("Pathoschild.ContentPatcher")
        layout.addRow(QLabel("ContentPackFor UID:"), self.manifest_content_for)

        manifest_widget.setLayout(layout)
        return manifest_widget

    def create_preview_tab(self):
        preview_widget = QWidget()
        layout = QHBoxLayout()

        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setStyleSheet("font-family: Consolas, monospace; font-size: 12px;")
        self.preview_text.setMinimumWidth(400)

        self.preview_image = QLabel()
        self.preview_image.setAlignment(Qt.AlignCenter)
        self.preview_image.setFixedSize(300, 300)
        self.preview_image.setStyleSheet("border: 1px solid #888; background-color: #222;")

        layout.addWidget(self.preview_text)
        layout.addWidget(self.preview_image)

        preview_widget.setLayout(layout)
        return preview_widget

    def create_my_library_tab(self):
        library_widget = QWidget()
        layout = QVBoxLayout()

        library_label = QLabel("<b>Oluşturduğunuz Modlar:</b>")
        library_label.setStyleSheet("font-size: 14px; color: #ff9900; padding: 10px;")
        layout.addWidget(library_label)

        self.library_list = QListWidget()
        self.library_list.setStyleSheet("""
            QListWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #555;
                font-size: 12px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #444;
            }
            QListWidget::item:selected {
                background-color: #ff9900;
                color: #000000;
            }
            QListWidget::item:hover {
                background-color: #404040;
            }
        """)
        layout.addWidget(self.library_list)

        button_layout = QHBoxLayout()

        refresh_button = QPushButton("🔄 Yenile")
        refresh_button.clicked.connect(self.load_library)
        refresh_button.setStyleSheet("padding: 8px; font-size: 12px;")
        button_layout.addWidget(refresh_button)

        clear_button = QPushButton("🗑️ Temizle")
        clear_button.clicked.connect(self.clear_library)
        clear_button.setStyleSheet("padding: 8px; font-size: 12px;")
        button_layout.addWidget(clear_button)

        layout.addLayout(button_layout)

        library_widget.setLayout(layout)
        return library_widget

    def create_about_tab(self):
        about_widget = QWidget()
        layout = QVBoxLayout()

        about_text = QLabel(
            "<b>"
            "Merhaba dostum, ben FarmerDev!\n\n"
            "Stardew Valley benim için bir tutkudan fazlası, adeta bir yaşam tarzı.\n"
            "Bu eşsiz oyunu desteklemek için <i>çok kolay bir kılıç modu yapım aracı</i> geliştirdim.\n\n"
            "Bu aracı kullanarak istediğin gibi modlar üretebilirsin. Unutma: tüm modlar senin eserindir.\n\n"
            "Tek ricam; Stardew Valley'i sevin, sevdirin. Bana bu yeter.\n\n"
            "Bol modlu, yaratıcı günler!"
            "</b>"
        )
        about_text.setWordWrap(True)
        about_text.setAlignment(Qt.AlignTop)
        about_text.setStyleSheet("font-size: 13px; padding: 10px; color: #ff9900;")

        layout.addWidget(about_text)
        about_widget.setLayout(layout)
        return about_widget

    def on_tab_changed(self, index):
        if self.tabs.tabText(index) == "Preview":
            self.update_preview()
        elif self.tabs.tabText(index) == "My Library":
            self.load_library()

    def update_preview(self):
        lines = [
            f"ID: {self.weapon_id.text()}",
            f"İsim: {self.weapon_name.text()}",
            f"Açıklama: {self.weapon_desc.text()}",
            f"Min Damage: {self.min_damage.value()}",
            f"Max Damage: {self.max_damage.value()}",
            f"Knockback: {self.knockback.value()}",
            f"Speed: {self.speed.value()}",
            f"Precision: {self.precision.value()}",
            f"Defense: {self.defense.value()}",
            f"Crit Chance: {self.crit_chance.value()}",
            f"Crit Multiplier: {self.crit_multiplier.value()}",
            f"Area Of Effect: {self.area_of_effect.value()}",
            f"Mine Level: {self.mine_level.value()}",
            f"Projectiles Null: {self.projectiles_null.isChecked()}",
            f"CustomFields Null: {self.custom_fields_null.isChecked()}",
            f"Shop ID: {self.shop_id.text()}",
            f"Shop Price: {self.shop_price.value()}",
            f"Shop Condition: {self.shop_condition.text()}"
        ]

        self.preview_text.setText("\n".join(lines))

        if self.image_path and os.path.exists(self.image_path):
            pixmap = QPixmap(self.image_path)
            scaled = pixmap.scaled(self.preview_image.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.preview_image.setPixmap(scaled)
        else:
            self.preview_image.clear()
            self.preview_image.setText("Resim seçilmedi")

    def load_library(self):
        """Kütüphaneyi yükle ve listeyi güncelle"""
        self.library_list.clear()

        try:
            if os.path.exists(self.library_file):
                with open(self.library_file, 'r', encoding='utf-8') as f:
                    library_data = json.load(f)

                if library_data.get('mods'):
                    for mod in library_data['mods']:
                        mod_name = mod.get('name', 'Bilinmeyen Mod')
                        date_created = mod.get('date_created', 'Tarih bilinmiyor')

                        item = QListWidgetItem(f"📦 {mod_name}\n📅 {date_created}")
                        self.library_list.addItem(item)
                else:
                    item = QListWidgetItem("📋 Henüz hiç mod oluşturmadınız.")
                    self.library_list.addItem(item)
            else:
                item = QListWidgetItem("📋 Henüz hiç mod oluşturmadınız.")
                self.library_list.addItem(item)

        except Exception as e:
            item = QListWidgetItem(f"❌ Kütüphane yüklenirken hata: {str(e)}")
            self.library_list.addItem(item)

    def save_to_library(self, mod_name):
        """Oluşturulan modu kütüphaneye kaydet"""
        try:
            library_data = {'mods': []}

            if os.path.exists(self.library_file):
                with open(self.library_file, 'r', encoding='utf-8') as f:
                    library_data = json.load(f)

            # Yeni mod bilgilerini ekle
            from datetime import datetime
            new_mod = {
                'name': mod_name,
                'date_created': datetime.now().strftime("%d.%m.%Y %H:%M"),
                'weapon_id': self.weapon_id.text(),
                'author': self.manifest_author.text()
            }

            library_data['mods'].append(new_mod)

            # Dosyaya kaydet
            with open(self.library_file, 'w', encoding='utf-8') as f:
                json.dump(library_data, f, indent=4, ensure_ascii=False)

        except Exception as e:
            print(f"Kütüphaneye kaydetme hatası: {str(e)}")

    def clear_library(self):
        """Kütüphaneyi temizle"""
        reply = QMessageBox.question(
            self,
            "Kütüphaneyi Temizle",
            "Tüm mod geçmişinizi silmek istediğinizden emin misiniz?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                if os.path.exists(self.library_file):
                    os.remove(self.library_file)
                self.load_library()
                QMessageBox.information(self, "Başarılı", "Kütüphane temizlendi.")
            except Exception as e:
                QMessageBox.warning(self, "Hata", f"Kütüphane temizlenirken hata: {str(e)}")

    def validate_characters(self, text, field_name):
        """Geçersiz karakterleri kontrol et"""
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '/', '\\']
        for char in invalid_chars:
            if char in text:
                return False, f"{field_name} geçersiz karakter içeriyor: {char}"
        return True, ""

    def validate_image(self, image_path):
        """Resim formatı ve boyutunu kontrol et"""
        try:
            if not os.path.exists(image_path):
                return False, "Resim dosyası bulunamadı!"

            # Dosya uzantısı kontrolü
            valid_extensions = ['.png', '.jpg', '.jpeg']
            file_ext = os.path.splitext(image_path)[1].lower()
            if file_ext not in valid_extensions:
                return False, f"Geçersiz resim formatı! Sadece PNG, JPG, JPEG destekleniyor."

            # Resim boyutu kontrolü
            with Image.open(image_path) as img:
                width, height = img.size
                if width > 16 or height > 16:
                    return False, f"Resim çok büyük! Maksimum 16x16 piksel olmalı. Mevcut: {width}x{height}"
                if width < 16 or height < 16:
                    return False, f"Resim çok küçük! Minimum 16x16 piksel olmalı. Mevcut: {width}x{height}"

            return True, ""
        except Exception as e:
            return False, f"Resim doğrulama hatası: {str(e)}"

    def check_write_permissions(self, path):
        """Dosya yazma izinlerini kontrol et"""
        try:
            # Test dosyası oluştur
            test_file = os.path.join(path, "test_write_permission.tmp")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            return True, ""
        except Exception as e:
            return False, f"Yazma izni yok: {str(e)}"

    def select_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Resim Seç", "", "Görseller (*.png *.jpg *.jpeg)")
        if path:
            # Resim doğrulamasi
            is_valid, error_msg = self.validate_image(path)
            if not is_valid:
                QMessageBox.warning(self, "Geçersiz Resim", error_msg)
                return

            self.image_path = path
            self.texture_path.setText(f"Assets/{os.path.basename(path)}")

    def generate_mod(self):
        # Content Tab Validasyonu
        if not self.weapon_id.text().strip():
            QMessageBox.warning(self, "Hata", "Silah ID boş olamaz!")
            return

        # Geçersiz karakter kontrolü - Silah ID
        is_valid, error_msg = self.validate_characters(self.weapon_id.text().strip(), "Silah ID")
        if not is_valid:
            QMessageBox.warning(self, "Hata", error_msg)
            return

        if not self.weapon_name.text().strip():
            QMessageBox.warning(self, "Hata", "Silah ismi boş olamaz!")
            return

        # Geçersiz karakter kontrolü - Silah İsmi
        is_valid, error_msg = self.validate_characters(self.weapon_name.text().strip(), "Silah İsmi")
        if not is_valid:
            QMessageBox.warning(self, "Hata", error_msg)
            return

        if not self.weapon_desc.text().strip():
            QMessageBox.warning(self, "Hata", "Silah açıklaması boş olamaz!")
            return

        if not self.texture_path.text().strip():
            QMessageBox.warning(self, "Hata", "Texture path boş olamaz!")
            return

        if not self.image_path:
            QMessageBox.warning(self, "Hata", "Resim seçilmedi!")
            return

        # Resim doğrulama
        is_valid, error_msg = self.validate_image(self.image_path)
        if not is_valid:
            QMessageBox.warning(self, "Resim Hatası", error_msg)
            return

        if not self.shop_id.text().strip():
            QMessageBox.warning(self, "Hata", "Shop ID boş olamaz!")
            return

        # Geçersiz karakter kontrolü - Shop ID
        is_valid, error_msg = self.validate_characters(self.shop_id.text().strip(), "Shop ID")
        if not is_valid:
            QMessageBox.warning(self, "Hata", error_msg)
            return

        if not self.shop_condition.text().strip():
            QMessageBox.warning(self, "Hata", "Shop koşulu boş olamaz!")
            return

        # Manifest Tab Validasyonu
        if not self.manifest_name.text().strip():
            QMessageBox.warning(self, "Hata", "Mod adı boş olamaz!")
            return

        # Geçersiz karakter kontrolü - Mod Adı
        is_valid, error_msg = self.validate_characters(self.manifest_name.text().strip(), "Mod Adı")
        if not is_valid:
            QMessageBox.warning(self, "Hata", error_msg)
            return

        if not self.manifest_author.text().strip():
            QMessageBox.warning(self, "Hata", "Yazar ismi boş olamaz!")
            return

        # Geçersiz karakter kontrolü - Yazar
        is_valid, error_msg = self.validate_characters(self.manifest_author.text().strip(), "Yazar İsmi")
        if not is_valid:
            QMessageBox.warning(self, "Hata", error_msg)
            return

        if not self.manifest_version.text().strip():
            QMessageBox.warning(self, "Hata", "Versiyon boş olamaz!")
            return

        if not self.manifest_description.text().strip():
            QMessageBox.warning(self, "Hata", "Manifest açıklaması boş olamaz!")
            return

        if not self.manifest_uid.text().strip():
            QMessageBox.warning(self, "Hata", "Unique ID boş olamaz!")
            return

        # Geçersiz karakter kontrolü - Unique ID
        is_valid, error_msg = self.validate_characters(self.manifest_uid.text().strip(), "Unique ID")
        if not is_valid:
            QMessageBox.warning(self, "Hata", error_msg)
            return

        if not self.manifest_min_api.text().strip():
            QMessageBox.warning(self, "Hata", "Minimum API sürümü boş olamaz!")
            return

        if not self.manifest_content_for.text().strip():
            QMessageBox.warning(self, "Hata", "ContentPackFor UID boş olamaz!")
            return

        # Klasör seçimi
        save_base = QFileDialog.getExistingDirectory(self, "Modu Kaydet")
        if not save_base:
            return

        # Yazma izni kontrolü
        is_valid, error_msg = self.check_write_permissions(save_base)
        if not is_valid:
            QMessageBox.warning(self, "İzin Hatası", error_msg)
            return

        weapon_id = self.weapon_id.text().strip()
        texture_str = f"Assets/{os.path.basename(self.image_path)}" if self.image_path else ""

        weapon_entry = {
            "Name": self.weapon_name.text(),
            "DisplayName": self.weapon_name.text(),
            "Description": self.weapon_desc.text(),
            "MinDamage": self.min_damage.value(),
            "MaxDamage": self.max_damage.value(),
            "Knockback": self.knockback.value(),
            "Speed": self.speed.value(),
            "Precision": self.precision.value(),
            "Defense": self.defense.value(),
            "Type": 3,
            "MineBaseLevel": -1,
            "MineMinLevel": self.mine_level.value(),
            "AreaOfEffect": self.area_of_effect.value(),
            "CritChance": self.crit_chance.value(),
            "CritMultiplier": self.crit_multiplier.value(),
            "CanBeLostOnDeath": False,
            "Texture": texture_str,
            "SpriteIndex": 0,
            "Projectiles": None if self.projectiles_null.isChecked() else [],
            "CustomFields": None if self.custom_fields_null.isChecked() else {}
        }

        content_json = {
    "Format": "2.0.0",
    "Changes": [
        {
            "Action": "Load",
            "Target": "Assets/" + os.path.basename(self.image_path),
            "FromFile": texture_str
        },
        {
            "Action": "EditData",
            "Target": "Data/weapons",
            "Entries": {
                weapon_id: weapon_entry
            }
        },
        {
            "Action": "EditData",
            "Target": "Data/shops",
            "TargetField": ["AdventureShop", "Items"],
            "Entries": {
                self.shop_id.text(): {
                    "Id": weapon_id,
                    "ItemId": weapon_id,
                    "Price": self.shop_price.value(),
                    "Condition": self.shop_condition.text()
                }
            }
        }
    ]
}


        manifest_json = {
            "Name": self.manifest_name.text(),
            "Author": self.manifest_author.text(),
            "Version": self.manifest_version.text(),
            "Description": self.manifest_description.text(),
            "UniqueID": self.manifest_uid.text(),
            "MinimumApiVersion": self.manifest_min_api.text(),
            "ContentPackFor": {
                "UniqueID": self.manifest_content_for.text()
            }
        }

        try:
            mod_folder = os.path.join(save_base, self.manifest_name.text())
            os.makedirs(mod_folder, exist_ok=True)

            with open(os.path.join(mod_folder, "content.json"), "w", encoding="utf-8") as f:
                json.dump(content_json, f, indent=4)
            with open(os.path.join(mod_folder, "manifest.json"), "w", encoding="utf-8") as f:
                json.dump(manifest_json, f, indent=4)

            if self.image_path:
                assets_dir = os.path.join(mod_folder, "Assets")
                os.makedirs(assets_dir, exist_ok=True)
                shutil.copy(self.image_path, os.path.join(assets_dir, os.path.basename(self.image_path)))

            # ZIP dosyası oluştur
            zip_path = os.path.join(save_base, f"{self.manifest_name.text()}.zip")
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(mod_folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, mod_folder)
                        zipf.write(file_path, arcname)

            # Kütüphaneye kaydet
            self.save_to_library(self.manifest_name.text())

            QMessageBox.information(self, "Başarılı", f"Mod başarıyla oluşturuldu!\nKonum: {mod_folder}\nZIP: {zip_path}")

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Mod oluşturulurken hata: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StardewWeaponEditor()
    window.show()
    sys.exit(app.exec_())
