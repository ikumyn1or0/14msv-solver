import customtkinter as ctk
import pprint


class MinesweeperVariantsApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 画面の設定
        self.title("14 Minewsweeper Variants Solver/Helper App")
        self.geometry("900x600")

        # フィールドサイズの初期設定
        self.field_size_dict = {
            "5x5": 5, "6x6": 6,
            "7x7": 7, "8x8": 8}
        self.default_field_size = 8
        self.field_size = self.default_field_size

        # ルールの一覧
        self.field_rule_dict = {
            "V": "vanilla", "Q": "quad", "C": "connected", "T": "triplet",
            "O": "outside", "D": "dual", "S": "snake", "B": "balance",
            "T'": "triplet'", "D'": "battleship", "A": "anti-knight", "H": "horizontal",
            "CD": "connected-dual", "CQ": "connected-quad", "CT": "connected-triplet",
            "OQ": "outside-quad", "OT": "outside-triplet", "QT": "quad-triplet",
        }
        self.default_field_rule = "vanilla"

        self.cell_rule_dict = {
            "?": "hidden",
            "V": "vanilla", "M": "multiple", "L": "liar", "W": "wall",
            "N": "negation", "X": "cross", "P": "partition", "E": "eyesight",
            "X'": "mini cross", "K": "knight", "W'": "longest wall", "E'": "eyesight'",
            "LM": "liar-multiple", "MC": "multiple-cross", "MN": "multiple-negation",
            "NX": "negation-cross", "UW": "unary-wall",
        }
        self.default_cell_rule = "vanilla"

        # セルの設定
        self.init_cells_field()

        # フィールドの描画
        self.display_field()

        # 設定の描画
        self.display_setting()

    def field_size_dict_inversed(self, target_value):
        """self.field_size_dictのvalueからkeyを返す関数"""
        keys = [key for key, value in self.field_size_dict.items() if value == target_value]
        if len(keys) == 0:
            return None
        else:
            return keys[0]

    def field_rule_dict_inversed(self, target_value):
        """self.field_rule_dictのvalueからkeyを返す関数"""
        keys = [key for key, value in self.field_rule_dict.items() if value == target_value]
        if len(keys) == 0:
            return None
        else:
            return keys[0]

    def cell_rule_dict_inversed(self, target_value):
        """self.cell_rule_dictのvalueからkeyを返す関数"""
        keys = [key for key, value in self.cell_rule_dict.items() if value == target_value]
        if len(keys) == 0:
            return None
        else:
            return keys[0]

    def init_cells_field(self):
        """セルとフィールドを初期化する関数"""
        # フィールドの初期化
        self.field_rule = self.default_field_rule
        self.num_mine = 2 * self.field_size if self.field_size <= 6 else 3 * self.field_size
        self.num_mine_found = 0
        # セルの初期化
        self.cells = {}
        self.focused_cell_index = (-1, -1)
        for i in range(self.field_size):
            for j in range(self.field_size):
                self.cells[(i, j)] = {
                    "state": "close",
                    "cell_rule": self.default_cell_rule,
                    "numbers": [0,]
                }

    def display_field(self):
        """マインスイーパ部分の描画、self.cells["cell"]にセルを格納"""
        # フィールドの配置
        self.field_frame = ctk.CTkFrame(self)
        self.field_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        for i in range(self.field_size):
            for j in range(self.field_size):
                # セルの配置
                cell = ctk.CTkButton(
                    self.field_frame,
                    text="", fg_color="black",
                    width=60, height=60,
                    border_color="yellow", border_width=0,
                    hover=False,
                    command=lambda i=i, j=j: self.toggle_cell(i, j))
                cell.grid(
                    row=i, column=j,
                    padx=2, pady=2, sticky="nsew")
                # セルの格納
                self.cells[(i, j)]["cell"] = cell

        # セルのウェイトを設定
        for i in range(self.field_size):
            self.grid_columnconfigure(i, weight=1)
            self.grid_rowconfigure(i, weight=1)

    def toggle_cell(self, i, j):
        """セルを押した際の挙動を管理する関数"""
        # 押したときにcloseならばopenにする
        if self.cells[(i, j)]["state"] == "close":
            self.cells[(i, j)]["state"] = "open"
            text, fg_color = self.generate_cell_info_text_bgc(self.cells[(i, j)])
            self.cells[(i, j)]["cell"].configure(text=text, fg_color=fg_color)
            self.focused_cell_index = (i, j)
        # 押したときにopenならばbombにする
        elif self.cells[(i, j)]["state"] == "open":
            self.cells[(i, j)]["state"] = "bomb"
            text, fg_color = self.generate_cell_info_text_bgc(self.cells[(i, j)])
            self.cells[(i, j)]["cell"].configure(text=text, fg_color=fg_color)
            self.focused_cell_index = (-1, -1)
        # 押したときにbombならcloseにする
        else:
            self.cells[(i, j)]["state"] = "close"
            text, fg_color = self.generate_cell_info_text_bgc(self.cells[(i, j)])
            self.cells[(i, j)]["cell"].configure(text=text, fg_color=fg_color)
            self.focused_cell_index = (-1, -1)

        # セルを描画する
        for i_ in range(self.field_size):
            for j_ in range(self.field_size):
                if i_ == self.focused_cell_index[0] and j_ == self.focused_cell_index[1]:
                    self.cells[(i_, j_)]["cell"].configure(border_width=2)
                else:
                    self.cells[(i_, j_)]["cell"].configure(border_width=0)

        # 地雷の個数をカウント
        mine_count = 0
        for i_ in range(self.field_size):
            for j_ in range(self.field_size):
                if self.cells[(i_, j_)]["state"] == "bomb":
                    mine_count += 1
        self.num_mine_found = mine_count
        self.field_info_text.configure(text=self.generate_field_info_text())

        # セルのルールセレクタの状態を変更
        self.cell_rule_scope_checkbox.configure(state=self.enable_change_cell())
        self.cell_rule_selector.configure(state=self.enable_change_cell())
        self.set_cell_rule_selector_value()
        self.cell_number_entry.configure(state=self.enable_change_cell())
        self.cell_number_button.configure(state=self.enable_change_cell())

    def display_setting(self):
        """設定部分の画面を描画する関数"""
        # 設定の配置
        self.setting_frame = ctk.CTkFrame(self)
        self.setting_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.setting_frame.columnconfigure(0, weight=1)

        # フレームの配置
        self.field_size_frame = ctk.CTkFrame(self.setting_frame)
        self.field_size_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.field_size_frame.columnconfigure(0, weight=1)

        # テキストの配置
        self.change_field_size_text = ctk.CTkLabel(self.field_size_frame, text="Change Minesweeper Size")
        self.change_field_size_text.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

        # ドロップダウンメニューの配置
        self.field_size_selector = ctk.CTkComboBox(
            self.field_size_frame,
            values=list(self.field_size_dict.keys()),
            command=self.change_field_size)
        self.field_size_selector.set(self.field_size_dict_inversed(self.field_size))
        self.field_size_selector.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        # フィールドの配置
        self.field_rule_frame = ctk.CTkFrame(self.setting_frame)
        self.field_rule_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.field_rule_frame.columnconfigure(0, weight=1)

        # テキストの配置
        self.change_field_rule_text = ctk.CTkLabel(self.field_rule_frame, text="Change Field Rule")
        self.change_field_rule_text.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

        # ドロップダウンメニューの配置
        self.field_rule_selector = ctk.CTkComboBox(
            self.field_rule_frame,
            values=list(self.field_rule_dict.keys()),
            command=self.change_field_rule)
        self.field_rule_selector.set(self.field_rule_dict_inversed(self.field_rule))
        self.field_rule_selector.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        # フィールドの配置
        self.cell_rule_num_frame = ctk.CTkFrame(self.setting_frame)
        self.cell_rule_num_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.cell_rule_num_frame.columnconfigure(0, weight=1)

        # テキストの配置
        self.change_cell_rule_text = ctk.CTkLabel(self.cell_rule_num_frame, text="Change Cell Rule")
        self.change_cell_rule_text.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

        # チェックボックスの配置
        self.cell_rule_scope_checkbox = ctk.CTkCheckBox(
            self.cell_rule_num_frame,
            text="Change all cell")
        self.cell_rule_scope_checkbox.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        # ドロップダウンメニューの配置
        self.cell_rule_selector = ctk.CTkComboBox(
            self.cell_rule_num_frame,
            values=list(self.cell_rule_dict.keys()),
            state=self.enable_change_cell(),
            command=self.change_cell_rule)
        self.set_cell_rule_selector_value()
        self.cell_rule_selector.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")

        # テキストの配置
        self.change_cell_number_text = ctk.CTkLabel(
            self.cell_rule_num_frame,
            text="Change Cell Number\n(For multiple, separate them with comma)")
        self.change_cell_number_text.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")

        self.cell_number_entry = ctk.CTkEntry(
            self.cell_rule_num_frame,
            state=self.enable_change_cell())
        self.cell_number_entry.grid(row=4, column=0, padx=10, pady=5, sticky="nsew")

        self.cell_number_button = ctk.CTkButton(
            self.cell_rule_num_frame,
            text="confirm cell number",
            state=self.enable_change_cell(),
            command=self.change_cell_number)
        self.cell_number_button.grid(row=5, column=0, padx=10, pady=5)

        # テキストの配置
        self.field_info_text = ctk.CTkLabel(
            self.setting_frame,
            justify="left",
            text=self.generate_field_info_text())
        self.field_info_text.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

        # ボタンの配置
        self.solve_button = ctk.CTkButton(
            self.setting_frame,
            text="find safe cell",
            command=self.solve_field)
        self.solve_button.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")

    def change_field_size(self, key):
        """フィールドサイズが変更された際の挙動を管理する関数"""
        self.field_size = self.field_size_dict.get(key, self.default_field_size)

        self.init_cells_field()
        self.display_field()
        self.display_setting()

    def change_field_rule(self, key):
        """フィールドルールが変更された際の挙動を管理する関数"""
        self.field_rule = self.field_rule_dict.get(key, self.default_field_rule)
        self.field_info_text.configure(text=self.generate_field_info_text())

    def generate_field_info_text(self):
        """フィールドの情報(ルール・地雷数)を表示するためのテキストを生成する関数"""
        return f"field rule: {self.field_rule}\ntotal mine: {self.num_mine}\nfounded mine: {self.num_mine_found}"

    def enable_change_cell(self):
        """クリックされたセルが変更可能かを返す関数"""
        if 0 <= self.focused_cell_index[0] and self.focused_cell_index[0] < self.field_size and \
           0 <= self.focused_cell_index[1] and self.focused_cell_index[1] < self.field_size:
            return "normal"
        else:
            return "disabled"

    def set_cell_rule_selector_value(self):
        """セルルール選択用ドロップダウンメニューにテキストをセットする関数"""
        if self.enable_change_cell() == "normal":
            self.cell_rule_selector.set(self.cell_rule_dict_inversed(self.cells[self.focused_cell_index]["cell_rule"]))
        else:
            self.cell_rule_selector.set("")

    def generate_cell_info_text_bgc(self, cell):
        """セルの情報(ルール・数字)を表示するためのテキストを生成する関数"""
        state = cell["state"]
        cell_rule = cell["cell_rule"]
        cell_rule_text = self.cell_rule_dict_inversed(cell_rule)
        numbers = ",".join(map(str, cell["numbers"]))

        ret_text = ""
        ret_bgc = ""
        if state == "open":
            if cell_rule == "hidden":
                ret_text = cell_rule_text
                ret_bgc = "gray"
            else:
                ret_text = f"{cell_rule_text}\n{numbers}"
                ret_bgc = "blue"
        elif state == "bomb":
            ret_text = "BOMB"
            ret_bgc = "red"
        else:
            ret_text = ""
            ret_bgc = "black"
        return ret_text, ret_bgc

    def change_cell_rule(self, key):
        """セルルールが変更された際の挙動を管理する関数"""
        if self.enable_change_cell() == "normal" and\
           self.cells[self.focused_cell_index]["state"] == "open":
            if self.cell_rule_scope_checkbox.get() == 0:
                self.cells[self.focused_cell_index]["cell_rule"] = self.cell_rule_dict.get(key, self.default_cell_rule)
                text, fg_color = self.generate_cell_info_text_bgc(self.cells[self.focused_cell_index])
                self.cells[self.focused_cell_index]["cell"].configure(
                    text=text, fg_color=fg_color)
            else:
                for i in range(self.field_size):
                    for j in range(self.field_size):
                        self.cells[(i, j)]["cell_rule"] = self.cell_rule_dict.get(key, self.default_cell_rule)
                        text, fg_color = self.generate_cell_info_text_bgc(self.cells[(i, j)])
                        self.cells[(i, j)]["cell"].configure(
                            text=text, fg_color=fg_color)

    def change_cell_number(self):
        """セルの数字が変更された際の挙動を管理する関数"""
        cell_numbers = []
        for num in self.cell_number_entry.get().split(","):
            if num.strip().isdigit():
                cell_numbers.append(int(num))
        if self.enable_change_cell() == "normal" and\
           self.cells[self.focused_cell_index]["state"] == "open":
            self.cells[self.focused_cell_index]["numbers"] = cell_numbers
            text, fg_color = self.generate_cell_info_text_bgc(self.cells[self.focused_cell_index])
            self.cells[self.focused_cell_index]["cell"].configure(
                text=text, fg_color=fg_color)

    def solve_field(self):
        field_dict = self.field_to_dict()
        pprint.pprint(field_dict)

    def field_to_dict(self):
        field_dict = {}
        field_dict["field_size"] = self.field_size
        field_dict["num_mine"] = self.num_mine
        field_dict["num_mine_found"] = self.num_mine_found
        field_dict["field_rule"] = self.field_rule
        cell_list = []
        for i in range(self.field_size):
            for j in range(self.field_size):
                cell_dict = {}
                cell_dict["position"] = (i, j)
                cell_dict["state"] = self.cells[(i, j)]["state"]
                cell_dict["cell_rule"] = self.cells[(i, j)]["cell_rule"]
                cell_dict["numbers"] = self.cells[(i, j)]["numbers"]
                cell_list.append(cell_dict)
        field_dict["cells"] = cell_list
        return field_dict


if __name__ == "__main__":
    ctk.set_appearance_mode("Light")
    ctk.set_default_color_theme("blue")

    app = MinesweeperVariantsApp()
    app.mainloop()
