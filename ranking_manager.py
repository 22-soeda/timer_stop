class RankingManager:
    def __init__(self):
        # ランキングを保持するリスト
        self.ranking = []
        
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
            
    def get_ranking(self):
        return self.ranking
        
    def clear_all(self):
        # 【clear】リストの中身をすべて空にする（※今回はリセット用として用意）
        self.ranking.clear()