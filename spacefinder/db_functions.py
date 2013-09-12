from models import db, Listing


def init_db():
    db.drop_all()
    db.create_all()
    db.session.add(Listing("1500 Union Ave #2500, Baltimore, MD", "39.334497","-76.64081", "office", 2500, "Headquarters for Maryland Nonprofits"))
    db.session.commit()
