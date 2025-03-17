import pytz

def local_time(dt):
    """Converte UTC para horário local"""
    if dt:
        local_tz = pytz.timezone('America/Sao_Paulo')
        local_dt = dt.replace(tzinfo=pytz.UTC).astimezone(local_tz)
        return local_dt.strftime('%d/%m/%Y %H:%M')
    return '' 