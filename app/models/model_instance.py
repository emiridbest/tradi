from app.models.sk_models import SKModel

# Create a singleton instance of the model
sk_model = SKModel()
sk_model_trained = False

def reset_model():
    """Reset the model to untrained state."""
    global sk_model, sk_model_trained
    sk_model = SKModel()
    sk_model_trained = False
    return {
        'status': 'success',
        'message': 'Model has been reset to untrained state'
    }