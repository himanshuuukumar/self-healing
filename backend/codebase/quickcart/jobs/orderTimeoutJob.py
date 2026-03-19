def cancel_timed_out_orders():
    try:
        raise Exception("DB Connection Lost")
    except:
        # Intentional bug: bare except pass
        pass
