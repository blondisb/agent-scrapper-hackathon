import datetime

dttn = datetime.datetime.now()

def log_normal(data):
    print(
        f"\n{dttn} || MSG: {data}"
    )

def log_error(data):
    print(
        f"\n============================\n {dttn} || ERROR: {data} \n\n"
    )
