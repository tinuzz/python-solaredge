from peewee import *

db_proxy = Proxy()

class BaseModel(Model):
    class Meta:
        database = db_proxy

class Inverter(BaseModel):
    dev_id = CharField()
    timestamp = TimestampField()
    date = CharField()
    time = CharField()
    uptime = BigIntegerField()
    interval = IntegerField()
    mode = SmallIntegerField()
    v_ac = FloatField()
    v_dc = FloatField()
    i_ac = FloatField()
    p_active = FloatField()
    p_apparent = FloatField()
    p_reactive = FloatField()
    p_max = FloatField()
    e_day = FloatField()
    e_total = FloatField()
    frequency = FloatField()
    temperature = FloatField()
    pf_pct = FloatField()
    cos_phi = FloatField()
    e_ac_intv = FloatField()
    i_dc = FloatField()
    i_rcd = FloatField()
    i_out_dc = FloatField()

class Optimizer(BaseModel):
    dev_id = CharField()
    timestamp = TimestampField()
    date = CharField()
    time = CharField()
    uptime = BigIntegerField()
    v_in = FloatField()
    v_out = FloatField()
    i_in = FloatField()
    e_day = FloatField()
    temperature = FloatField()

class Event(BaseModel):
    dev_id = CharField()
    timestamp = TimestampField()
    date = CharField()
    time = CharField()
    e_type = SmallIntegerField()
    param1 = IntegerField()
    param2 = IntegerField()
    param3 = IntegerField()
    param4 = IntegerField()
    param5 = IntegerField()
