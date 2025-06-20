from App.DB_side_of_the_Force import dew_it
from App.ETL_DWH import db_fülle
from App.Dashboard import *

if __name__ == "__main__":
    dew_it()
    db_fülle()
    app.run()
