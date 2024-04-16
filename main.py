from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float

'''
On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)


# Creating and Initializing Database
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///library.db"
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CREATE TABLE
class Book(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)

    # Optional: this will allow each book object to be identified by its title when printed.
    def __repr__(self):
        return f'<Book {self.title}>'


# Create table schema in the database. Requires application context.
with app.app_context():
    db.create_all()


@app.route('/')
def home():
    # Read Records
    result = db.session.execute(db.select(Book).order_by(Book.title))
    all_books = result.scalars().all()
    return render_template("index.html", books=all_books)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        # Create Record
        new_book = Book(
            title=request.form["book_name"],
            author=request.form["author"],
            rating=request.form["rating"])
        db.session.add(new_book)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template("add.html")


@app.route("/edit", methods=["GET", "POST"])
def edit():
    book_id = request.args.get("id")
    book_to_update = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar()
    if request.method == "POST":
        book_to_update.rating = request.form["new_rating"]
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", updating=book_to_update)


@app.route("/delete")
def delete():
    book_id = request.args.get("id")
    book_to_delete = db.get_or_404(Book, book_id)
    db.session.delete(book_to_delete)
    db.session.commit()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
