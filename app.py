from flask import Flask, jsonify, request, render_template
import random
# 分割したランキング管理モジュールを読み込む
from ranking_manager import RankingManager

app = Flask(__name__)
# ランキング管理クラスのインスタンス化
ranking_mgr = RankingManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start', methods=['GET'])
def start_game():
    target_seconds = random.randint(6, 15)
    return jsonify({"target_seconds": target_seconds})

@app.route('/api/evaluate', methods=['POST'])
def evaluate():
    data = request.json
    target_seconds = data.get('target_seconds')
    actual_seconds = data.get('actual_seconds')
    # フロントエンドから名前を受け取る（空の場合は「ゲスト」）
    player_name = data.get('player_name', 'ゲスト').strip()
    if not player_name:
        player_name = 'ゲスト'
    
    diff = round(actual_seconds - target_seconds, 2)
    abs_diff = abs(diff)
    
    # 🌟 独自のスコア演算アルゴリズム 🌟
    # 1. 基本点：1000点満点。誤差1秒につき500点減点（最低0点）
    base_score = max(0, 1000 - (abs_diff * 500))
    # 2. 難易度ボーナス：目標秒数が長いほど倍率アップ（1秒につき+5%のボーナス）
    difficulty_multiplier = 1.0 + (target_seconds * 0.05)
    # 3. 最終スコア算出
    final_score = int(base_score * difficulty_multiplier)
    
    if abs_diff <= 0.5:
        message = "素晴らしい！ほぼピッタリです！👏"
    elif abs_diff <= 1.5:
        message = "おしい！いい線いってます👍"
    else:
        message = "まだまだですね。体感を鍛えましょう！💪"
        final_score = 0 # 誤差が大きすぎる場合は0点
        
    # スコアが0より大きければランキングに登録を試みる
    if final_score > 0:
        ranking_mgr.add_record(player_name, final_score, diff)
        
    return jsonify({
        "diff": diff,
        "score": final_score,
        "message": message,
        "ranking": ranking_mgr.get_ranking()
    })

# 最新のランキングを取得するAPI
@app.route('/api/ranking', methods=['GET'])
def get_ranking():
    return jsonify(ranking_mgr.get_ranking())

if __name__ == '__main__':
    app.run(debug=True)