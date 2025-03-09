
from app.models.sk_models import SKModel
from app.models.tf_models import TFModel

# Create shared instances
sk_model = SKModel()
tf_model = TFModel()

# Tracking variables
sk_model_trained = False
tf_model_trained = False

# Combined model_trained status
@property
def model_trained():
    return sk_model_trained or tf_model_trained