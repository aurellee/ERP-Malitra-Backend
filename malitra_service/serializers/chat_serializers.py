from rest_framework import serializers
from malitra_service.models import Chatbot

class ChatRequestSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    question = serializers.CharField(max_length=1000)
    
class ChatResponseSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    answer = serializers.CharField()
    
class ChatbotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chatbot
        fields = ['question', 'answer', 'timestamp']
        read_only_fields = ['question', 'answer', 'timestamp']