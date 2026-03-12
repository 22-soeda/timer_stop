import json
import os

class RankingManager:
    def __init__(self):
        # 保存先ファイルのパス
        self.filename = 'ranking_data.json'
        self.ranking = []
        
        # クラスが呼び出された時、ファイルがあれば読み込む
        self.load_data()
        
    def load_data(self):
        """JSONファイルからランキングデータを読み込む"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    self.ranking = json.load(f)
            except json.JSONDecodeError:
                # ファイルが空や壊れている場合は空リストで初期化
                self.ranking = []
        else:
            self.ranking = []

    def save_data(self):
        """ランキングデータをJSONファイルに保存する"""
        with open(self.filename, 'w', encoding='utf-8') as f:
            # 日本語が文字化けしないように ensure_ascii=False を指定
            json.dump(self.ranking, f, ensure_ascii=False, indent=4)

    def add_record(self, name, score, diff):
        record = {"name": name, "score": score, "diff": diff}
        
        # 【in】リスト内にすでに同じ名前のプレイヤーがいるかチェック
        existing_names = [r["name"] for r in self.ranking]
        if name in existing_names:
            # 【index】指定したプレイヤーがリストの何番目にいるかを取得
            idx = existing_names.index(name)
            
            # 既存のスコアより今回の方が高ければ、更新するために古い記録を削除
            if score > self.ranking[idx]["score"]:
                # 【pop】指定したインデックスの要素を取り除いて削除
                self.ranking.pop(idx)
            else:
                # 今回のスコアが自己ベスト以下なら追加せずに終了
                return

        # スコアが高い順になるように挿入場所を探す
        inserted = False
        for i in range(len(self.ranking)):
            if score > self.ranking[i]["score"]:
                # 【insert】指定した位置に要素を割り込ませる
                self.ranking.insert(i, record)
                inserted = True
                break
        
        # 既存のどのスコアよりも低かった（またはリストが空だった）場合は末尾に追加
        if not inserted:
            # 【append】リストの最後に要素を追加
            self.ranking.append(record)
            
        # ランキングが5件を超えたら、末尾（最も低いスコア）を取り除いて上位5名を維持
        while len(self.ranking) > 5:
            # 引数なしの pop() はリストの一番最後を削除します
            self.ranking.pop()
            
        # ★記録が更新されたので、ファイルに保存する★
        self.save_data()
            
    def get_ranking(self):
        return self.ranking
        
    def clear_all(self):
        # 【clear】リストの中身をすべて空にする
        self.ranking.clear()
        # ★クリアした状態をファイルに保存する★
        self.save_data()