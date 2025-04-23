from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from .models import Chatbot
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            question = request.data.get("question")

            embedding = OpenAIEmbeddings()
            vectorstore = Chroma(persist_directory="./db", embedding_function=embedding)
            retriever = vectorstore.as_retriever()

            qa = RetrievalQA.from_chain_type(
                llm=OpenAI(),
                retriever=retriever
            )
            answer = qa.run(question)

            # Simpan ke database
            Chatbot.objects.create(
                user=request.user,
                question=question,
                answer=answer
            )

            # Return response
            return Response({
                "status": 201,
                "data": {
                    "answer": answer
                }
            }, status=201)

        except Exception as e:
            return Response({
                "status": 500,
                "error": str(e)
            }, status=500)
