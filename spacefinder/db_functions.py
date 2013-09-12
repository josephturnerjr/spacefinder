from models import db


def init_db():
    db.drop_all()
    db.create_all()
    ##db.session.add(Redirect("docs", "/turnerj9/Documentation-and-Info"))
    ##db.session.commit()
