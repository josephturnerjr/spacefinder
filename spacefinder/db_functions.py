from models import db, Listing, Account


def init_db():
    db.drop_all()
    db.create_all()
    for i in range(1):
        db.session.add(Listing("1500 Union Ave #2500, Baltimore, MD",
                               "39.334497", "-76.64081",
                               "Headquarters for Maryland Nonprofits", "office", 2500,
                               """Set in beautiful downtown Baltimore, this is the perfect space for you.

1800 sq ft., with spacious meeting rooms.

Large windows, free wifi, free parking, quiet neighbors."""))
    db.session.add(Account("admin", "example@example.com", "Pass1234"))
    db.session.commit()
