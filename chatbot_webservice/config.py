

class Intent:
    SELECT_SERVICE = 'Select Service'
    SHOW_SPECIFICATION = 'Show Specification'
    ADD_SPECIFICATION = 'Add Specification'
    DELETE_SPECIFICATION = 'Delete Specification'
    EDIT_SPECIFICATION_LOSS = 'Edit specification loss'
    EDIT_SPECIFICATION_RECOVERY_TIME = 'Edit Specification recovery time'


class Param:
    SERVICE_NAME = 'service_name'
    TB_CAUSE = 'tb_cause'
    INITIAL_LOSS = 'initial_loss'
    RECOVERY_TIME = 'recovery_time'
    AMOUNT = 'amount'
    UNIT = 'unit'
    LOSS_OFF_RESILIENCE = 'loss_of_resilience'
    SCENARIO = 'scenario'


class ReqParam:
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
    SCENARIO = 'scenario'


class TbCause:
    FAILURE = 'failure'
    DEPLOYMENT = 'deployment'
    LOAD_BALANCING = 'load-balancing'
