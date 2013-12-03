from models import db, Listing, Account, ListingType, RateType


def init_db():
    db.drop_all()
    db.create_all()
    type_ids = {}
    rate_type_ids = {}
    for type_name in ["office", "meeting", "other"]:
        t = ListingType(type_name)
        db.session.add(t)
        db.session.commit()
        type_ids[type_name] = t
    for type_name in ["Hour", "Day", "Week", "Month", "3 Months", "6 Months", "Year"]:
        t = RateType(type_name)
        db.session.add(t)
        db.session.commit()
        rate_type_ids[type_name] = t
    db.session.add(Listing("1500 Union Ave #2500, Baltimore, MD",
                           "39.334497", "-76.64081",
                           "Headquarters for Maryland Nonprofits", type_ids["office"], 2500,
                           """Set in beautiful downtown Baltimore, this is the perfect space for you.

1800 sq ft., with spacious meeting rooms.

Large windows, free wifi, free parking, quiet neighbors.""", rate_type=rate_type_ids['Month']))
    db.session.add(Listing("6695 Dobbin Rd, Columbia, MD",
                           "39.186198", "-76.824842",
                           "Frisco Taphouse and Brewery", type_ids["meeting"], 1700,
                           """Large open space in a quiet subdivision near Columbia.

High ceilings, lots of parking, good beer selection.""", rate_type=rate_type_ids['Day']))
    db.session.add(Account("admin", "example@example.com", "Pass1234"))
    db.session.commit()
