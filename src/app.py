import customtkinter as ctk
import json


class MinesweeperVariantsApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ウィンドウの設定
        self.title("14 Minewsweeper Variants Solver/Helper App")
        self.geometry("1000x500")

        # フィールドサイズ
        self.field_size_dict = {
            "5x5": 5, "6x6": 6,
            "7x7": 7, "8x8": 8}
        self.default_field_size = 8

        # デフォルトのルール
        self.default_rule = "vanilla"
        # フィールド全体のルール
        self.field_rule_dict = {
            "V": self.default_rule, "Q": "quad", "C": "connected", "T": "triplet",
            "O": "outside", "D": "dual", "S": "snake", "B": "balance",
            "T'": "triplet'", "D'": "battleship", "A": "anti-knight", "H": "horizontal",
            "CD": "connected-dual", "CQ": "connected-quad", "CT": "connected-triplet",
            "OQ": "outside-quad", "OT": "outside-triplet", "QT": "quad-triplet",
        }
        self.default_field_rule = self.default_rule

        # セル個別のルール
        self.cell_rule_dict = {
            "?": "hidden",
            "V": self.default_rule, "M": "multiple", "L": "liar", "W": "wall",
            "N": "negation", "X": "cross", "P": "partition", "E": "eyesight",
            "X'": "mini cross", "K": "knight", "W'": "longest wall", "E'": "eyesight'",
            "LM": "liar-multiple", "MC": "multiple-cross", "MN": "multiple-negation",
            "NX": "negation-cross", "UW": "unary-wall",
        }
        self.default_cell_rule = self.default_rule

        # セルの状態定義
        self.cell_states = ("close", "open", "bomb")
        self.closed_cell = self.cell_states[0]
        self.opened_cell = self.cell_states[1]
        self.bomb_cell = self.cell_states[2]
        self.default_cell_state = self.closed_cell

        # フィールド・セルの初期化
        self.init_field(field_size=self.default_field_size)
        self.init_cells()

        # フィールドの描画
        self.display_field()

        # 設定の描画
        self.display_setting()

    def field_size_dict_v2k(self, value):
        """self.field_size_dictのvalueからkeyを返す関数"""
        keys = [k for k, v in self.field_size_dict.items() if v == value]
        if len(keys) == 0:
            return self.field_size_dict_v2k(self.default_field_size)
        else:
            return keys[0]

    def field_rule_dict_v2k(self, value):
        """self.field_rule_dictのvalueからkeyを返す関数"""
        keys = [k for k, v in self.field_rule_dict.items() if v == value]
        if len(keys) == 0:
            return self.field_rule_dict_v2k(self.default_field_rule)
        else:
            return keys[0]

    def cell_rule_dict_v2k(self, value):
        """self.cell_rule_dictのvalueからkeyを返す関数"""
        keys = [k for k, v in self.cell_rule_dict.items() if v == value]
        if len(keys) == 0:
            return self.cell_rule_dict_v2k(self.default_cell_rule)
        else:
            return keys[0]

    def init_field(self, field_size=None, field_rule=None, mine_total=None, mine_found=None):
        """フィールドに関する値を初期化する関数"""
        if field_size is not None:
            self.field_size = field_size
        if field_rule is not None:
            self.field_rule = field_rule
        else:
            self.field_rule = self.default_field_rule
        if mine_total is not None:
            self.mine_total = mine_total
        else:
            if self.field_size <= 6:
                self.mine_total = 2 * self.field_size
            else:
                self.mine_total = 3 * self.field_size
        if mine_found is not None:
            self.mine_found = mine_found
        else:
            self.mine_found = 0

    def init_cell(self, pos, state=None, cell_rule=None, numbers=None):
        """セル単体を初期化する関数"""
        cell = {}
        if state is not None:
            cell["state"] = state
        else:
            cell["state"] = self.default_cell_state
        if cell_rule is not None:
            cell["cell_rule"] = cell_rule
        else:
            cell["cell_rule"] = self.default_cell_rule
        if numbers is not None:
            cell["numbers"] = numbers
        else:
            cell["numbers"] = [0,]
        self.cells[pos] = cell

    def init_cells(self):
        """セルを初期化する関数"""
        self.cells = {}
        for i in range(self.field_size):
            for j in range(self.field_size):
                self.init_cell(pos=(i, j))
        self.focused_cell_pos = (-1, -1)

    def init_cells_from_json(self, cells):
        """セルをリストから初期化する関数"""
        for cell in cells:
            self.init_cell(
                pos=tuple(cell["pos"]),
                state=cell["state"],
                cell_rule=cell["cell_rule"],
                numbers=cell["numbers"])
        self.focused_cell_pos = (-1, -1)

    def display_field(self):
        """マインスイーパ部分の描画、self.cells["cell"]にセルを格納"""
        # フィールドフレームの配置
        self.field_frame = ctk.CTkFrame(self)
        self.field_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # セルの配置
        for i in range(self.field_size):
            for j in range(self.field_size):
                pos = (i, j)
                text, fg_color, border_width = self.get_cell_text_fgc_bwidth(self.cells[pos], pos)
                cell = ctk.CTkButton(
                    self.field_frame,
                    text=text, fg_color=fg_color,
                    width=50, height=50,
                    border_color="yellow", border_width=border_width,
                    hover=False,
                    command=lambda pos=pos: self.toggle_cell(pos))
                cell.grid(
                    row=i, column=j,
                    padx=1, pady=1, sticky="nsew")
                # セルの格納
                self.cells[pos]["cell"] = cell

        # セルのウェイトを設定
        for i in range(self.field_size):
            self.grid_columnconfigure(i, weight=1)
            self.grid_rowconfigure(i, weight=1)

    def toggle_cell(self, pos):
        """セルを押した際の挙動を管理する関数"""
        # セルがcloseならopenにし、focusする
        if self.cells[pos]["state"] == self.closed_cell:
            self.cells[pos]["state"] = self.opened_cell
            self.focused_cell_pos = pos
        elif self.cells[pos]["state"] == self.opened_cell:
            # セルがopenかつfocusなら、bombにする
            if self.focused_cell_pos == pos:
                self.cells[pos]["state"] = self.bomb_cell
                self.focused_cell_pos = (-1, -1)
            # セルがopenかつfocusしていないなら、focusする
            else:
                self.focused_cell_pos = pos
        # セルがそれ以外なら、closeにする
        else:
            self.cells[pos]["state"] = self.closed_cell
            self.focused_cell_pos = (-1, -1)

        # セルを描画する
        for i in range(self.field_size):
            for j in range(self.field_size):
                pos = (i, j)
                text, fg_color, border_width = self.get_cell_text_fgc_bwidth(self.cells[pos], pos)
                self.cells[pos]["cell"].configure(
                    text=text,
                    fg_color=fg_color,
                    border_width=border_width
                )

        # 地雷の個数をカウント
        bomb_count = 0
        for i in range(self.field_size):
            for j in range(self.field_size):
                pos = (i, j)
                if self.cells[pos]["state"] == self.bomb_cell:
                    bomb_count += 1
        self.mine_found = bomb_count
        self.field_info_text.configure(text=self.get_field_info_text())

        # セルのルールセレクタの状態を変更
        self.cell_rule_scope_checkbox.configure(state=self.is_cell_focused())
        self.cell_rule_selector.configure(state=self.is_cell_focused())
        self.set_cell_rule_selector_value()
        self.cell_number_entry.configure(state=self.is_cell_focused())
        self.cell_number_button.configure(state=self.is_cell_focused())

    def display_setting(self):
        """設定部分の画面を描画する関数"""
        # 設定フレームの配置
        self.setting_frame = ctk.CTkFrame(self)
        self.setting_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.setting_frame.columnconfigure(0, weight=1)

        # フィールドサイズ変更フレームの配置
        self.field_size_frame = ctk.CTkFrame(self.setting_frame)
        self.field_size_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.field_size_frame.columnconfigure(0, weight=1)

        # フィールドサイズ変更テキストの配置
        self.change_field_size_text = ctk.CTkLabel(self.field_size_frame, text="Change Minesweeper Size")
        self.change_field_size_text.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

        # フィールドサイズ変更ドロップダウンメニューの配置
        self.field_size_selector = ctk.CTkComboBox(
            self.field_size_frame,
            values=list(self.field_size_dict.keys()),
            command=self.change_field_size)
        self.field_size_selector.set(self.field_size_dict_v2k(self.field_size))
        self.field_size_selector.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        # フィールドルール変更フィールドの配置
        self.field_rule_frame = ctk.CTkFrame(self.setting_frame)
        self.field_rule_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.field_rule_frame.columnconfigure(0, weight=1)

        # フィールドルール変更テキストの配置
        self.change_field_rule_text = ctk.CTkLabel(self.field_rule_frame, text="Change Field Rule")
        self.change_field_rule_text.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

        # フィールドルール変更ドロップダウンメニューの配置
        self.field_rule_selector = ctk.CTkComboBox(
            self.field_rule_frame,
            values=list(self.field_rule_dict.keys()),
            command=self.change_field_rule)
        self.field_rule_selector.set(self.field_rule_dict_v2k(self.field_rule))
        self.field_rule_selector.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        # セルルール変更フィールドの配置
        self.cell_rule_num_frame = ctk.CTkFrame(self.setting_frame)
        self.cell_rule_num_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.cell_rule_num_frame.columnconfigure(0, weight=1)

        # セルルール変更テキストの配置
        self.change_cell_rule_text = ctk.CTkLabel(self.cell_rule_num_frame, text="Change Cell Rule")
        self.change_cell_rule_text.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

        # セルルール変更チェックボックスの配置
        self.cell_rule_scope_checkbox = ctk.CTkCheckBox(
            self.cell_rule_num_frame,
            text="Change all cell")
        self.cell_rule_scope_checkbox.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        # セルルール変更ドロップダウンメニューの配置
        self.cell_rule_selector = ctk.CTkComboBox(
            self.cell_rule_num_frame,
            values=list(self.cell_rule_dict.keys()),
            state=self.is_cell_focused(),
            command=self.change_cell_rule)
        self.set_cell_rule_selector_value()
        self.cell_rule_selector.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")

        # セル数値変更テキストの配置
        self.change_cell_number_text = ctk.CTkLabel(
            self.cell_rule_num_frame,
            text="Change Cell Number\n(For multi, separate with comma)")
        self.change_cell_number_text.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")

        # セル数値変更エントリーの配置
        self.cell_number_entry = ctk.CTkEntry(
            self.cell_rule_num_frame,
            state=self.is_cell_focused())
        self.cell_number_entry.grid(row=4, column=0, padx=10, pady=5, sticky="nsew")

        # セル数値変更ボタンの配置
        self.cell_number_button = ctk.CTkButton(
            self.cell_rule_num_frame,
            text="confirm cell number",
            state=self.is_cell_focused(),
            command=self.change_cell_number)
        self.cell_number_button.grid(row=5, column=0, padx=10, pady=5)

        self.field_info_frame = ctk.CTkFrame(self.setting_frame)
        self.field_info_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew", rowspan=3)
        self.field_info_frame.columnconfigure(0, weight=1)

        # フィールド情報表示テキストの配置
        self.field_info_text = ctk.CTkLabel(
            self.field_info_frame,
            justify="left",
            text=self.get_field_info_text())
        self.field_info_text.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # 解探索ボタンの配置
        self.solve_button = ctk.CTkButton(
            self.field_info_frame,
            text="find safe cell",
            command=self.solve_field)
        self.solve_button.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # 盤面保存ボタンの配置
        self.save_button = ctk.CTkButton(
            self.field_info_frame,
            text="save as json",
            command=self.save_field)
        self.save_button.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        # 盤面読み込みボタンの配置
        self.load_button = ctk.CTkButton(
            self.field_info_frame,
            text="load from json",
            command=self.load_field)
        self.load_button.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

    def change_field_size(self, key):
        """フィールドサイズが変更された際の挙動を管理する関数"""
        self.field_size = self.field_size_dict.get(key, self.default_field_size)
        self.init_field()
        self.init_cells()
        self.display_field()
        self.display_setting()

    def change_field_rule(self, key):
        """フィールドルールが変更された際の挙動を管理する関数"""
        self.field_rule = self.field_rule_dict.get(key, self.default_field_rule)
        self.field_info_text.configure(text=self.get_field_info_text())

    def get_field_info_text(self):
        """フィールドの情報(ルール・地雷数)を表示するためのテキストを生成する関数"""
        return f"field rule: {self.field_rule}\ntotal mine: {self.mine_total}\nfounded mine: {self.mine_found}"

    def is_cell_focused(self, boolean=False):
        """クリックされたセルが変更可能かを返す関数"""
        is_focused = (0 <= self.focused_cell_pos[0] and self.focused_cell_pos[0] < self.field_size and
                      0 <= self.focused_cell_pos[1] and self.focused_cell_pos[1] < self.field_size)
        if boolean is True:
            return is_focused
        else:
            if is_focused is True:
                return "normal"
            else:
                return "disabled"

    def set_cell_rule_selector_value(self):
        """セルルール選択用ドロップダウンメニューにテキストをセットする関数"""
        if self.is_cell_focused(boolean=True) is True:
            self.cell_rule_selector.set(
                self.cell_rule_dict_v2k(self.cells[self.focused_cell_pos]["cell_rule"]))
        else:
            self.cell_rule_selector.set("")

    def get_cell_text_fgc_bwidth(self, cell, pos):
        """セルの情報(ルール・数字)を表示するためのテキストを生成する関数"""
        state = cell["state"]
        cell_rule = cell["cell_rule"]
        cell_rule_text = self.cell_rule_dict_v2k(cell_rule)
        numbers_text = ",".join(map(str, cell["numbers"]))

        text = ""
        fg_color = ""
        border_width = 0
        if state == self.opened_cell:
            if cell_rule == "hidden":
                text = cell_rule_text
                fg_color = "blue"
            else:
                text = f"{cell_rule_text}\n{numbers_text}"
                fg_color = "blue"
        elif state == self.bomb_cell:
            text = "BOMB"
            fg_color = "red"
        else:
            text = ""
            fg_color = "black"
        if self.focused_cell_pos == pos:
            border_width = 2
        else:
            border_width = 0
        return text, fg_color, border_width

    def change_cell_rule(self, key):
        """セルルールが変更された際の挙動を管理する関数"""
        if self.is_cell_focused() == "normal" and\
           self.cells[self.focused_cell_pos]["state"] == "open":
            if self.cell_rule_scope_checkbox.get() == 0:
                self.cells[self.focused_cell_pos]["cell_rule"] = self.cell_rule_dict.get(key, self.default_cell_rule)
                text, fg_color, border_width = self.get_cell_text_fgc_bwidth(
                    self.cells[self.focused_cell_pos], self.focused_cell_pos)
                self.cells[self.focused_cell_pos]["cell"].configure(
                    text=text, fg_color=fg_color, border_width=border_width)
            else:
                for i in range(self.field_size):
                    for j in range(self.field_size):
                        pos = (i, j)
                        self.cells[pos]["cell_rule"] = self.cell_rule_dict.get(key, self.default_cell_rule)
                        text, fg_color, border_width = self.get_cell_text_fgc_bwidth(self.cells[pos], pos)
                        self.cells[pos]["cell"].configure(
                            text=text, fg_color=fg_color, border_width=border_width)

    def change_cell_number(self):
        """セルの数字が変更された際の挙動を管理する関数"""
        cell_numbers = []
        for num in self.cell_number_entry.get().split(","):
            if num.strip().isdigit():
                cell_numbers.append(int(num))
        if self.is_cell_focused() == "normal" and\
           self.cells[self.focused_cell_pos]["state"] == "open":
            self.cells[self.focused_cell_pos]["numbers"] = cell_numbers
            text, fg_color = self.get_cell_text_fgc_bwidth(self.cells[self.focused_cell_pos])
            self.cells[self.focused_cell_pos]["cell"].configure(
                text=text, fg_color=fg_color)

    def solve_field(self):
        print("now solving...(eternally)")

    def save_field(self):
        """フィールド盤面をjsonに出力する関数"""
        field_dict = self.field_to_dict()
        with open("./json/field.json", "w") as f:
            json.dump(field_dict, f, indent=4)
        print("save completed")

    def load_field(self):
        """jsonに出力したフィールドを読み込む関数"""
        with open("./json/field.json") as f:
            field_dict = json.load(f)
        print("load completed")

        self.init_field(
            field_size=field_dict["field_size"],
            field_rule=field_dict["field_rule"],
            mine_total=field_dict["mine_total"],
            mine_found=field_dict["mine_found"])

        self.init_cells_from_json(field_dict["cells"])

        self.display_field()
        self.display_setting()

    def field_to_dict(self):
        """フィールド盤面を辞書型に変換する関数"""
        field_dict = {}
        field_dict["field_size"] = self.field_size
        field_dict["mine_total"] = self.mine_total
        field_dict["mine_found"] = self.mine_found
        field_dict["field_rule"] = self.field_rule
        cell_list = []
        for i in range(self.field_size):
            for j in range(self.field_size):
                cell_dict = {}
                cell_dict["pos"] = (i, j)
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
