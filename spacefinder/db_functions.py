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
    db.session.add(Listing(address="1500 Union Ave #2500, Baltimore, MD",
                           lat="39.334497", lon="-76.64081",
                           name="Headquarters for Maryland Nonprofits", space_type=type_ids["office"], price=2500,
                           description="""Set in beautiful downtown Baltimore, this is the perfect space for you.

1800 sq ft., with spacious meeting rooms.

Large windows, free wifi, free parking, quiet neighbors.""", contact_phone="55555555555", rate_type=rate_type_ids['Month']))
    db.session.add(Listing(address="6695 Dobbin Rd, Columbia, MD",
                           lat="39.186198", lon="-76.824842",
                           name="Frisco Taphouse and Brewery", space_type=type_ids["meeting"], price=1700,
                           description="""Large open space in a quiet subdivision near Columbia.

High ceilings, lots of parking, good beer selection.""", rate_type=rate_type_ids['Day'], contact_phone="55555555555", expires_in_days=-1))
    db.session.add(Account("admin", "example@example.com", "Pass1234"))
    db.session.commit()
