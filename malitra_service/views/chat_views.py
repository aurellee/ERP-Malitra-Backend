from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from django.contrib.auth import get_user_model
from malitra_service.models import Chatbot
from malitra_service.serializers.chat_serializers import ChatRequestSerializer, ChatResponseSerializer, ChatbotSerializer
import os
from langchain import LLMChain, PromptTemplate
from rest_framework.generics import ListAPIView

User = get_user_model()

# # one-time LLM setup for translation and spell correction
llm_for_prep = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    temperature=0,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)
# # Translator: Bahasa Indonesia -> English
# translate_prompt = PromptTemplate.from_template(
#     """
# Translate this question into English, preserving the original meaning:

# {question}

# English:
# """
# )
# translator = LLMChain(llm=llm_for_prep, prompt=translate_prompt)

# Spell-corrector for English question
spell_fix_prompt = PromptTemplate.from_template(
    """
Fix the spelling in this English question, preserving meaning:

{question}

Corrected:
"""
)
corrector = LLMChain(llm=llm_for_prep, prompt=spell_fix_prompt)

class ChatView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"status": 400, "error": serializer.errors}, status=400)

        user_id     = serializer.validated_data["user_id"]
        raw_question = serializer.validated_data["question"].strip()

        # 2) Spell-correct the English question
        fixed_question = corrector.run(raw_question)

        # 3) Load JSON-based index
        emb     = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
        vectordb = Chroma(persist_directory="./db", embedding_function=emb)

        # 4) Retrieve with higher k
        retriever = vectordb.as_retriever(search_kwargs={"k": 12})

        # 5) Map-reduce QA
        llm = ChatOpenAI(
            model_name="gpt-4.1",
            temperature=0,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        qa = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            chain_type="map_reduce",
            return_source_documents=False
        )

        # 6) Run QA on the prepared question
        answer = qa.run(fixed_question)

        # 7) Persist chat record using raw question
        user = User.objects.get(id=user_id)
        Chatbot.objects.create(
            user=user,
            question=raw_question,
            answer=answer
        )

        # 8) Return
        response_data = {"user_id": user.id, "answer": answer}
        serialized = ChatResponseSerializer(response_data)
        return Response({"status": 201, "data": serialized.data}, status=201)

class ChatListView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({"status": 400, "error": "user_id is required"}, status=400)

        # Fetch the 5 most recent chats for this user
        chats = Chatbot.objects.filter(user__id=user_id).order_by('-timestamp')[:5]
        serializer = ChatbotSerializer(chats, many=True)

        return Response({
            "status": 200,
            "data": serializer.data
        })
