from app.models.sk_models import SKModel

# Create shared instances
sk_model = SKModel()

# Tracking variables
sk_model_trained = False

def reset_model():
    """Reset the model to untrained state"""
    global sk_model, sk_model_trained
    sk_model = SKModel()  # Create a new instance
    sk_model_trained = False
    return {"status": "reset", "message": "Model reset successfully"}
