from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os



# アプリの初期設定
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key' # 本番環境では複雑なキーに変更してください
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = './static/uploads'
db = SQLAlchemy(app)




# --- データベースモデル定義 ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)

class Slide(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    image_filename = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    order = db.Column(db.Integer, nullable=False)




# --- ページごとの処理（ルーティング） ---

# ログインページ
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username).first()
        if user:
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            return redirect(url_for('dashboard'))
    return render_template('login.html')

# 教材一覧ダッシュボード
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    courses = Course.query.all()
    return render_template('dashboard.html', courses=courses)

# 学習ページ（スライドショー）
@app.route('/course/<int:course_id>')
def course(course_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    slides = Slide.query.filter_by(course_id=course_id).order_by(Slide.order).all()
    course = Course.query.get(course_id)
    return render_template('course.html', slides=slides, course_title=course.title)

# 管理者ページ
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('is_admin'):
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        course_id = request.form['course_id']
        description = request.form['description']
        order = request.form['order']
        file = request.files['image']
        
        if file:
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            new_slide = Slide(course_id=course_id, image_filename=filename, description=description, order=order)
            db.session.add(new_slide)
            db.session.commit()
    
    courses = Course.query.all()
    return render_template('admin.html', courses=courses)


# ログアウト
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    # データベースと初期データ作成
    with app.app_context():
        db.create_all()
        # ユーザーがいない場合、サンプルユーザーを作成
        if not User.query.first():
            user = User(username='student', is_admin=False)
            admin = User(username='admin', is_admin=True)
            db.session.add(user)
            db.session.add(admin)
            db.session.commit()
        # コースがない場合、サンプルコースを作成
        if not Course.query.first():
            course1 = Course(title='知的財産権入門')
            db.session.add(course1)
            db.session.commit()
@app.route('/admin/manage', methods=['GET', 'POST'])
def manage_slides():
    # 管理者でなければダッシュボードへリダイレクト
    if not session.get('is_admin'):
        return redirect(url_for('dashboard'))

    # 削除リクエスト（POST）があった場合の処理
    if request.method == 'POST':
        slide_id_to_delete = request.form.get('slide_id')
        slide = Slide.query.get(slide_id_to_delete)
        if slide:
            # 1. 画像ファイルをサーバーから物理的に削除
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], slide.image_filename)
            if os.path.exists(image_path):
                os.remove(image_path)
            
            # 2. データベースからスライドの記録を削除
            db.session.delete(slide)
            db.session.commit()
        return redirect(url_for('manage_slides'))

    # 一覧表示（GET）の処理
    # コース情報も併せて取得し、コース名と表示順で並び替え
    slides_with_courses = db.session.query(Slide, Course).join(Course, Slide.course_id == Course.id).order_by(Course.title, Slide.order).all()
    
    return render_template('manage_slides.html', slides_with_courses=slides_with_courses)

app.run(debug=True,port=os.getenv('PORT', 5000))
# --- JavaScriptのスライドショー機能 ---