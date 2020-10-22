from enum import Enum


class Intent(Enum):
    SELECT_SERVICE = 'Select Service'
    SHOW_SPECIFICATION = 'Show Specification'
    SPECIFICATION = 'Specification'


class Param(Enum):
    SERVICE_NAME = 'service_name'
    TB_CAUSE = 'tb_cause'
    INITIAL_LOSS = 'initial_loss'
    RECOVERY_TIME = 'recovery_time'
    AMOUNT = 'amount'
    UNIT = 'unit'
    LOSS_OFF_RESILIENCE = 'loss_of_resilience'


class ReqParam(Enum):
    QUERY_RESULT = 'queryResult'
    INTENT = 'intent'
    DISPLAY_NAME = 'displayName'
    PARAMETERS = 'parameters'
    SERVICE_NAME = 'service_name'
    TB_CAUSE = 'tb_cause'
    INITIAL_LOSS = 'initial_loss'
    RECOVERY_TIME = 'recovery_time'
    AMOUNT = 'amount'
    UNIT = 'unit'
    LOSS_OFF_RESILIENCE = 'loss_of_resilience'
