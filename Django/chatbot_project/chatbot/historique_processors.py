from .models import Conversation

def conversations_processor(request):
    """Context processor to add conversations to all templates"""
    conversations = Conversation.objects.all().order_by('-created_at')[:10]  # Get 10 most recent conversations
    return {'conversations': conversations}
