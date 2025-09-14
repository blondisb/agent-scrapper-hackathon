import datetime
from typing import Optional

def log_normal(data, where: Optional[str] = None):
    dttn = datetime.datetime.now()
    print(
        f"\n{dttn} || {where} || MSG: {data}"
    )

def log_error(data,  where: Optional[str] = None):
    dttn = datetime.datetime.now()
    print(
        f"\n============================\n {dttn} || {where} || ERROR: {data} \n\n"
    )
