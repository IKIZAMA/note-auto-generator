import json
import random
import os
import google.generativeai as genai
from datetime import datetime

class NoteArticleGenerator:
    def __init__(self):
        self.gemini_api_key = os.environ.get('GEMINI_API_KEY')
        
        # Gemini AI設定
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
    def load_themes(self):
        """テーマファイルを読み込む"""
        with open('src/themes.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_used_themes(self):
        """使用済みテーマを読み込む"""
        try:
            with open('src/used_themes.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"used_theme_ids": []}
    
    def save_used_themes(self, used_themes):
        """使用済みテーマを保存"""
        with open('src/used_themes.json', 'w', encoding='utf-8') as f:
            json.dump(used_themes, f, ensure_ascii=False, indent=2)
    
    def select_theme(self):
        """未使用のテーマを選択"""
        themes_data = self.load_themes()
        used_themes = self.load_used_themes()
        
        # 未使用のテーマを抽出
        available_themes = [
            theme for theme in themes_data['themes'] 
            if theme['id'] not in used_themes['used_theme_ids']
        ]
        
        # 全テーマを使い切った場合はリセット
        if not available_themes:
            used_themes['used_theme_ids'] = []
            available_themes = themes_data['themes']
            print("全テーマを使用完了。リセットしました。")
        
        # ランダムに選択
        selected_theme = random.choice(available_themes)
        
        # 使用済みリストに追加
        used_themes['used_theme_ids'].append(selected_theme['id'])
        self.save_used_themes(used_themes)
        
        return selected_theme
    
    def generate_article(self, theme):
        """AIで記事を生成"""
        prompt = f"""
以下のテーマで、読者が思わずスキを押したくなったり、チップをあげたくなるような魅力的なNote記事を作成してください。

テーマ: {theme['title']}
カテゴリ: {theme['category']}
キーワード: {', '.join(theme['keywords'])}

記事の要件:
- 文字数: 1000-1500文字程度
- 読者の心を動かす感動的なストーリー要素を含む
- 実体験に基づいているような具体的なエピソード
- 読者が「これは役に立つ！」と感じる実用的な内容
- 読者が「共感できる」と思える悩みや体験
- 読者が「試してみたい」と思う具体的な行動指針
- 親しみやすく、まるで友人が話しかけているような文体
- 読者の背中を押すような励ましの言葉
- 著作権に配慮したオリジナルコンテンツ

構成:
1. キャッチーなタイトル（読者の興味を引く）
2. 共感できる導入（読者の悩みに寄り添う）
3. 具体的な体験談やエピソード
4. 実践的な解決策（3-5つのポイント）
5. 読者への励ましと行動を促すまとめ
6. 読者との交流を促す呼びかけ

読者がスキを押したくなる要素:
- 心に響く言葉や表現
- 「わかる！」と共感できる内容
- 具体的で実践しやすい方法
- 読者の成長を応援するメッセージ
- 読者とのつながりを感じられる文章

以下の形式で出力してください:
# [ここにタイトル]

[ここに記事本文]

---
使用テーマ: {theme['title']}
カテゴリ: {theme['category']}
生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"記事生成エラー: {e}")
            return None
    
    def save_article(self, content, theme):
        """記事をファイルに保存"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # タイトルを抽出（ファイル名用）
        lines = content.split('\n')
        title_line = lines[0] if lines else "無題"
        title = title_line.replace('# ', '').strip()
        
        # ファイル名に使えない文字を置換
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title[:50]  # 長さ制限
        
        filename = f"generated_articles/{today}_{safe_title}.md"
        
        # フォルダが存在しない場合は作成
        os.makedirs('generated_articles', exist_ok=True)
        
        # ファイルに保存
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"記事を保存しました: {filename}")
        return filename
    
    def run(self):
        """メイン処理"""
        print(f"記事生成開始: {datetime.now()}")
        
        # テーマ選択
        theme = self.select_theme()
        print(f"選択されたテーマ: {theme['title']}")
        
        # 記事生成
        article = self.generate_article(theme)
        if not article:
            print("記事生成に失敗しました")
            return False
        
        print("記事生成完了")
        
        # 記事をファイルに保存
        filename = self.save_article(article, theme)
        
        # 記事の一部を表示
        print("-" * 50)
        print("生成された記事の冒頭:")
        print(article[:300] + "...")
        print("-" * 50)
        print(f"記事ファイル: {filename}")
        print("手動でNoteに投稿してください。")
        
        return True

if __name__ == "__main__":
    generator = NoteArticleGenerator()
    generator.run()
