from chatbot_webservice.utils import LossService

ls = LossService(5, 'failure', 120)
ls.compute_resilience_loss()
